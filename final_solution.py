import os
import tkinter as tk
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
        file_paths = [os.path.join(directory_path, f) for f in all_files_and_dirs if os.path.isfile(
            os.path.join(directory_path, f))]

        # Insert file names into the listbox
        for file_path in file_paths:
            file_listbox.insert(tk.END, os.path.basename(file_path))

        # Store the file paths list globally for use in TSP optimization
        global selected_file_paths
        selected_file_paths = file_paths
    else:
        messagebox.showinfo("Information", "No directory selected.")


def TSPoptimization():
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
    results = [["File" + str(i+1) for i in range(len(selected_file_paths))],
               ["Result" + str(i+1) for i in range(len(selected_file_paths))]]

    # Clear previous results
    for i in tree.get_children():
        tree.delete(i)

    # Insert new results into the table
    tree.insert('', 'end', values=results[0])
    tree.insert('', 'end', values=results[1])


# Create the main window
root = tk.Tk()
root.title("Drill Path Optimizer")
root.configure(bg="#e0f7fa")  # Light cyan background color

# Create a title label
title_label = tk.Label(root, text="Drill Path Optimizer", font=(
    "Helvetica", 24, "bold"), bg="#00695c", fg="white")
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
choose_button = tk.Button(frame, text="Choose Directory", command=choose_directory, font=(
    "Helvetica", 12), bg="#004d40", fg="white", activebackground="#00796b", activeforeground="white")
choose_button.grid(row=0, column=0, padx=10, pady=5)

# Create a listbox to display file names
file_listbox = tk.Listbox(frame, width=50, height=10, font=(
    "Helvetica", 12), bg="#b2dfdb", fg="#004d40")
file_listbox.grid(row=1, column=0, padx=10, pady=5)

# Create a button to start the TSP optimization
optimize_button = tk.Button(frame, text="Optimize", command=TSPoptimization, font=(
    "Helvetica", 12), bg="#004d40", fg="white", activebackground="#00796b", activeforeground="white")
optimize_button.grid(row=2, column=0, padx=10, pady=5)

# Create a frame for the result table
result_frame = tk.Frame(root, bg="#e0f7fa")
result_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

# Create a Treeview to display the results of the TSP optimization
# Initially set to 10 columns; adjust as needed
columns = [''] + ['File' + str(i+1) for i in range(10)]

tree = ttk.Treeview(result_frame, columns=columns, show='headings', height=4)
tree.pack(pady=10)

# Define the headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Apply styles to the Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"),
                background="#004d40", foreground="white")
style.configure("Treeview", font=("Helvetica", 12), background="#b2dfdb",
                foreground="#004d40", fieldbackground="#b2dfdb")

# Create a frame for the status window
status_frame = tk.Frame(root, bg="#e0f7fa")
status_frame.grid(row=0, column=2, rowspan=3, pady=10, padx=10)

# Create a Text widget to display status messages
status_text = tk.Text(status_frame, width=50, height=20, font=(
    "Helvetica", 12), bg="#e0f7fa", fg="#004d40", wrap=tk.WORD)
status_text.pack()

# Run the application
root.mainloop()
