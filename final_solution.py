import os
import sys
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from all_functions import (
    get_distance_dict,
    nearest_neighbour_v2,
    twoOpt,
    optimize_tsp_with_initial_solution,
    calculate_total_distance,
)
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
    directory_path = filedialog.askdirectory()
    file_listbox.delete(0, tk.END)
    if directory_path:
        all_files_and_dirs = os.listdir(directory_path)
        file_paths = [
            os.path.join(directory_path, f)
            for f in all_files_and_dirs
            if os.path.isfile(os.path.join(directory_path, f))
        ]
        for file_path in file_paths:
            file_listbox.insert(tk.END, os.path.basename(file_path))
        global selected_file_paths
        selected_file_paths = file_paths
    else:
        messagebox.showinfo("Information", "No directory selected.")


def start_stopwatch():
    global stopwatch_start
    stopwatch_start = datetime.now()
    update_stopwatch()


def stop_stopwatch():
    global stopwatch_start
    stopwatch_start = None
    update_stopwatch()


def reset_stopwatch():
    global stopwatch_start
    stopwatch_start = None
    stopwatch_label.config(text="00:00:00")


def update_stopwatch():
    if stopwatch_start is not None:
        now = datetime.now()
        elapsed = now - stopwatch_start
        elapsed_time = str(elapsed).split(".")[0]  # Format as H:MM:SS
        stopwatch_label.config(text=elapsed_time)
        root.after(1000, update_stopwatch)
    else:
        stopwatch_label.config(text="00:00:00")


def start_time_limit():
    global time_limit_start, time_limit_duration, stopwatch_start
    time_limit_start = datetime.now()
    try:
        available_time = float(available_time_entry.get())
        time_limit_duration = available_time
        stopwatch_start = datetime.now()  # Start the stopwatch here
        update_stopwatch()  # Update the stopwatch display
        check_time_limit()
    except ValueError:
        messagebox.showerror(
            "Invalid Input", "Please enter a valid number for the available time."
        )


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


def optimize_file(distance_dict, points, queue, total_time):
    try:
        start_time = time.time()
        queue.put("NN started\n")
        initial_tour = nearest_neighbour_v2(distance_dict=distance_dict, points=points)
        queue.put("NN completed, 2opt started\n")
        two_opt_tour = twoOpt(initial_tour, distance_dict, total_time)
        queue.put("2opt completed\n")
        end_time = time.time()
        elapsed_time_seconds = end_time - start_time
        elapsed_time_minutes = elapsed_time_seconds / 60
        print(f"Time left: {total_time - elapsed_time_minutes} minutes.")
        if elapsed_time_minutes < total_time:
            optimal_tour = (
                optimize_tsp_with_initial_solution(
                    distance_dict,
                    points,
                    initial_tour,
                    total_time - elapsed_time_minutes,
                ),
                False,
            )
            queue.put("Optimization with initial solution completed\n")
        else:
            optimal_tour = (two_opt_tour, True)
            queue.put("2opt tour is optimal\n")
        return optimal_tour
    except Exception as e:
        queue.put(f"Error in optimize_file: {e}\n")
        raise


def TSPoptimization():
    global stopwatch_start, time_limit_duration
    try:
        available_time = float(available_time_entry.get())
        time_limit_duration = available_time
        start_stopwatch()
        start_time_limit()
    except ValueError:
        messagebox.showerror(
            "Invalid Input", "Please enter a valid number for the available time."
        )
        return

    status_text.delete(1.0, tk.END)
    distance_dicts = {}
    points_sets = {}
    points_dicts = {}
    for file_path in selected_file_paths:
        try:
            distance_dict, points_dict = get_distance_dict(file_path)
            distance_dicts[file_path] = distance_dict
            points_dicts[file_path] = points_dict
            points = set()
            for i, j in distance_dict.keys():
                points.add(i)
                points.add(j)
            points_sets[file_path] = points

            status_message = (
                f"{file_path} distance dictionary and points set have been created.\n"
            )
            queue.put(status_message)
            root.update_idletasks()
        except Exception as e:
            error_message = (
                f"Error in generating distance dictionary and points set: {e}\n"
            )
            queue.put(error_message)
            status_message = f"Error in {file_path}: {e}\n"
            queue.put(status_message)
            root.update_idletasks()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_file = {
            executor.submit(
                optimize_file,
                distance_dicts[file_path],
                points_sets[file_path],
                queue,
                time_limit_duration,
            ): file_path
            for file_path in selected_file_paths
        }
        results = {}
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                optimal_tour = future.result()
                results[file_path] = optimal_tour
                status_message = f"{file_path} optimization completed.\n"
            except Exception as exc:
                status_message = f"{file_path} generated an exception: {exc}\n"
            queue.put(status_message)
            root.update_idletasks()

    result_rows = [
        [os.path.basename(file_path) for file_path in results.keys()],
        [
            str(
                calculate_total_distance(
                    distance_dict=distance_dicts[file_path],
                    route=results[file_path][0],
                    nn=results[file_path][1],
                )
            )
            for file_path in results.keys()
        ],
    ]

    for key, value in results.items():
        with open(f"{key[:-4]}_best_path.txt", "w") as file:
            if value[1]:
                for i, point in enumerate(value[0], start=1):
                    file.write(
                        f"{i}: {points_dicts[key][point].x_coordinate} {points_dicts[key][point].y_coordinate} \n"
                    )

    for i in tree.get_children():
        tree.delete(i)

    for i in range(len(result_rows[0])):
        tree.insert("", "end", values=(result_rows[0][i], result_rows[1][i]))
    stopwatch_start = None
    update_stopwatch()


def poll_queue():
    while not queue.empty():
        msg = queue.get_nowait()
        print(msg)
    root.after(100, poll_queue)


if __name__ == "__main__":

    root = tk.Tk()
    root.title("Drill Path Optimizer")
    root.configure(bg="#e0f7fa")

    title_label = tk.Label(
        root,
        text="Drill Path Optimizer",
        font=("Helvetica", 24, "bold"),
        bg="#00695c",
        fg="white",
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    graphic_path = "b81e75c3-bba7-4f5c-9f61-8e879f5b7a15.png"
    graphic = Image.open(graphic_path)
    graphic = graphic.resize((400, 200), Image.ANTIALIAS)
    graphic_img = ImageTk.PhotoImage(graphic)
    graphic_label = tk.Label(root, image=graphic_img, bg="#e0f7fa")
    graphic_label.grid(row=1, column=0, pady=10, padx=10)

    frame = tk.Frame(root, bg="#e0f7fa")
    frame.grid(row=1, column=1, pady=10, padx=10)

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

    file_listbox = tk.Listbox(
        frame, width=50, height=10, font=("Helvetica", 12), bg="#b2dfdb", fg="#004d40"
    )
    file_listbox.grid(row=1, column=0, padx=10, pady=5)

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

    result_frame = tk.Frame(root, bg="#e0f7fa")
    result_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

    columns = ["File", "Total Distance"]
    tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=4)
    tree.pack(pady=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

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

    status_frame = tk.Frame(root, bg="#e0f7fa")
    status_frame.grid(row=0, column=2, rowspan=3, pady=10, padx=10)

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

    time_entry_frame = tk.Frame(root, bg="#e0f7fa")
    time_entry_frame.grid(row=3, column=0, pady=5, padx=10)

    time_label = tk.Label(
        time_entry_frame,
        text="Available Time (minutes):",
        bg="#e0f7fa",
        font=("Helvetica", 12),
    )
    time_label.pack(side=tk.LEFT)

    available_time_entry = tk.Entry(time_entry_frame, width=10, font=("Helvetica", 12))
    available_time_entry.pack(side=tk.LEFT)

    stopwatch_label = tk.Label(
        root, text="00:00:00", font=("Helvetica", 16), bg="#e0f7fa"
    )
    stopwatch_label.grid(row=4, column=0, pady=5, padx=10)

    redirect_text = RedirectText(status_text)
    sys.stdout = redirect_text

    reset_button = tk.Button(
        root,
        text="Reset Stopwatch",
        command=reset_stopwatch,
        font=("Helvetica", 12),
        bg="#004d40",
        fg="white",
        activebackground="#00796b",
        activeforeground="white",
    )
    reset_button.grid(row=4, column=1, pady=5, padx=10)

    manager = Manager()
    queue = manager.Queue()

    root.after(100, poll_queue)

    root.mainloop()
