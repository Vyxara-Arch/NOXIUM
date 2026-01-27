import json
import os


class ThemeManager:
    def __init__(self, themes_file="themes.json"):
        self.themes_file = themes_file
        self.accents = {
            "Noxium Teal": {
                "accent": "#0f766e",
                "secondary": "#f59e0b",
                "tertiary": "#0ea5a4",
            },
            "Ocean Blue": {
                "accent": "#0ea5e9",
                "secondary": "#22d3ee",
                "tertiary": "#0284c7",
            },
            "Crimson": {
                "accent": "#dc2626",
                "secondary": "#fb923c",
                "tertiary": "#f97316",
            },
            "Midnight": {
                "accent": "#6366f1",
                "secondary": "#a855f7",
                "tertiary": "#0ea5a4",
            },
        }
        self.load_custom_themes()

    def load_custom_themes(self):
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, "r", encoding="utf-8") as f:
                    custom = json.load(f)
                    self.accents.update(custom)
            except Exception:
                pass

    def save_custom_theme(self, name, palette):
        custom_themes = {}
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, "r", encoding="utf-8") as f:
                    custom_themes = json.load(f)
            except Exception:
                pass

        custom_themes[name] = palette
        self.accents[name] = palette

        try:
            with open(self.themes_file, "w", encoding="utf-8") as f:
                json.dump(custom_themes, f, indent=4)
            return True
        except Exception:
            return False

    def get_theme(self, name):
        return self.accents.get(name, self.accents["Noxium Teal"])

    def get_all_theme_names(self):
        return list(self.accents.keys())

    @staticmethod
    def _rgba(hex_color, alpha):
        value = hex_color.lstrip("#")
        if len(value) != 6:
            return f"rgba(15, 118, 110, {alpha})"
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    def get_palette(self, mode, accent_name=None):
        accent = self.get_theme(accent_name or "Noxium Teal")
        if mode == "dark":
            base = {
                "bg_gradient_start": "#0b0e14",
                "bg_gradient_end": "#151a22",
                "card": "rgba(17, 24, 39, 0.92)",
                "card_hover": "rgba(24, 33, 46, 0.96)",
                "border": "rgba(148, 163, 184, 0.12)",
                "dialog_bg": "#0f141c",
                "text": "#e2e8f0",
                "text_muted": "#94a3b8",
                "field_bg": "#0f141c",
                "surface_bg": "#111827",
                "sidebar_bg": "rgba(15, 23, 42, 0.88)",
                "table_header_bg": "rgba(148, 163, 184, 0.08)",
                "table_grid": "rgba(148, 163, 184, 0.12)",
            }
        else:
            base = {
                "bg_gradient_start": "#f9f7f3",
                "bg_gradient_end": "#e9f1ea",
                "card": "rgba(255, 255, 255, 0.92)",
                "card_hover": "rgba(255, 255, 255, 0.98)",
                "border": "rgba(17, 24, 39, 0.08)",
                "dialog_bg": "#f7f5f1",
                "text": "#111827",
                "text_muted": "#6b7280",
                "field_bg": "#ffffff",
                "surface_bg": "#ffffff",
                "sidebar_bg": "rgba(255, 255, 255, 0.78)",
                "table_header_bg": "rgba(15, 23, 42, 0.04)",
                "table_grid": "rgba(15, 23, 42, 0.08)",
            }

        palette = {**base, **accent}
        palette["accent_soft"] = self._rgba(accent["accent"], 0.12)
        palette["accent_soft_border"] = self._rgba(accent["accent"], 0.2)
        palette["mode"] = mode
        return palette
