import json
import os


class ThemeManager:
    def __init__(self, themes_file="themes.json"):
        self.themes_file = themes_file
        self.themes = {
            "Cyber Green": {
                "accent": "#00e676",
                "secondary": "#7f5af0",
                "tertiary": "#00b4d8",
            },
            "Matrix Code": {
                "accent": "#00ff41",
                "secondary": "#39ff14",
                "tertiary": "#0dff00",
            },
            "Cyberpunk Pink": {
                "accent": "#ff006e",
                "secondary": "#fb5607",
                "tertiary": "#8338ec",
            },
            "Ocean Blue": {
                "accent": "#00b4d8",
                "secondary": "#0077b6",
                "tertiary": "#90e0ef",
            },
            "Sunset Orange": {
                "accent": "#ff6b35",
                "secondary": "#f7931e",
                "tertiary": "#ffd23f",
            },
            "Red Alert": {
                "accent": "#ff3d3d",
                "secondary": "#ff6b6b",
                "tertiary": "#ff8787",
            },
            "Deep Purple": {
                "accent": "#7f5af0",
                "secondary": "#9f7af0",
                "tertiary": "#b794f6",
            },
        }
        self.load_custom_themes()

    def load_custom_themes(self):
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, "r") as f:
                    custom = json.load(f)
                    self.themes.update(custom)
            except Exception as e:
                print(f"Error loading custom themes: {e}")

    def save_custom_theme(self, name, palette):
        """
        palette: dict with 'accent', 'secondary', 'tertiary'
        """
        # Ensure we don't overwrite built-ins permanently in the file if we only want to save custom ones.
        # But treating all equal is easier.
        # Let's verify we are not saving EVERYTHING, just the custom ones.
        # Or simple approach: Just load existing file, update, save.

        custom_themes = {}
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, "r") as f:
                    custom_themes = json.load(f)
            except:
                pass

        custom_themes[name] = palette
        self.themes[name] = palette  # Update runtime

        try:
            with open(self.themes_file, "w") as f:
                json.dump(custom_themes, f, indent=4)
            return True
        except Exception as e:
            return False

    def get_theme(self, name):
        return self.themes.get(name, self.themes["Cyber Green"])

    def get_all_theme_names(self):
        return list(self.themes.keys())

    def apply_theme_to_stylesheet(self, stylesheet_template, theme_name):
        theme = self.get_theme(theme_name)

        # We need to know what placeholder keys are used in the template.
        # In app_qt.py, it uses ACCENT_COLOR etc constants.
        # Ideally, the template should use {accent}, {secondary}, {tertiary}.

        # Since refactoring the entire stylesheet to use format() might be error prone given its size and CSS syntax (braces),
        # we will use string replace like the original code did.

        # We need the original placeholder values to replace them.
        # But if the stylesheet is already processed, we can't easily replace.
        # Strategy: The app should keep a CONSTANT template and generate dynamic stylesheet from it.
        # Or we replace known tokens.

        # For now, let's assume the App passes the TEMPLATE (with placeholders or default values).
        # Actually, replacing the defaults works if we know what they are.

        # Best approach:
        # Define placeholders in ThemeManager as class constants?
        # Or just accept that we replace the default colors.

        # Default (Cyber Green)
        DEFAULTS = {
            "accent": "#00e676",
            "secondary": "#7f5af0",
            "tertiary": "#00b4d8",
        }

        new_sheet = stylesheet_template
        new_sheet = new_sheet.replace(DEFAULTS["accent"], theme["accent"])
        new_sheet = new_sheet.replace(DEFAULTS["secondary"], theme["secondary"])
        new_sheet = new_sheet.replace(DEFAULTS["tertiary"], theme["tertiary"])

        return new_sheet
