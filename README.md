# ChatBot GUI Projekt

Ein lokal laufender, erweiterbarer Chatbot mit grafischer Benutzeroberfläche (Tkinter), gesteuert nach dem MVC-Prinzip und verbunden mit einem Ollama-Modell wie `mistral`.

## Projektziel

Demonstration und Lernplattform für:
- KI-gestützte Chatbots
- MVC-Architektur in Python
- GUI-Entwicklung mit `tkinter`
- Lokale Sprachmodelle über [`ollama`](https://ollama.com/)

## Anforderungen

- Python ≥ 3.9
- Ollama installiert und lauffähig

## Lizenz Dieses Projekt steht unter der MIT-Lizenz.

### Installation Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama run mistral  # Modell starten (ggf. zuerst laden)
