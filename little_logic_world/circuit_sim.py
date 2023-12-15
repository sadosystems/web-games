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

# table = [0xA, 0x2, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1,
#          0x1, 0x1, 0x1, 0x0, 0x1, 0x1, 0x1, 0x1, 0x0, 0x1,
#          0x0, 0x0, 0x0, 0x0, 0x1, 0x0, 0x0, 0x1, 0x0, 0x1,
#          0x0, 0x0, 0x0, 0x0, 0x1, 0x0, 0x0, 0x1, 0x1, 0x1,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
#          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
#          ]

def check_adjacent(table, index) -> set:
    adjacent_trace_indexes = set()
    table_size = len(table)
    width = 20

    # Directions: left, right, above, below
    directions = [-1, 1, -width, width]

    if (index) % width == 0: # hugging left wall
        directions.remove(-1)
    if (index+1) % width == 0: # hugging right wall
        directions.remove(1)

    for direction in directions:
        adjacent_index = index + direction
        if 0 <= adjacent_index < table_size and table[adjacent_index] in (0x1, 0x2):
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
        if element == 0xA:
            line = walk(table_copy, i)
            illuminated = illuminated | line

    all_indexes = {x for x in range(len(table_copy))}
    non_illuminated = all_indexes - illuminated
    for element in non_illuminated:
        if table_copy[element] == 0x2:
            table_copy[element] = 0x1
    for element in illuminated:
        if table_copy[element] == 0x1:
            table_copy[element] = 0x2
    return table_copy



