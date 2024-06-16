import sys
from Platform_Class  import Platform

# Create a class to manage the main application logic
class app_Intializer:
    def __init__(self, app_instance):
        self.app = app_instance  # Assign the provided app_instance

    def start(self):
        self.setup_styles()
        self.platform = Platform(None)  # Passing None as parent
        self.platform.show()
        sys.exit(self.app.exec_())  # Call exec_() on the QApplication instance


    def setup_styles(self):
        button_style = '''
            QPushButton {
                background-color: #4169E1;
                color: #FFFFFF;
                font-family: Helvetica;
                font-size: 16px;
            }
        '''
        label_style = '''
            QLabel {
                background-color: #FFFFFF;
                color: #050505;
                font-family: Helvetica;
                font-size: 12px;
            }
        '''
        list_widget_style = '''
            QListWidget {
                background-color:#F0F0F0;
                color: #050505;
                font-family: Helvetica;
                font-size: 12px;
            }
        '''
        tab_style = '''
            QTabWidget::pane {
                border: none;
                background-color: #050505;
            }
            QTabWidget::tab-bar {
                alignment: center;
                color: #050505;
            }
            QTabWidget::tab {
                background-color: #FFFFFF;
                color: #050505;
                font-family: Helvetica;
                font-size: 12px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #FFFFFF;
                color: #050505;
                font-family: Helvetica;
                font-size: 12px;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background-color:#4169E1;
                color: #050505;
            }
        '''
        textedit_style = '''
            QTextEdit {
                background-color: #EFEFEF;
                color: #050505;
                font-family: Helvetica;
                font-size: 12px;
                border: none;
                padding: 10px;
            }
        '''
        stylesheet = f'''
            Platform {{
                background-color: #FFFFFF;
            }}
        {button_style}{label_style}{list_widget_style}{tab_style}{textedit_style}
        '''
        self.app.setStyleSheet(stylesheet) 