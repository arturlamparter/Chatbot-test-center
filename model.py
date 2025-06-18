"""
Modul für Modell- und Datenverarbeitung im Chatbot-Projekt.

Dieses Modul `model` enthält alle nicht-visuellen Logik-Komponenten des Projekts. Es steuert die
Kommunikation mit dem lokalen Ollama-Server und verwaltet das Laden und Speichern von Chatdaten.

Hauptfunktionen:
- Verbindung mit Ollama über HTTP-API
- Verarbeitung von Benutzer- und Bot-Nachrichten (Prompt-Verlauf)
- Konsolenbasierte Interaktion im Testmodus
- Lesen und Schreiben von JSON-Dateien zur lokalen Persistenz

Klassen:
    LocalChatbot: Verwaltet die Kommunikation mit dem Ollama-Chatmodell.
    DataStorage: Verwaltet das Speichern und Laden von Chatverläufen in einer JSON-Datei.

Nützliche Befehle (für Setup & manuelles Testen):
    Starten: ollama serve
    Modell starten: ollama run mistral  # z.B. für Mistral-7B-Instruct

Der Ollama-Server läuft typischerweise unter http://localhost:11434

Autor: Artur Lamparter <arturlamparter@web.de>
"""
import textwrap
import requests
import random
import json
import os

import config
import main


class LocalChatbot:
    """
    Schnittstelle zum lokalen Ollama-Chatmodell.

    Diese Klasse kommuniziert über HTTP mit dem lokalen Ollama-Server,
    verwaltet den Nachrichtenkontext (Prompts) und kann testweise über
    die Konsole betrieben werden.
    """

    def __init__(self):
        self.ollama_url = config.OLLAMA_URL
        self.model = config.MODEL
        self.prompts = []
        self.test = False    # ----------------- Setze auf False, um echte Anfragen zu stellen -------------

    def send_to_ollama(self, messages):
        """
        Sendet eine Nachricht(enliste) an den Ollama-Server.

        Args:
            messages (list): Liste von Nachrichten im OpenAI-Format [{"role": "...", "content": "..."}]

        Returns:
            str: Antworttext vom Modell
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False # Die komplette Antwort wird auf einmal zurückgegeben.
        }

        # Testen der App ohne ChatBot
        if self.test:
            return f"Testfall: Antwort nr: {random.random()}"
        else:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]

    def chat_input(self):
        """
        Konsolen-Eingabezeilen sammeln, bis eine leere Zeile eingegeben wird.

        Returns:
            str: Zusammengesetzter Text aus mehreren Zeilen
        """
        print("->")
        lines = []
        line = input().strip()  # Entfernt Leerzeichen, Tabs, Zeilenumbrüche(Vorne und Hinten)
        lines.append(line)
        return "\n ".join(lines)

    def chat(self):
        """
        Führt eine einfache Konsolen-Konversation mit dem Chatbot.
        Eingabe: Benutzer
        Ausgabe: Antwort des Chatbots
        """
        print("Spreche mit Chatbot (bye zum Beenden)\n")
        while True:
            user_input = self.chat_input()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Bis bald!")
                break

            self.prompts.append({"role": "user", "content": user_input})
            context = self.prompts[-10:]

            try:
                pass
                response_text = self.send_to_ollama(context)
                print("Bot:", textwrap.fill(response_text, width=80)) # 40 Zeichen pro Zeile
                self.prompts.append({"role": "assistant", "content": response_text}) # antwort anhängen
            except Exception as e:
                print("Fehler bei der Kommunikation mit Ollama:", e)

class DataStorage:
    """
    Einfache JSON-Datei-Schnittstelle zur Speicherung und zum Laden von Prompts.
    """

    def __init__(self):
        pass # Aktuell keine Initialisierung nötig

    def load_json(self):
        """
        Lädt gespeicherte Prompts aus einer JSON-Datei.

        Returns:
            list: Liste von Prompt-Dictionaries oder leere Liste bei Fehler.
        """
        if os.path.exists(config.FILE_NAME):
            with open(config.FILE_NAME, "r", encoding="utf-8") as f:    # f als json
                return json.load(f)                                     # Erzeugt ein Dictionary
        return []

    def save_json(self, prompts):
        """
        Speichert eine Liste von Prompts in eine JSON-Datei.

        Args:
            prompts (list): Promptliste im Format [{"role": "...", "content": "..."}]
        """
        with open(config.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2)

if __name__ == '__main__':
    main.main()