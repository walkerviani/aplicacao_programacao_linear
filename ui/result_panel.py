from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# GraphCanvas inherits from FigureCanvasQTAgg
# This makes the Matplotlib figure behave as a Qt widget
class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self):
        # Create a blank Matplotlib figure
        fig = Figure()
        # Add a single plot area inside the figure
        # 111 means: 1 row, 1 column, position 1 (single plot)
        self.axes = fig.add_subplot(111)
        # Pass the figure to the parent class so it can render it
        super().__init__(fig)


# ResultPanel is the full right-side panel of the UI
# It contains a stack that switches between the graph and a message
class ResultPanel(QWidget):
    def __init__(self):
        # Initialize the parent QWidget
        super().__init__()

        # Create a vertical layout for this panel
        layout = QVBoxLayout()
        self.setLayout(layout)

        # QStackedWidget holds multiple widgets but shows only one at a time
        # index 0 = graph, index 1 = message
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # --- Index 0: Graph widget ---
        self.canvas = GraphCanvas()
        self.stack.addWidget(self.canvas)

        # --- Index 1: Message label ---
        self.message_label = QLabel("No data to display.")
        # Center the text horizontally and vertically
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.message_label)

        # Start by showing the message (no data yet)
        self.show_message("No data to display.")

    def update_graph(self, function, constraints):
        # Clear the previous plot before drawing a new one
        self.canvas.axes.clear()

        # Plot each constraint
        for i, (x, y) in enumerate(constraints):
            self.canvas.axes.plot(x, y, label=f'Constraint {i+1}')
        
        # Plot the objective function
        self.canvas.axes.plot(function['x'], function['y'], linewidth=2, label='Objective')
        
        # Show the legend
        self.canvas.axes.legend()

        # Refresh the canvas so the new plot appears on screen
        self.canvas.draw()
        
        # Switch the stack to show the graph (index 0)
        self.stack.setCurrentIndex(0)

    def show_message(self, text):
        # Update the message label text
        self.message_label.setText(text)
        self.message_label.setStyleSheet("""
        font: 24px Arial;
        color: #000000;
        font-weight: bold;
        """)
        # Switch the stack to show the message (index 1)
        self.stack.setCurrentIndex(1)