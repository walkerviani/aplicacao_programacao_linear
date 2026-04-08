import sys # Only needed for access to command line arguments
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window title
        self.setWindowTitle("Cálculo de Programação Linear")
        
        # Set the minimum screen size
        self.setMinimumSize(800,600)

        # Split the screen in left and right
        container = QHBoxLayout()
        # Left view is the input session
        leftView = QVBoxLayout()

        # App title
        title = QLabel()
        title.setText("Linear Programming Calculator")
        title.setStyleSheet("""
        font: 24px Arial;
        color: #000000;
        font-weight: bold;
        """)
        title.setMaximumHeight(50)
        leftView.addWidget(title)

        # User input hint message
        message1 = QLabel()
        message1.setText("Insert your problem:")
        message1.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        """)
        message1.setMaximumHeight(25)
        leftView.addWidget(message1)

        # User input text
        textInput = QTextEdit()
        textInput.setStyleSheet("""
        font: 15px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000""")
        textInput.setMaximumHeight(200)
        leftView.addWidget(textInput)

        # Send information button
        button = QPushButton()
        button.setText("Send")
        button.setStyleSheet("""
        background-color:#000000;
        color: #ffffff""")
        button.setMaximumHeight(50)
        leftView.addWidget(button)

        # Output hint message
        message2 = QLabel()
        message2.setText("Result:")
        message2.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        """)
        message2.setMaximumHeight(25)
        leftView.addWidget(message2)

        # Result label
        result = QLabel()
        result.setStyleSheet("""
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000""")
        result.setMaximumHeight(100)
        leftView.addWidget(result)

        # Right view is the graphic session
        rightView = QVBoxLayout()
        rightView.addWidget(QLabel('Graphic'))

        container.addLayout(leftView, 1)
        container.addLayout(rightView, 2)

        widget = QWidget()
        # App background color
        widget.setStyleSheet("background-color: #E3E3E3")
        widget.setLayout(container)
        self.setCentralWidget(widget)


# The svs.argv allows to use command line arguments on the app
# If not using command line arguments = QApplication([])
app = QApplication(sys.argv) 

window = MainWindow()
window.show()  # Show the screen

app.exec() # Execute the screen