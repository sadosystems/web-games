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

def check_adjacent(table, index, paint) -> set:
    adjacent_trace_indexes = set()
    table_size = len(table)
    width = 20
    if paint == 'trace':
        values_to_check = ("T0", "T1", "R0", "R1")
    elif paint == 'and':
        values_to_check = ("A0", "A1")
    elif paint == 'or':
        values_to_check = ("O0", "O1")
    elif paint == 'nand':
        values_to_check = ("N0", "N1")
    elif paint == 'xor':
        values_to_check = ("X0", "X1")
    elif paint == 'write':
        values_to_check = ("W0", "W1")
    elif paint == 'read':
        values_to_check = ("R0", "R1")
    elif paint == 'logic':
        values_to_check = ("A0", "A1", "O0", "O1", "N0", "N1", "X0", "X1")

    # Directions: left, right, above, below
    directions = [-1, 1, -width, width]

    if (index) % width == 0: # hugging left wall
        directions.remove(-1)
    if (index+1) % width == 0: # hugging right wall
        directions.remove(1)

    for direction in directions:
        adjacent_index = index + direction
        if 0 <= adjacent_index < table_size and table[adjacent_index] in values_to_check:
            adjacent_trace_indexes.add(adjacent_index)

    return adjacent_trace_indexes

def walk(table, startpoint, paint, traversed=None):
    if traversed is None:
        traversed = set()
    traversed.add(startpoint)
    traces = check_adjacent(table, startpoint, paint)
    for trace in traces:
        if trace not in traversed:
            traversed.add(trace)
            walk(table, trace, paint, traversed=traversed)
    return traversed

def index_set_to_bool_list(table, index_set):
    boolean_reads = []
    for i in index_set:
        if "0" in table[i]:
            boolean_reads.append(0)
        if "1" in table[i]:
            boolean_reads.append(1)
    return boolean_reads

def logic_walk(table, all_logic_cells, conditon, operation, traversed=None):
    if traversed is None:
        traversed = set()

    unseen_cells = all_logic_cells - traversed
    illuminated_cells = set()

    for random_cell in unseen_cells:
        traversed.add(random_cell)  
        cell_block = walk(table, random_cell, operation)

        adjacent_reads = set()
        for element in cell_block:
            some_read = check_adjacent(table, element, "read")
            adjacent_reads = adjacent_reads | some_read

        boolean_reads = index_set_to_bool_list(table, adjacent_reads)

        if conditon(boolean_reads):
            illuminated_cells = illuminated_cells | cell_block
    
        illuminated_cells |= logic_walk(table, all_logic_cells, conditon, operation, traversed)

    return illuminated_cells

def write_walk(table, all_writes, traversed=None):
    illuminated_writes = set()
    if traversed is None:
        traversed = set()
    unseen_writes = all_writes - traversed
    for element in unseen_writes:
        adjacent_logic_blocks = check_adjacent(table, element, "logic")
        for logic_block in adjacent_logic_blocks:
            if "1" == table[logic_block][1]:
                illuminated_writes.add(element)
                break
    return illuminated_writes

def create_index_sets(table):
    all_writes = set()
    all_ands = set()
    all_ors = set()
    all_nands = set()
    all_xors = set()

    for index, value in enumerate(table):
        if value in {"W1", "W0"}:
            all_writes.add(index)
        if value in {"A1", "A0"}:
            all_ands.add(index)
        if value in {"O1", "O0"}:
            all_ors.add(index)
        if value in {"N1", "N0"}:
            all_nands.add(index)
        if value in {"X1", "X0"}:
            all_xors.add(index)

    return all_writes, all_ands, all_ors, all_nands, all_xors

def nand_operation(boolean_list):
    return not all(boolean_list)

def xor_operation(boolean_list):
    return sum(boolean_list) == 1

def and_walk(table_copy, all_ands):
    illuminated_ands = logic_walk(table_copy, all_ands, all, 'and')
    return illuminated_ands

def or_walk(table_copy, all_ors):
    illuminated_ors = logic_walk(table_copy, all_ors, any, 'or')
    return illuminated_ors

def nand_walk(table_copy, all_nands):
    illuminated_nands = logic_walk(table_copy, all_nands, nand_operation, 'nand')
    return illuminated_nands

def xor_walk(table_copy, all_xors):
    illuminated_xors = logic_walk(table_copy, all_xors, xor_operation, 'xor')
    return illuminated_xors

def simulate(table):
    table_copy = table[:]  
    illuminated = set()
    for i, element in enumerate(table_copy):
        if element in ["P1"]:
            line = walk(table_copy, i, 'trace')
            illuminated = illuminated | line

    all_indexes = {x for x in range(len(table_copy))}
    all_writes, all_ands, all_ors, all_nands, all_xors = create_index_sets(table)
    try:
        and_illuminated = and_walk(table_copy, all_ands)
        illuminated = illuminated | and_illuminated
    except:
        pass
    try: 
        write_iluminated = write_walk(table_copy, all_writes)
        illuminated = illuminated | write_iluminated
    except:
        pass

    try: 
        or_iluminated = or_walk(table_copy, all_ors)
        illuminated = illuminated | or_iluminated
    except:
        pass
    try: 
        nand_iluminated = nand_walk(table_copy, all_nands)
        illuminated = illuminated | nand_iluminated
    except:
        pass
    try: 
        xor_iluminated = xor_walk(table_copy, all_xors)
        illuminated = illuminated | xor_iluminated
    except:
        pass
    non_illuminated = all_indexes - illuminated
    for element in non_illuminated:
        if table_copy[element] == "T1":
            table_copy[element] = "T0"
        if table_copy[element] == "R1":
            table_copy[element] = "R0"
        if table_copy[element] == "A1":
            table_copy[element] = "A0"
        if table_copy[element] == "W1":
            table_copy[element] = "W0"
        if table_copy[element] == "O1":
            table_copy[element] = "O0"
        if table_copy[element] == "N1":
            table_copy[element] = "N0"
        if table_copy[element] == "X1":
            table_copy[element] = "X0"

    for element in illuminated:
        if table_copy[element] == "T0":
            table_copy[element] = "T1"
        if table_copy[element] == "R0":
            table_copy[element] = "R1"
        if table_copy[element] == "A0":
            table_copy[element] = "A1"
        if table_copy[element] == "W0":
            table_copy[element] = "W1"
        if table_copy[element] == "O0":
            table_copy[element] = "O1"
        if table_copy[element] == "N0":
            table_copy[element] = "N1"
        if table_copy[element] == "X0":
            table_copy[element] = "X1"

    for i, element in enumerate(table_copy):
        if element in ["W1"]:
            line = walk(table_copy, i, 'trace')
            illuminated = illuminated | line
    non_illuminated = all_indexes - illuminated
    for element in non_illuminated:
        if table_copy[element] == "T1":
            table_copy[element] = "T0"
        if table_copy[element] == "R1":
            table_copy[element] = "R0"
        if table_copy[element] == "A1":
            table_copy[element] = "A0"
        if table_copy[element] == "W1":
            table_copy[element] = "W0"
        if table_copy[element] == "O1":
            table_copy[element] = "O0"
        if table_copy[element] == "N1":
            table_copy[element] = "N0"
        if table_copy[element] == "X1":
            table_copy[element] = "X0"

    for element in illuminated:
        if table_copy[element] == "T0":
            table_copy[element] = "T1"
        if table_copy[element] == "R0":
            table_copy[element] = "R1"
        if table_copy[element] == "A0":
            table_copy[element] = "A1"
        if table_copy[element] == "W0":
            table_copy[element] = "W1"
        if table_copy[element] == "O0":
            table_copy[element] = "O1"
        if table_copy[element] == "N0":
            table_copy[element] = "N1"
        if table_copy[element] == "X0":
            table_copy[element] = "X1"
            
    return table_copy

