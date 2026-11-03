import flet as ft
import json
import os

class Translator:
    def __init__(self, initial_lang: str = "es"):
        self.languages = {}
        self.current_lang = initial_lang
        self._load_languages()

    def _load_languages(self):
        """Loads all .json language files from the i18n directory."""
        i18n_dir = "i18n"
        if not os.path.exists(i18n_dir):
            print(f"Warning: Directory '{i18n_dir}' not found.")
            return

        for filename in os.listdir(i18n_dir):
            if filename.endswith(".json"):
                lang_code = filename.split(".")[0]
                try:
                    with open(os.path.join(i18n_dir, filename), "r", encoding="utf-8") as f:
                        self.languages[lang_code] = json.load(f)
                        print(f"Loaded language: {lang_code}")
                except Exception as e:
                    print(f"Error loading language file {filename}: {e}")

    def set_language(self, page: ft.Page, lang_code: str):
        """Sets the current language for the user's session and refreshes the page."""
        if lang_code in self.languages:
            self.current_lang = lang_code
            if page.session:
                page.session.set("user_lang", lang_code)
            print(f"Language set to: {lang_code}")
            # The view itself will need to handle the refresh
            page.update()
        else:
            print(f"Warning: Language '{lang_code}' not found.")

    def t(self, key: str, lang_override: str = None) -> str:
        """
        Translates a given key into the current language.
        Returns the key itself if the translation is not found.
        """
        lang = lang_override if lang_override else self.current_lang
        return self.languages.get(lang, {}).get(key, key)

# Example of how it would be used in the main app
# This is just for conceptual understanding.
if __name__ == '__main__':
    # 1. Create an instance of the translator
    translator = Translator(initial_lang="es")

    # 2. Get a translation
    print(f"In Spanish: {translator.t('login.title')}")

    # 3. Change the language
    translator.current_lang = "en"
    print(f"In English: {translator.t('login.title')}")

    # 4. Get a key that doesn't exist
    print(f"Missing key: {translator.t('non.existent.key')}")
