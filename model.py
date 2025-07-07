"""
Module for model and data processing in the chatbot project.

This `model` module contains all non-visual logic components of the project. It handles
communication with the local Ollama server and manages loading and saving chat data.

Main functions:
- Connects to Ollama via HTTP API
- Processes user and bot messages (prompt history)
- Console-based interaction in test mode
- Reading and writing JSON files for local persistence

Classes:
    LocalChatbot: Manages communication with the Ollama chat model.
    DataStorage: Manages saving and loading chat histories in a JSON file.

Useful commands (for setup & manual testing):
    Start: ollama serve
    Start model: ollama run mistral  # e.g. for Mistral-7B-Instruct

The Ollama server typically runs under http://localhost:11434

Author: Artur Lamparter <arturlamparter@web.de>
"""
import requests
import random
import json
import os

import main
import controller


class LocalChatbot:
    """
    Interface to the local Ollama chat model.

    This class communicates via HTTP with the local Ollama server,
    manages the message context (prompts), and can be run in a test mode via the console.
    """

    def __init__(self):
        self.ollama_url = controller.OLLAMA_URL
        self.model = controller.MODEL
        self.prompts = []
        self.test = controller.TEST

    def send_to_ollama(self, messages):
        """
        Sends a message (or list of messages) to the Ollama server.

        Args:
            messages (list): List of messages in OpenAI format [{"role": "...", "content": "..."}]

        Returns:
            str: Response text from the model
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False # The entire response will be returned at once.
        }

        # Test the app without ChatBot
        if self.test:
            return f"Test case: Response nr: {random.randint(0, 999999)}"
        else:
            try:
                response = requests.post(self.ollama_url, json=payload)
                response.raise_for_status()  # Raise an error if the HTTP status code is not OK
                return response.json()["message"]["content"]
            except requests.exceptions.RequestException as e:
                controller.logger.error(f"Request to Ollama failed: {e}")
                return "There was a problem connecting to the bot."
            except KeyError:
                controller.logger.error("Ollama response format is unexpected.")
                return "Malformed response from the model."

    def chat_input(self):
        """
        Collects console input lines until an empty line is entered.

        Returns:
            str: A composed text from multiple lines
        """
        print("->")
        lines = []
        line = input().strip()  # Removes spaces, tabs, and line breaks (leading and trailing)
        lines.append(line)
        return "\n ".join(lines)

    def chat(self):
        """
        Conducts a simple console conversation with the chatbot.
        Input: User
        Output: Chatbot's response
        """
        print("Talk to the chatbot (bye to exit)\n")
        while True:
            user_input = self.chat_input()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            self.prompts.append({"role": "user", "content": user_input})
            context = self.prompts[-10:]

            try:
                pass
                response_text = self.send_to_ollama(context)
                # print("Bot:", textwrap.fill(response_text, width=80)) # 40 characters per line
                self.prompts.append({"role": "assistant", "content": response_text})
            except Exception as e:
                controller.logger.error(f"Error communicating with Ollama: {e}")

class DataStorage:
    """
    Simple JSON file interface for saving and loading prompts.
    """

    def __init__(self):
        pass # Currently no initialization needed

    def load_json(self, file_name=None):
        """
        Loads from a JSON file.

        Args:
            file_name (str, optional): The name of the configuration file.

        Returns:
            dict: The loaded configuration as a dictionary.
                  Returns an empty dictionary in case of error (e.g., file not found, invalid JSON).
        """
        if file_name:
            path = file_name
        else:
            path = controller.FILE_NAME

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file) # Dictionary
            except FileNotFoundError:
                controller.logger.error(f"Configuration file {path} not found.")
                raise FileNotFoundError(f"Configuration file {path} not found.")
            except json.JSONDecodeError:
                controller.logger.error(f"Configuration file {path} contains invalid JSON.")
                raise json.JSONDecodeError(f"Configuration file {path} contains invalid JSON.")
            except Exception as e:
                controller.logger.error(f"An error occurred while loading the config file: {e}")
                raise Exception(f"An error occurred while loading the config file: {e}")
        else:
            controller.logger.warning(f"The file {path} does not exist.")
            return {}  # empty Dictionary

    def save_json(self, prompts, file_name=None):
        """
        Saves a list of prompts to a JSON file.

        Args:
            prompts (list): List of prompts in the format [{"role": "...", "content": "..."}]

        Raises:
            IOError: If there is an issue opening or writing to the file.
            ValueError: If the prompts are not in the expected format.
        """
        if file_name:
            path = file_name
        else:
            path = controller.FILE_NAME

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(prompts, f, indent=2)  # Save prompts as JSON
        except IOError as e:
            controller.logger.error(f"Error opening or writing to the file {path}: {e}")
            raise IOError(f"Error opening or writing to the file {path}: {e}")
        except ValueError as e:
            controller.logger.error(f"Invalid data format for prompts: {e}")
            raise ValueError(f"Invalid data format for prompts: {e}")
        except Exception as e:
            controller.logger.error(f"An unexpected error occurred while saving the file: {e}")
            raise Exception(f"An unexpected error occurred while saving the file: {e}")

if __name__ == '__main__':
    main.main()
