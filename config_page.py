
from PySide6.QtWidgets import QBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout


class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: green;")
        
        layout = QVBoxLayout()
        label = QLabel("Config Page")

        layout.addWidget(label)

        self.setLayout(layout)
