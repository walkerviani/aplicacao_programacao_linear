import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def main():

    # Tells Windows to treat this as its own app, separate from Python
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "linear-programming-calculation"
        )

    app = QApplication(sys.argv)

    # Sets the icon globally for all windows in the app
    app.setWindowIcon(QIcon("assets/icon.ico"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()