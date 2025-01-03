############################################################
# airport_planning.py
#
# Your main PyQt application that imports the 'interval_partitioning'
# function and 'Aircraft' class from interval_partitioning.py and uses them
# to plan gates visually.
############################################################

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
    QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

from interval_partitioning import Aircraft, interval_partitioning


class AirportPlanningApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airport Gate Planning")
        self.setGeometry(230, 30, 1200, 780)
        
        # Initialize data structures
        self.aircraft_list = []
        self.gate_assignments = []
        self.gates_needed = 0
        
        # Set up the UI
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        """
        Build and configure the main user interface elements.
        """
        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Input section at the top
        input_layout = QHBoxLayout()
        
        # Input fields
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Aircraft Code")
        self.arrival_input = QLineEdit()
        self.arrival_input.setPlaceholderText("Arrival (HH:MM)")
        self.departure_input = QLineEdit()
        self.departure_input.setPlaceholderText("Departure (HH:MM)")
        
        # Set fixed width for input fields for clarity
        for input_field in [self.code_input, self.arrival_input, self.departure_input]:
            input_field.setFixedWidth(120)
        
        # Buttons
        self.add_button = QPushButton("Add Aircraft")
        self.add_button.clicked.connect(self.add_aircraft)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_aircraft)
        self.save_button = QPushButton("Save Chart")
        self.save_button.clicked.connect(self.save_chart)
        
        # Add input widgets to the layout
        input_layout.addWidget(self.code_input)
        input_layout.addWidget(self.arrival_input)
        input_layout.addWidget(self.departure_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.delete_button)
        input_layout.addStretch()
        input_layout.addWidget(self.save_button)
        
        self.layout.addLayout(input_layout)
        
        # Aircraft table
        self.aircraft_table = QTableWidget()
        self.aircraft_table.setColumnCount(4)
        self.aircraft_table.setHorizontalHeaderLabels(["Aircraft Code", "Arrival", "Departure", "Gate"])
        self.aircraft_table.setMinimumHeight(300)
        self.layout.addWidget(self.aircraft_table)
        
        # Planning button
        self.plan_button = QPushButton("Run Planning and Visualize")
        self.plan_button.clicked.connect(self.run_planning)
        self.layout.addWidget(self.plan_button)
        
        # Matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Control how the vertical space is shared
        self.layout.setStretchFactor(self.aircraft_table, 30)
        self.layout.setStretchFactor(self.canvas, 70)

    def minutes_to_time_str(self, minutes):
        """
        Convert an integer representing minutes from midnight
        into an HH:MM string format.
        """
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def to_m(self, time_str):
        """
        Convert an HH:MM time string into an integer
        representing minutes from midnight.
        """
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M")
            return parsed_time.hour * 60 + parsed_time.minute
        except ValueError:
            raise ValueError("Invalid time format")

    def add_aircraft(self):
        """
        Adds a new aircraft to the list based on the input fields (code, arrival,
        and departure times). This method then performs an incremental assignment
        for the newly added aircraft so that existing gate assignments remain 
        unchanged.

        Steps:
        1. Validate the user inputs for arrival and departure times.
        2. If valid, create a new Aircraft object and add it to self.aircraft_list.
        3. Attempt to find a suitable gate for this new aircraft using 
        assign_flight_incrementally() without altering existing assignments.
        4. Clear the input fields, update the table, and refresh the visualization.
        """
        try:
            code = self.code_input.text().strip()
            arrival = self.to_m(self.arrival_input.text().strip())
            departure = self.to_m(self.departure_input.text().strip())
            
            if departure <= arrival:
                raise ValueError("Departure must be after arrival")
                
            # Create a new Aircraft object
            aircraft = Aircraft(code, arrival, departure)

            # Add the new aircraft to the list
            self.aircraft_list.append(aircraft)
            
            # Perform incremental gate assignment for just this aircraft
            self.assign_flight_incrementally(aircraft)
            
            # Clear input fields and update UI
            self.code_input.clear()
            self.arrival_input.clear()
            self.departure_input.clear()
            self.update_table()
            self.visualize()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def assign_flight_incrementally(self, new_plane):
        """
        Searches for a suitable gate within gate_assignments for the new aircraft
        without modifying any existing assignments. If no existing gate is suitable,
        a new gate is created.

        Explanation of overlap check:
        If the condition (A's departure <= B's arrival) OR (A's arrival >= B's departure)
        does NOT hold, it means the time windows overlap and a conflict is present.
        """
        placed = False
        for gate in self.gate_assignments:
            conflict_found = False
            for plane in gate:
                # Overlap check:
                # If it's NOT true that (new_plane.departure <= plane.arrival)
                # OR (new_plane.arrival >= plane.departure), there's a conflict.
                if not (new_plane.departure <= plane.arrival or new_plane.arrival >= plane.departure):
                    conflict_found = True
                    break
            if not conflict_found:
                # If this gate can accommodate the new aircraft, assign it and stop searching
                gate.append(new_plane)
                placed = True
                break
        
        # If no suitable gate was found, create a new one
        if not placed:
            self.gate_assignments.append([new_plane])

    def delete_selected_aircraft(self):
        """
        Removes the selected aircraft rows from the table and from the gate assignments.
        After deletion, the interval_partitioning algorithm is re-run to ensure
        the schedule remains optimal and any empty gates are removed.

        Steps:
        1. Identify and remove the selected aircraft from both self.aircraft_list
        and the existing gate_assignments.
        2. Clear all gate assignments (self.gate_assignments).
        3. If there are still aircraft remaining, run the interval_partitioning 
        function on the updated list to compute a new optimal gate assignment.
        4. Refresh the UI by updating the table and visualizing the new schedule.
        """
        selected_rows = set(item.row() for item in self.aircraft_table.selectedItems())
        if not selected_rows:
            return

        # 1) Remove the selected aircraft from self.aircraft_list and gate_assignments
        for row in sorted(selected_rows, reverse=True):
            removed_plane = self.aircraft_list.pop(row)
            for gate in self.gate_assignments:
                if removed_plane in gate:
                    gate.remove(removed_plane)

        # 2) Reset gate assignments
        self.gate_assignments = []

        # 3) Re-run scheduling if there are remaining aircraft
        if self.aircraft_list:
            gates_needed, assignments = interval_partitioning(self.aircraft_list)
            self.gates_needed = gates_needed
            self.gate_assignments = assignments

        # 4) Update the UI
        self.update_table()
        self.visualize()

    def run_planning(self):
        """
        Run the Interval Partitioning algorithm to determine the minimum
        number of gates required and reassign all existing aircraft.
        Be aware that this process will discard any current assignments
        and may shift flights to different gates. If you want to preserve 
        existing assignments, do not call this method or implement a 
        confirmation step to proceed.

        Steps:
        1. Check if any gate assignments already exist. If so, prompt the user 
        to confirm before discarding them.
        2. Clear all current gate assignments.
        3. If no aircraft are available, show a warning and return.
        4. Use the interval_partitioning function to calculate new assignments.
        5. Update the UI table and visualize the new schedule.
        """
        # Prompt user if gates are already assigned
        if self.gate_assignments:
            reply = QMessageBox.question(
                self,
                "Existing Assignments",
                (
                    "Re-running the planning will discard all current assignments "
                    "and potentially reassign flights to different gates.\n"
                    "Do you wish to continue?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        # Clear previous assignments
        self.gate_assignments = []

        # Check if there are any aircraft to schedule
        if not self.aircraft_list:
            QMessageBox.warning(self, "Error", "No aircraft to schedule.")
            return

        # Run the interval partitioning algorithm
        gates_needed, assignments = interval_partitioning(self.aircraft_list)

        # Store and update assignments
        self.gates_needed = gates_needed
        self.gate_assignments = assignments

        # Refresh the table and visualize the new schedule
        self.update_table()
        self.visualize()

    def update_table(self):
        """
        Refresh the table to show all aircraft and their assigned gates (if any).
        """
        self.aircraft_table.setRowCount(len(self.aircraft_list))
        
        for i, aircraft in enumerate(self.aircraft_list):
            # Find the gate this aircraft belongs to (if assigned)
            gate_num = "-"
            for gate_idx, gate in enumerate(self.gate_assignments):
                if aircraft in gate:
                    gate_num = str(gate_idx + 1)
                    break
            
            # Fill the row in the table
            self.aircraft_table.setItem(i, 0, QTableWidgetItem(aircraft.code))
            self.aircraft_table.setItem(i, 1, QTableWidgetItem(self.minutes_to_time_str(aircraft.arrival)))
            self.aircraft_table.setItem(i, 2, QTableWidgetItem(self.minutes_to_time_str(aircraft.departure)))
            self.aircraft_table.setItem(i, 3, QTableWidgetItem(gate_num))
            
        self.aircraft_table.resizeColumnsToContents()

    def visualize(self):
        """
        Plot the gate assignments as a timeline using matplotlib.
        Each gate appears on a separate horizontal row.
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Some colors to make different gates distinct
        colors = [
            'tab:blue', 'tab:orange', 'tab:green', 'tab:red',
            'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray'
        ]
        
        # Plot each gate (row) with its assigned aircraft
        for gate_idx, gate in enumerate(self.gate_assignments):
            color = colors[gate_idx % len(colors)]
            for plane in gate:
                start = plane.arrival
                duration = plane.departure - plane.arrival
                ax.broken_barh(
                    [(start, duration)],
                    (gate_idx - 0.4, 0.8),
                    facecolors=color,
                    edgecolor='black',
                    alpha=0.7
                )
                # Label the aircraft code in the middle of the bar
                ax.text(
                    start + duration / 2.0,
                    gate_idx,
                    plane.code,
                    ha='center',
                    va='center',
                    color='black',
                    fontweight='bold'
                )
        
        # Set y-limits to fit all gates
        ax.set_ylim(-0.5, len(self.gate_assignments) - 0.5)
        ax.set_yticks(range(len(self.gate_assignments)))
        ax.set_yticklabels([f'Gate {i+1}' for i in range(len(self.gate_assignments))])
        
        # Configure x-axis as times from 0..1440 (minutes in a day)
        hour_marks = range(0, 1441, 60)
        ax.set_xticks(hour_marks)
        ax.set_xticklabels([f'{h//60:02d}:00' for h in hour_marks], rotation=45, ha='right')
        
        # Title, labels, grid
        ax.set_title('Gate Assignment Timeline', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (HH:MM)', fontsize=12)
        ax.set_ylabel('Gates', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.92, bottom=0.25)
        ax.set_xlim(0, 1440)  # 0 to 24*60 = 1440 minutes
        
        self.canvas.draw()

    def save_chart(self):
        """
        Save the currently displayed chart as a PNG file.
        """
        filename = "./images/gate_assignment_chart.png"
        self.figure.savefig(filename)
        QMessageBox.information(self, "Success", f"Chart saved as {filename}")

    def load_sample_data(self):
        """Load sample aircraft data with HH:MM time format."""
        sample_data = [
            # Format: Aircraft(code, arrival_time, departure_time)
            
            Aircraft("a", self.to_m("09:00"), self.to_m("10:30")),
            Aircraft("b", self.to_m("09:00"), self.to_m("12:30")),
            Aircraft("d", self.to_m("11:00"), self.to_m("12:30")),
            Aircraft("e", self.to_m("11:00"), self.to_m("14:00")),
            Aircraft("f", self.to_m("13:00"), self.to_m("14:30")),
            Aircraft("g", self.to_m("13:00"), self.to_m("14:30")),
            Aircraft("h", self.to_m("14:00"), self.to_m("16:30")),
            Aircraft("i", self.to_m("15:00"), self.to_m("16:30")),
            Aircraft("j", self.to_m("15:00"), self.to_m("16:30"))
        ]
        
        self.aircraft_list.extend(sample_data)
        self.update_table()
        self.run_planning()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = AirportPlanningApp()
    main_window.show()
    sys.exit(app.exec())
