from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QSlider
from PySide6.QtCore import Qt,Signal
import json
from pathlib import Path

class ConfigPage(QWidget):
    # Emit signals when timer values change
    pomo_time_changed = Signal(int)
    s_break_changed = Signal(int)
    l_break_changed = Signal(int)

    def __init__(self):
        super().__init__()
        """Load timer settings from JSON file"""
        try:
            with open("data/timer_settings.json") as f:
                timer_settings_json = f.read()
                self.timer_settings = json.loads(timer_settings_json)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create a json file with default settings
            timer_settings_json = Path("data/timer_settings.json")
            timer_settings_json.touch()
            self.timer_settings = [25, 5, 15] # Default timer settings (pomo, short break, long break)
            with open("data/timer_settings.json", "w") as f:
                json.dump(self.timer_settings, f)

        # Slider settings
        self.pomo_slider = QSlider(Qt.Horizontal)
        self.pomo_slider.setMaximum(60)
        self.pomo_slider.setMinimum(15)
        self.pomo_slider.setSingleStep(5)
        self.pomo_slider.setValue(self.timer_settings[0])

        self.s_break_slider = QSlider(Qt.Horizontal)
        self.s_break_slider.setMaximum(20)
        self.s_break_slider.setMinimum(3)
        self.s_break_slider.setValue(self.timer_settings[1])

        self.l_break_slider = QSlider(Qt.Horizontal)
        self.l_break_slider.setMaximum(30)
        self.l_break_slider.setMinimum(15)
        self.l_break_slider.setSingleStep(5)
        self.l_break_slider.setValue(self.timer_settings[2])

        self.pomo_label = QLabel()
        self.pomo_discription = QLabel("Pomo timer")
        self.pomo_label.setAlignment(Qt.AlignCenter)
        self.pomo_discription.setAlignment(Qt.AlignCenter)
        self.pomo_slider.valueChanged.connect(self.update_pomo)
        self.update_pomo(self.timer_settings[0])

        self.s_break_label = QLabel()
        self.s_break_discription = QLabel("Short break timer")
        self.s_break_label.setAlignment(Qt.AlignCenter)
        self.s_break_discription.setAlignment(Qt.AlignCenter)
        self.s_break_slider.valueChanged.connect(self.update_s_break)
        self.update_s_break(self.timer_settings[1])

        self.l_break_label = QLabel()
        self.l_break_discription = QLabel("Long break timer")
        self.l_break_label.setAlignment(Qt.AlignCenter)
        self.l_break_discription.setAlignment(Qt.AlignCenter)
        self.l_break_slider.valueChanged.connect(self.update_l_break)
        self.update_l_break(self.timer_settings[2])

        # Layout settings
        layout = QVBoxLayout()

        layout.addWidget(self.pomo_discription)
        layout.addWidget(self.pomo_label)
        layout.addWidget(self.pomo_slider)

        layout.addWidget(self.s_break_discription)
        layout.addWidget(self.s_break_label)
        layout.addWidget(self.s_break_slider)

        layout.addWidget(self.l_break_discription)
        layout.addWidget(self.l_break_label)
        layout.addWidget(self.l_break_slider)

        self.setLayout(layout)

        self.setStyleSheet("""
        QLabel{
        color: white;
        font-size: 30px;
        }

        QSlider::groove:horizontal {
        border: 1px solid;
        height: 10px;
        margin: 0px;
        }

        QSlider::handle:horizontal {
        background-color: green;
        border: 1px solid;
        height: 40px;
        width: 20px;
        margin: -15px 0px;
        }
        """)

    def update_pomo(self, value):
        step = 5
        adjusted_value = round(value / step) * step
        if adjusted_value != value:
            self.pomo_slider.setValue(adjusted_value)
        self.pomo_label.setText(str(adjusted_value))
        self.pomo_time_changed.emit(adjusted_value)
        self.timer_settings[0] = adjusted_value
        self.save_changes()

    def update_s_break(self, value):
        self.s_break_label.setText(str(value))
        self.s_break_changed.emit(value)
        self.timer_settings[1] = value
        self.save_changes()

    def update_l_break(self, value):
        step = 5
        adjusted_value = round(value / step) * step
        if adjusted_value != value:
            self.l_break_slider.setValue(adjusted_value)
        self.l_break_label.setText(str(adjusted_value))
        self.l_break_changed.emit(adjusted_value)
        self.timer_settings[2] = adjusted_value
        self.save_changes()

    def save_changes(self):
        """Save timer settings to JSON file"""
        with open("data/timer_settings.json", "w") as f:
            json.dump(self.timer_settings, f)
