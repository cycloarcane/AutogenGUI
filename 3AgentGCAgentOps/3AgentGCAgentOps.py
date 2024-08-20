import tkinter as tk
from tkinter import messagebox, ttk
import autogen
import threading
import sys
import os
import agentops


global dark_mode
dark_mode = True  # Start in dark mode by default

agentops.init(default_tags=["simple-autogenGUI-example"])


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

api_key = os.getenv("OPENAI_API_KEY", "default-api-key")

default_base_url = "http://127.0.0.1:5000/v1/"
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": api_key
#        "tags": ["gpt-4o-mini"]
#        "base_url": default_base_url
    }
]

llm_config = {"config_list": config_list, "cache_seed": 42}

def toggle_agent_config():
    if agent_frame.winfo_ismapped():
        agent_frame.grid_remove()
        url_frame.grid_remove()
        toggle_agent_config_button.config(text="Show Agent Config")
        set_input_height(12)  # Increase height when agent config is hidden
    else:
        agent_frame.grid()
        url_frame.grid()
        toggle_agent_config_button.config(text="Hide Agent Config")
        set_input_height(6)  # Decrease height when agent config is shown
    
    root.update_idletasks()

def update_config():
    base_url = url_entry.get().strip()
    if not base_url:
        messagebox.showerror("Error", "Base URL cannot be empty!")
        return
    config_list[0]["base_url"] = base_url
    reinitialize_agents()
    messagebox.showinfo("Config Updated", "Base URL has been updated successfully!")
    update_status("Base URL updated")

def reinitialize_agents():
    global agent1, agent2, agent3, groupchat, manager

    agent1_name = agent1_name_entry.get().strip()
    agent1_message = agent1_message_entry.get("1.0", tk.END).strip()
    agent2_name = agent2_name_entry.get().strip()
    agent2_message = agent2_message_entry.get("1.0", tk.END).strip()
    agent3_name = agent3_name_entry.get().strip()
    agent3_message = agent3_message_entry.get("1.0", tk.END).strip()

    if not all([agent1_name, agent1_message, agent2_name, agent2_message, agent3_name, agent3_message]):
        messagebox.showerror("Error", "All agent names and messages must be filled!")
        return

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
    update_status("Agent configurations updated")

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config=False,
    human_input_mode="TERMINATE",
)

def handle_request():
    def run_request():
        user_request = input_text.get("1.0", tk.END).strip()
        if user_request:
            try:
                update_status("Processing request...")
                
                # Initiate or continue the chat with context preservation
                user_proxy.initiate_chat(manager, message=user_request)

                # Ensure chat history is updated
                for agent_response in manager.groupchat.messages:
                    formatted_output = format_output(agent_response["content"])
                    output_text.insert(tk.END, formatted_output + '\n')

                output_text.see(tk.END)
                root.update_idletasks()
                update_status("Request completed")
            except Exception as e:
                print(f"Error: {e}")
                update_status("Error occurred")
        else:
            messagebox.showerror("Error", "Please enter a request!")

    request_thread = threading.Thread(target=run_request)
    request_thread.start()

def format_output(chat_res):
    return f"Output:\n{chat_res}\n"

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    try:
        update_color_scheme()
    except Exception as e:
        print(f"Error toggling dark mode: {str(e)}")
        messagebox.showerror("Error", f"Failed to toggle dark mode: {str(e)}")

def update_color_scheme():
    global dark_mode
    bg_color = "black" if dark_mode else "white"
    fg_color = "green" if dark_mode else "black"
    highlight_color = "green" if dark_mode else "black"
    
    try:
        root.configure(bg=bg_color)
        for widget in root.winfo_children():
            update_widget_colors(widget, bg_color, fg_color, highlight_color)
    except Exception as e:
        print(f"Error updating color scheme: {str(e)}")
        messagebox.showerror("Error", f"Failed to update color scheme: {str(e)}")

def update_widget_colors(widget, bg_color, fg_color, highlight_color):
    widget_type = widget.winfo_class()
    try:
        if widget_type in ('Frame', 'Toplevel', 'Tk'):
            widget.configure(bg=bg_color)
        elif widget_type in ('Label', 'Button', 'Radiobutton', 'Checkbutton'):
            widget.configure(bg=bg_color, fg=fg_color)
        elif widget_type == 'Entry':
            widget.configure(bg=bg_color, fg=fg_color, highlightbackground=highlight_color, highlightcolor=highlight_color, insertbackground=fg_color)
        elif widget_type == 'Text':
            widget.configure(bg=bg_color, fg=fg_color, highlightbackground=highlight_color, highlightcolor=highlight_color, insertbackground=fg_color)
        elif widget_type == 'Scrollbar':
            widget.configure(bg=bg_color, troughcolor=bg_color)
    except tk.TclError as e:
        print(f"Error configuring {widget_type}: {str(e)}")

    for child in widget.winfo_children():
        update_widget_colors(child, bg_color, fg_color, highlight_color)

def clear_output():
    output_text.delete(1.0, tk.END)
    update_status("Output cleared")

def update_status(message):
    status_bar.config(text=message)
    root.update_idletasks()

# GUI setup
root = tk.Tk()
root.title("3AgentGCAgentOps")
root.configure(bg="black")
root.columnconfigure(0, weight=1)
root.rowconfigure(5, weight=1)  # This is the row of the input_frame

# Configure root row and column to expand
root.rowconfigure(5, weight=1)
root.columnconfigure(0, weight=1)

label_font = ("Helvetica", 10, "bold")

url_label = tk.Label(root, text="Enter Base URL:", fg="green", bg="black", font=label_font)
url_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

url_frame = tk.Frame(root, bg="black")
url_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
url_frame.columnconfigure(0, weight=1)

url_entry = tk.Entry(url_frame, width=60, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green")
url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
url_entry.insert(0, default_base_url)

set_url_button = tk.Button(url_frame, text="Set URL", command=update_config, fg="green", bg="black")
set_url_button.grid(row=1, column=0, sticky="w", pady=(5, 0))

agent_frame = tk.Frame(root, bg="black")
agent_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
agent_frame.columnconfigure(0, weight=1)
agent_frame.columnconfigure(1, weight=1)
agent_frame.columnconfigure(2, weight=1)
agent_frame.columnconfigure(3, weight=1)

# Agent 1
agent1_name_label = tk.Label(agent_frame, text="Agent 1 Name:", fg="green", bg="black", font=label_font)
agent1_name_label.grid(row=0, column=0, sticky="w")
agent1_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green")
agent1_name_entry.grid(row=1, column=0, sticky="w")
agent1_name_entry.insert(0, "Agent1")

agent1_message_label = tk.Label(agent_frame, text="Agent 1 Message:", fg="green", bg="black", font=label_font)
agent1_message_label.grid(row=0, column=1, sticky="w")
agent1_message_frame = tk.Frame(agent_frame, bg="black")
agent1_message_frame.grid(row=1, column=1, sticky="ew")
agent1_message_frame.columnconfigure(0, weight=1)
agent1_message_entry = tk.Text(agent1_message_frame, height=2, width=100, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green", wrap=tk.WORD)
agent1_message_entry.grid(row=0, column=0, sticky="ew")
agent1_message_scrollbar = tk.Scrollbar(agent1_message_frame, command=agent1_message_entry.yview, bg="black")
agent1_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent1_message_entry.config(yscrollcommand=agent1_message_scrollbar.set)
agent1_message_entry.insert(tk.END, "Agent 1 system message.")

# Agent 2
agent2_name_label = tk.Label(agent_frame, text="Agent 2 Name:", fg="green", bg="black", font=label_font)
agent2_name_label.grid(row=2, column=0, sticky="w")
agent2_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green")
agent2_name_entry.grid(row=3, column=0, sticky="w")
agent2_name_entry.insert(0, "Agent2")

agent2_message_label = tk.Label(agent_frame, text="Agent 2 Message:", fg="green", bg="black", font=label_font)
agent2_message_label.grid(row=2, column=1, sticky="w")
agent2_message_frame = tk.Frame(agent_frame, bg="black")
agent2_message_frame.grid(row=3, column=1, sticky="ew")
agent2_message_frame.columnconfigure(0, weight=1)
agent2_message_entry = tk.Text(agent2_message_frame, height=2, width=100, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green", wrap=tk.WORD)
agent2_message_entry.grid(row=0, column=0, sticky="ew")
agent2_message_scrollbar = tk.Scrollbar(agent2_message_frame, command=agent2_message_entry.yview, bg="black")
agent2_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent2_message_entry.config(yscrollcommand=agent2_message_scrollbar.set)
agent2_message_entry.insert(tk.END, "Agent 2 system message.")

# Agent 3
agent3_name_label = tk.Label(agent_frame, text="Agent 3 Name:", fg="green", bg="black", font=label_font)
agent3_name_label.grid(row=4, column=0, sticky="w")
agent3_name_entry = tk.Entry(agent_frame, width=25, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green")
agent3_name_entry.grid(row=5, column=0, sticky="w")
agent3_name_entry.insert(0, "Agent3")

agent3_message_label = tk.Label(agent_frame, text="Agent 3 Message:", fg="green", bg="black", font=label_font)
agent3_message_label.grid(row=4, column=1, sticky="w")
agent3_message_frame = tk.Frame(agent_frame, bg="black")
agent3_message_frame.grid(row=5, column=1, sticky="ew")
agent3_message_frame.columnconfigure(0, weight=1)
agent3_message_entry = tk.Text(agent3_message_frame, height=2, width=100, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green", wrap=tk.WORD)
agent3_message_entry.grid(row=0, column=0, sticky="ew")
agent3_message_scrollbar = tk.Scrollbar(agent3_message_frame, command=agent3_message_entry.yview, bg="black")
agent3_message_scrollbar.grid(row=0, column=1, sticky="ns")
agent3_message_entry.config(yscrollcommand=agent3_message_scrollbar.set)
agent3_message_entry.insert(tk.END, "Agent 3 system message.")

set_agent_button = tk.Button(agent_frame, text="Set Agent Config", command=update_agent_config, fg="green", bg="black")
set_agent_button.grid(row=6, column=0, sticky="w", pady=10, columnspan=2)

toggle_agent_config_button = tk.Button(root, text="Hide Agent Config", command=toggle_agent_config, fg="green", bg="black")
toggle_agent_config_button.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 0))

input_label = tk.Label(root, text="Enter initial prompt:", fg="green", bg="black", font=label_font)
input_label.grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))

input_frame = tk.Frame(root, bg="black")
input_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))
root.rowconfigure(5, weight=1)

input_text = tk.Text(input_frame, width=40, bg="black", fg="green", highlightbackground="green", highlightcolor="green", highlightthickness=1, insertbackground="green", wrap=tk.WORD)
input_text.pack(side="left", fill="both", expand=True)

input_scrollbar = tk.Scrollbar(input_frame, command=input_text.yview, bg="black")
input_scrollbar.pack(side="right", fill="y")
input_text.config(yscrollcommand=input_scrollbar.set)

def set_input_height(height):
    input_text.config(height=height)
    input_frame.update_idletasks()
    input_frame.config(height=input_text.winfo_reqheight())

set_input_height(6)  # Set initial height to 6 lines


# Set minimum height for input_text
input_text.config(height=4)
input_frame.grid_propagate(False)
input_frame.config(height=100)  # Adjust this value as needed

button_frame = tk.Frame(root, bg="black")
button_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)

start_button = tk.Button(button_frame, text="Start", command=handle_request, fg="green", bg="black")
start_button.grid(row=0, column=0, sticky="w")

clear_button = tk.Button(button_frame, text="Clear Output", command=clear_output, fg="green", bg="black")
clear_button.grid(row=0, column=1)

dark_mode_button = tk.Button(button_frame, text="Toggle Dark Mode", command=toggle_dark_mode, fg="green", bg="black")
dark_mode_button.grid(row=0, column=2, sticky="e")

output_frame = tk.Frame(root, bg="black")
output_frame.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0, 10))
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)

scrollbar = tk.Scrollbar(output_frame, bg="black")
scrollbar.grid(row=0, column=1, sticky="ns")

output_text = tk.Text(output_frame, wrap=tk.WORD, fg="green", bg="black", yscrollcommand=scrollbar.set, insertbackground="green")
output_text.grid(row=0, column=0, sticky="nsew")

scrollbar.config(command=output_text.yview)

status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, fg="green", bg="black")
status_bar.grid(row=8, column=0, sticky="ew")

sys.stdout = TextRedirector(output_text)
sys.stderr = TextRedirector(output_text)

# Initial agent setup after GUI elements are defined
reinitialize_agents()

root.mainloop()

agentops.end_session("Success")