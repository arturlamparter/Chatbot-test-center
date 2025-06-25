"""
GUI module for the chatbot project with influence on prompts.

The `view` module contains all graphical user interface components of the project.
It defines both the main application window (`MainView`) and the input masks
for prompts (`CreatePrompt`), which are dynamically created and managed.

Features and Highlights:
- Displays the chatbot's name (based on configuration)
- Dynamically scrollable area for an arbitrary number of prompt elements
- Input fields with automatic height adjustment
- Control buttons to navigate through multiple variants of a prompt

Classes:
    MainView: Creates the main window and provides a scroll area.
    CreatePrompt: Represents an input mask for prompts, including control and history.

Author: Artur Lamparter <arturlamparter@web.de>
"""

import tkinter as tk
from tkinter import ttk

import main
import controller

class MainView(tk.Tk):
    """
    Main window of the application, containing the scrollbar, canvas, and
    the placeholder for dynamically generated prompt elements.
    """

    def __init__(self):
        super().__init__()

        # --- General window settings ---
        self.name = "Chat Window"
        self.title(self.name)
        self.geometry("1800x800")

        tk.Label(self, text=f"You are talking to the chatbot: {controller.MODEL}",
                 anchor="w", font=("Arial", 20)).pack(side="top", fill="y")

        # --- Canvas and scrollbar ---
        canvas = tk.Canvas(self)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # --- Frame for content (placed into the canvas) ---
        self.scrollable_frame = ttk.Frame(canvas)  # Set scroll area
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # --- Enable mouse scrolling (Linux/Mac) ---
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

class CreatePrompt:
    """
    Represents a single prompt field (with multiple variants) including:
    - Input field
    - Control buttons (Submit, Back, Forward)
    - Activation checkbox
    - Display of role and index
    """

    def __init__(self, frame, pos, txt_lst):
        """
        Initializes a prompt object within a frame.

        Args:
            frame (tk.Frame): The parent frame (from MainView).
            pos (int): Position of the prompt (for vertical arrangement).
            txt_lst (list): List of variants (dictionaries with "role" and "content").
            Beispiel:
                self.txt_lst = [{'position': 0, 'role': 'system', 'content': 'Dein Name ist Jana.'}]
                self.prompt = {'position': 0, 'role': 'system', 'content': 'Dein Name ist Jana.'}
        """
        self.frame = frame
        self.pos = pos
        self.pos_frame = pos * controller.WIDGET_DISTANCE
        self.txt_lst = txt_lst
        self.prompt = None
        self.txt_nummer = 0
        self.chk_btn_var = tk.IntVar(value=1)  # Checkbox state (0 = off, 1 = on)

        # Placeholder row for spacing and setting length
        for i in range(10):
            tk.Label(self.frame, text="                         ", font=("Arial", 20)).grid(row=1 + self.pos_frame, column=i)

        self.chk_btn = tk.Checkbutton(self.frame, text="Activate", variable=self.chk_btn_var)
        self.chk_btn.grid(row=5 + self.pos_frame, column=0)

        self.btn_delete = self.create_button(self.frame, f"Delete",
                                             lambda: self.txt_wdg.delete("1.0", "end"), 5, 1)

        self.lbl_pos = tk.Label(self.frame, text="0", anchor="w", font=("Arial", 14))
        self.lbl_pos.grid(row=5 + self.pos_frame, column=2)

        self.lbl_role = tk.Label(self.frame, text="role = None", anchor="w", font=("Arial", 14))
        self.lbl_role.grid(row=5 + self.pos_frame, column=4)

        # Text field with scrollbar
        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid(row=10 + self.pos_frame, column=0, columnspan=10, rowspan=10, padx=5, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical")
        scrollbar.grid(row=0 + self.pos_frame, column=1, sticky="ns")

        self.txt_wdg = tk.Text(self.text_frame, width=55, height=5, font=("Arial", 14), wrap="word",
                               yscrollcommand=scrollbar.set, state="normal", bg="white", relief="flat")
        self.txt_wdg.grid(row=0 + self.pos_frame, column=0, sticky="nsew")
        scrollbar.config(command=self.txt_wdg.yview)
        self.txt_wdg.bind("<<Modified>>", self.on_text_change)  # Auto-adjust

        # Control buttons
        self.btn_send = self.create_button(self.frame, f"Submit", "", 20, 0)
        self.btn_back = self.create_button(self.frame, f"Back", self.btn_back_click, 20, 8)
        self.btn_before = self.create_button(self.frame, f"Forward", self.btn_forward_click, 20, 9)

        self.update_prompt(lbl_pos=str(self.txt_nummer),
                           lbl_role=self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg=self.txt_lst[self.txt_nummer]["content"])

    def create_button(self, parent, text, command, row, col):
        """Helper method to create buttons."""
        btn = ttk.Button(parent, text=text, command=command)
        btn.grid(row=row + self.pos_frame, column=col)
        return btn

    def on_text_change(self, event):
        """Automatically adjusts the height of the text field based on its content."""
        self.txt_wdg.edit_modified(False)  # Reset modified flag

        content = self.txt_wdg.get("1.0", "end-1c")
        num_lines = content.count("\n") + 1
        content = self.wrap_by_words(content)
        num_lines = content.count("\n") + 1 + num_lines

        max_lines = 20  # Maximum height in lines
        new_height = min(num_lines, max_lines)
        self.txt_wdg.config(height=new_height)

    def wrap_by_words(self, text, words_per_line=26):
        """Wraps long text based on words."""
        words = text.split()
        lines = [" ".join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)]
        return "\n".join(lines)

    def btn_back_click(self):
        """Jumps to the previous prompt."""
        if self.txt_nummer == 0:
            print("Wir sind am anfang.")
        else:
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
            self.txt_nummer -= 1
        self.update_prompt(lbl_pos=str(self.txt_nummer),
                           lbl_role=self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg=self.txt_lst[self.txt_nummer]["content"])

    def btn_forward_click(self):
        """Jumps to the next prompt or creates a new one."""
        if self.txt_nummer < len(self.txt_lst) - 1:  # If position is less than list length
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
        else:
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
            self.txt_lst.append({"role": self.txt_lst[self.txt_nummer]["role"],
                                 "content": "New"
                                 })
        self.txt_nummer += 1
        self.update_prompt(lbl_pos=str(self.txt_nummer),
                           lbl_role=self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg=self.txt_lst[self.txt_nummer]["content"])

    def chk_btn_var_show(self):
        """Returns the status of the activation checkbox."""
        return self.chk_btn_var.get()  # Returns 1 (True) or 0 (False)

    def get_prompt(self):
        """Returns the current prompt as a dictionary."""
        return {"role": self.txt_lst[self.txt_nummer]["role"],
                "content": self.txt_wdg.get("1.0", "end-1c")}

    def set_btn_send(self, callback):
        """Sets the callback function for the submit button."""
        self.btn_send.config(command=lambda: callback(self))

    def update_prompt(self, lbl_pos=None, lbl_role=None, txt_wdg=None):
        """Updates the display and content of the prompt."""
        if lbl_pos:
            self.lbl_pos.config(text=lbl_pos)
        if lbl_role:
            self.lbl_role.config(text=lbl_role)
        if txt_wdg:
            self.txt_wdg.delete("1.0", "end")
            self.txt_wdg.insert("1.0", txt_wdg)

if __name__ == '__main__':
    main.main()
