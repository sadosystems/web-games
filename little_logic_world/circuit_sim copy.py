"""
# ------ Three Fills -------
blank - 0x0
trace - 0x1
input - 0xA

"""
import time 

# void = 0x0
# trace = 0x1
# ergize_trace = 0x2

# and_gate = 0x3
# nor_gate = 0x4
# not_gate = 0x5
# or_gate = 0x6
# xor_gate = 0x7
# light = 0x8
# switch = 0x9
# logic_high = 0xA
# pin = 0xB
# something = 0xC
# something = 0xD
# something = 0xE
# something = 0xF

void = "00" # was 0
trace = "T0" # was 1
ergize_trace = "T1" # was 2
power_in = "P1" # was 0xA / 10

and_gate = "A0"
energized_and_gate = "A1"

write_high = "W1"
write_low = "W0"

read_high = "R1"
read_low = "R0"

def check_adjacent(table, index) -> set:
    adjacent_trace_indexes = set()
    table_size = len(table)
    width = 30

    # Directions: left, right, above, below
    directions = [-1, 1, -width, width]

    if (index) % width == 0: # hugging left wall
        directions.remove(-1)
    if (index+1) % width == 0: # hugging right wall
        directions.remove(1)

    for direction in directions:
        adjacent_index = index + direction
        if 0 <= adjacent_index < table_size and table[adjacent_index] in ("T0", "T1", "R0", "R1"):
            adjacent_trace_indexes.add(adjacent_index)

    return adjacent_trace_indexes

def walk(table, startpoint, traversed=None):
    if traversed is None:
        traversed = set()
    traversed.add(startpoint)
    traces = check_adjacent(table, startpoint)
    for trace in traces:
        if trace not in traversed:
            traversed.add(trace)
            walk(table, trace, traversed)

    return traversed

def simulate(table):
    print(table, flush=True)
    table_copy = table[:]  
    illuminated = set()
    for i, element in enumerate(table_copy):
        if element == "P1":
            line = walk(table_copy, i)
            illuminated = illuminated | line

    all_indexes = {x for x in range(len(table_copy))}
    non_illuminated = all_indexes - illuminated
    for element in non_illuminated:
        if table_copy[element] == "T1":
            table_copy[element] = "T0"
        if table_copy[element] == "T0":
            table_copy[element] = "T1"

    for element in illuminated:
        if table_copy[element] == "R0":
            table_copy[element] = "R1"
        if table_copy[element] == "R0":
            table_copy[element] = "R1"
    return table_copy



