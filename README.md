# ChatBot GUI Project

A locally running, extensible chatbot with a graphical user interface (Tkinter), following the MVC pattern, and connected to an Ollama model like `mistral`.

## Project Objective

This project serves as a demonstration and learning platform for:
- AI-powered chatbots
- MVC architecture in Python
- GUI development with `tkinter`
- Local language models via [`ollama`](https://ollama.com/)

## Requirements

- Python ≥ 3.9
- Ollama installed and running

## License

This project is licensed under the MIT License.

## Installation

### 1. Install Ollama

To install Ollama, run the following commands:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama run mistral  # Start the model (may need to be loaded first)

