import tkinter as tk
from tkinter import simpledialog, messagebox
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
from PIL import Image, ImageTk
import os
import threading
import sys
import requests
import tempfile
from pypdf import PdfReader
from docx import Document

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

config_list = [
    {
        "model": "gpt-4",
        "api_key": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "tags": ["gpt-4"],
        "base_url": "http://127.0.0.1:5000/v1/"
    }
]

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 41,
        "config_list": config_list,
        "temperature": 0,
    },
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
    },
)

context_documents = []

default_prompt = (
    "You're running on arch linux not debian. You don't need to write scripts to disk "
    "or save them to a file to be executed, anything inside three backtick codeblocks will be executed. "
    "Based on the user's request, formulate an appropriate bash command to execute it:"
)

default_base_url = "http://127.0.0.1:5000/v1/"

current_prompt = default_prompt

def read_document(path):
    if path.startswith('http://') or path.startswith('https://'):
        if path.endswith('.pdf'):
            response = requests.get(path)
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_pdf.write(response.content)
            temp_pdf.close()
            return read_pdf(temp_pdf.name)
        elif path.endswith('.docx'):
            response = requests.get(path)
            temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_docx.write(response.content)
            temp_docx.close()
            return read_docx(temp_docx.name)
        else:
            response = requests.get(path)
            return response.text
    elif path.endswith('.pdf'):
        return read_pdf(path)
    elif path.endswith('.docx'):
        return read_docx(path)
    else:
        with open(path, 'r') as file:
            return file.read()

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx(file_path):
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def add_document():
    document_paths = document_entry.get().split(',')
    global context_documents
    context_documents = [doc.strip() for doc in document_paths if doc.strip()]
    messagebox.showinfo("Documents Updated", f"Documents updated: {context_documents}")

def update_prompt():
    global current_prompt
    current_prompt = prompt_text.get("1.0", tk.END).strip()
    messagebox.showinfo("Prompt Updated", "The prompt has been updated successfully!")

def my_message_generator(sender, recipient, context):
    user_request = context.get("user_request")
    documents_content = "\n".join([read_document(doc) for doc in context_documents])
    return f"{current_prompt}\nUser Request: {user_request}\nDocuments:\n{documents_content}"

def handle_request():
    def run_request():
        user_request = input_text.get("1.0", tk.END).strip()
        if user_request:
            try:
                chat_res = user_proxy.initiate_chat(
                    assistant,
                    message=my_message_generator,
                    user_request=user_request,
                    summary_method="reflection_with_llm",
                    summary_args={"summary_prompt": "Return entire conversation in plain text."},
                )
                formatted_output = format_output(chat_res)
                for line in formatted_output.split('\n'):
                    output_text.insert(tk.END, line + '\n')
                    output_text.see(tk.END)
                    root.update_idletasks()
            except Exception as e:
                print(f"Error: {e}")

    request_thread = threading.Thread(target=run_request)
    request_thread.start()

def format_output(chat_res):
    content = chat_res.summary
    return f"Output:\n{content}\n"

def set_base_url():
    base_url = url_entry.get()
    config_list[0]["base_url"] = base_url

    global assistant
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 41,
            "config_list": config_list,
            "temperature": 0,
        },
    )
    messagebox.showinfo("URL Set", "The base URL has been set successfully!")

root = tk.Tk()
root.title("CodeExecRAGv1")

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "images", "wp8082828.jpg")
bg_image = Image.open(image_path)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relx=0.5, rely=0.5, anchor='center')

url_label = tk.Label(root, text="Enter Base URL:", fg="red", bg="black")
url_label.pack(pady=(10, 0))

url_frame = tk.Frame(root)
url_frame.pack(pady=10)

url_entry = tk.Entry(url_frame, width=60, bg="black", fg="red")
url_entry.pack(side=tk.LEFT, padx=10)

url_entry.insert(0, default_base_url)

set_url_button = tk.Button(url_frame, text="Set URL", command=set_base_url, fg="red", bg="black")
set_url_button.pack(side=tk.RIGHT)

document_label = tk.Label(root, text="Enter URL or File Path:", fg="red", bg="black")
document_label.pack(pady=(10, 0))

document_frame = tk.Frame(root)
document_frame.pack(pady=10)

document_entry = tk.Entry(document_frame, width=60, bg="black", fg="red")
document_entry.pack(side=tk.LEFT, padx=10)

add_document_button = tk.Button(document_frame, text="Update Documents", command=add_document, fg="red", bg="black")
add_document_button.pack(side=tk.RIGHT)

prompt_label = tk.Label(root, text="Edit Prompt:", fg="red", bg="black")
prompt_label.pack(pady=(10, 0))

prompt_frame = tk.Frame(root)
prompt_frame.pack(pady=10)

prompt_text = tk.Text(prompt_frame, height=3, width=60, bg="black", fg="red", wrap=tk.WORD)
prompt_text.pack(side=tk.LEFT, padx=10)

prompt_scrollbar = tk.Scrollbar(prompt_frame, command=prompt_text.yview)
prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
prompt_text.config(yscrollcommand=prompt_scrollbar.set)

prompt_text.insert(tk.END, default_prompt)

update_prompt_button = tk.Button(prompt_frame, text="Update Prompt", command=update_prompt, fg="red", bg="black")
update_prompt_button.pack(side=tk.RIGHT, padx=10)

input_label = tk.Label(root, text="Tell me your desire:", fg="red", bg="black")
input_label.pack(pady=(10, 0))

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

input_text = tk.Text(input_frame, height=3, width=60, bg="black", fg="red", wrap=tk.WORD)
input_text.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

input_scrollbar = tk.Scrollbar(input_frame, command=input_text.yview)
input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
input_text.config(yscrollcommand=input_scrollbar.set)

start_button = tk.Button(input_frame, text="Start", command=handle_request, fg="red", bg="black")
start_button.pack(side=tk.RIGHT, padx=10)

output_frame = tk.Frame(root)
output_frame.pack(pady=10, expand=True, fill=tk.BOTH)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(output_frame, wrap=tk.WORD, fg="red", bg="black", yscrollcommand=scrollbar.set)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=output_text.yview)

sys.stdout = TextRedirector(output_text)
sys.stderr = TextRedirector(output_text)

root.mainloop()
