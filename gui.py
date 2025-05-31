import os
import sys
import yaml
import threading
import subprocess
import tkinter as tk
from queue import Queue, Empty
from tkinter import ttk, messagebox, filedialog

import global_constants as gc


# --- Define parameters with limited options ---
# Keys here should match keys in your config.yaml
# For booleans, use [True, False]
# For other enums, provide a list of allowed values (can be str, int, float)
PARAMETER_OPTIONS = {
    'verbose': [True, False],
    'save_media': [True, False],
    'output_on_file': [True, False],
    'input_type': ['video', 'image'],
    'region_type': ['vertical_line', 'rectangle'],
}

# --- Define parameters that are system paths ---
# Keys here should match keys in your config.yaml
# You can specify 'file' or 'directory' for each path.
PATH_PARAMETERS = {
    'file_folder': 'directory',
    'file_name': 'file',
}


def load_config(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if config is None:
            return {}
        return config
    except yaml.YAMLError as e:
        messagebox.showerror(title="YAML Error", message=f"Error parsing YAML file '{file_path}':\n{e}")
        return None
    except Exception as e:
        messagebox.showerror(title="Load Error", message=f"Failed to load config from '{file_path}':\n{e}")
        return None


def save_config_to_file(file_path, data) -> bool:
    """Saves configuration data to a YAML file, shows message."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        messagebox.showinfo(title="Success", message=f"Configuration saved successfully to '{file_path}'!")
        return True
    except Exception as e:
        messagebox.showerror(title="Save Error", message=f"Failed to save config to '{file_path}':\n{e}")
        return False


# --- Console Redirector ---
class ConsoleRedirector:
    def __init__(self, text_widget, queue):
        self.text_widget = text_widget
        self.queue = queue
        self.text_widget.config(state='disabled')  # Make it read-only
        self.after_id = None

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass  # Required for file-like objects

    def process_queue(self):
        try:
            while True:
                line = self.queue.get_nowait()
                self.text_widget.config(state='normal')
                self.text_widget.insert(tk.END, line)
                self.text_widget.see(tk.END)
                self.text_widget.config(state='disabled')
                self.queue.task_done()
        except Empty:
            pass
        finally:
            self.after_id = self.text_widget.after(100, self.process_queue)

    def start(self):
        self.after_id = self.text_widget.after(100, self.process_queue)

    def stop(self):
        if self.after_id:
            self.text_widget.after_cancel(self.after_id)
            self.after_id = None


# --- GUI Application ---
class ConfigEditorApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("YAML Configuration Editor")
        # initial window size
        self.root.geometry("650x750")
        self.initialized_properly = False
        self.config_data = None
        self.entries = {}
        self.console_output_queue = Queue()
        self.console_redirector = None
        self.console_text = None

        if not os.path.exists(gc.CONFIG_PARAMETER_PATH):
            messagebox.showinfo(title="Info", message="Application will close as no config is available.")
            self.root.destroy()
            return

        if self.config_data is None:
            self.config_data = load_config(gc.CONFIG_PARAMETER_PATH)

        if self.config_data is None:
            if os.path.exists(gc.CONFIG_PARAMETER_PATH):
                messagebox.showerror(
                    title="Error",
                    message=f"Failed to load '{gc.CONFIG_PARAMETER_PATH}'. Check messages or file.",
                )
            self.root.destroy()
            return

        self.create_widgets()
        self.initialized_properly = True

    def create_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.entries.clear()

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(index=0, weight=1)
        self.root.rowconfigure(index=0, weight=1)

        # Frame for parameters and scrollbar
        param_frame = ttk.Frame(main_frame)
        param_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(index=0, weight=3)
        main_frame.columnconfigure(index=0, weight=1)

        canvas = tk.Canvas(param_frame)
        scrollbar = ttk.Scrollbar(param_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        param_frame.rowconfigure(index=0, weight=1)
        param_frame.columnconfigure(index=0, weight=1)

        row_idx = 0
        if not self.config_data:
            ttk.Label(scrollable_frame, text="No configuration parameters found or config is empty.") \
                .grid(row=row_idx, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
        else:
            for key, value in self.config_data.items():
                ttk.Label(scrollable_frame, text=f"{key}:").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=3)
                if key in PARAMETER_OPTIONS:
                    options = PARAMETER_OPTIONS[key]
                    current_value = value
                    if options == [True, False] or options == [False, True]:
                        bool_var = tk.BooleanVar(value=bool(current_value))
                        self.entries[key] = bool_var
                        rb_frame = ttk.Frame(scrollable_frame)
                        ttk.Radiobutton(rb_frame, text="True", variable=bool_var, value=True).pack(side=tk.LEFT, padx=2)
                        ttk.Radiobutton(rb_frame, text="False", variable=bool_var, value=False).pack(side=tk.LEFT,
                                                                                                     padx=2)
                        rb_frame.grid(row=row_idx, column=1, sticky=tk.W, padx=5, pady=3)
                    else:
                        combo_var = tk.StringVar()
                        self.entries[key] = (combo_var, options)
                        display_options = [str(opt) for opt in options]
                        combobox = ttk.Combobox(
                            scrollable_frame,
                            textvariable=combo_var,
                            values=display_options,
                            state="readonly",
                            width=47,
                        )
                        str_current_value = str(current_value)
                        if str_current_value in display_options:
                            combobox.set(str_current_value)
                        elif display_options:
                            combobox.set(display_options[0])
                        combobox.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=3)
                elif key in PATH_PARAMETERS:
                    frame_path = ttk.Frame(scrollable_frame)
                    frame_path.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=3)
                    frame_path.columnconfigure(index=0, weight=1)

                    path_var = tk.StringVar(value=str(value if value is not None else ""))
                    entry_path = ttk.Entry(frame_path, textvariable=path_var, width=40)
                    entry_path.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))
                    self.entries[key] = path_var

                    button_text = "Select Directory" if PATH_PARAMETERS[key] == 'directory' else "Select File"
                    (ttk.Button(
                        frame_path,
                        text=button_text,
                        command=lambda k=key, pv=path_var: self._select_path(k, pv)
                    ).grid(row=0, column=1, sticky=tk.E))
                elif isinstance(value, (dict, list)):
                    display_val = yaml.dump(value, indent=2, sort_keys=False).strip()
                    text_area = tk.Text(scrollable_frame, height=min(5, display_val.count('\n') + 2), width=50,
                                        wrap=tk.WORD)
                    text_area.insert(tk.END, display_val)
                    text_area.config(state=tk.DISABLED, background=self.root.cget('bg'))
                    text_area.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=3)
                    self.entries[key] = value
                else:
                    entry_var = tk.StringVar(value=str(value if value is not None else ""))
                    entry = ttk.Entry(scrollable_frame, textvariable=entry_var, width=50)
                    entry.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=3)
                    self.entries[key] = entry_var
                row_idx += 1
        scrollable_frame.columnconfigure(index=1, weight=1)

        # Button frame
        button_frame_east = ttk.Frame(main_frame)
        button_frame_west = ttk.Frame(main_frame)
        button_frame_east.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.E)
        button_frame_west.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.W)

        ttk.Button(button_frame_west, text="Exit", command=self.discard_and_exit).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame_east, text="Save & Run", command=self.save_and_run).pack(side=tk.RIGHT, padx=20)
        ttk.Button(button_frame_east, text="Save", command=self.save_only).pack(side=tk.LEFT)

        # Console output frame
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="5")
        console_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        main_frame.rowconfigure(index=2, weight=1)

        self.console_text = tk.Text(
            console_frame,
            wrap=tk.WORD,
            height=10,
            bg="black",
            fg="lightgray",
            font=("Consolas", 10)
        )
        self.console_text.pack(expand=True, fill="both")

        console_scrollbar = ttk.Scrollbar(console_frame, command=self.console_text.yview)
        console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.config(yscrollcommand=console_scrollbar.set)

        self.console_redirector = ConsoleRedirector(self.console_text, self.console_output_queue)
        self.console_redirector.start()

    @staticmethod
    def _select_path(key, path_var):
        """Opens a file/directory dialog and updates the path_var."""
        path_type = PATH_PARAMETERS.get(key)
        if path_type == 'directory':
            selected_path = filedialog.askdirectory(title=f"Select {key} Directory", initialdir=gc.DATA_FOLDER)
        elif path_type == 'file':
            selected_path = filedialog.askopenfilename(title=f"Select {key} File", initialdir=gc.DATA_FOLDER)
        else:
            selected_path = None

        if selected_path:
            path_var.set(selected_path)

    def _perform_save(self):
        if self.config_data is None:
            messagebox.showerror(title="Error", message="No configuration loaded.")
            return False

        updated_config = self.config_data.copy()
        for key, stored_item in self.entries.items():
            original_value_in_config = self.config_data.get(key)
            try:
                if isinstance(stored_item, tk.BooleanVar):
                    updated_config[key] = stored_item.get()
                elif isinstance(stored_item, tuple) and isinstance(stored_item[0], tk.StringVar):
                    combo_var, original_options = stored_item
                    selected_str_value = combo_var.get()
                    value_found = False
                    for opt in original_options:
                        if str(opt) == selected_str_value:
                            updated_config[key] = opt
                            value_found = True
                            break
                    if not value_found:  # Should not happen with readonly combobox
                        updated_config[key] = selected_str_value  # Fallback
                elif isinstance(stored_item, tk.StringVar):  # Entry
                    new_value_str = stored_item.get()
                    if new_value_str == "" and not isinstance(original_value_in_config, str):
                        updated_config[key] = None
                    elif isinstance(original_value_in_config, bool):
                        if new_value_str.lower() == 'true':
                            updated_config[key] = True
                        elif new_value_str.lower() == 'false':
                            updated_config[key] = False
                        else:
                            raise ValueError("Boolean value must be 'true' or 'false'.")
                    elif isinstance(original_value_in_config, int):
                        updated_config[key] = int(new_value_str)
                    elif isinstance(original_value_in_config, float):
                        updated_config[key] = float(new_value_str)
                    elif original_value_in_config is None:
                        if new_value_str.lower() in ['none', 'null', '~', '']:
                            updated_config[key] = None
                        else:
                            updated_config[key] = new_value_str
                    else:
                        updated_config[key] = new_value_str
                # else: complex type, already in updated_config via copy()
            except ValueError as e:
                messagebox.showerror(title="Validation Error",
                                     message=f"Invalid value for '{key}': '{new_value_str if isinstance(stored_item, tk.StringVar) else stored_item}'.\n"
                                     f"Original type: {type(original_value_in_config).__name__}.\nError: {e}")
                return False  # Stop saving

        if save_config_to_file(gc.CONFIG_PARAMETER_PATH, updated_config):
            self.config_data = updated_config  # Update in-memory config
            return True
        return False

    def save_only(self):
        self._perform_save()

    def save_and_run(self):
        if self._perform_save():
            self.execute_main_script()

    def discard_and_exit(self):
        if self.console_redirector:
            self.console_redirector.stop()
        self.root.destroy()

    def execute_main_script(self):
        self.console_text.config(state='normal')
        self.console_text.delete(1.0, tk.END)  # Clear previous output
        self.console_text.config(state='disabled')
        self.console_output_queue.queue.clear()  # Clear any pending queue items

        self.console_redirector.write("--- Starting all_files_in_folder.py.py ---\n")
        # Run the script in a separate thread to keep GUI responsive
        threading.Thread(target=self._run_script_in_thread).start()

    def _run_script_in_thread(self):
        try:
            # Construct the command to run your script
            # We assume all_files_in_folder.py.py is in the same directory
            script_path = "all_files_in_folder.py.py"
            if not os.path.exists(script_path):
                self.console_redirector.write(f"Error: Script '{script_path}' not found!\n")
                return

            # Example: Running the script with python executable
            # You might need to add arguments based on how your script uses the config.yaml
            command = [sys.executable, script_path]  # Use sys.executable to ensure correct python env

            # Redirect stdout and stderr to the Popen object's pipes
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Decode stdout/stderr as text
                bufsize=1,  # Line-buffered output
                universal_newlines=True  # Ensure consistent newline handling
            )

            # Read output line by line and put into queue
            for line in iter(process.stdout.readline, ''):
                self.console_redirector.write(line)
            for line in iter(process.stderr.readline, ''):
                self.console_redirector.write(f"ERROR: {line}")  # Differentiate stderr

            process.stdout.close()
            process.stderr.close()
            return_code = process.wait()

            if return_code == 0:
                self.console_redirector.write("\n--- Script Finished Successfully ---\n")
            else:
                self.console_redirector.write(f"\n--- Script Exited with Error (Code: {return_code}) ---\n")

        except Exception as e:
            self.console_redirector.write(f"\n--- An unexpected error occurred while running the script: {e} ---\n")


def main_gui():
    root = tk.Tk()
    app = ConfigEditorApp(root)
    if app.initialized_properly:
        root.mainloop()


if __name__ == '__main__':
    if not os.path.exists(gc.CONFIG_PARAMETER_PATH):
        print(f"'{gc.CONFIG_PARAMETER_PATH}' not found.")
        exit()

    main_gui()
