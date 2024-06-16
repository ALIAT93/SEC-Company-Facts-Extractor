from PySide6.QtWidgets import QMainWindow
from Style_Setup_Class import app_Intializer

# Create a class for the main window
class MainWindow(QMainWindow):
    def __init__(self, app_instance):
        super().__init__()

        self.app = app_instance  # Assign the provided app_instance

        self.setWindowTitle("Financial Facts Extractor")
        self.setGeometry(100, 100, 1200, 600)
        self.init_ui()

    def init_ui(self):
        app_starter = app_Intializer(self.app)  # Pass the QApplication instance
        app_starter.start()