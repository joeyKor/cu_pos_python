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

# Scaling support
SCALE_FACTOR = 1.0

def s(px):
    """ Scales a pixel value (int) """
    if isinstance(px, (int, float)):
        return int(px * SCALE_FACTOR)
    return px

def fs(pt):
    """ Scales a font size (points) """
    if isinstance(pt, str) and pt.endswith('pt'):
        pt = int(pt[:-2])
    return f"{int(pt * SCALE_FACTOR)}pt"

def reload_styles():
    global MAIN_WINDOW_STYLE, TABLE_STYLE, BUTTON_PURPLE_STYLE, BUTTON_GREEN_STYLE, BUTTON_RED_STYLE
    global BUTTON_BOTTOM_STYLE, LABEL_HEADER_STYLE, TOTAL_AREA_STYLE, BIG_PRICE_STYLE, INPUT_STYLE
    global COMBO_STYLE, WELCOME_DASHBOARD_BUTTON, WELCOME_SMALL_BUTTON, WELCOME_STATS_LABEL
    global WELCOME_INPUT_CONTAINER, WELCOME_INPUT_STYLE, WELCOME_SUB_BUTTON, WELCOME_CATEGORY_BUTTON
    global WELCOME_QUICK_ITEM_FRAME, WELCOME_PRICE_LABEL, WELCOME_ITEM_NAME_LABEL
    global SUMMARY_LABEL_STYLE, SUMMARY_TOTAL_RED, SUMMARY_TOTAL_DARK, SUMMARY_UNIT
    global SUMMARY_CONTAINER_STYLE, BARCODE_INPUT_STYLE, SCROLLBAR_STYLE, WELCOME_SCROLL_BUTTON_STYLE
    global FONT_SIZE_XL, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, FONT_SIZE_TINY

    FONT_SIZE_XL = fs(24)
    FONT_SIZE_LARGE = fs(18)
    FONT_SIZE_MEDIUM = fs(14)
    FONT_SIZE_SMALL = fs(12)
    FONT_SIZE_TINY = fs(8)

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
            font-size: {fs(22)};
            selection-background-color: #D1C4E9;
            selection-color: {TEXT_COLOR};
        }}
        QTableWidget::item {{
            border-bottom: 1px solid #DEE2E6;
            padding-top: {s(20)}px;
            padding-bottom: {s(20)}px;
        }}
        QTableWidget::item:selected {{
            background-color: #D1C4E9;
            color: {TEXT_COLOR};
        }}
        QHeaderView::section {{
            background-color: #D1D5DB;
            color: #333;
            padding: {s(8)}px;
            border: none;
            border-right: 1px solid #99A1AC;
            border-bottom: 1px solid #99A1AC;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(21)};
            font-weight: bold;
        }}
    """

    BUTTON_PURPLE_STYLE = f"""
        QPushButton {{
            background-color: {PRIMARY_PURPLE};
            color: {WHITE};
            border: none;
            border-radius: {s(5)}px;
            padding: {s(15)}px;
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
            border-radius: {s(5)}px;
            padding: {s(15)}px;
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
            border-radius: {s(5)}px;
            padding: {s(15)}px;
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
            border-radius: {s(4)}px;
            padding: {s(5)}px;
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
            padding: {s(5)}px;
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
            font-size: {fs(30)};
            color: #D32F2F; /* Red price color */
            font-weight: bold;
        }}
    """

    INPUT_STYLE = f"""
        QLineEdit {{
            background-color: {WHITE};
            color: {TEXT_COLOR};
            border: none;
            border-bottom: {s(2)}px solid {PRIMARY_PURPLE};
            padding: {s(10)}px;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(16)};
        }}
    """

    COMBO_STYLE = f"""
        QComboBox {{
            background-color: {WHITE};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            padding: {s(8)}px;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(12)};
        }}
        QComboBox QAbstractItemView {{
            background-color: {WHITE};
            color: {TEXT_COLOR};
            selection-background-color: #D1C4E9;
        }}
    """

    WELCOME_DASHBOARD_BUTTON = f"""
        QPushButton {{
            border-radius: {s(8)}px;
            color: white;
            font-family: '{FONT_FAMILY}';
            font-weight: bold;
            font-size: {fs(18)};
            text-align: center;
            border: none;
        }}
    """

    WELCOME_SMALL_BUTTON = f"""
        QPushButton {{
            background-color: #AAB3BF;
            border: 1px solid #99A1AC;
            border-radius: {s(5)}px;
            color: #FFFFFF;
            font-family: '{FONT_FAMILY}';
            font-weight: bold;
            font-size: {fs(11)};
        }}
        QPushButton:pressed {{
            background-color: #8C95A1;
        }}
    """

    WELCOME_STATS_LABEL = f"""
        QLabel {{
            font-family: '{FONT_FAMILY}';
            font-size: {fs(9)};
            color: #495057;
        }}
    """

    WELCOME_INPUT_CONTAINER = f"""
        QWidget#input_container {{
            background-color: white;
            border: {s(2)}px solid #DEE2E6;
            border-radius: {s(25)}px;
            padding: {s(5)}px;
        }}
    """

    WELCOME_INPUT_STYLE = f"""
        QLineEdit {{
            background-color: transparent;
            border: none;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(20)};
            color: #212529;
        }}
    """

    WELCOME_SUB_BUTTON = f"""
        QPushButton {{
            background-color: #3C3C46;
            color: white;
            border-radius: {s(4)}px;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(12)};
            font-weight: bold;
            padding: {s(5)}px;
        }}
    """

    WELCOME_CATEGORY_BUTTON = f"""
        QPushButton {{
            background-color: #E9ECEF;
            color: #495057;
            border-top: {s(4)}px solid #6C757D;
            border-radius: 0px;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(11)};
            font-weight: bold;
        }}
    """

    WELCOME_QUICK_ITEM_FRAME = f"""
        QFrame {{
            background-color: white;
            border: none;
            border-radius: {s(4)}px;
        }}
    """

    WELCOME_PRICE_LABEL = f"color: #D32F2F; font-weight: bold; font-size: {fs(10)};"
    WELCOME_ITEM_NAME_LABEL = f"color: #333333; font-weight: bold; font-size: {fs(9)};"

    # Payment Summary Meticulous Styles
    SUMMARY_LABEL_STYLE = f"font-family: '{FONT_FAMILY}'; font-size: {fs(16)}; color: #444; font-weight: bold;"
    SUMMARY_TOTAL_RED = f"font-family: '{FONT_FAMILY}'; font-size: {fs(32)}; color: #D32F2F; font-weight: bold;"
    SUMMARY_TOTAL_DARK = f"font-family: '{FONT_FAMILY}'; font-size: {fs(18)}; color: #333; font-weight: bold;"
    SUMMARY_UNIT = f"font-family: '{FONT_FAMILY}'; font-size: {fs(12)}; color: #666; font-weight: bold; padding-left: {s(5)}px;"

    SUMMARY_CONTAINER_STYLE = "background-color: #F8F9FA; border: none;"
    BARCODE_INPUT_STYLE = f"""
        QLineEdit {{
            background-color: white;
            border: {s(2)}px solid #DEDEDE;
            border-radius: {s(4)}px;
            padding: {s(10)}px;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(20)};
            color: #333;
        }}
        QLineEdit:focus {{
            border: {s(2)}px solid #7B68EE;
        }}
    """

    SCROLLBAR_STYLE = f"""
        QScrollBar:vertical {{
            border: none;
            background: #F1F1F1;
            width: {s(14)}px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #C1C1C1;
            min-height: {s(30)}px;
            border-radius: {s(7)}px;
            margin: {s(2)}px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #A1A1A1;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

    WELCOME_SCROLL_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: #00A6ED;
            color: white;
            border: 1px solid #0084BD;
            font-family: '{FONT_FAMILY}';
            font-size: {fs(16)};
            font-weight: bold;
        }}
        QPushButton:pressed {{
            background-color: #0084BD;
        }}
    """

# Initial load
reload_styles()
