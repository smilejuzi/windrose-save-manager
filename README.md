# Windrose Save Manager

A simple save backup and restore tool for Windrose.

This tool does not connect to the internet or collect any data.

----------------------------------------

## Build Instructions

1. Install Python 3.12  
2. Install dependencies:
   pip install pyinstaller send2trash  

3. Run:
   py -3.12 -m PyInstaller --onefile --noconsole --clean --icon=favicon.ico --name "Windrose Save Manager" --hidden-import=send2trash windrose_gui.py
