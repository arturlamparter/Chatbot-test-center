"""
Steuerungsmodul für das Chatbot-Projekt.

Das Modul `controller` enthält die zentrale Logik zur Verbindung von Benutzeroberfläche
und Datenverarbeitung bzw. Kommunikation mit dem lokalen Chatbot-Modell in Ollama.
Es fungiert als Vermittler zwischen View-Elementen, Nutzereingaben und dem Sprachmodell.

Funktionen und Besonderheiten:
- Initialisierung der Chat-Komponenten mit gespeicherten Prompts
- Verwaltung der Benutzerinteraktion (z.B. Absenden von Nachrichten, Fortschalten von Prompts)
- Dynamisches Erzeugen neuer Eingabefelder
- Aufbereitung der Eingaben und Kommunikation mit dem Chatbot
- Optionales Speichern und Laden von Promptverläufen

Klassen:
    ChatController: Steuert die gesamte Chat-Logik inklusive GUI-Verknüpfung und Modellanfragen.

Verwendete interne Module:
    - model: Für Datenhaltung und Persistenz (z.B. Laden/Speichern von Prompts)
    - view: Für die Anzeige und Interaktion in der Benutzeroberfläche
    - main: Einstiegspunkt des Programms (nicht direkt in dieser Datei genutzt, aber als Strukturgeber)

Autor: Artur Lamparter <arturlamparter@web.de>
"""

import logging

import main
import view
import model

# Logger-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatController:
    """
    Die zentrale Controller-Klasse, die die View, das Model und den Chatbot orchestriert.
    """

    def __init__(self, main_view, local_chatbot):
        """
        Initialisiert den Controller.

        Args:
            main_view: Das Haupt-GUI-Element.
            local_chatbot: Eine Instanz des lokalen Chatbots, der mit Ollama kommuniziert.

            Beispiel self.prompts = [[{"position": 0, "role": "system", "content": "Dein Name ist Jana."}]]
        """
        self.main_view = main_view
        self.local_chatbot = local_chatbot
        self.view_objects = []
        self.save_prompts = True # --- Prompts speichern? ---
        self.prompts = self.convert_prompts(model.DataStorage().load_json())
        self.create_view_objects(self.prompts)

    def chat_start(self):
        """
        Startet die Chat-Kommunikation.
        Test version für die Konsole
        """
        self.local_chatbot.chat()

    def create_view_objects(self, prompts, row=0):
        """
        Erstellt GUI-Komponenten basierend auf gespeicherten Prompts.

        Args:
            prompts (list): Liste von Prompts (als dict).
            row (int): Startzeile in der GUI.
        """
        for prompt in prompts:
            view_object = view.CreatePrompt(self.main_view.scrollable_frame, row, prompt)
            view_object.set_btn_send(self.btn_send_callback)
            self.view_objects.append(view_object)
            row += 1

    def convert_prompts(self, json_data):
        """
        Wandelt JSON-Daten aus dem Storage in nutzbare Prompt-Strukturen um.
        View verwaltet mehrere Versionen der Prompts in der Liste

        Args:
            json_data (list): Geladene JSON-Daten.

        Returns:
            list: Strukturierte Prompt-Daten.
        """
        return [[{"role": item["role"], "content": item["content"]}] for item in json_data]

    def btn_send_callback(self, obj):
        """
        Callback-Funktion für den Senden-Button jedes Prompt-Objekts.

        Args:
            obj: Das aufrufende View-Objekt.
        """
        # --- Prompterstellung bestehend aus vorhergehenden Anfragen/Antworten ---
        prompt = []
        for view_objects in self.view_objects:
            if view_objects.pos <= obj.pos and view_objects.chk_btn_var_show():
                prompt.append(view_objects.get_prompt())

        # Optional speichern
        if self.save_prompts:
            model.DataStorage().save_json(prompt)

        # --- Anfrage an den Bot senden ---
        try:
            response_text = self.local_chatbot.send_to_ollama(prompt)
        except Exception as e:
            logger.error("Fehler bei der Kommunikation mit Ollama: %s", e)
            response_text = f"Es gab ein Problem mit der Verbindung zum Bot. Fehler: {e}"

        # --- Antwortverarbeitung ---
        response_prompt = {"role": "assistant", "content": response_text}

        # Antwort anzeigen oder neue View-Objekte anlegen
        if obj.pos < len(self.view_objects) - 1:
            next_view = self.view_objects[obj.pos + 1]
            next_view.txt_lst.append(response_prompt)
            next_view.txt_nummer += 1
            next_view.update_prompt(lbl_pos=None, lbl_role=None, txt_wdg=response_prompt["content"])
        else:
            new_prompt = {"role": "user", "content": "Def:"} # Platzhalter
            self.create_view_objects([[response_prompt],[new_prompt]], len(self.view_objects))

if __name__ == '__main__':
    main.main()
