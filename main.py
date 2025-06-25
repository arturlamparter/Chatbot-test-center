#!/usr/bin/env python3

"""
Main module for the chatbot project with a graphical user interface (GUI).

This script initializes and starts the main application following the MVC architecture pattern (Model-View-Controller).
It connects the GUI (View), control logic (Controller), and chat model (Model)
to enable interactive chat communication with a locally running Ollama server.

Use cases:
    - Demonstration of a chatbot agent
    - Integration of AI models into desktop applications
    - Educational project for artificial intelligence and software architecture

Project goal: Demonstration of a chatbot agent with guided communication

Prerequisites:
    - The Ollama server must be running locally (see `model.py`)
    - Configuration is handled via `config.json`

Version:
    0.1.0

Author: Artur Lamparter <arturlamparter@web.de>
"""

__author__ = "Artur Lamparter <arturlamparter@web.de>"
__version__ = "0.1.0"  # git tag v0.1.0

import view
import controller
import model

def main():
    """
    Initializes the main components of the application and starts the GUI main loop.
    """
    main_view_object = view.MainView()
    local_chatbot_object = model.LocalChatbot()
    controller_object = controller.ChatController(main_view_object, local_chatbot_object)
    # controller_object.chat_start()
    controller_object.main_view.mainloop()

if __name__ == '__main__':
    main()
