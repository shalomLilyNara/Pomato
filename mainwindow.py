from PySide6.QtWidgets import QBoxLayout, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from timer_page import TimerPage
from stats_page import StatsPage
from config_page import ConfigPage

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Pomato")

        # Create the pages
        self.timer_page = TimerPage()
        self.stats_page = StatsPage()
        self.config_page = ConfigPage()

        # Connect the signals from config_page to slots in timer_page
        self.config_page.pomo_time_changed.connect(self.timer_page.update_pomo_time)
        self.config_page.s_break_changed.connect(self.timer_page.update_s_break_time)
        self.config_page.l_break_changed.connect(self.timer_page.update_l_break_time)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.timer_page)
        self.stacked_widget.addWidget(self.stats_page)
        self.stacked_widget.addWidget(self.config_page)

        timer_button= QPushButton()
        timer_button.setStyleSheet("border: none;")
        timer_button.setIcon(QIcon("./resources/stopwatch.png"))
        timer_button.setIconSize(QSize(64, 64))
        timer_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        stats_button = QPushButton()
        stats_button.setStyleSheet("border: none;")
        stats_button.setIcon(QIcon("./resources/stopwatch.png"))
        stats_button.setIconSize(QSize(64, 64))
        stats_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        config_button = QPushButton()
        config_button.setStyleSheet("border: none;")
        config_button.setIcon(QIcon("./resources/stopwatch.png"))
        config_button.setIconSize(QSize(64, 64))
        config_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Layout settings
        layout = QHBoxLayout()

        layout_switch = QVBoxLayout()
        layout_switch.addWidget(timer_button)
        layout_switch.addWidget(stats_button)
        layout_switch.addWidget(config_button)

        layout.addLayout(layout_switch)
        layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #191919;")
        central_widget.setLayout(layout)
        central_widget.setMouseTracking(True)
        self.setMouseTracking(True)
        self.setCentralWidget(central_widget)
