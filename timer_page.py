from PySide6.QtWidgets import QBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QComboBox
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import Qt, QTime, QTimer, QUrl, Slot
import json
import pathlib
from stats_page import StatsPage

class TimerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #191919;")

        # Import stats from stats page
        self.stats_instance = StatsPage()

        # Timer settings
        self.pomo_time = QTime(0, 0, 2)  # 25 minutes for default pomo time
        self.s_break = QTime(0, 5, 0)  # 5 minutes for default short break
        self.l_break = QTime(0, 15, 0)  # 15 minutes for default long break
        self.timer = QTimer(self)
        self.time_left = QTime(self.pomo_time)
        self.timer.timeout.connect(self.update_timer)

        # Sound settings
        self.pomo_done_sound = QSoundEffect()
        self.pomo_done_sound.setSource(QUrl.fromLocalFile("./resources/mixkit-correct-answer-tone-2870.wav"))

        # Session tracking
        self.session_count = 0
        self.timer_mode = "pomodoro"  # possible modes: pomodoro, short_break, long_break
        # State variables
        # self.tasks = {}
        # self.current_task = None
        self.state = "stopped" # possible states: stopped, running, paused, overtime
        # self.data_file = Path("tasks.json")
        # Setup UI and Load data
        self._setup_ui()


    def _setup_ui(self):
        """Set up the UI components and layouts"""
        # ComboBox: Add every item's name from the dictionary 
        self.task_combobox = QComboBox(self)
        for task in self.stats_instance.stats:
            self.task_combobox.addItem(task["name"])
        self.task_combobox.setStyleSheet("QComboBox::item:selected { background-color: rgb(255, 0, 0); }")
        # Timer elements
        self.timer_label = QLabel(self.time_left.toString("mm:ss"), self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px; color: white;")
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        # Session indicator
        self.session_label = QLabel(f"Session: {self.session_count % 4 + 1} (Pomodoro)", self)
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("font-size: 14px; color: white")

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.addWidget(self.task_combobox)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.session_label)
        layout.addLayout(button_layout)

        # Color theme
        self.start_button.setStyleSheet("color: white")
        self.stop_button.setStyleSheet("color: white")

        # Connect signals
        self.start_button.clicked.connect(self.toggle_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        # Set layout
        self.setLayout(layout)
        self.setStyleSheet("""
        QComboBox{
        color: white;
        }

        QComboBox::item:selected {
        background-color: #FF4433;
        }
        """)


    # Slots to receive signals from config_page
    @Slot(int)
    def update_pomo_time(self, minutes):
        self.pomo_time = QTime(0, minutes, 0)
        # Update the timer if it isn't running
        if self.timer_mode == "pomodoro" and self.state == "stopped":
            self.time_left = QTime(self.pomo_time)
            self.timer_label.setText(self.time_left.toString("mm:ss"))

    @Slot(int)
    def update_s_break_time(self, minutes):
        self.s_break= QTime(0, minutes, 0)
        if self.timer_mode == "short_break" and self.state == "stopped":
            self.time_left = QTime(self.s_break)
            self.timer_label.setText(self.time_left.toString("mm:ss"))

    @Slot(int)
    def update_l_break_time(self, minutes):
        self.lbreak = QTime(0, minutes, 0)
        if self.timer_mode == "long_break" and self.state == "stopped":
            self.time_left = QTime(self.l_break)
            self.timer_label.setText(self.time_left.toString("mm:ss"))


    def update_timer(self):
        """Update the timer display and track task time"""
        if self.state != "overtime":
            self.time_left = self.time_left.addSecs(-1)
            self.timer_label.setText(self.time_left.toString("mm:ss"))

            # Add working time to current task
            self.stats_instance.stats[self.task_combobox.currentIndex()]["time"] += 1
            self.stats_instance.save_task()

            if self.time_left == QTime(0, 0, 0):
                self.state = "overtime"
                self.set_timer_color()
                if self.timer_mode == "pomodoro":
                    self.pomo_done_sound.play()
                else:
                    self.pomo_done_sound.play()
                self.overtime_time = QTime(0, 0, 0)
        else:
            # If it's overtime, add "+" simbol to the display time
            self.overtime_time = self.overtime_time.addSecs(1)
            self.timer_label.setText("+" + self.overtime_time.toString("mm:ss"))
            # Add working time to current task for overtime
            self.stats_instance.stats[self.task_combobox.currentIndex()]["time"] += 1
            self.stats_instance.save_task()

    def toggle_timer(self):
        """Start, pause or resume the timer"""
        if self.state == "stopped" or self.state == "paused":
            self.state = "running"
            self.start_button.setText("Pause")
            self.timer.start(1000)
        elif self.state == "running":
            self.state = "paused"
            self.start_button.setText("Resume")
            self.timer.stop()
        self.set_timer_color()

    def stop_timer(self):
        """Stop the timer and reset to default state"""
        self.timer.stop()
        # Add 1 to session count if it is overtime (if the user has finished the pomo)
        if self.state == "overtime" and self.timer_mode == "pomodoro":
            self.session_count += 1

            if self.session_count % 4 == 0:
                self.timer_mode = "long_break"
                self.time_left = QTime(self.l_break)
                self.session_label.setText("(Long Break)")
            else:
                self.timer_mode = "short_break"
                self.time_left = QTime(self.s_break)
                self.session_label.setText("(Short Break)")
        else:
            self.timer_mode = "pomodoro"
            self.time_left = QTime(self.pomo_time)
            self.session_label.setText(f"Session: {self.session_count % 4 + 1} (Pomodoro)")

        self.state = "stopped"

        if self.timer_mode == "short_break" or self.timer_mode == "long_break":
            self.stop_button.setText("Finish break")
        else:
            self.stop_button.setText("Stop")

        self.current_task = None
        self.start_button.setText("Start")
        self.timer_label.setText(self.time_left.toString("mm:ss"))  # Update display from time_left
        self.set_timer_color()

    def set_timer_color(self):
        if self.state == "running":
            if self.timer_mode == "pomodoro":
                self.timer_label.setStyleSheet("font-size: 48px; color: #FF4433;")
            elif self.timer_mode == "short_break":
                self.timer_label.setStyleSheet("font-size: 48px; color: #4CAF50;")
            elif self.timer_mode == "long_break":
                self.timer_label.setStyleSheet("font-size: 48px; color: #2196F3;")
        elif self.state == "paused":
            self.timer_label.setStyleSheet("font-size: 48px; color: #088F8F;")
        elif self.state == "stopped":
            self.timer_label.setStyleSheet("font-size: 48px; color: white;")
        elif self.state == "overtime":
            self.timer_label.setStyleSheet("font-size: 48px; color: yellow;")
