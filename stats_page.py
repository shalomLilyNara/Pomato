import json
import pathlib
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QLabel, QPushButton,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QMessageBox, QHeaderView)

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QPushButton{
            color: white;
            }
            QLineEdit{
            color: white;
            }
            QTableWidget::item:selected {
                background-color: transparent;
                color: white;
            }
            QHeaderView::section{
            color: white;
            }
            QLabel{
            color: white;
            }
        """)

        """ Load stats.json, create one if it doesn't exist """
        self.json_path = pathlib.Path('./data/stats.json')
        try:
            with self.json_path.open() as f:
                self.stats = json.load(f)
                self.create_table(self.stats)
        except( FileNotFoundError, json.JSONDecodeError):
            # Create the file and directory
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            self.stats = [{
                "name": "Coding",
                "time": 0
            }]
            self.save_task()
            # Load the file that was just created
            with self.json_path.open() as f:
                self.stats = json.load(f)
                self.create_table(self.stats)

        # Task management ui
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Input category name")
        self.add_task_button = QPushButton("Add", self)
        self.add_task_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)

        # Layout set up
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_task_button)
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_table(self, stats):
        self.tasks = []
        keys = ["Name", "Time(min)"]
        # Create table if it doesn't exist yet
        if not hasattr(self, "table"):
            self.table = QTableWidget(self)
            self.table.setColumnCount(2)
            self.header = self.table.horizontalHeader()
            self.table.setHorizontalHeaderLabels(keys)
            self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            # Disable direct editing of a task
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Clear existing rows and set new row count
        self.table.setRowCount(0)
        self.table.setRowCount(len(stats))

        for row, task in enumerate(stats):
            # Add each value of the task to the table
            n = QTableWidgetItem(task["name"])
            n.setForeground(QColor("white"))
            t = QTableWidgetItem(str(round(task["time"] / 60)))
            t.setForeground(QColor("white"))
            self.table.setItem(row, 0, n)
            self.table.setItem(row, 1, t)
            # Append task name to "tasks" list
            self.tasks.append(task["name"])
        self.table.itemDoubleClicked.connect(self.configure_task) # activate configure window when double clicking a task

    def configure_task(self):
        item = self.table.selectedItems()
        row = self.table.row(item[0])
        task_name = self.table.item(row, 0).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Configure")
        layout = QVBoxLayout(dialog)

        # Rename
        name_label = QLabel("Category name:")
        name_input = QLineEdit(dialog)
        name_input.setText(task_name)
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        # Delete button
        delete_button = QPushButton("Delete", dialog)
        layout.addWidget(delete_button)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(button_box)

        def delete_task():
            reply = QMessageBox.question(
                dialog, "Delete Task", f"Are you sure you want to delete '{task_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.table.removeRow(row)
                self.tasks.remove(task_name)
                self.stats = [item for item in self.stats if item["name"] != task_name]
                self.save_task()
                dialog.accept()
        delete_button.clicked.connect(delete_task)

        def save_changes():
            nonlocal task_name
            nonlocal name_input
            # Check if new name is empty
            if not name_input.text().strip():
                QMessageBox.warning(dialog, "Invalid Name", "Task name cannot be empty.")
                return
            # Check if new name is already taken
            if name_input != task_name and name_input in self.tasks:
                QMessageBox.warning(dialog, "Duplicate Name", "This task name already exists.")
                return
            # Update task name
            for item in self.stats:
                if item["name"] == task_name:
                    item["name"] = name_input.text()
                    break
            # Update color
            self.save_task()
            dialog.accept()

        button_box.accepted.connect(save_changes)
        name_input.returnPressed.connect(save_changes)
        button_box.rejected.connect(dialog.reject)
        dialog.exec()

    def add_task(self):
        task_name = self.task_input.text().strip()
        # Add a task if the task name is not empty and the task doesn't alredy exist
        if task_name and task_name not in self.tasks:
            # Add a new row to table
            new_task = {
                "name": task_name,
                "time": 0
            }
            self.stats.append(new_task)
            # Update json file
            self.save_task()
            self.create_table(self.stats)
            # Clear the placeholder
            self.task_input.clear()

    def save_task(self):
        with self.json_path.open(mode="w+") as f:
            json.dump(self.stats, f, indent=2)
