import json
import os

class Translator:
    def __init__(self, lang="en"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        locale_path = os.path.join(base_dir, "..", "media", "language", f"{lang}.json")
        locale_path = os.path.normpath(locale_path)
        with open(locale_path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def t(self, key: str, **kwargs):
        """Trả về text theo key, hỗ trợ format biến."""
        keys = key.split(".")
        text = self.translations
        for k in keys:
            text = text.get(k, {})
        if isinstance(text, str):
            return text.format(**kwargs)
        return ""
