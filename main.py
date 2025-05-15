import sys
from pathlib import Path
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QHBoxLayout, QWidget, QPushButton, QLineEdit,
                             QTableWidget, QTableWidgetItem, QDialog,
                             QColorDialog, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import QColor
# import winsound


class TimerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # App configuration
        self.setWindowTitle("Pomato")
        self.resize(500, 300)
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
        self.load_tasks()


    def _setup_ui(self):
        """Set up the UI components and layouts"""
        # Task management elements
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Input task name")
        self.add_task_button = QPushButton("Add task", self)
        self.config_button = QPushButton("Configure tasks", self)
        
        # Timer elements
        self.timer_label = QLabel(self.time_left.toString("mm:ss"), self)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 48px;")
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.set_timer_button = QPushButton("Set timer", self)
        # Session indicator
        self.session_label = QLabel(f"Session: {self.session_count % 4 + 1} (Pomodoro)", self)
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("font-size: 14px")
        # Table
        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(2)
        self.task_table.setHorizontalHeaderLabels(["Name", "Time"])
        self.task_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: transparent;
                color: white;
            }
        """) 
        self.task_table.itemDoubleClicked.connect(self.configure_task) # activate configure window when double clicking a task
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # disable direct editing of a task
        
        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_task_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.config_button)
        button_layout.addWidget(self.set_timer_button)

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.task_table)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.session_label)
        layout.addLayout(button_layout)

        # Connect signals
        self.add_task_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        self.start_button.clicked.connect(self.toggle_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.config_button.clicked.connect(self.configure_task)
        self.set_timer_button.clicked.connect(self.set_pomo_time)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_pomo_time(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set pomo time")
        layout = QVBoxLayout(dialog)

        pomo_label = QLabel("Pomodoro length (in minutes):")
        pomo_input = QLineEdit()
        pomo_input.setPlaceholderText(f"Current value: {self.pomo_time.toString('m')}")

        s_break_label = QLabel("Short break length after pomo (in minutes):")
        s_break_input = QLineEdit()
        s_break_input.setPlaceholderText(f"Current value: {self.s_break.toString('m')}")

        l_break_label = QLabel("Long break length after 4 pomos (in minutes):")
        l_break_input = QLineEdit()
        l_break_input.setPlaceholderText(f"Current value: {self.l_break.toString('m')}")

        confirm_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        layout.addWidget(pomo_label)
        layout.addWidget(pomo_input)
        layout.addWidget(s_break_label)
        layout.addWidget(s_break_input)
        layout.addWidget(l_break_label)
        layout.addWidget(l_break_input)
        layout.addWidget(confirm_buttons)

        def get_value_or_current(input_field, current_time):
            """Get user input or return current value if empty"""
            time_input = input_field.text().strip()
            if not time_input:
                return int(current_time.toString("m"))
            
            if int(time_input) <= 0:
                raise ValueError("Time value must be positive")
            
            return int(time_input)

        def on_accept():
            try:
                # Process all inputs
                after_pomo = get_value_or_current(pomo_input, self.pomo_time)
                after_s_break = get_value_or_current(s_break_input, self.s_break)
                after_l_break = get_value_or_current(l_break_input, self.l_break)
    
                # Update the time settings
                self.pomo_time = QTime(0, after_pomo, 0)
                self.s_break = QTime(0, after_s_break, 0)
                self.l_break = QTime(0, after_l_break, 0)
                self.time_left = QTime(self.pomo_time)
                self.timer_label.setText(self.time_left.toString("mm:ss"))
                dialog.accept()
            except ValueError:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter a positive integer.")

        confirm_buttons.accepted.connect(on_accept)
        confirm_buttons.rejected.connect(dialog.reject)
        dialog.exec()
    

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
        selected_items = self.task_table.selectedItems()
        if selected_items:
            row = self.task_table.row(selected_items[0])
            self.current_task = self.task_table.item(row, 0).text()

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


    def add_task(self):
        task_name = self.task_input.text().strip()
        if task_name and task_name not in self.tasks:
            row = self.task_table.rowCount() # get current row
            self.task_table.insertRow(row) # add new row
            self.task_table.setItem(row, 0, QTableWidgetItem(task_name))
            self.task_table.setItem(row, 1, QTableWidgetItem("0"))
            self.tasks[task_name] = {"time": 0, "color": QColor("transparent")}
            self.task_input.clear()
            self.update_table_colors()
            self.save_tasks()

    def save_tasks(self):
        serialized_tasks = {
            name: {"time": data["time"], "color": data["color"].name()}
            for name, data in self.tasks.items()
        }
        self.data_file.write_text(json.dumps(serialized_tasks, indent=4))

    def load_tasks(self):
        if self.data_file.exists():
            data = json.loads(self.data_file.read_text())
            for task_name, info in data.items():
                row = self.task_table.rowCount()
                self.task_table.insertRow(row)
                self.task_table.setItem(row, 0, QTableWidgetItem(task_name))
                self.task_table.setItem(row, 1, QTableWidgetItem(str(info["time"])))
                self.tasks[task_name] = {
                    "time": info["time"],
                    "color": QColor(info["color"])
                }
            self.update_table_colors()

    def configure_task(self):
        selected_items = self.task_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Task Selected", "Please select a task to configure.")
            return

        row = self.task_table.row(selected_items[0])
        task_name = self.task_table.item(row, 0).text()
        task_data = self.tasks[task_name]

        dialog = QDialog(self)
        dialog.setWindowTitle("Configure Task")
        layout = QVBoxLayout(dialog)

        # Rename
        name_label = QLabel("Rename Task:")
        name_input = QLineEdit(dialog)
        name_input.setText(task_name)
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        # Color selection
        color_label = QLabel("Task Color:")
        layout.addWidget(color_label)
        
        color_preview = QLabel()
        color_preview.setFixedSize(100, 30)
        color_preview.setStyleSheet(f"background-color: {task_data['color'].name()}; border: 1px solid black;")
        layout.addWidget(color_preview)
        
        color_button = QPushButton("Change Color")
        layout.addWidget(color_button)
        
        current_color = task_data["color"]
        
        def select_color():
            nonlocal current_color
            color = QColorDialog.getColor(current_color, dialog, "Select Task Color")
            if color.isValid():
                current_color = color
                color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
        
        color_button.clicked.connect(select_color)

        # Delete Button
        delete_button = QPushButton("Delete Task", dialog)
        layout.addWidget(delete_button)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                      QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)

        # Delete task function
        def delete_task():
            reply = QMessageBox.question(
                dialog, "Delete Task", f"Are you sure you want to delete '{task_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.task_table.removeRow(row)
                del self.tasks[task_name]
                self.save_tasks()
                dialog.accept()
        
        delete_button.clicked.connect(delete_task)

        # Save function
        def save_changes():
            new_name = name_input.text().strip()
            
            # Check if new name is empty
            if not new_name:
                QMessageBox.warning(dialog, "Invalid Name", "Task name cannot be empty.")
                return
                
            # Check if new name is already taken (unless it's the same name)
            if new_name != task_name and new_name in self.tasks:
                QMessageBox.warning(dialog, "Duplicate Name", "This task name already exists.")
                return
                
            # Update task data
            if new_name != task_name:
                task_data = self.tasks.pop(task_name)  # Remove old name entry
                self.tasks[new_name] = task_data       # Add with new name
                self.task_table.item(row, 0).setText(new_name)  # Update table display
                
            # Update color
            self.tasks[new_name]["color"] = current_color
            self.update_table_colors()
            self.save_tasks()
            dialog.accept()
            
        button_box.accepted.connect(save_changes)
        button_box.rejected.connect(dialog.reject)

        dialog.setMinimumWidth(250)
        dialog.exec()

    def update_table_colors(self):
        for row in range(self.task_table.rowCount()): 
            task_name = self.task_table.item(row, 0).text()  # get task name
            if task_name in self.tasks:  # Make sure the task exists
                color = self.tasks[task_name]["color"]  # get color from dictionary
                item_task = self.task_table.item(row, 0)  # task name cell
                item_time = self.task_table.item(row, 1)  # time cell
                if item_task:
                    item_task.setBackground(color)  # set background color for task
                if item_time:
                    item_time.setBackground(color)  # set background color for time

    def closeEvent(self, event):
        # Save tasks to JSON before closing
        self.save_tasks()
        event.accept()  # Proceed with closing the window

def main():
    app = QApplication(sys.argv)
    window = TimerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
