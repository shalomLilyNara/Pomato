from PySide6.QtWidgets import QBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QSlider
from PySide6.QtCore import Qt, QTime, Signal


class ConfigPage(QWidget):
    # Emit signals when timer values change
    pomo_time_changed = Signal(int)
    s_break_changed = Signal(int)
    l_break_changed = Signal(int)

    def __init__(self):
        super().__init__()

        # Slider settings
        self.pomo_slider = QSlider(Qt.Horizontal)
        self.pomo_slider.setMaximum(60)
        self.pomo_slider.setMinimum(15)
        self.pomo_slider.setSingleStep(5)
        self.pomo_slider.setValue(25) # Set default pomo timer to 25 minutes

        self.s_break_slider = QSlider(Qt.Horizontal)
        self.s_break_slider.setMaximum(20)
        self.s_break_slider.setMinimum(3)
        self.s_break_slider.setValue(5) # Set default short break to 5 minutes

        self.l_break_slider = QSlider(Qt.Horizontal)
        self.l_break_slider.setMaximum(30)
        self.l_break_slider.setMinimum(15)
        self.l_break_slider.setSingleStep(5)
        self.l_break_slider.setValue(15) # Set default long break to 20 minutes

        self.pomo_label = QLabel()
        self.pomo_discription = QLabel("Pomo timer")
        self.pomo_label.setAlignment(Qt.AlignCenter)
        self.pomo_discription.setAlignment(Qt.AlignCenter)
        self.pomo_slider.valueChanged.connect(self.update_pomo)
        self.update_pomo(25)

        self.s_break_label = QLabel()
        self.s_break_discription = QLabel("Short break timer")
        self.s_break_label.setAlignment(Qt.AlignCenter)
        self.s_break_discription.setAlignment(Qt.AlignCenter)
        self.s_break_slider.valueChanged.connect(self.update_s_break)
        self.update_s_break(5)

        self.l_break_label = QLabel()
        self.l_break_discription = QLabel("Long break timer")
        self.l_break_label.setAlignment(Qt.AlignCenter)
        self.l_break_discription.setAlignment(Qt.AlignCenter)
        self.l_break_slider.valueChanged.connect(self.update_l_break)
        self.update_l_break(15)

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

    def update_s_break(self, value):
        self.s_break_label.setText(str(value))
        self.s_break_changed.emit(value)

    def update_l_break(self, value):
        step = 5
        adjusted_value = round(value / step) * step
        if adjusted_value != value:
            self.l_break_slider.setValue(adjusted_value)
        self.l_break_label.setText(str(adjusted_value))
        self.l_break_changed.emit(adjusted_value)

