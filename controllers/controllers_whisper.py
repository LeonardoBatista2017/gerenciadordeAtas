# controllers_whisper.py
import os
import sys
import whisper

def get_model_path(model_name):
    model_map = {
        "tiny": "tiny.pt",
        "base": "base.pt",
        "small": "small.pt",
        "medium": "medium.pt",
        "large": "large.pt",
        "large-v1": "large-v1.pt",
        "large-v2": "large-v2.pt",
        "large-v3": "large-v3.pt",
    }

    if model_name not in model_map:
        raise ValueError(f"Modelo '{model_name}' não suportado.")

    filename = model_map[model_name]

    if hasattr(sys, '_MEIPASS'):
        # No executável: PyInstaller coloca em sys._MEIPASS/models/
        return os.path.join(sys._MEIPASS, 'models', filename)
    else:
        # No terminal: busca em ./models_whisper/
        return os.path.join(os.path.dirname(__file__), '..', 'models_whisper', filename)