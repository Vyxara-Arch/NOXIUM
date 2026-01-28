ACCENT_COLOR = "#0f766e"
ACCENT_SECONDARY = "#f59e0b"
ACCENT_TERTIARY = "#0ea5a4"
ACCENT_SOFT = "rgba(15, 118, 110, 0.12)"
ACCENT_SOFT_BORDER = "rgba(15, 118, 110, 0.2)"
BG_COLOR = "#f4f7fb"
BG_GRADIENT_START = "#f4f7fb"
BG_GRADIENT_END = "#e9eef5"
CARD_COLOR = "rgba(255, 255, 255, 0.92)"
CARD_HOVER = "rgba(255, 255, 255, 0.98)"
GLASS_BORDER = "rgba(15, 23, 42, 0.08)"
TEXT_COLOR = "#0f172a"
TEXT_MUTED = "#64748b"
SHADOW_COLOR = "rgba(15, 23, 42, 0.08)"
DIALOG_BG = "#f1f5f9"
FIELD_BG = "rgba(255, 255, 255, 0.95)"
SURFACE_BG = "#ffffff"
SIDEBAR_BG = "rgba(255, 255, 255, 0.82)"
TABLE_HEADER_BG = "rgba(15, 23, 42, 0.04)"
TABLE_GRID = "rgba(15, 23, 42, 0.08)"
TABLE_ALT_BG = "rgba(15, 23, 42, 0.02)"


def apply_palette(palette):
    global ACCENT_COLOR
    global ACCENT_SECONDARY
    global ACCENT_TERTIARY
    global ACCENT_SOFT
    global ACCENT_SOFT_BORDER
    global BG_COLOR
    global BG_GRADIENT_START
    global BG_GRADIENT_END
    global CARD_COLOR
    global CARD_HOVER
    global GLASS_BORDER
    global TEXT_COLOR
    global TEXT_MUTED
    global SHADOW_COLOR
    global DIALOG_BG
    global FIELD_BG
    global SURFACE_BG
    global SIDEBAR_BG
    global TABLE_HEADER_BG
    global TABLE_GRID
    global TABLE_ALT_BG

    ACCENT_COLOR = palette["accent"]
    ACCENT_SECONDARY = palette["secondary"]
    ACCENT_TERTIARY = palette["tertiary"]
    ACCENT_SOFT = palette.get("accent_soft", ACCENT_SOFT)
    ACCENT_SOFT_BORDER = palette.get("accent_soft_border", ACCENT_SOFT_BORDER)
    BG_GRADIENT_START = palette["bg_gradient_start"]
    BG_GRADIENT_END = palette["bg_gradient_end"]
    CARD_COLOR = palette["card"]
    CARD_HOVER = palette["card_hover"]
    GLASS_BORDER = palette["border"]
    TEXT_COLOR = palette["text"]
    TEXT_MUTED = palette["text_muted"]
    DIALOG_BG = palette["dialog_bg"]
    FIELD_BG = palette.get("field_bg", FIELD_BG)
    SURFACE_BG = palette.get("surface_bg", SURFACE_BG)
    SIDEBAR_BG = palette.get("sidebar_bg", SIDEBAR_BG)
    TABLE_HEADER_BG = palette.get("table_header_bg", TABLE_HEADER_BG)
    TABLE_GRID = palette.get("table_grid", TABLE_GRID)
    TABLE_ALT_BG = palette.get("table_alt_bg", TABLE_ALT_BG)


def build_stylesheet():
    return f"""
QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_GRADIENT_START}, stop:0.65 {BG_GRADIENT_END}, stop:1 {ACCENT_SOFT});
}}

QWidget#LoginPage {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_GRADIENT_START}, stop:0.7 {BG_GRADIENT_END}, stop:1 {ACCENT_SOFT});
}}

QWidget {{
    color: {TEXT_COLOR};
    font-family: 'Sora', 'Manrope', 'IBM Plex Sans', 'Segoe UI Variable', 'Segoe UI', sans-serif;
    font-size: 14px;
    font-weight: 400;
}}

QFrame#Card {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {CARD_COLOR}, stop:1 {SURFACE_BG});
    border: 1px solid {GLASS_BORDER};
    border-radius: 18px;
}}

QFrame#Card:hover {{
    background: {CARD_HOVER};
    border: 1px solid {ACCENT_SOFT_BORDER};
}}

QFrame#Panel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {CARD_COLOR}, stop:1 {SURFACE_BG});
    border: 1px solid {GLASS_BORDER};
    border-radius: 24px;
}}

QFrame#Sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {SIDEBAR_BG}, stop:1 {BG_GRADIENT_END});
    border-right: 1px solid {GLASS_BORDER};
}}

QLineEdit, QComboBox, QSpinBox, QTextEdit {{
    background: {FIELD_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 10px 14px;
    color: {TEXT_COLOR};
    font-size: 14px;
    selection-background-color: {ACCENT_COLOR};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT_COLOR};
    background: {FIELD_BG};
}}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QTextEdit:hover {{
    border: 1px solid {ACCENT_SOFT_BORDER};
}}

QLineEdit#SearchField {{
    border-radius: 999px;
    padding: 9px 16px;
    background: {SURFACE_BG};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {TEXT_MUTED};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background: {SURFACE_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 10px;
    selection-background-color: {ACCENT_SOFT};
    selection-color: {TEXT_COLOR};
    padding: 6px;
}}

QPushButton {{
    background: {SURFACE_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 10px 16px;
    color: {TEXT_COLOR};
    font-weight: 600;
    font-size: 13px;
    text-align: center;
    min-height: 36px;
}}

QPushButton:hover {{
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid {ACCENT_SOFT_BORDER};
}}

QPushButton:pressed {{
    background: rgba(15, 23, 42, 0.08);
}}

QPushButton#Primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_COLOR}, stop:1 {ACCENT_TERTIARY});
    color: #ffffff;
    font-weight: 700;
    border: none;
}}

QPushButton#Primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_TERTIARY}, stop:1 {ACCENT_COLOR});
}}

QPushButton#Secondary {{
    background: {ACCENT_SECONDARY};
    color: #1f2937;
    font-weight: 700;
    border: none;
}}

QPushButton#Secondary:hover {{
    background: #f7c45a;
}}

QPushButton#Danger {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ef4444, stop:1 #b91c1c);
    color: #ffffff;
    font-weight: 700;
    border: none;
}}

QPushButton#Danger:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f05252, stop:1 #991b1b);
}}

QPushButton#LinkButton {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    padding: 6px 8px;
}}

QPushButton#LinkButton:hover {{
    color: {ACCENT_COLOR};
}}

QPushButton[nav="true"] {{
    text-align: left;
    padding: 12px 14px;
    border-radius: 12px;
    color: {TEXT_MUTED};
    background: transparent;
    border: 1px solid transparent;
    font-weight: 600;
}}

QPushButton[nav="true"]:hover {{
    color: {TEXT_COLOR};
    background: rgba(15, 23, 42, 0.04);
}}

QPushButton[nav="true"][active="true"] {{
    background: {ACCENT_SOFT};
    color: {ACCENT_COLOR};
    border: 1px solid {ACCENT_SOFT_BORDER};
    border-left: 3px solid {ACCENT_COLOR};
}}

QCheckBox {{
    color: {TEXT_COLOR};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid {GLASS_BORDER};
    background: {FIELD_BG};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT_COLOR};
    border: 1px solid {ACCENT_COLOR};
    image: none;
}}

QProgressBar {{
    border: none;
    background: {GLASS_BORDER};
    border-radius: 8px;
    height: 10px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_COLOR}, stop:1 {ACCENT_TERTIARY});
    border-radius: 8px;
}}

QListWidget {{
    background: {SURFACE_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 6px;
    color: {TEXT_COLOR};
}}

QListWidget::item {{
    padding: 8px 10px;
    border-radius: 8px;
    margin: 2px 0;
}}

QListWidget::item:hover {{
    background: rgba(15, 23, 42, 0.04);
}}

QListWidget::item:selected {{
    background: {ACCENT_SOFT};
    border-left: 3px solid {ACCENT_COLOR};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {GLASS_BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {ACCENT_SOFT_BORDER};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QTabWidget::pane {{
    border: none;
    background: transparent;
}}

QTabBar::tab {{
    background: {SURFACE_BG};
    color: {TEXT_MUTED};
    padding: 10px 20px;
    margin-right: 4px;
    border-radius: 12px 12px 0 0;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background: {CARD_COLOR};
    color: {ACCENT_COLOR};
    border-bottom: 2px solid {ACCENT_COLOR};
}}

QToolTip {{
    background: {SURFACE_BG};
    color: {TEXT_COLOR};
    border: 1px solid {GLASS_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}}

QGroupBox {{
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: {TEXT_COLOR};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}}

QLabel[tone="muted"] {{
    color: {TEXT_MUTED};
}}

QLabel[tone="accent"] {{
    color: {ACCENT_COLOR};
}}

QLabel[tone="accent-secondary"] {{
    color: {ACCENT_SECONDARY};
}}

QLabel[mono="true"] {{
    font-family: Consolas;
}}

QTableWidget {{
    background: {SURFACE_BG};
    border: 1px solid {GLASS_BORDER};
    color: {TEXT_COLOR};
    gridline-color: {TABLE_GRID};
    alternate-background-color: {TABLE_ALT_BG};
    border-radius: 12px;
}}

QTableWidget::item:selected {{
    background: {ACCENT_SOFT};
    color: {TEXT_COLOR};
}}

QHeaderView::section {{
    background: {TABLE_HEADER_BG};
    color: {TEXT_MUTED};
    padding: 8px;
    border: none;
    font-weight: 600;
}}

QTableWidget#DropTable {{
    border: 1px dashed {TABLE_GRID};
}}
"""
