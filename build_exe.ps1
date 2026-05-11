# Build script for CU POS
# Ensures assets are included and console is hidden

pyinstaller --noconsole --onefile --add-data "assets;assets" --name "CUPOS" main.py
