# Build script for CU POS
# Ensures assets are included and console is hidden

pyinstaller --noconsole --onefile --add-data "assets;assets" --add-data "json;json" --name "CUPOS" main.py
