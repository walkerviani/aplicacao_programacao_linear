from PySide6.QtWidgets import QWidget, QLineEdit, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from .result_panel import ResultPanel
from backend.config_api import set_api_key, set_message
from backend.lp_solver import solve_linear_problem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window title
        self.setWindowTitle("Linear Programming Calculation")
        
        # Set the minimum screen size
        self.setMinimumSize(800,600)

        # Split the screen in left and right
        container = QHBoxLayout()
        # Left view is the input session
        leftView = QVBoxLayout()

        # App Title Label
        title = QLabel()
        title.setText("Linear Programming Calculator")
        title.setStyleSheet("""
        font: 24px Arial;
        color: #000000;
        font-weight: bold;
        padding-bottom:10px;
        """)
        leftView.addWidget(title)

        apiView = QHBoxLayout()

        # API Input Text
        apiMessage = QLabel()
        apiMessage.setText("API Key:")
        apiMessage.setStyleSheet("font: 16px Arial;color: #000000;")

        self.apiInput = QLineEdit()
        self.apiInput.setStyleSheet("""
        font: 16px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        padding: 4px; 
        """)
        self.apiInput.textChanged.connect(self.on_api_key_changed)

        apiView.addWidget(apiMessage)
        apiView.addWidget(self.apiInput)
        leftView.addLayout(apiView)

        # User Input Message
        message1 = QLabel()
        message1.setText("Insert your problem:")
        message1.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        """)
        leftView.addWidget(message1)

        # User Input
        self.textInput = QTextEdit()
        self.textInput.setStyleSheet("""
        font: 15px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        margin-bottom: 10px;
        """)
        leftView.addWidget(self.textInput)

        # Send Button
        button = QPushButton()
        button.setText("Send")
        button.setStyleSheet("""
        QPushButton {
        background-color:#000000;
        color: #ffffff;
        padding:10px;
        }
        QPushButton:hover{
        background-color:#333333;
        }
        QPushButton:pressed{
        background-color:#555555;
        }""")
        button.clicked.connect(self.on_send_clicked) # Set button function
        leftView.addWidget(button)

        # Result Label Message
        message2 = QLabel()
        message2.setText("Result:")
        message2.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        padding-top:20px;
        """)
        leftView.addWidget(message2)

        # Result Label
        self.result = QTextEdit()
        self.result.setReadOnly(True) 
        self.result.setStyleSheet("""
        font: 15px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        """)
        leftView.addWidget(self.result)

        # Push all widgets to the top
        leftView.addStretch() 

        # Right view is the graphic session
        rightView = QVBoxLayout()
        # Set a margin
        rightView.setContentsMargins(10, 10, 10, 10)

        self.result_panel = ResultPanel()
        rightView.addWidget(self.result_panel)

        container.addLayout(leftView, 1)
        container.addLayout(rightView, 2)

        widget = QWidget()
        # App background color
        widget.setStyleSheet("background-color: #E3E3E3")
        widget.setLayout(container)
        self.setCentralWidget(widget)

    def on_send_clicked(self):
        text = self.textInput.toPlainText() # User text
        message = ""
        if not text.strip():
            message = "You need to type a valid linear programming problem"
        else:
            message = "Loading..."

            self.result.setText(message)
            set_message(text)
            
            try:
                result = solve_linear_problem()

                if not result["success"]:
                    self.result.setText(f"Erro:\n{result['error']}")
                    return
                self.result.setText("result")
            except Exception as e:
                self.result.setText(e)      
    
    def on_api_key_changed(self):
        set_api_key(self.apiInput.text())