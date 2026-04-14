from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from backend.graphic_data import get_lines
from backend.lp_solver import get_result

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

    def update_graph(self):
        try:
            # Clear the previous plot before drawing a new one
            self.canvas.axes.clear()
            result = get_result()
            num_vars = len(result["parts"][2].split(";")) # Number of index in the array

            if num_vars == 0 or num_vars == 1:
                self.show_message("Something went wrong.\nTry Again!")
            elif num_vars == 2:
                # Plot each constraint
                for i, (x, y) in enumerate(get_lines()):
                    self.canvas.axes.plot(x, y, label=f'Constraint {i+1}')
            
                # Plot the objective function
                obj_vars_values = list(result["variables"].values()) # Ex: [10.0, 20.0]
                x_optimal = obj_vars_values[0]
                y_optimal = obj_vars_values[1]
                self.canvas.axes.plot(x_optimal, y_optimal, 
                        marker='.',
                        markersize=15,
                        color='red', 
                        label=f'Optimal: ({x_optimal}, {y_optimal})')
            
                # Show the legend
                self.canvas.axes.legend()

                lines = get_lines()
                all_x = [p for x_pts, _ in lines for p in x_pts]
                all_y = [p for _, y_pts in lines for p in y_pts]
                x_max = max(all_x) * 1.1
                y_max = max(all_y) * 1.1
                self.canvas.axes.set_xlim(0, x_max)
                self.canvas.axes.set_ylim(0, y_max)

                # Refresh the canvas so the new plot appears on screen
                self.canvas.draw()
            
                # Switch the stack to show the graph (index 0)
                self.stack.setCurrentIndex(0)
            else:
                self.show_message("Graph not available for problems\nwith more than 2 variables.")
        except Exception as e:
            self.show_message("Something went wrong.\nTry Again!")

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