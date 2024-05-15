import os
import tkinter as tk
import time
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from all_functions import get_distance_dict


def choose_directory():
    # Open a dialog to select a directory
    directory_path = filedialog.askdirectory()

    # Clear the listbox
    file_listbox.delete(0, tk.END)

    if directory_path:
        # Get all files in the directory
        all_files_and_dirs = os.listdir(directory_path)
        file_paths = [
            os.path.join(directory_path, f)
            for f in all_files_and_dirs
            if os.path.isfile(os.path.join(directory_path, f))
        ]

        # Insert file names into the listbox
        for file_path in file_paths:
            file_listbox.insert(tk.END, os.path.basename(file_path))

        # Store the file paths list globally for use in TSP optimization
        global selected_file_paths
        selected_file_paths = file_paths
    else:
        messagebox.showinfo("Information", "No directory selected.")


def update_clock():
    now = time.strftime("%H:%M:%S")  # Get current time in hour:minute:second
    clock_label.config(text=now)  # Update the label with the current time
    root.after(1000, update_clock)  # Schedule the function to be called after 1000ms


def update_stopwatch():
    if stopwatch_start is not None:
        elapsed = datetime.now() - stopwatch_start
        elapsed_time = str(elapsed).split(".")[0]  # Format as H:MM:SS
        stopwatch_label.config(text=elapsed_time)
        root.after(1000, update_stopwatch)  # Schedule next update in 1 second
    else:
        stopwatch_label.config(text="00:00:00")  # Reset stopwatch display when stopped


def start_time_limit():
    global time_limit_start
    time_limit_start = datetime.now()
    check_time_limit()


def check_time_limit():
    if time_limit_start is not None and time_limit_duration is not None:
        elapsed = datetime.now() - time_limit_start
        if (
            elapsed.total_seconds() >= time_limit_duration * 60
        ):  # Convert minutes to seconds
            time_limit_reached()
        else:
            root.after(1000, check_time_limit)  # Check again in 1 second


def time_limit_reached():
    global stopwatch_start
    stopwatch_start = None  # Stop the stopwatch
    update_stopwatch()  # Update the stopwatch display to show stopped time
    messagebox.showinfo(
        "Time Limit Reached", "The specified time limit has been reached."
    )
    # Optionally stop any ongoing processes related to optimization here


def TSPoptimization():
    global stopwatch_start, time_limit_duration
    try:
        available_time = float(
            available_time_entry.get()
        )  # Read and convert the available time to float
        time_limit_duration = (
            available_time  # Set the time limit duration to the available time
        )
    except ValueError:
        messagebox.showerror(
            "Invalid Input", "Please enter a valid number for the available time."
        )
        return
    stopwatch_start = datetime.now()
    update_stopwatch()
    start_time_limit()
    # Clear the status text box
    status_text.delete(1.0, tk.END)

    # Generate distance dictionaries for each file path
    distance_dicts = {}
    for file_path in selected_file_paths:
        distance_dicts[file_path] = get_distance_dict(file_path)
        # Update the status text box
        status_message = f"{file_path} distance dictionary has been created.\n"
        status_text.insert(tk.END, status_message)
        root.update_idletasks()  # Update the GUI

    # Placeholder for TSP optimization logic using distance_dicts
    results = [
        ["File" + str(i + 1) for i in range(len(selected_file_paths))],
        ["Result" + str(i + 1) for i in range(len(selected_file_paths))],
    ]

    # Clear previous results
    for i in tree.get_children():
        tree.delete(i)

    # Insert new results into the table
    tree.insert("", "end", values=results[0])
    tree.insert("", "end", values=results[1])
    stopwatch_start = None


# Create the main window
# Label for asking available time
time_limit_start = None
time_limit_duration = None


stopwatch_start = None
root = tk.Tk()
root.title("Drill Path Optimizer")
root.configure(bg="#e0f7fa")  # Light cyan background color

# Create a title label
title_label = tk.Label(
    root,
    text="Drill Path Optimizer",
    font=("Helvetica", 24, "bold"),
    bg="#00695c",
    fg="white",
)
title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

# Load and display the graphic
graphic_path = "b81e75c3-bba7-4f5c-9f61-8e879f5b7a15.png"
graphic = Image.open(graphic_path)
graphic = graphic.resize((400, 200), Image.ANTIALIAS)  # Reduced size
graphic_img = ImageTk.PhotoImage(graphic)
graphic_label = tk.Label(root, image=graphic_img, bg="#e0f7fa")
graphic_label.grid(row=1, column=0, pady=10, padx=10)

# Create a frame for the directory selection and file list
frame = tk.Frame(root, bg="#e0f7fa")
frame.grid(row=1, column=1, pady=10, padx=10)

# Create a button to choose a directory
choose_button = tk.Button(
    frame,
    text="Choose Directory",
    command=choose_directory,
    font=("Helvetica", 12),
    bg="#004d40",
    fg="white",
    activebackground="#00796b",
    activeforeground="white",
)
choose_button.grid(row=0, column=0, padx=10, pady=5)
stopwatch_label = tk.Label(
    root, text="00:00:00", font=("Helvetica", 16), bg="#e0f7fa", fg="#004d40"
)
stopwatch_label.grid(row=4, column=0, columnspan=2, pady=10, padx=10)
# Create a listbox to display file names
file_listbox = tk.Listbox(
    frame, width=50, height=10, font=("Helvetica", 12), bg="#b2dfdb", fg="#004d40"
)
file_listbox.grid(row=1, column=0, padx=10, pady=5)

# Create a button to start the TSP optimization
optimize_button = tk.Button(
    frame,
    text="Optimize",
    command=TSPoptimization,
    font=("Helvetica", 12),
    bg="#004d40",
    fg="white",
    activebackground="#00796b",
    activeforeground="white",
)
optimize_button.grid(row=2, column=0, padx=10, pady=5)


available_time_label = tk.Label(
    frame,
    text="How much time do you have? (min):",
    font=("Helvetica", 12),
    bg="#e0f7fa",
    fg="#004d40",
)
available_time_label.grid(row=4, column=0, sticky="w", padx=10, pady=2)

# Entry for inputting available time
available_time_entry = tk.Entry(
    frame, width=7, font=("Helvetica", 12), bg="white", fg="#004d40"
)
available_time_entry.grid(row=4, column=0, padx=10, pady=2)

# Create a frame for the result table
result_frame = tk.Frame(root, bg="#e0f7fa")
result_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

# Create a Treeview to display the results of the TSP optimization
# Initially set to 10 columns; adjust as needed
columns = [""] + ["File" + str(i + 1) for i in range(10)]

tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=4)
tree.pack(pady=10)

# Define the headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Apply styles to the Treeview
style = ttk.Style()
style.configure(
    "Treeview.Heading",
    font=("Helvetica", 12, "bold"),
    background="#004d40",
    foreground="white",
)
style.configure(
    "Treeview",
    font=("Helvetica", 12),
    background="#b2dfdb",
    foreground="#004d40",
    fieldbackground="#b2dfdb",
)

# Create a frame for the status window
status_frame = tk.Frame(root, bg="#e0f7fa")
status_frame.grid(row=0, column=2, rowspan=3, pady=10, padx=10)

# Create a Text widget to display status messages
status_text = tk.Text(
    status_frame,
    width=50,
    height=20,
    font=("Helvetica", 12),
    bg="#e0f7fa",
    fg="#004d40",
    wrap=tk.WORD,
)
status_text.pack()
# Create a clock label
clock_label = tk.Label(root, font=("Helvetica", 16), bg="#e0f7fa", fg="#004d40")
clock_label.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

# Initialize the clock update
update_clock()

# Run the application
root.mainloop()
