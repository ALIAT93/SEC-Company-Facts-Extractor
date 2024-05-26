import sys
from PySide6.QtWidgets import QApplication
from Pyside6_UI_Classes.MainWindow_Class import MainWindow

if __name__ == "__main__":
    app = QApplication([])  # Create a single instance of QApplication

    main_window = MainWindow(app)  # Pass the QApplication instance to MainWindow
    main_window.show()
    sys.exit(app.exec_())  # Call exec_() on the QApplication instance
    