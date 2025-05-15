import sys
from pathlib import Path
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QHBoxLayout, QWidget, QPushButton, QLineEdit,
                             QTableWidget, QTableWidgetItem, QDialog,
                             QColorDialog, QDialogButtonBox, QMessageBox, QStackedWidget, QComboBox)
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import QColor

class TimerScene(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Timer settings
        self.pomo_time = QTime(0, 25, 0)  # 25 minutes for default pomo time
        self.s_break = QTime(0, 5, 0)  # 5 minutes for default short break
        self.l_break = QTime(0, 15, 0)  # 15 minutes for default long break
        self.timer = QTimer(self)
        self.time_left = QTime(self.pomo_time)
        self.timer.timeout.connect(self.update_timer)
        # Session tracking
        self.session_count = 0
        self.timer_mode = "pomodoro"  # possible modes: pomodoro, short_break, long_break
        # State variables
        self.tasks = {}
        self.current_task = None
        self.state = "stopped" # possible states: stopped, running, paused, overtime
        self.data_file = Path("tasks.json")
        # Setup UI and Load data
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components and layouts"""
        # Dropdown menu
        combobox = QComboBox()
        combobox.addItem("one")

        # Timer elements
        self.timer_label = QLabel(self.time_left.toString("mm:ss"), self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px; color: white;")
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.set_timer_button = QPushButton("Set timer", self)
        # Session indicator
        self.session_label = QLabel(f"Session: {self.session_count % 4 + 1} (Pomodoro)", self)
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("font-size: 14px; color: white")

        # Layout
        combobox_layout = QVBoxLayout()
        combobox_layout.addWidget(combobox)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.set_timer_button)

        layout = QVBoxLayout()
        layout.addLayout(combobox_layout)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.session_label)
        layout.addLayout(button_layout)

        # Color theme
        self.start_button.setStyleSheet("color: white")
        self.stop_button.setStyleSheet("color: white")
        self.set_timer_button.setStyleSheet("color: white")

        # Connect signals
        self.start_button.clicked.connect(self.toggle_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_timer(self):
        """Update the timer display and track task time"""
        # Update task time if a task is selected
        if self.state != "overtime":
            self.time_left = self.time_left.addSecs(-1)
            self.timer_label.setText(self.time_left.toString("mm:ss"))

            if self.time_left == QTime(0, 0, 0):
                self.state = "overtime"
                self.set_timer_color()
                # winsound.MessageBeep()
                message_text = ""
                if self.timer_mode == "pomodoro":
                    message_text = "Pomodoro completed! Let's take a break"
                else:
                    message_text = "Break time is up! Ready for another pomo session?"
                self.msg = QMessageBox(self)
                self.msg.setWindowTitle("Pomato Time Up")
                self.msg.setText(message_text)
                ok_button = self.msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
                ok_button.clicked.connect(self.on_msg_closed)
                self.msg.show()
                self.overtime_time = QTime(0, 0, 0)
        else:
            # If it's overtime, add "+" simbol to the display time
            self.overtime_time = self.overtime_time.addSecs(1)
            self.timer_label.setText("+" + self.overtime_time.toString("mm:ss"))

        if self.current_task and self.current_task in self.tasks:
            self.tasks[self.current_task]["time"] += 1
            
            # Find the row for the current task and update the displayed time
            for row in range(self.task_table.rowCount()):
                if self.task_table.item(row, 0).text() == self.current_task:
                    self.task_table.item(row, 1).setText(str(self.tasks[self.current_task]["time"]))
                    break


    def on_msg_closed(self):
        self.msg.close()

    def toggle_timer(self):
        """Start, pause or resume the timer"""
        # Set current task from selection if available
        # selected_items = self.task_table.selectedItems()
        # if selected_items:
        #     row = self.task_table.row(selected_items[0])
        #     self.current_task = self.task_table.item(row, 0).text()

        # Toggle timer state
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
        self.current_task = None
        self.start_button.setText("Start")
        self.timer_label.setText(self.time_left.toString("mm:ss"))  # Update display from time_left
        self.set_timer_color()
        self.save_tasks()

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

class StatsScene(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout2 = QVBoxLayout()
        label2 = QLabel("Screen2")
        layout2.addWidget(label2)
        self.setLayout(layout2)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.screen1 = TimerScene()
        self.screen2 = StatsScene()
        self.stacked_widget.addWidget(self.screen1)
        self.stacked_widget.addWidget(self.screen2)

        self.button1 = QPushButton("Timer")
        self.button1.setObjectName("button1")
        self.button1.setFixedSize(80, 40)
        self.button2 = QPushButton("Stats")
        self.button2.setObjectName("button2")
        self.button2.setFixedSize(80, 40)
        self.button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)

        self.setStyleSheet("""
            QPushButton#button1{
            background-color: #c71a16;
            border-style: solid;
            border-width: 0px;
            border-radius: 5px;
            }
            QPushButton:hover#button1{
            background-color: #8f0a07;
            }
            QPushButton:pressed#button1{
            background-color: #c71a16;
            }

            QPushButton#button2{
            background-color: #36701b;
            border-style: solid;
            border-width: 0px;
            border-radius: 5px;
            }
            QPushButton:hover#button2{
            background-color: #21520b;
            }
            QPushButton:pressed#button2{
            background-color: #36701b;
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)
        self.setWindowTitle("test")
        self.resize(500, 500)
    
    def closeEvent(self, event):
        # Save tasks to JSON before closing
        self.save_tasks()
        event.accept()  # Proceed with closing the window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())