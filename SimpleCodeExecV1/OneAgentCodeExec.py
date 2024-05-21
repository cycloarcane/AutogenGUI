import tkinter as tk
from tkinter import simpledialog, messagebox
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
from PIL import Image, ImageTk  # Import PIL for image handling
import os
import threading
import sys

# Redirect stdout and stderr to the tkinter Text widget
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

# Initialize the config_list without the base_url
config_list = [
    {
        "model": "gpt-4",
        "api_key": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "tags": ["gpt-4"],
        "base_url": ""
    }
]

# create an AssistantAgent named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 41,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
    },
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # Enable user input mode
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        # the executor to run the generated code
        "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
    },
)

# Function to generate a message with a bash command based on user input
def my_message_generator(sender, recipient, context):
    user_request = context.get("user_request")
    return f"You're running on arch linux not debian. You don't need to write scripts to disk or save them to a file to be executed, anything inside three backtick codeblocks will be executed. Based on the user's request, formulate an appropriate bash command to execute it: \nUser Request: {user_request}"

# Function to handle the request and display the output
def handle_request():
    def run_request():
        user_request = input_entry.get()
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
                    root.update_idletasks()  # Force the GUI to update
            except Exception as e:
                print(f"Error: {e}")

    # Run the request in a separate thread
    request_thread = threading.Thread(target=run_request)
    request_thread.start()

def format_output(chat_res):
    content = chat_res.summary
    return f"Output:\n{content}\n"

# Function to set the base_url and update the config_list
def set_base_url():
    base_url = url_entry.get()
    config_list[0]["base_url"] = base_url

    global assistant  # Update the assistant with the new base_url
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 41,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },
    )
    messagebox.showinfo("URL Set", "The base URL has been set successfully!")

# Create the main window
root = tk.Tk()
root.title("HELLWAVE")

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "images", "wp8082828.jpg")
bg_image = Image.open(image_path)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Create a label for the URL Entry widget
url_label = tk.Label(root, text="Enter Base URL:", fg="red", bg="black")
url_label.pack(pady=(10, 0))

# Create an Entry widget for base URL input
url_entry = tk.Entry(root, width=60, bg="black", fg="red")
url_entry.pack(pady=10)

# Create a button to set the base URL
set_url_button = tk.Button(root, text="Set URL", command=set_base_url, fg="red", bg="black")
set_url_button.pack(pady=10)

# Create a label for the user request Entry widget
input_label = tk.Label(root, text="Tell me your desire:", fg="red", bg="black")
input_label.pack(pady=(10, 0))

# Create an Entry widget for user input
input_entry = tk.Entry(root, width=60, bg="black", fg="red")
input_entry.pack(pady=10)

# Create a Frame to hold the Text widget and the Scrollbar
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

# Create a Scrollbar widget
scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a Text widget for displaying the output
output_text = tk.Text(output_frame, wrap=tk.WORD, fg="red", bg="black", yscrollcommand=scrollbar.set)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure the Scrollbar
scrollbar.config(command=output_text.yview)

# Redirect stdout and stderr
sys.stdout = TextRedirector(output_text)
sys.stderr = TextRedirector(output_text)

# Bind the Enter key to handle_request function
input_entry.bind("<Return>", lambda event: handle_request())

# Run the application
root.mainloop()
