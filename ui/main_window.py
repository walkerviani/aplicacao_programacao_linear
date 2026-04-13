from PySide6.QtWidgets import QWidget, QStackedWidget, QLineEdit, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from ui.result_panel import ResultPanel
from backend.config_api import set_api_key, set_message
from backend.lp_solver import solve_linear_problem
from PySide6.QtCore import QThread, Qt, Signal, QSize
from PySide6.QtGui import QMovie, QIcon

# A Worker that runs the solver in a different thread
class SolverWorker(QThread):
    finished = Signal(dict) # Emits the result when finished

    def run(self):
        result = solve_linear_problem()
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None # Worker reference

        # Window title
        self.setWindowTitle("Linear Programming Calculation")

        self.setWindowIcon(QIcon("assets/icon.svg"))

        # Set the minimum screen size
        self.setMinimumSize(800,600)

        # Split the screen in left and right
        container = QHBoxLayout()
        # Left view is the input session
        left_view = QVBoxLayout()

        # App Title Label
        title = QLabel()
        title.setText("Linear Programming Calculator")
        title.setStyleSheet("""
        font: 24px Arial;
        color: #000000;
        font-weight: bold;
        padding-bottom:10px;
        """)
        left_view.addWidget(title)

        api_view = QHBoxLayout()

        # API Input Text
        api_message = QLabel()
        api_message.setText("API Key:")
        api_message.setStyleSheet("font: 16px Arial;color: #000000;")

        self.api_input = QLineEdit()
        self.api_input.setStyleSheet("""
        font: 16px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        padding: 4px; 
        """)
        self.api_input.textChanged.connect(self.on_api_key_changed)

        api_view.addWidget(api_message)
        api_view.addWidget(self.api_input)
        left_view.addLayout(api_view)

        # User Input Message
        msg_user_input = QLabel()
        msg_user_input.setText("Insert your problem:")
        msg_user_input.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        """)
        left_view.addWidget(msg_user_input)

        # User Input
        self.txt_input = QTextEdit()
        self.txt_input.setStyleSheet("""
        font: 15px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        margin-bottom: 10px;
        """)
        left_view.addWidget(self.txt_input)

        self.stack = QStackedWidget()
        self.stack.setFixedHeight(44)

        # Send Button
        self.button = QPushButton()
        self.button.setText("Send")
        self.button.setStyleSheet("""
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
        self.button.clicked.connect(self.on_send_clicked) # Set button function
        
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("assets/loading.gif")
        self.movie.setScaledSize(QSize(44, 44))
        self.spinner.setMovie(self.movie)

        self.stack.addWidget(self.button) # Index 0
        self.stack.addWidget(self.spinner) # Index 1
        left_view.addWidget(self.stack)

        # Result Label Message
        msg_result = QLabel()
        msg_result.setText("Result:")
        msg_result.setStyleSheet("""
        font: 16px Arial;
        color: #000000;
        padding-top:20px;
        """)
        left_view.addWidget(msg_result)

        # Result Label
        self.result = QTextEdit()
        self.result.setReadOnly(True) 
        self.result.setStyleSheet("""
        font: 15px Arial;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        """)
        left_view.addWidget(self.result)

        # Push all widgets to the top
        left_view.addStretch() 

        # Right view is the graphic session
        right_view = QVBoxLayout()
        # Set a margin
        right_view.setContentsMargins(10, 10, 10, 10)

        self.result_panel = ResultPanel()
        right_view.addWidget(self.result_panel)

        container.addLayout(left_view, 1)
        container.addLayout(right_view, 2)

        widget = QWidget()
        # App background color
        widget.setStyleSheet("background-color: #CCCCCC")
        widget.setLayout(container)
        self.setCentralWidget(widget)

    def on_send_clicked(self):
        text = self.txt_input.toPlainText() # User input text
        if not text.strip():
            self.result.setText("You need to type a valid linear programming problem")
            return
        
        if not self.api_input.text().strip():
            self.result.setText("You need to enter an API key")
            return
        
        self.result.setText("") # Clean previous message

        set_message(text) # Set the question to AI

        self.set_loading(True) # Enables loading

        self.worker = SolverWorker()
        self.worker.finished.connect(self.on_solver_finished)
        self.worker.start()

    def on_solver_finished(self, result):
        self.set_loading(False) # Disables loading
        try:
            if result["success"]:
                self.showResult(result)
                self.result_panel.update_graph()
            elif "error" in result:
                self.result.setStyleSheet("""
                    font: 15px Arial;
                    background-color: #ffffff;
                    color: #FF4040;
                    border: 1px solid #000000;
                """)
                self.result.setText("AI's response was not valid. Try again")
            else:
                self.result.setStyleSheet("""
                    font: 15px Arial;
                    background-color: #ffffff;
                    color: #FF4040;
                    border: 1px solid #000000;
                """)
                self.result.setText(f"Error:\n{result['error']}")
        except Exception as e:
            self.result.setText(str(e))      
    
    def set_loading(self, is_loading: bool):
        if is_loading:
            self.movie.start()
            self.stack.setCurrentIndex(1) # Show Spinner
        else:
            self.movie.stop()
            self.stack.setCurrentIndex(0) # Show Button

    def on_api_key_changed(self):
        set_api_key(self.api_input.text())
        
    
    def showResult(self, result):
        # Objective function
        obj_fun = "Max" if result["of_type"] == "LpMaximize" else "Min"
        
        message = f"------- RESULT -------\n"
        message += f"FO {obj_fun}: {result['of']}\n"
        message += f"----- Variables -----\n"
        for name, value in result["variables"].items():
            message += f"{name} = {value}\n"
        message += f"----- Restrictions -----\n"
        for restr in result["restrictions"]:
            message += f"{restr}\n"
        message += f"------ Non-negativity ------\n"
        for var in result["variables"]:
            message += f"{var} ≥ 0\n"
        message+= f"Best result = {result["of_value"]}"
        self.result.setText(message)