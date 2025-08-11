from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QListWidget, QCheckBox, QWidget, QListWidgetItem, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys
import json

class TaskItem(QWidget):
    def __init__(self, task_name, task_list, new_item, main_window):
        super().__init__()
        self.task_name = task_name
        self.task_list = task_list
        self.new_item = new_item
        self.main_window = main_window

        # Load the task widget UI
        self.load_ui()

        # Set the task name
        self.task_checkbox.setText(task_name)

        # Connect signals
        self.delete_button.clicked.connect(self.delete_task)

    def load_ui(self):
        loader_task = QUiLoader()
        file_task = QFile("ui/task_item.ui")
        file_task.open(QFile.ReadOnly)

        # Load the UI into widget
        widget_task = loader_task.load(file_task, self)
        file_task.close()

        # Get references to the UI elements
        self.task_checkbox: QCheckBox = widget_task.findChild(QCheckBox, "taskCheckbox")
        self.delete_button: QPushButton = widget_task.findChild(QPushButton, "deleteButton")

        # Set the layout of this widget to match the loaded UI
        if widget_task.layout():
            self.setLayout(widget_task.layout())    
    
    def delete_task(self):
        row: int = self.task_list.row(self.new_item)
        if row >= 0:
            self.task_list.takeItem(row)
            self.main_window.tasks.remove(self.task_name)
            self.main_window.save_tasks_to_file()


class TodoPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Load UI and setup connections
        self.load_ui()
        self.connect_signals()
        
        # Load tasks from file
        self.load_tasks_from_file()
    
    def load_tasks_from_file(self):
        """Load tasks from JSON file"""
        try:
            with open("data/tasks.json") as task_file:
                tasks_json = task_file.read()
            self.tasks = json.loads(tasks_json)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
        for task_name in self.tasks:
            self.add_task_to_list(task_name)

    def save_tasks_to_file(self):
        """Save tasks to JSON file"""
        try:
            with open("data/tasks.json", "w") as task_file:
                json.dump(self.tasks, task_file, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def load_ui(self):
        """Load the main window UI file"""
        loader = QUiLoader()
        file_ui = QFile("ui/todo.ui")
        file_ui.open(QFile.ReadOnly)
        ui_widget = loader.load(file_ui, self)
        file_ui.close()
        
        # Get references to UI elements
        self.task_input: QLineEdit = self.findChild(QLineEdit, "taskInput")
        self.add_button: QPushButton = self.findChild(QPushButton, "addButton")
        self.task_list: QListWidget = self.findChild(QListWidget, "taskList")

        # Set the loaded UI as the layout of this widget
        layout = ui_widget.layout()
        self.setLayout(layout)
    
    def connect_signals(self):
        """Connect UI signals to methods"""
        self.add_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
      
    def add_task(self):
        """Add a new task from input field"""
        task_name = self.task_input.text().strip()
        if task_name and task_name not in self.tasks:
            self.add_task_to_list(task_name)
            # Add to list
            self.tasks.append(task_name)
            self.save_tasks_to_file()
            # Clear input field
            self.task_input.clear()
    
    def add_task_to_list(self, task_name):
        """Add a task to the list widget"""
        # Create a new list item
        new_item = QListWidgetItem()

        # Create custom widget for this task
        task_widget = TaskItem(task_name, self.task_list, new_item, self)

        # Set the item size to fit the widget
        new_item.setSizeHint(task_widget.sizeHint())

        # Add item to list and set the custom widget
        self.task_list.addItem(new_item)
        self.task_list.setItemWidget(new_item, task_widget)

    def closeEvent(self, event):
        """Save tasks when closing the application"""
        self.save_tasks_to_file()
        event.accept()