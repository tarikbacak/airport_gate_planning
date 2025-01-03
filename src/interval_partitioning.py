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

from heapq import heappush, heappop


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
    Sort the list of Aircraft objects in ascending order by their arrival time
    using the QuickSort algorithm. This implementation uses the divide-and-conquer
    strategy with a pivot element.

    Time Complexity: O(n log n) average case
    Space Complexity: O(log n) due to recursion stack

    Args:
        aircraft_list (list): A list of Aircraft objects to be sorted
    
    Returns:
        list: The sorted list of Aircraft objects by arrival time
    """
    def quicksort(arr, low, high):
        if low < high:
            # Find the partition index
            pi = partition(arr, low, high)
            
            # Recursively sort the left part
            quicksort(arr, low, pi - 1)
            # Recursively sort the right part
            quicksort(arr, pi + 1, high)
    
    def partition(arr, low, high):
        # Choose the rightmost element as pivot
        pivot = arr[high].arrival
        i = low - 1  # Index of smaller element
        
        for j in range(low, high):
            # If current element is smaller than or equal to pivot
            if arr[j].arrival <= pivot:
                i += 1  # Increment index of smaller element
                arr[i], arr[j] = arr[j], arr[i]
        
        # Place pivot in its correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    # Start QuickSort
    quicksort(aircraft_list, 0, len(aircraft_list) - 1)
    return aircraft_list

def interval_partitioning(aircrafts):
    """
    Implements an optimized Interval Partitioning algorithm using a priority queue
    for O(n log n) time complexity.

    Algorithm Steps:
    1) Sort all aircraft by arrival time using QuickSort - O(n log n)
    2) Use a priority queue to track the earliest available time for each gate
    3) For each aircraft:
       - If the min gate's available time <= current aircraft's arrival,
         reuse that gate
       - Otherwise, open a new gate
       The priority queue operations take O(log n), done n times: O(n log n)

    Total Time Complexity: O(n log n)
    Space Complexity: O(n) for the priority queue

    Args:
        aircrafts (list): List of Aircraft objects

    Returns:
        (num_gates, gate_assignments): Tuple containing:
            - num_gates (int): Minimum number of gates required
            - gate_assignments (list): List of lists, each sublist represents
              aircraft assigned to a gate
    """

    if not aircrafts:
        return 0, []

    # 1) Sort aircraft by arrival time - O(n log n)
    sorted_aircrafts = manual_sort_by_arrival(aircrafts)
    
    # Initialize data structures
    gate_assignments = []  # List of lists to store assignments
    gates_heap = []       # Priority queue storing (departure_time, gate_index)
    
    # Process each aircraft in sorted order
    for plane in sorted_aircrafts:
        # Check if we can reuse an existing gate
        if gates_heap and gates_heap[0][0] <= plane.arrival:
            # Get the earliest available gate
            _, gate_index = heappop(gates_heap)
            # Add plane to existing gate
            gate_assignments[gate_index].append(plane)
            # Update gate's availability time
            heappush(gates_heap, (plane.departure, gate_index))
        else:
            # Need to open a new gate
            new_gate_index = len(gate_assignments)
            gate_assignments.append([plane])
            heappush(gates_heap, (plane.departure, new_gate_index))
    
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
