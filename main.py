#!/usr/bin/env python3

"""
Startmodul für das Chatbot-Projekt mit grafischer Benutzeroberfläche.

Dieses Skript initialisiert und startet die Hauptanwendung im MVC-Stil (Model-View-Controller).
Es verknüpft die GUI (View), die Steuerlogik (Controller) und das Chatmodell (Model),
wodurch eine interaktive Chat-Kommunikation mit einem lokal laufenden Ollama-Server ermöglicht wird.

Anwendungszweck:
    - Demonstration von Chatbot-Agenten
    - Integration von KI-Modellen in Desktop-Oberflächen
    - Lernprojekt für künstliche Intelligenz und Softwarearchitektur

Projektziel: Demonstration Chat Bot Agenten mit gelenkter Kommunikation

Startvoraussetzungen:
    - Ollama-Server muss lokal laufen (siehe `model.py`)
    - Konfiguration erfolgt über `config.py`

Version:
    0.1.0

Autor: Artur Lamparter <arturlamparter@web.de>
"""

__author__ = "Artur Lamparter <arturlamparter@web.de>"
__version__ = "0.1.0"  # git tag v0.1.0

import view
import controller
import model

def main():
    """
    Initialisiert die Hauptkomponenten und startet die GUI-Hauptschleife.
    """
    main_view_object = view.MainView()
    local_chatbot_object = model.LocalChatbot()
    controller_object = controller.ChatController(main_view_object, local_chatbot_object)
    # controller_object.chat_start()
    controller_object.main_view.mainloop()

if __name__ == '__main__':
    main()

