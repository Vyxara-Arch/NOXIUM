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
                "light": {
                    "bg_gradient_start": "#f4f7fb",
                    "bg_gradient_end": "#e6f3ef",
                    "sidebar_bg": "rgba(255, 255, 255, 0.86)",
                },
                "dark": {
                    "bg_gradient_start": "#0b1017",
                    "bg_gradient_end": "#101a24",
                    "sidebar_bg": "rgba(12, 20, 28, 0.92)",
                },
            },
            "Glacier Blue": {
                "accent": "#2563eb",
                "secondary": "#38bdf8",
                "tertiary": "#60a5fa",
                "light": {
                    "bg_gradient_start": "#eff6ff",
                    "bg_gradient_end": "#e0f2fe",
                    "dialog_bg": "#eef4ff",
                    "sidebar_bg": "rgba(255, 255, 255, 0.9)",
                },
                "dark": {
                    "bg_gradient_start": "#0a1220",
                    "bg_gradient_end": "#0f172a",
                    "dialog_bg": "#0b1220",
                    "sidebar_bg": "rgba(10, 16, 30, 0.92)",
                },
            },
            "Crimson Ember": {
                "accent": "#dc2626",
                "secondary": "#fb923c",
                "tertiary": "#f97316",
                "light": {
                    "bg_gradient_start": "#fff5f5",
                    "bg_gradient_end": "#fee2e2",
                    "dialog_bg": "#fff1f2",
                },
                "dark": {
                    "bg_gradient_start": "#120b0d",
                    "bg_gradient_end": "#1a0f12",
                    "dialog_bg": "#10090b",
                },
            },
            "Sandstone": {
                "accent": "#c2410c",
                "secondary": "#eab308",
                "tertiary": "#f59e0b",
                "light": {
                    "bg_gradient_start": "#fff7ed",
                    "bg_gradient_end": "#fdebd2",
                    "dialog_bg": "#fff4e5",
                },
                "dark": {
                    "bg_gradient_start": "#120e0a",
                    "bg_gradient_end": "#1b140e",
                    "dialog_bg": "#0f0c09",
                },
            },
            "Obsidian": {
                "accent": "#22d3ee",
                "secondary": "#38bdf8",
                "tertiary": "#0ea5e9",
                "light": {
                    "bg_gradient_start": "#f4f8fb",
                    "bg_gradient_end": "#e2e8f0",
                    "dialog_bg": "#f1f5f9",
                },
                "dark": {
                    "bg_gradient_start": "#05070c",
                    "bg_gradient_end": "#0b1220",
                    "dialog_bg": "#0b111c",
                    "sidebar_bg": "rgba(6, 10, 18, 0.94)",
                },
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
        theme = self.get_theme(accent_name or "Noxium Teal")
        accent = {
            "accent": theme.get("accent", "#0f766e"),
            "secondary": theme.get("secondary", "#f59e0b"),
            "tertiary": theme.get("tertiary", "#0ea5a4"),
        }
        if mode == "dark":
            base = {
                "bg_gradient_start": "#0b0f16",
                "bg_gradient_end": "#111827",
                "card": "rgba(15, 23, 42, 0.92)",
                "card_hover": "rgba(20, 30, 50, 0.96)",
                "border": "rgba(148, 163, 184, 0.14)",
                "dialog_bg": "#0c111b",
                "text": "#e2e8f0",
                "text_muted": "#94a3b8",
                "field_bg": "#0f1623",
                "surface_bg": "#0f1623",
                "sidebar_bg": "rgba(12, 18, 30, 0.92)",
                "table_header_bg": "rgba(148, 163, 184, 0.08)",
                "table_grid": "rgba(148, 163, 184, 0.14)",
                "table_alt_bg": "rgba(148, 163, 184, 0.04)",
            }
        else:
            base = {
                "bg_gradient_start": "#f4f7fb",
                "bg_gradient_end": "#e9eef5",
                "card": "rgba(255, 255, 255, 0.92)",
                "card_hover": "rgba(255, 255, 255, 0.98)",
                "border": "rgba(15, 23, 42, 0.08)",
                "dialog_bg": "#f1f5f9",
                "text": "#0f172a",
                "text_muted": "#64748b",
                "field_bg": "rgba(255, 255, 255, 0.95)",
                "surface_bg": "#ffffff",
                "sidebar_bg": "rgba(255, 255, 255, 0.82)",
                "table_header_bg": "rgba(15, 23, 42, 0.04)",
                "table_grid": "rgba(15, 23, 42, 0.08)",
                "table_alt_bg": "rgba(15, 23, 42, 0.02)",
            }

        overrides = theme.get(mode, {}) if isinstance(theme, dict) else {}
        palette = {**base, **overrides, **accent}
        palette["accent_soft"] = self._rgba(accent["accent"], 0.12)
        palette["accent_soft_border"] = self._rgba(accent["accent"], 0.2)
        palette["mode"] = mode
        return palette
