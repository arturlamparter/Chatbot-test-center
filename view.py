"""
GUI-Modul für das Chatbot-Projekt mit Einfluss auf Prompts.

Dieses Modul `view` enthält alle grafischen Benutzeroberflächen-Komponenten des Projekts.
Es definiert sowohl das Hauptfenster der Anwendung (`MainView`) als auch die Eingabemasken
für Prompts (`CreatePrompt`), die dynamisch erstellt und verwaltet werden.

Funktionen und Besonderheiten:
- Anzeige des Chatbot-Namens (basierend auf der Konfiguration)
- Dynamisch scrollbarer Bereich für beliebig viele Promptelemente
- Eingabefelder mit automatischer Höhenanpassung
- Steuerbuttons zum Blättern durch mehrere Varianten eines Prompts

Klassen:
    MainView: Erzeugt das Hauptfenster und stellt einen Scrollbereich bereit.
    CreatePrompt: Repräsentiert eine einzelne Eingabemaske für Prompts inkl. Steuerung, History.

Autor: Artur Lamparter <arturlamparter@web.de>
"""

import tkinter as tk
from tkinter import ttk

import config
import main

class MainView(tk.Tk):
    """
    Hauptfenster der Anwendung, das die Scrollbar, das Canvas und
    den Platzhalter für dynamisch erzeugte Prompt-Elemente enthält.
    """

    def __init__(self):
        super().__init__()

        # --- Allgemeine Fenstereinstellungen ---
        self.name = "Chat Window"
        self.title(self.name)
        self.geometry("1800x800")

        tk.Label(self, text=f"Du sprichst mit dem Chatbot: {config.MODEL}",
                 anchor="w", font=("Arial", 20)).pack(side="top", fill="y")

        # --- Canvas und Scrollbar ---
        canvas = tk.Canvas(self)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # --- Frame für Inhalt (wird in Canvas gelegt) ---
        self.scrollable_frame = ttk.Frame(canvas) # Scrollbereich setzen
        self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # --- Maus-Scrolling aktivieren (Linux/Mac) ---
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))


class CreatePrompt:
    """
    Repräsentiert ein einzelnes Prompt-Feld (mit mehreren Varianten) inklusive:
    - Eingabefeld
    - Steuerbuttons (Absenden, Zurück, Vor)
    - Aktivierungs-Checkbox
    - Anzeige von Rolle und Index
    """

    def __init__(self, frame, pos, txt_lst):
        """
        Initialisiert ein Prompt-Objekt innerhalb eines Frames.

        Args:
            frame (tk.Frame): Das übergeordnete Frame (aus MainView).
            pos (int): Position des Prompts (für vertikale Einordnung).
            txt_lst (list): Liste mit Varianten (Dictionaries mit "role" und "content").
            Beispiel:
            self.txt_lst = [{'position': 0, 'role': 'system', 'content': 'Dein Name ist Jana.'}]
            self.prompt = {'position': 0, 'role': 'system', 'content': 'Dein Name ist Jana.'}
        """
        self.frame = frame
        self.pos = pos
        self.pos_frame = pos * config.WIDGET_DISTANCE
        self.txt_lst = txt_lst
        self.prompt = None
        self.txt_nummer = 0
        self.chk_btn_var = tk.IntVar(value=1)  # Zustand CheckBox (0 = aus, 1 = an)

        # Platzhalter-Zeile für Abstand und länge festlegen
        for i in range(10):
            tk.Label(self.frame, text="                         ", font=("Arial", 20)).grid(row=1 + self.pos_frame, column=i)

        self.chk_btn = tk.Checkbutton(self.frame, text="Aktivieren", variable=self.chk_btn_var)
        self.chk_btn.grid(row=5 + self.pos_frame, column=0)

        self.btn_delete = ttk.Button(self.frame, text=f"Löschen", command=lambda: self.txt_wdg.delete("1.0", "end"))
        self.btn_delete.grid(row=5 + self.pos_frame, column=1)

        self.lbl_pos = tk.Label(self.frame, text="0", anchor="w", font=("Arial", 14))
        self.lbl_pos.grid(row=5 + self.pos_frame, column=2)

        self.lbl_role = tk.Label(self.frame, text="role = None", anchor="w", font=("Arial", 14))
        self.lbl_role.grid(row=5 + self.pos_frame, column=4)

        # Textfeld mit Scrollbar
        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.grid_rowconfigure(0, weight=1) #
        self.text_frame.grid_columnconfigure(0, weight=1) #
        self.text_frame.grid(row=10 + self.pos_frame, column=0, columnspan=10, rowspan=10, padx=5, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical")
        scrollbar.grid(row=0 + self.pos_frame, column=1, sticky="ns")

        self.txt_wdg = tk.Text(self.text_frame, width=55, height=5, font=("Arial", 14), wrap="word",
                              yscrollcommand=scrollbar.set, state="normal", bg="white", #
                              relief="flat")
        self.txt_wdg.grid(row=0 + self.pos_frame, column=0, sticky="nsew")
        scrollbar.config(command=self.txt_wdg.yview)
        self.txt_wdg.bind("<<Modified>>", self.on_text_change) # Automatisch anpassen

        # Steuerbuttons
        self.btn_send = ttk.Button(self.frame, text=f"Absenden")
        self.btn_send.grid(row=20 + self.pos_frame, column=0)

        self.btn_back = ttk.Button(self.frame, text=f"Zurück", command=self.btn_back_click)
        self.btn_back.grid(row=20 + self.pos_frame, column=8)

        self.btn_before = ttk.Button(self.frame, text=f"Vor", command=self.btn_forward_click)
        self.btn_before.grid(row=20 + self.pos_frame, column=9)

        self.update_prompt(lbl_pos = str(self.txt_nummer),
                           lbl_role=self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg=self.txt_lst[self.txt_nummer]["content"])

    def on_text_change(self, event):
        """Passt die Höhe des Textfelds automatisch an den Inhalt an."""
        self.txt_wdg.edit_modified(False)  # Reset modified flag

        content = self.txt_wdg.get("1.0", "end-1c")
        num_lines = content.count("\n") + 1
        content = self.wrap_by_words(content)
        num_lines = content.count("\n") + 1 + num_lines

        max_lines = 20  # Maximalhöhe in Zeilen
        new_height = min(num_lines, max_lines)
        self.txt_wdg.config(height=new_height)

    def wrap_by_words(self, text, words_per_line=26):
        """Bricht langen Text anhand von Wörtern um."""
        words = text.split()
        lines = [" ".join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)]
        return "\n".join(lines)

    def btn_back_click(self):
        """Springt zum vorherigen Prompt."""
        if self.txt_nummer == 0:
            print("Wir sind am anfang")
        else:
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
            self.txt_nummer -= 1
        self.update_prompt(lbl_pos = str(self.txt_nummer),
                           lbl_role=self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg=self.txt_lst[self.txt_nummer]["content"])

    def btn_forward_click(self):
        """Springt zum nächsten Prompt oder erstellt einen neuen."""
        print(f" index:{self.txt_nummer}")
        if self.txt_nummer < len(self.txt_lst) - 1:  # Wenn position kleoner als liste länge
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
        else:
            self.txt_lst[self.txt_nummer]["content"] = self.txt_wdg.get("1.0", "end-1c")
            self.txt_lst.append({"role": self.txt_lst[self.txt_nummer]["role"],
                                 "content": "Neu"
                                 })
        self.txt_nummer += 1
        self.update_prompt(lbl_pos = str(self.txt_nummer),
                           lbl_role = self.txt_lst[self.txt_nummer]["role"],
                           txt_wdg = self.txt_lst[self.txt_nummer]["content"])

    def chk_btn_var_show(self):
        """Gibt den Status der Aktivierungs-Checkbox zurück."""
        return self.chk_btn_var.get()  # Gibt 1 (True) oder 0 (False) zurück

    def get_prompt(self):
        """Liefert den aktuellen Prompt als Dictionary."""
        return {"role": self.txt_lst[self.txt_nummer]["role"],
                "content": self.txt_wdg.get("1.0", "end-1c")}

    def set_btn_send(self, callback):
        """Setzt die Callback-Funktion für den Absenden-Button."""
        self.btn_send.config(command=lambda: callback(self))

    def update_prompt(self, lbl_pos=None, lbl_role=None, txt_wdg=None):
        """Aktualisiert Anzeige und Inhalt des Prompts."""
        if lbl_pos:
            self.lbl_pos.config(text=lbl_pos)
        if lbl_role:
            self.lbl_role.config(text=lbl_role)
        if txt_wdg:
            self.txt_wdg.delete("1.0", "end")
            self.txt_wdg.insert("1.0", txt_wdg)


if __name__ == '__main__':
    main.main()