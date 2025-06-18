"""
Konfigurationsmodul für das Chatbot-Projekt.

Dieses Modul enthält zentrale Konstanten zur Steuerung der Anwendung, z.B.:
- API-Endpunkt des lokalen Ollama-Servers
- Modellname (z.B. "mistral")
- Dateipfad für die lokale Speicherung des Chatverlaufs
- Abstände zur Positionierung von GUI-Elementen

Diese Konfigurationswerte werden von allen anderen Modulen (model, view, controller) genutzt
und dienen der zentralen Wartbarkeit.

Änderungen an diesen Werten wirken sich direkt auf das Verhalten der Anwendung aus.

Beispiel:
    Um ein anderes Modell zu testen, ändere `MODEL = "gemma"` oder `MODEL = "llama3"`.

Autor: Artur Lamparter <arturlamparter@web.de>
"""

# === Konstanten ===
# Zieladresse für HTTP-Anfragen an den Ollama-Chat-Endpunkt
OLLAMA_URL = "http://localhost:11434/api/chat"

# Name des zu nutzenden Sprachmodells
MODEL="mistral"

# Name der JSON-Datei, in der Prompt-Verläufe lokal gespeichert werden
FILE_NAME = "chat_memory.json"

# Zeilenabstand zwischen den GUI-Komponenten (für die vertikale Positionierung)
WIDGET_DISTANCE = 20