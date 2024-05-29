import tkinter as tk
from tkinter import messagebox
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
import threading
import sys
import os




class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

default_base_url = "http://127.0.0.1:5000/v1/"
config_list = [
    {
        "model": "gpt-4",
        "api_key": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "tags": ["gpt-4"],
        "base_url": default_base_url
    }
]

llm_config = {"config_list": config_list, "cache_seed": 42}

def toggle_agent_config():
    if agent_frame.winfo_ismapped():
        agent_frame.grid_remove()
        url_frame.grid_remove()
        toggle_agent_config_button.config(text="Show Agent Config")
        root.rowconfigure(4, weight=1)  # Make the output frame fill available space
    else:
        agent_frame.grid()
        url_frame.grid()
        toggle_agent_config_button.config(text="Hide Agent Config")
        root.rowconfigure(4, weight=0)  # Adjust the weight when agent config is visible


def update_config():
    base_url = url_entry.get()
    config_list[0]["base_url"] = base_url
    reinitialize_agents()
    messagebox.showinfo("Config Updated", "Base URL has been updated successfully!")

def reinitialize_agents():
    global agent1, agent2, agent3, groupchat, manager

    agent1_name = agent1_name_entry.get()
    agent1_message = agent1_message_entry.get("1.0", tk.END).strip()
    agent2_name = agent2_name_entry.get()
    agent2_message = agent2_message_entry.get("1.0", tk.END).strip()
    agent3_name = agent3_name_entry.get()
    agent3_message = agent3_message_entry.get("1.0", tk.END).strip()

    print(f"Initializing agents with names: {agent1_name}, {agent2_name}, {agent3_name}")
    print(f"Agent messages:\n{agent1_message}\n{agent2_message}\n{agent3_message}")

    agent1 = autogen.AssistantAgent(
        name=agent1_name,
        llm_config=llm_config,
        system_message=agent1_message,
    )

    agent2 = autogen.AssistantAgent(
        name=agent2_name,
        system_message=agent2_message,
        llm_config=llm_config,
    )

    agent3 = autogen.AssistantAgent(
        name=agent3_name,
        system_message=agent3_message,
        llm_config=llm_config,
    )

    groupchat = autogen.GroupChat(agents=[user_proxy, agent1, agent2, agent3], messages=[], max_round=12, speaker_selection_method="round_robin")
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

def update_agent_config():
    reinitialize_agents()
    messagebox.showinfo("Config Updated", "Agent configurations have been updated successfully!")

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={
        # the executor to run the generated code
        "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
    },
    human_input_mode="TERMINATE",
)

def handle_request():
    def run_request():
        user_request = input_text.get("1.0", tk.END).strip()
        if user_request:
            try:
                user_proxy.initiate_chat(manager, message=user_request)
                formatted_output = format_output("Chat Ended.")
                output_text.insert(tk.END, formatted_output + '\n')
                output_text.see(tk.END)
                root.update_idletasks()
            except Exception as e:
                print(f"Error: {e}")

    request_thread = threading.Thread(target=run_request)
    request_thread.start()

def format_output(chat_res):
    # Ensure the triple backticks are handled properly
    chat_res = chat_res.replace("```", "\n```")
    return f"Output:\n{chat_res}\n"

# GUI setup
root = tk.Tk()
root.title("3AgentGC")
root.configure(bg="black")
toggle_agent_config_button = tk.Button(root, text="Hide Agent Config", command=toggle_agent_config, fg="red", bg="black")
toggle_agent_config_button.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))


# Configure root row and column to expand
root.rowconfigure(4, weight=1)
root.columnconfigure(0, weight=1)

label_font = ("Helvetica", 10, "bold")

url_label = tk.Label(root, text="Enter Base URL:", fg="white", bg="black", font=label_font)
url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

url_frame = tk.Frame(root, bg="black")
url_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
url_frame.columnconfigure(0, weight=1)

url_entry = tk.Entry(url_frame, width=60, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red")
url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
url_entry.insert(0, default_base_url)

set_url_button = tk.Button(url_frame, text="Set URL", command=update_config, fg="red", bg="black")
set_url_button.grid(row=1, column=0, sticky="w", pady=(5, 0))

agent_frame = tk.Frame(root, bg="black")
agent_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
agent_frame.columnconfigure(0, weight=1)
agent_frame.columnconfigure(1, weight=1)
agent_frame.columnconfigure(2, weight=1)
agent_frame.columnconfigure(3, weight=1)

# Agent 1
agent1_name_label = tk.Label(agent_frame, text="Agent 1 Name:", fg="white", bg="black", font=label_font)
agent1_name_label.grid(row=0, column=0, sticky="w")
agent1_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red")
agent1_name_entry.grid(row=1, column=0, sticky="w")
agent1_name_entry.insert(0, "Agent 1")

agent1_message_label = tk.Label(agent_frame, text="Agent 1 Message:", fg="white", bg="black", font=label_font)
agent1_message_label.grid(row=0, column=1, sticky="w")
agent1_message_frame = tk.Frame(agent_frame, bg="black")
agent1_message_frame.grid(row=1, column=1, sticky="ew")
agent1_message_frame.columnconfigure(0, weight=1)
agent1_message_entry = tk.Text(agent1_message_frame, height=2, width=100, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red", wrap=tk.WORD)
agent1_message_entry.grid(row=0, column=0, sticky="ew")
agent1_message_scrollbar = tk.Scrollbar(agent1_message_frame, command=agent1_message_entry.yview, bg="black")
agent1_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent1_message_entry.config(yscrollcommand=agent1_message_scrollbar.set)
agent1_message_entry.insert(tk.END, "Agent 1 system message.")

# Agent 2
agent2_name_label = tk.Label(agent_frame, text="Agent 2 Name:", fg="white", bg="black", font=label_font)
agent2_name_label.grid(row=2, column=0, sticky="w")
agent2_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red")
agent2_name_entry.grid(row=3, column=0, sticky="w")
agent2_name_entry.insert(0, "Agent 2")

agent2_message_label = tk.Label(agent_frame, text="Agent 2 Message:", fg="white", bg="black", font=label_font)
agent2_message_label.grid(row=2, column=1, sticky="w")
agent2_message_frame = tk.Frame(agent_frame, bg="black")
agent2_message_frame.grid(row=3, column=1, sticky="ew")
agent2_message_frame.columnconfigure(0, weight=1)
agent2_message_entry = tk.Text(agent2_message_frame, height=2, width=100, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red", wrap=tk.WORD)
agent2_message_entry.grid(row=0, column=0, sticky="ew")
agent2_message_scrollbar = tk.Scrollbar(agent2_message_frame, command=agent2_message_entry.yview, bg="black")
agent2_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent2_message_entry.config(yscrollcommand=agent2_message_scrollbar.set)
agent2_message_entry.insert(tk.END, "Agent 2 system message.")

# Agent 3
agent3_name_label = tk.Label(agent_frame, text="Agent 3 Name:", fg="white", bg="black", font=label_font)
agent3_name_label.grid(row=4, column=0, sticky="w")
agent3_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red")
agent3_name_entry.grid(row=5, column=0, sticky="w")
agent3_name_entry.insert(0, "Agent 3")

agent3_message_label = tk.Label(agent_frame, text="Agent 3 Message:", fg="white", bg="black", font=label_font)
agent3_message_label.grid(row=4, column=1, sticky="w")
agent3_message_frame = tk.Frame(agent_frame, bg="black")
agent3_message_frame.grid(row=5, column=1, sticky="ew")
agent3_message_frame.columnconfigure(0, weight=1)
agent3_message_entry = tk.Text(agent3_message_frame, height=2, width=100, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red", wrap=tk.WORD)
agent3_message_entry.grid(row=0, column=0, sticky="ew")
agent3_message_scrollbar = tk.Scrollbar(agent3_message_frame, command=agent3_message_entry.yview, bg="black")
agent3_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent3_message_entry.config(yscrollcommand=agent3_message_scrollbar.set)
agent3_message_entry.insert(tk.END, "Agent 3 system message.")

set_agent_button = tk.Button(agent_frame, text="Set Agent Config", command=update_agent_config, fg="red", bg="black")
set_agent_button.grid(row=6, column=0, sticky="w", pady=10, columnspan=2)

input_label = tk.Label(agent_frame, text="Enter initial prompt:", fg="white", bg="black", font=label_font)
input_label.grid(row=7, column=0, sticky="w", pady=(0, 0), columnspan=2)

input_frame = tk.Frame(agent_frame, bg="black")
input_frame.grid(row=8, column=0, columnspan=3, sticky="ew")
input_frame.columnconfigure(0, weight=1)

input_text = tk.Text(input_frame, height=4, width=40, bg="black", fg="red", highlightbackground="red", highlightcolor="red", highlightthickness=1, insertbackground="red", wrap=tk.WORD)
input_text.grid(row=0, column=0, sticky="ew")

input_scrollbar = tk.Scrollbar(input_frame, command=input_text.yview, bg="black")
input_scrollbar.grid(row=0, column=1, sticky="ns")
input_text.config(yscrollcommand=input_scrollbar.set)

start_button = tk.Button(input_frame, text="Start", command=handle_request, fg="red", bg="black")
start_button.grid(row=1, column=0, sticky="w", pady=(5, 0))

output_frame = tk.Frame(root, bg="black")
output_frame.grid(row=4, column=0, columnspan=1, sticky="nsew", padx=10, pady=(10, 10))
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)

scrollbar = tk.Scrollbar(output_frame, bg="black")
scrollbar.grid(row=0, column=1, sticky="ns")

output_text = tk.Text(output_frame, wrap=tk.WORD, fg="red", bg="black", yscrollcommand=scrollbar.set, insertbackground="red")
output_text.grid(row=0, column=0, sticky="nsew")

scrollbar.config(command=output_text.yview)

sys.stdout = TextRedirector(output_text)
sys.stderr = TextRedirector(output_text)

# Initial agent setup after GUI elements are defined
reinitialize_agents()

root.mainloop()
