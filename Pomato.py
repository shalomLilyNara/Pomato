from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
import sys
from mainwindow import MainWindow


app = QApplication(sys.argv)
QFontDatabase.addApplicationFont("resources\GohuFont14NerdFontMono-Regular.ttf")
app.setFont(QFont("GohuFont 14 Nerd Font Mono", 14))  # (Font family, size)

window = MainWindow(app)
window.resize(500, 500)
window.show()

sys.exit(app.exec())
