from colorama import init, Fore, Style
import yaml 

class TuringMachine:
    def __init__(self, alphabet: set, input_symbols: set, states: set, initial_state: str,
                 accepting_states: set, transition_function: dict, blank_symbol: str = "_"):
        self.alphabet = alphabet
        self.blank_symbol = blank_symbol
        self.input_symbols = input_symbols
        self.states = states
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.transition_function = transition_function

        self.tape = None
        self.cache = self.blank_symbol
        self.current_state = initial_state
        self.rejection_reason = None

    def run(self, input_string: str):
        self.tape = Tape(input_string, self.blank_symbol)
        self.print_current_string(input_string)

        while self.current_state not in self.accepting_states:
            self.print_instant_description()

            curr_char = self.tape.get_current()
            new_state, new_cache, tape_output, head_direction = self.get_transition(
                self.current_state, curr_char, self.cache)
            
            if new_state is None:
                self.rejection_reason = f"No valid transition for ({self.current_state}, {curr_char})"
                break

            self.current_state = new_state
            self.cache = new_cache
            self.tape.write(tape_output)

            if head_direction == "R":
                self.tape.go_right()
            elif head_direction == "L":
                self.tape.go_left()

        if self.current_state in self.accepting_states:
            self.print_is_accepted(input_string)
        else:
            self.print_is_rejected(input_string)

    def get_transition(self, state, tape_value, cache_value):
        if ((state, cache_value), tape_value) in self.transition_function:
            transition = self.transition_function[((state, cache_value), tape_value)]
            try:
                new_state = transition[0][0]
                new_cache = transition[0][1]
                tape_output = transition[1]
                head_direction = transition[2]
            except IndexError:
                self.rejection_reason = "Malformed transition in configuration"
                exit("Transition function is not in the correct format")

            return new_state, new_cache, tape_output, head_direction
        else:
            return None, None, None, None

    def print_instant_description(self):
        left_side = self.tape.get_left_side()
        right_side = self.tape.get_right_side()
        current_char = self.tape.get_current()
        state_tuple = self.current_state
        cache_value = self.cache
        print(f"{Fore.YELLOW}\t꜔  {left_side} [{state_tuple}, {cache_value}] {current_char},{right_side}{Style.RESET_ALL}")

    def print_is_accepted(self, string: str):
        print(f"{Fore.GREEN}String: {string} is ACCEPTED by the TM{Style.RESET_ALL}\n")

    def print_is_rejected(self, string: str):
        rejection_msg = f"\n{self.rejection_reason}\n" if self.rejection_reason else "\n"
        print(f"{Fore.RED}String: {string} is REJECTED{rejection_msg}{Style.RESET_ALL}")

    def print_current_string(self, string: str):
        print(f"{Fore.BLUE}Input String: {string}{Style.RESET_ALL}")

# Tape.py
class Node:
    def __init__(self, value):
        self.char = value
        self.next = None
        self.prev = None

class Tape:
    def __init__(self, string, blank_symbol):
        self.blank_symbol = blank_symbol
        self.current = None
        self.head = None
        self.tail = None
        self.origin = None

        self._set_initial_node(string[0])
        for char in string[1:]:
            self._set_next(char)
        self._return_to_origin()

    def go_right(self):
        if self.current.next is None:
            self._set_next(self.blank_symbol)
        else:
            self.current = self.current.next

    def go_left(self):
        if self.current.prev is None:
            self._set_prev(self.blank_symbol)
        else:
            self.current = self.current.prev

    def write(self, value):
        self.current.char = value

    def get_current(self):
        return self.current.char

    def get_left_side(self):
        left = ""
        current = self.current
        while current.prev is not None:
            left = current.prev.char + ", " + left
            current = current.prev
        return left

    def get_right_side(self):
        right = ""
        current = self.current
        while current.next is not None:
            right += current.next.char + ", "
            current = current.next
        return right

    def _set_initial_node(self, value):
        self.origin = Node(value)
        self.current = self.origin

    def _set_next(self, value):
        new_node = Node(value)
        self.current.next = new_node
        new_node.prev = self.current
        self.current = new_node
        self.head = self.current

    def _set_prev(self, value):
        new_node = Node(value)
        self.current.prev = new_node
        new_node.next = self.current
        self.current = new_node
        self.tail = self.current

    def _return_to_origin(self):
        self.current = self.origin

    def __str__(self):
        right = self.get_right_side()
        left = self.get_left_side()
        return "[" + left + " >" + self.current.char + "," + right + "]"

# Parser

def load_config(filename):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)
    return config

def parse_config(config):
    q_states = config['q_states']
    delta = config['delta']

    def replace_empty_with_underscore(value):
        return '_' if value == 'None' or value is None else str(value)

    parsed_config = {}

    for t in delta:
        initial_state = replace_empty_with_underscore(str(t['params']['initial_state']))
        cache_value = replace_empty_with_underscore(str(t['params'].get('mem_cache_value', '_')))
        new_cache_value = replace_empty_with_underscore(str(t['output'].get('mem_cache_value', '_')))
        tape_input = replace_empty_with_underscore(t['params']['tape_input'])

        state_cache_key = ((initial_state, cache_value), tape_input)

        new_state = replace_empty_with_underscore(str(t['output']['final_state']))
        tape_output = replace_empty_with_underscore(t['output']['tape_output'])
        tape_displacement = replace_empty_with_underscore(t['output']['tape_displacement'])

        tape_values = ((new_state, new_cache_value), tape_output, tape_displacement)
        parsed_config[state_cache_key] = tape_values

    return parsed_config

def get_turing_machine_attr(filename):
    config = load_config(filename)
    parsed_config = parse_config(config)

    input_symbols = set(config['alphabet'])
    alphabet = set(config['tape_alphabet'])
    states = set(config['q_states']['q_list'])
    initial_state = config['q_states']['initial']
    accepting_states = {config['q_states']['final']}
    transition_function = parsed_config
    simulation_strings = config['simulation_strings']

    return alphabet, input_symbols, states, initial_state, accepting_states, transition_function, simulation_strings


def main():
    init()  # Initialize colorama
    
    # Turing machine 1
    print(f"\n{Fore.CYAN}=== RECOGNIZER Machine ==={Style.RESET_ALL}")
    alphabet, input_symbols, states, initial_state, accepting_states, transition_function, simulation_strings = (
        get_turing_machine_attr('mt_reconocedora.yaml'))

    for string in simulation_strings:
        tm = TuringMachine(alphabet, input_symbols, states, initial_state, accepting_states, transition_function)
        tm.run(string)

    # Turing machine 2
    print(f"\n{Fore.CYAN}=== TRANSFORMER Machine ==={Style.RESET_ALL}")
    alphabet, input_symbols, states, initial_state, accepting_states, transition_function, simulation_strings = (
        get_turing_machine_attr('mt_alteradora.yaml'))

    for string in simulation_strings:
        tm = TuringMachine(alphabet, input_symbols, states, initial_state, accepting_states, transition_function)
        tm.run(string)

if __name__ == "__main__":
    main()
