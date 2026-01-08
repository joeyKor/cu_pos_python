# Colors based on the provided image
PRIMARY_PURPLE = "#7B68EE"  # A lighter purple for buttons
DARK_PURPLE = "#483D8B"     # Darker purple for header/side
ACCENT_GREEN = "#8BC34A"    # Light green for discount/coupons
DARK_GREEN = "#689F38"      # Darker green for main action
CANCEL_RED = "#Ef5350"      # Red for cancel
GRAY_BG = "#F5F5F5"         # Background gray
WHITE = "#FFFFFF"
BORDER_COLOR = "#D3D3D3"
TEXT_COLOR = "#333333"

# Welcome Page Colors
DASHBOARD_PURPLE = "#8A79B6"
DASHBOARD_GREEN = "#7AB800"
DASHBOARD_GRAY = "#E9ECEF"
DASHBOARD_DARK_GRAY = "#6C757D"
DASHBOARD_SOFT_GRAY = "#F8F9FA"
DASHBOARD_ACCENT_RED = "#E54B4B"

# Font settings
FONT_FAMILY = "Malgun Gothic"
FONT_SIZE_XL = "26pt"
FONT_SIZE_LARGE = "18pt"
FONT_SIZE_MEDIUM = "14pt"
FONT_SIZE_SMALL = "12pt"
FONT_SIZE_TINY = "8pt"

# QSS Stylesheets
MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {GRAY_BG};
    }}
"""

TABLE_STYLE = f"""
    QTableWidget {{
        background-color: #F2F4F6;
        color: {TEXT_COLOR};
        border: none;
        gridline-color: #DEE2E6;
        font-family: '{FONT_FAMILY}';
        font-size: 20pt;
        selection-background-color: #D1C4E9;
        selection-color: {TEXT_COLOR};
    }}
    QTableWidget::item {{
        border-bottom: 1px solid #DEE2E6;
        padding-top: 5px;
        padding-bottom: 5px;
    }}
    QTableWidget::item:selected {{
        background-color: #D1C4E9;
        color: {TEXT_COLOR};
    }}
    QHeaderView::section {{
        background-color: #D1D5DB;
        color: #333;
        padding: 8px;
        border: none;
        border-right: 1px solid #99A1AC;
        border-bottom: 1px solid #99A1AC;
        font-family: '{FONT_FAMILY}';
        font-size: 18pt;
        font-weight: bold;
    }}
"""

BUTTON_PURPLE_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_PURPLE};
        color: {WHITE};
        border: none;
        border-radius: 5px;
        padding: 15px;
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_LARGE};
        font-weight: bold;
    }}
    QPushButton:pressed {{
        background-color: {DARK_PURPLE};
    }}
"""

BUTTON_GREEN_STYLE = f"""
    QPushButton {{
        background-color: {ACCENT_GREEN};
        color: {WHITE};
        border: none;
        border-radius: 5px;
        padding: 15px;
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_LARGE};
        font-weight: bold;
    }}
    QPushButton:pressed {{
        background-color: {DARK_GREEN};
    }}
"""

BUTTON_RED_STYLE = f"""
    QPushButton {{
        background-color: {CANCEL_RED};
        color: {WHITE};
        border: none;
        border-radius: 5px;
        padding: 15px;
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_LARGE};
        font-weight: bold;
    }}
"""

BUTTON_BOTTOM_STYLE = f"""
    QPushButton {{
        background-color: #F5F5F5;
        color: {TEXT_COLOR};
        border: none;
        border-radius: 4px;
        padding: 5px;
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_MEDIUM};
    }}
    QPushButton:pressed {{
        background-color: #BDBDBD;
    }}
"""

LABEL_HEADER_STYLE = f"""
    QLabel {{
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_MEDIUM};
        font-weight: bold;
        color: {TEXT_COLOR};
        padding: 5px;
    }}
"""

TOTAL_AREA_STYLE = f"""
    QFrame {{
        background-color: {WHITE};
        border: none;
    }}
    QLabel {{
        font-family: '{FONT_FAMILY}';
        font-size: {FONT_SIZE_LARGE};
        color: {TEXT_COLOR};
    }}
"""

BIG_PRICE_STYLE = f"""
    QLabel {{
        font-family: '{FONT_FAMILY}';
        font-size: 30pt;
        color: #D32F2F; /* Red price color */
        font-weight: bold;
    }}
"""

INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {WHITE};
        color: {TEXT_COLOR};
        border: none;
        border-bottom: 2px solid {PRIMARY_PURPLE};
        padding: 10px;
        font-family: '{FONT_FAMILY}';
        font-size: 16pt;
    }}
"""

COMBO_STYLE = f"""
    QComboBox {{
        background-color: {WHITE};
        color: {TEXT_COLOR};
        border: 1px solid {BORDER_COLOR};
        padding: 8px;
        font-family: '{FONT_FAMILY}';
        font-size: 12pt;
    }}
    QComboBox QAbstractItemView {{
        background-color: {WHITE};
        color: {TEXT_COLOR};
        selection-background-color: #D1C4E9;
    }}
"""

WELCOME_DASHBOARD_BUTTON = """
    QPushButton {
        border-radius: 8px;
        color: white;
        font-family: 'Malgun Gothic';
        font-weight: bold;
        font-size: 18pt;
        text-align: center;
        border: none;
    }
"""

WELCOME_SMALL_BUTTON = """
    QPushButton {
        background-color: #AAB3BF;
        border: 1px solid #99A1AC;
        border-radius: 5px;
        color: #FFFFFF;
        font-family: 'Malgun Gothic';
        font-weight: bold;
        font-size: 11pt;
    }
    QPushButton:pressed {
        background-color: #8C95A1;
    }
"""

WELCOME_STATS_LABEL = """
    QLabel {
        font-family: 'Malgun Gothic';
        font-size: 9pt;
        color: #495057;
    }
"""

WELCOME_INPUT_CONTAINER = """
    QWidget#input_container {
        background-color: white;
        border: 2px solid #DEE2E6;
        border-radius: 25px;
        padding: 5px;
    }
"""

WELCOME_INPUT_STYLE = """
    QLineEdit {
        background-color: transparent;
        border: none;
        font-family: 'Malgun Gothic';
        font-size: 20pt;
        color: #212529;
    }
"""

WELCOME_SUB_BUTTON = """
    QPushButton {
        background-color: #3C3C46;
        color: white;
        border-radius: 4px;
        font-family: 'Malgun Gothic';
        font-size: 12pt;
        font-weight: bold;
        padding: 5px;
    }
"""

WELCOME_CATEGORY_BUTTON = """
    QPushButton {
        background-color: #E9ECEF;
        color: #495057;
        border-top: 4px solid #6C757D;
        border-radius: 0px;
        font-family: 'Malgun Gothic';
        font-size: 11pt;
        font-weight: bold;
    }
"""

WELCOME_QUICK_ITEM_FRAME = """
    QFrame {
        background-color: white;
        border: none;
        border-radius: 4px;
    }
"""

WELCOME_PRICE_LABEL = "color: #D32F2F; font-weight: bold; font-size: 10pt;"
WELCOME_ITEM_NAME_LABEL = "color: #333333; font-weight: bold; font-size: 9pt;"

# Payment Summary Meticulous Styles
SUMMARY_LABEL_STYLE = "font-family: 'Malgun Gothic'; font-size: 16pt; color: #444; font-weight: bold;"
SUMMARY_TOTAL_RED = "font-family: 'Malgun Gothic'; font-size: 34pt; color: #D32F2F; font-weight: bold;"
SUMMARY_TOTAL_DARK = "font-family: 'Malgun Gothic'; font-size: 20pt; color: #333; font-weight: bold;"
SUMMARY_UNIT = "font-family: 'Malgun Gothic'; font-size: 14pt; color: #666; font-weight: bold; padding-left: 5px; margin-bottom: 5px;"

SUMMARY_CONTAINER_STYLE = "background-color: #F8F9FA; border: none;"
BARCODE_INPUT_STYLE = """
    QLineEdit {
        background-color: white;
        border: 2px solid #DEDEDE;
        border-radius: 4px;
        padding: 10px;
        font-family: 'Malgun Gothic';
        font-size: 20pt;
        color: #333;
    }
    QLineEdit:focus {
        border: 2px solid #7B68EE;
    }
"""

SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        border: none;
        background: #F1F1F1;
        width: 14px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #C1C1C1;
        min-height: 30px;
        border-radius: 7px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #A1A1A1;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

WELCOME_SCROLL_BUTTON_STYLE = """
    QPushButton {
        background-color: #00A6ED; /* RGB(0, 166, 237) */
        color: white;
        border: 1px solid #0084BD;
        font-family: 'Malgun Gothic';
        font-size: 16pt;
        font-weight: bold;
    }
    QPushButton:pressed {
        background-color: #0084BD;
    }
"""
