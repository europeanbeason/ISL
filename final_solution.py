import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from all_functions import get_distance_dict, nearest_neighbour_v2, twoOpt, optimize_tsp_with_initial_solution, calculate_total_distance
import concurrent.futures
from multiprocessing import Queue, Manager


class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Scroll to the end
        self.text_widget.update_idletasks()  # Update the GUI

    def flush(self):
        pass  # Flush method is required for file-like object


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


def optimize_file(distance_dict, points, queue):
    import time
    try:
        start_time = time.time()
        queue.put("NN started\n")
        initial_tour = nearest_neighbour_v2(
            distance_dict=distance_dict, points=points)
        queue.put("NN completed, 2opt started\n")
        two_opt_tour = twoOpt(initial_tour, distance_dict)
        queue.put("2opt completed\n")
        end_time = time.time()
        elapsed_time_seconds = end_time - start_time
        elapsed_time_minutes = elapsed_time_seconds / 60
        print(f"Time left: {5-elapsed_time_minutes} minutes.")
        if elapsed_time_minutes < 5:
            optimal_tour = (optimize_tsp_with_initial_solution(
                distance_dict, points, initial_tour, 5 - elapsed_time_minutes), False)
            queue.put("Optimization with initial solution completed\n")
        else:
            optimal_tour = (two_opt_tour, True)
            queue.put("2opt tour is optimal\n")

        return optimal_tour

    except Exception as e:
        queue.put(f"Error in optimize_file: {e}\n")
        raise


def TSPoptimization():
    # Clear the status text box
    status_text.delete(1.0, tk.END)

    # Generate distance dictionaries and sets of points for each file path
    distance_dicts = {}
    points_sets = {}
    for file_path in selected_file_paths:
        try:
            distance_dict = get_distance_dict(file_path)
            distance_dicts[file_path] = distance_dict

            points = set()
            for (i, j) in distance_dict.keys():
                points.add(i)
                points.add(j)
            points_sets[file_path] = points

            # Update the status text box
            status_message = f"{file_path} distance dictionary and points set have been created.\n"
            queue.put(status_message)
            root.update_idletasks()  # Update the GUI

        except Exception as e:
            error_message = f"Error in generating distance dictionary and points set: {e}\n"
            queue.put(error_message)
            status_message = f"Error in {file_path}: {e}\n"
            queue.put(status_message)
            root.update_idletasks()

    # Run optimization in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_file = {executor.submit(
            optimize_file, distance_dicts[file_path], points_sets[file_path], queue): file_path for file_path in selected_file_paths}
        results = {}
        distances = {}
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                optimal_tour = future.result()
                results[file_path] = optimal_tour
                status_message = f"{file_path} optimization completed.\n"
            except Exception as exc:
                status_message = f"{file_path} generated an exception: {exc}\n"
            queue.put(status_message)
            root.update_idletasks()  # Update the GUI

    # Update the Treeview with results
    result_rows = [[os.path.basename(file_path) for file_path in results.keys()],
                   [str(calculate_total_distance(distance_dict=distance_dicts[file_path], route=results[file_path][0], nn=results[file_path][1])) for file_path in results.keys()]]  # Convert distances to strings for display

    # Clear previous results
    for i in tree.get_children():
        tree.delete(i)

    # Insert new results into the table
    for i in range(len(result_rows[0])):
        tree.insert('', 'end', values=(
            result_rows[0][i], result_rows[1][i]))


def poll_queue():
    while not queue.empty():
        msg = queue.get_nowait()
        print(msg)
    root.after(100, poll_queue)


if __name__ == "__main__":

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
    columns = ['File', 'Total Distance']  # Update column names
    tree = ttk.Treeview(result_frame, columns=columns,
                        show='headings', height=4)
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

    # Redirect stdout to the Text widget
    redirect_text = RedirectText(status_text)
    sys.stdout = redirect_text

    # Create a queue for inter-process communication
    manager = Manager()
    queue = manager.Queue()

    # Poll the queue
    root.after(100, poll_queue)

    # Run the application
    root.mainloop()
