############################################################
# interval_partitioning.py
#
# Contains a plain Interval Partitioning Algorithm from
# "Algorithm Design" (Kleinberg & Tardos). No external
# libraries are used (including built-in Python sorting).
# 
# The Interval Partitioning Algorithm:
# 1) Sort intervals (in this case, Aircraft objects) by their
#    start time (arrival).
# 2) Iterate over the intervals in ascending order of arrival.
#    - If an interval (aircraft) can go into an existing gate
#      (i.e., it does not overlap with the last assigned
#      aircraft in that gate), place it there.
#    - Otherwise, open a new gate for it.
#
# This guarantees a minimal number of gates (resources) needed
# so that no two overlapping intervals (aircraft) share the
# same gate.
############################################################


class Aircraft:
    """
    Represents an aircraft with a code identifier and 
    arrival/departure times (in minutes from midnight).

    Attributes:
        code (str): Unique identifier for the aircraft
        arrival (int): Arrival time in minutes from midnight (0-1439)
        departure (int): Departure time in minutes from midnight (0-1439)
    """
    def __init__(self, code, arrival, departure):
        # Store basic aircraft data
        self.code = code
        self.arrival = arrival
        self.departure = departure

    def __repr__(self):
        """
        Returns a string representation of the Aircraft,
        showing its code and [arrival-departure].
        """
        return f"{self.code} ({self.arrival}-{self.departure})"

def manual_sort_by_arrival(aircraft_list):
    """
    Manually sort the list of Aircraft objects in ascending order
    by their arrival time. This function does NOT use Python's
    built-in sort or sorted methods; it uses a simple
    "selection sort" approach to keep it library-free.

    Args:
        aircraft_list (list): A list of Aircraft objects to be sorted
    
    Returns:
        list: The sorted list of Aircraft objects by arrival time
    """
    # We will implement a basic selection sort
    n = len(aircraft_list)
    for i in range(n):
        # Assume the minimum is at position i
        min_index = i
        # Search for the aircraft with the smallest arrival time from i to n-1
        for j in range(i + 1, n):
            if aircraft_list[j].arrival < aircraft_list[min_index].arrival:
                min_index = j
        
        # If we found a smaller element, swap
        if min_index != i:
            aircraft_list[i], aircraft_list[min_index] = aircraft_list[min_index], aircraft_list[i]
    
    return aircraft_list

def interval_partitioning(aircrafts):
    """
    Implements the Interval Partitioning algorithm as described 
    in Kleinberg & Tardos, "Algorithm Design."

    Algorithm Steps:
    1) Sort all intervals (aircraft) by their start time.
    2) Create a set of 'gates' (initially empty). Each gate will
       be a list of Aircraft that do not overlap with each other.
    3) For each aircraft in ascending order of arrival:
       a) Try to place it into the first gate where it does not
          overlap with the last assigned aircraft in that gate.
       b) If no such gate exists, create a new gate and assign 
          the aircraft to it.

    Args:
        aircrafts (list): List of Aircraft objects

    Returns:
        (num_gates, gate_assignments):
            num_gates (int): The minimum number of gates required
            gate_assignments (list): A list of lists, where each
                                     sub-list represents a gate
                                     and contains Aircraft objects
    """
    # 1) Sort the aircraft list by arrival time (manually)
    sorted_aircrafts = manual_sort_by_arrival(aircrafts)

    # 2) Prepare a structure to store gates (each gate is a list of aircraft)
    gate_assignments = []

    # 3) Process each aircraft in order of increasing arrival
    for plane in sorted_aircrafts:
        # Try to place this aircraft in an existing gate
        placed = False
        for gate in gate_assignments:
            # The plane can be placed in this gate if its arrival time
            # is >= the departure of the last plane in that gate
            last_plane_in_gate = gate[-1]
            if plane.arrival >= last_plane_in_gate.departure:
                # We can place the plane in this gate
                gate.append(plane)
                placed = True
                break  # No need to check further gates
        
        # If not placed in any existing gate, create a new gate
        if not placed:
            new_gate = [plane]
            gate_assignments.append(new_gate)

    # The number of gates is simply the length of gate_assignments
    num_gates = len(gate_assignments)

    return num_gates, gate_assignments


if __name__ == "__main__":
    # Test the Interval Partitioning Algorithm
    aircrafts = [
            Aircraft("TC-LSU", 480, 570),   # 08:00 - 09:30
            Aircraft("TC-JSI", 525, 615),   # 08:45 - 10:15
            Aircraft("TC-JTR", 540, 660),   # 09:00 - 11:00
            Aircraft("TC-JOV", 600, 720),   # 10:00 - 12:00
            Aircraft("TC-NBK", 750, 840),   # 12:30 - 14:00
            Aircraft("TC-NCL", 780, 930),   # 13:00 - 15:30
            Aircraft("D-AIDW", 870, 960),   # 14:30 - 16:00
            Aircraft("SE-ROE", 960, 1080),  # 16:00 - 18:00
        ]

    num_gates, gate_assignments = interval_partitioning(aircrafts)
    print(f"Minimum number of gates needed: {num_gates}")
    for i, gate in enumerate(gate_assignments):
        print(f"Gate {i + 1}: {gate}")
