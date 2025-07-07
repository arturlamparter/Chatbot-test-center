"""
Controller module for the chatbot project.

The `controller` module contains the central logic to connect the user interface
and data processing or communication with the local chatbot model in Ollama.
It serves as a mediator between view elements, user inputs, and the language model.

Features and Highlights:
- Initialization of chat components with stored prompts
- Management of user interaction (e.g., sending messages, navigating through prompts)
- Dynamically generating new input fields
- Processing user inputs and communication with the chatbot
- Optional saving and loading of prompt histories

Classes:
    ChatController: Controls the entire chat logic, including UI linkage and model requests.

Used internal modules:
    - model: For data storage and persistence (e.g., loading/saving prompts)
    - view: For displaying and interacting with the user interface
    - main: Entry point of the program (not directly used in this file but serves as a structural guide)

Author: Artur Lamparter <arturlamparter@web.de>
"""

import logging

import main
import view
import model

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load JSON-Konfiguration
config = model.DataStorage().load_json("config.json")

OLLAMA_URL = config.get('OLLAMA_URL', "http://localhost:11434/api/chat")
MODEL = config.get('MODEL', "mistral")
FILE_NAME = config.get('FILE_NAME', "chat_memory.json")
TEST = config.get('TEST', False)

class ChatController:
    """
    The central controller class that orchestrates the View, the Model, and the Chatbot.
    """

    def __init__(self, main_view, local_chatbot):
        """
        Initializes the controller.

        Args:
            main_view: The main GUI element.
            local_chatbot: An instance of the local chatbot that communicates with Ollama.

            Example self.prompts = [[{"position": 0, "role": "system", "content": "Your name is Jana."}]]
        """
        self.main_view = main_view
        self.local_chatbot = local_chatbot
        self.view_objects = []
        self.save_prompts = True  # --- Save prompts? ---
        self.prompts = self.convert_prompts(model.DataStorage().load_json())
        self.create_view_objects()
        self.load_all_prompts()

    def chat_start(self):
        """
        Starts the chat communication.
        Test version for the console
        """
        self.local_chatbot.chat()

    def create_view_objects(self, prompts=None, row=0):
        """
        Creates GUI components based on stored prompts.

        Args:
            prompts (list): List of prompts (as dict).
            row (int): Starting row in the GUI.
        """
        if not prompts:
            prompts = self.prompts

        for prompt in prompts:
            view_object = view.CreatePrompt(self.main_view.scrollable_frame, row, prompt)
            view_object.set_btn_send(self.btn_send_callback)
            self.view_objects.append(view_object)
            row += 1

    def convert_prompts(self, json_data):
        """
        Converts JSON data from the storage into usable prompt structures.
        The view manages multiple versions of prompts in the list.

        Args:
            json_data (list): Loaded JSON data.

        Returns:
            list: Structured prompt data.
        """
        return [[{"role": item["role"], "content": item["content"]}] for item in json_data]

    def btn_send_callback(self, obj):
        """
        Callback function for the send button of each prompt object.

        Args:
            obj: The calling view object.
        """
        # --- Creating prompt consisting of previous queries/responses ---
        prompt = []
        for view_objects in self.view_objects:
            if view_objects.pos <= obj.pos and view_objects.chk_btn_var_show():
                prompt.append(view_objects.get_prompt())

        # Optional save
        if self.save_prompts:
            self.save_all_prompts()
            model.DataStorage().save_json(prompt)

        # --- Send request to the bot ---
        try:
            response_text = self.local_chatbot.send_to_ollama(prompt)
        except Exception as e:
            logger.error("Error communicating with Ollama: %s", e)
            response_text = f"There was a problem connecting to the bot. Error: {e}"

        # --- Processing response ---
        response_prompt = {"role": "assistant", "content": response_text}

        # Display the response or create new view objects
        if obj.pos < len(self.view_objects) - 1:
            next_view = self.view_objects[obj.pos + 1]
            next_view.txt_lst.append(response_prompt)
            next_view.txt_nummer += 1
            # lbl_role = "assistant", txt_wdg = response_prompt["content"]
            next_view.update_prompt()
        else:
            new_prompt = {"role": "user", "content": "Def:"}  # Placeholder
            self.create_view_objects([[response_prompt], [new_prompt]], len(self.view_objects))

    def save_all_prompts(self):
        for text_field in self.view_objects:
            text_field.txt_lst[text_field.txt_nummer]["content"] = text_field.txt_wdg.get("1.0", "end-1c")
            list = text_field.txt_lst
            number = text_field.pos
            model.DataStorage().save_json(list, f"Data/text_field{number}")

    def load_all_prompts(self):
        for text_field in self.view_objects:
            text_field.txt_lst = model.DataStorage().load_json(f"Data/text_field{text_field.pos}")
            for index, text in enumerate(text_field.txt_lst):
                if text == text_field.get_prompt():
                    text_field.txt_nummer = index
            text_field.update_prompt()


if __name__ == '__main__':
    main.main()
