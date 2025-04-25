import os
import random
import numpy as np

# This script generates random instances for a surgical scheduling model with constraints and setup times.

# -------------------------
# Global Parameters
# -------------------------

nb_operations = 15
nb_surgeons = 4
nb_rooms = 4
nb_equipment_types = 0
nb_equipments = 0
nb_patients = nb_operations
enable_setup_times = True
enable_surgeon_schedule = False
all_rooms_available = False

# -------------------------
# Variable + Set Declaration
# -------------------------

def define_sets(nb_surgeons, nb_rooms, nb_operations):
    """
    Define index sets used in the model.
    """
    output = ""
    output += "O = " + str(list(range(nb_operations))) + "; \n"
    output += "C = " + str(list(range(nb_surgeons))) + "; \n"
    output += "S = " + str(list(range(nb_rooms))) + "; \n"
    return output

# -------------------------
# Room Availability per Operation
# -------------------------

def generate_room_availability(nb_operations, nb_rooms, probability=0.9):
    """
    Generate matrix A[o][s] indicating if room s can host operation o.
    """
    matrix = []
    if all_rooms_available:
        probability = 1
    for o in range(nb_operations):
        row = []
        only_zeros = True
        for r in range(nb_rooms):
            if r == nb_rooms - 1 and only_zeros:
                row.append(1)
                continue
            if random.uniform(0, 1) < probability:
                row.append(1)
                only_zeros = False
            else:
                row.append(0)
        matrix.append(row)
    return "A = " + str(matrix) + "; \n"

# -------------------------
# Surgeon Eligibility Matrix
# -------------------------

def generate_surgeon_eligibility(nb_surgeons, nb_operations):
    """
    Create matrix X[c][o] indicating if surgeon c can perform operation o.
    Each surgeon takes turns cyclically.
    """
    matrix = [[] for _ in range(nb_surgeons)]
    for o in range(nb_operations):
        current_surgeon = o % nb_surgeons
        for c in range(nb_surgeons):
            matrix[c].append(1 if c == current_surgeon else 0)
    return matrix, "X = " + str(matrix) + "; \n"

# -------------------------
# Surgeon Working Hours
# -------------------------

def generate_surgeon_time_windows(nb_surgeons):
    """
    Generate start (F) and end (G) time availability for each surgeon.
    Three scenarios: morning (0–50), afternoon (50–100), or full day (0–100).
    """
    max_time = 10000
    if enable_surgeon_schedule:
        max_time = 800

    F, G = [], []
    for _ in range(nb_surgeons):
        shift_type = random.randint(2, 2)  # currently always full day
        if shift_type == 0:
            F.append(0)
            G.append(int(max_time / 2))
        elif shift_type == 1:
            F.append(int(max_time / 2))
            G.append(max_time)
        elif shift_type == 2:
            F.append(0)
            G.append(max_time)

    return "F = " + str(F) + "; \n" + "G = " + str(G) + "; \n"

# -------------------------
# Operation Types and Setup Times
# -------------------------

def generate_types_and_setup_times(nb_operations, eligibility_matrix, max_setup_time=30, nb_types=4):
    """
    Assign a speciality to each surgeon and compute then generate setup dependant time between
    two operations depending on specialities TD[o1][o2]
    """
    nb_surgeons = len(eligibility_matrix)
    type_by_surgeon = [random.randint(0, nb_types - 1) for _ in range(nb_surgeons)]

    T = [[0 for _ in range(nb_types)] for _ in range(nb_operations)]
    type_by_operation = [-1] * nb_operations

    for o in range(nb_operations):
        for c in range(nb_surgeons):
            if eligibility_matrix[c][o] == 1:
                t = type_by_surgeon[c]
                T[o][t] = 1
                type_by_operation[o] = t
                break

    # Generate transition times between types
    type_transition_time = [
        [0 if t1 == t2 or not enable_setup_times else random.randint(0, max_setup_time)
         for t2 in range(nb_types)] for t1 in range(nb_types)
    ]

    # Build TD[o1][o2]
    TD = []
    for o1 in range(nb_operations):
        TD.append([])
        for o2 in range(nb_operations):
            t1 = type_by_operation[o1]
            t2 = type_by_operation[o2]
            TD[o1].append(type_transition_time[t1][t2])

    return "T = " + str(T) + "; \n" + "TD = " + str(TD) + "; \n"

# -------------------------
# Operation Durations
# -------------------------

def generate_operation_durations(nb_operations):
    """
    Generate durations for preparation (TP), surgery (TC), cleaning (TN) and total (TT).
    """
    TP, TC, TN, TT = [], [], [], []
    for _ in range(nb_operations):
        prep = random.randint(5, 30)
        surg = int(np.random.lognormal(4, 0.5) + 1)
        clean = random.randint(10, 20)
        TP.append(prep)
        TC.append(surg)
        TN.append(clean)
        TT.append(prep + surg + clean)

    return (
        "TP = " + str(TP) + "; \n" +
        "TC = " + str(TC) + "; \n" +
        "TN = " + str(TN) + "; \n" +
        "TT = " + str(TT) + "; \n"
    )

# -------------------------
# File Generation
# -------------------------

def create_instance(nb_operations, nb_surgeons, nb_rooms, Tmax=45):
    instance = "\n"
    instance += define_sets(nb_surgeons, nb_rooms, nb_operations)
    instance += "\n"
    instance += generate_room_availability(nb_operations, nb_rooms)
    eligibility_matrix, matrix_X = generate_surgeon_eligibility(nb_surgeons, nb_operations)
    instance += matrix_X
    instance += generate_surgeon_time_windows(nb_surgeons)
    instance += generate_operation_durations(nb_operations)
    instance += generate_types_and_setup_times(nb_operations, eligibility_matrix, nb_types=4)
    instance += "Tmax = " + str(Tmax) + "; \n"
    instance += "M = 999999; \n"
    instance += "\n"
    return instance

# -------------------------
# Multiple Instance Export
# -------------------------

def generate_multiple_instances(n=10, output_folder=None):
    """
    Generate and export n instances as text files.
    """
    if output_folder is None:
        raise ValueError("An output folder path must be specified.")

    os.makedirs(output_folder, exist_ok=True)

    for i in range(n):
        instance_data = create_instance(
            nb_operations, nb_surgeons, nb_rooms
        )
        suffix = "_ST" if enable_setup_times else ""
        filename = f"o{nb_operations}_c{nb_surgeons}_s{nb_rooms}{suffix}_instance_{i}.txt"
        with open(os.path.join(output_folder, filename), 'w') as f:
            f.write(instance_data)
        print(instance_data)

# -------------------------
# Run
# -------------------------

output_dir = os.path.join(os.getcwd(), "generated_instances")
os.makedirs(output_dir, exist_ok=True)
generate_multiple_instances(n=1, output_folder=output_dir)
