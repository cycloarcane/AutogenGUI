import tkinter as tk
from tkinter import messagebox, ttk
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
import threading
import sys
import os
import requests
import tempfile
from pypdf import PdfReader
from docx import Document
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

class AgentConfig:
    def __init__(self, name, system_message):
        self.name = name
        self.system_message = system_message

class AppConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "default-api-key")
        self.default_base_url = "http://127.0.0.1:5000/v1/"
        self.config_list = [
            {
                "model": "gpt-4o-mini",
                "api_key": self.api_key,
                "tags": ["gpt-4o-mini"]
            }
        ]
        self.llm_config = {"config_list": self.config_list, "cache_seed": 42}
        self.context_documents = []

class DocumentHandler:
    @staticmethod
    def read_document(path):
        try:
            if path.startswith('http://') or path.startswith('https://'):
                return DocumentHandler._read_url_document(path)
            else:
                return DocumentHandler._read_local_document(path)
        except Exception as e:
            logger.error(f"Error reading document: {e}")
            raise

    @staticmethod
    def _read_url_document(url):
        response = requests.get(url)
        response.raise_for_status()
        if url.endswith('.pdf'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                return DocumentHandler._read_pdf(temp_file.name)
        elif url.endswith('.docx'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(response.content)
                return DocumentHandler._read_docx(temp_file.name)
        else:
            return response.text

    @staticmethod
    def _read_local_document(path):
        if path.endswith('.pdf'):
            return DocumentHandler._read_pdf(path)
        elif path.endswith('.docx'):
            return DocumentHandler._read_docx(path)
        else:
            with open(path, 'r') as file:
                return file.read()

    @staticmethod
    def _read_pdf(file_path):
        reader = PdfReader(file_path)
        return '\n'.join([page.extract_text() for page in reader.pages])

    @staticmethod
    def _read_docx(file_path):
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])

class AgentManager:
    def __init__(self, app_config):
        self.app_config = app_config
        self.agents = {}
        self.groupchat = None
        self.manager = None

    def create_agents(self, agent_configs):
        for config in agent_configs:
            self.agents[config.name] = autogen.AssistantAgent(
                name=config.name,
                llm_config=self.app_config.llm_config,
                system_message=config.system_message,
            )

        self.agents['user_proxy'] = autogen.UserProxyAgent(
            name="User_proxy",
            system_message="A human admin.",
            code_execution_config={
                "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
            },
            human_input_mode="TERMINATE",
        )

        writer = self.agents.get('Writer')
        critic = self.agents.get('Critic')
        agent1 = self.agents.get('Agent1')
        agent2 = self.agents.get('Agent2')
        agent3 = self.agents.get('Agent3')

        if writer and critic and agent1 and agent2 and agent3:
            self.agents['user_proxy'].register_nested_chats(
                [
                    {"recipient": critic, "message": self.reflection_message, "summary_method": "last_msg", "max_turns": 1},
                    {"recipient": agent1, "message": self.refine_message, "summary_method": "last_msg", "max_turns": 1},
                    {"recipient": agent2, "message": self.fact_check_message, "summary_method": "last_msg", "max_turns": 1},
                    {"recipient": agent3, "message": self.summarize_message, "summary_method": "last_msg", "max_turns": 1}
                ],
                trigger=writer,
            )

            self.groupchat = autogen.GroupChat(agents=list(self.agents.values()), messages=[], max_round=12, speaker_selection_method="round_robin")
            self.manager = autogen.GroupChatManager(groupchat=self.groupchat, llm_config=self.app_config.llm_config)

    @staticmethod
    def reflection_message(recipient, messages, sender, config):
        return f"Reflect and provide critique on the following writing. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

    @staticmethod
    def refine_message(recipient, messages, sender, config):
        return f"Please refine the following content based on the feedback provided. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

    @staticmethod
    def fact_check_message(recipient, messages, sender, config):
        return f"Please fact-check the following content and ensure its accuracy. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

    @staticmethod
    def summarize_message(recipient, messages, sender, config):
        return f"Please summarize the following content in a concise manner. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("3AgentGCExec")
        self.configure(bg="black")
        self.app_config = AppConfig()
        self.agent_manager = AgentManager(self.app_config)
        self.document_handler = DocumentHandler()
        self.create_widgets()

    def create_widgets(self):
        self.create_url_frame()
        self.create_agent_frame()
        self.create_document_frame()
        self.create_input_frame()
        self.create_output_frame()

    def create_url_frame(self):
        url_frame = ttk.Frame(self)
        url_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Label(url_frame, text="Enter Base URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.url_entry.insert(0, self.app_config.default_base_url)
        
        ttk.Button(url_frame, text="Set URL", command=self.update_config).grid(row=0, column=2)

    def create_agent_frame(self):
        agent_frame = ttk.Frame(self)
        agent_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.agent_configs = [
            AgentConfig("Agent1", "Agent 1 system message."),
            AgentConfig("Agent2", "Agent 2 system message."),
            AgentConfig("Agent3", "Agent 3 system message."),
            AgentConfig("Writer", "Writer agent system message."),
            AgentConfig("Critic", "Critic agent system message."),
        ]

        for i, config in enumerate(self.agent_configs):
            ttk.Label(agent_frame, text=f"{config.name} Name:").grid(row=i*2, column=0, sticky="w")
            name_entry = ttk.Entry(agent_frame, width=25)
            name_entry.grid(row=i*2+1, column=0, sticky="w")
            name_entry.insert(0, config.name)

            ttk.Label(agent_frame, text=f"{config.name} Message:").grid(row=i*2, column=1, sticky="w")
            message_entry = tk.Text(agent_frame, height=2, width=50)
            message_entry.grid(row=i*2+1, column=1, sticky="ew")
            message_entry.insert(tk.END, config.system_message)

            setattr(self, f"{config.name.lower()}_name_entry", name_entry)
            setattr(self, f"{config.name.lower()}_message_entry", message_entry)

        ttk.Button(agent_frame, text="Set Agent Config", command=self.update_agent_config).grid(row=len(self.agent_configs)*2, column=0, sticky="w", pady=10)

    def create_document_frame(self):
        document_frame = ttk.Frame(self)
        document_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(document_frame, text="Enter URL or File Path:").grid(row=0, column=0, sticky="w")
        self.document_entry = ttk.Entry(document_frame, width=60)
        self.document_entry.grid(row=1, column=0, sticky="ew")

        ttk.Button(document_frame, text="Update Documents", command=self.add_document).grid(row=2, column=0, sticky="w", pady=(5, 0))

    def create_input_frame(self):
        input_frame = ttk.Frame(self)
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        ttk.Label(input_frame, text="Enter initial prompt:").grid(row=0, column=0, sticky="w")
        self.input_text = tk.Text(input_frame, height=4, width=60)
        self.input_text.grid(row=1, column=0, sticky="ew")

        ttk.Button(input_frame, text="Start", command=self.handle_request).grid(row=2, column=0, sticky="w", pady=(5, 0))

    def create_output_frame(self):
        output_frame = ttk.Frame(self)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        sys.stdout = TextRedirector(self.output_text)
        sys.stderr = TextRedirector(self.output_text)

    def update_config(self):
        url = self.url_entry.get()
        if self.validate_url(url):
            self.app_config.config_list[0]["base_url"] = url
            self.agent_manager = AgentManager(self.app_config)
            messagebox.showinfo("Config Updated", "Base URL has been updated successfully!")
        else:
            messagebox.showerror("Invalid URL", "Please enter a valid URL.")

    def validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def update_agent_config(self):
        new_configs = []
        for config in self.agent_configs:
            name = getattr(self, f"{config.name.lower()}_name_entry").get()
            message = getattr(self, f"{config.name.lower()}_message_entry").get("1.0", tk.END).strip()
            new_configs.append(AgentConfig(name, message))

        self.agent_configs = new_configs
        self.agent_manager.create_agents(self.agent_configs)
        messagebox.showinfo("Config Updated", "Agent configurations have been updated successfully!")

    def add_document(self):
        document_paths = self.document_entry.get().split(',')
        self.app_config.context_documents = [doc.strip() for doc in document_paths if doc.strip()]
        messagebox.showinfo("Documents Updated", f"Documents updated: {self.app_config.context_documents}")

    def handle_request(self):
        def run_request():
            user_request = self.input_text.get("1.0", tk.END).strip()
            if user_request:
                try:
                    documents_content = "\n".join([self.document_handler.read_document(doc) for doc in self.app_config.context_documents])
                    context = f"User Request: {user_request}\nDocuments:\n{documents_content}"
                    res = self.agent_manager.agents['user_proxy'].initiate_chat(
                        recipient=self.agent_manager.agents['Writer'],
                        message=context,
                        max_turns=2,
                        summary_method="last_msg"
                    )
                    self.output_text.insert(tk.END, f"Output:\n{res}\n\nChat Ended.\n")
                    self.output_text.see(tk.END)
                except Exception as e:
                    logger.error(f"Error in chat: {e}")
                    messagebox.showerror("Error", f"An error occurred: {e}")

        threading.Thread(target=run_request).start()

if __name__ == "__main__":
    app = Application()
    app.mainloop()