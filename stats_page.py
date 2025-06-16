from PySide6.QtWidgets import QBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout


class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: red;")
        
        layout = QVBoxLayout()
        label = QLabel("Stats Page")

        layout.addWidget(label)

        self.setLayout(layout)
