from colorama import init, Fore, Style
import yaml
import os

# Constantes para valores por defecto
BLANK_SYMBOL = "_"
RIGHT = "R"
LEFT = "L"
MAX_STEPS = 500  # Límite de pasos añadido

class TuringMachine:
    def __init__(self, alphabet: set, input_symbols: set, states: set, initial_state: str,
                 accepting_states: set, transition_function: dict, blank_symbol: str = BLANK_SYMBOL):
        """
        Initialize the Turing Machine with the given parameters.
        """
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
        self.steps_count = 0  # Contador de pasos añadido

    def run(self, input_string: str):
        """
        Run the Turing Machine on the given input string.
        """
        self.tape = Tape(input_string, self.blank_symbol)
        self.print_current_string(input_string)
        self.steps_count = 0  # Reiniciar contador de pasos

        while self.current_state not in self.accepting_states:
            self.print_instant_description()

            # Verificar límite de pasos
            self.steps_count += 1
            if self.steps_count > MAX_STEPS:
                self.rejection_reason = f"Máximo de {MAX_STEPS} pasos excedido"
                break

            curr_char = self.tape.get_current()
            new_state, new_cache, tape_output, head_direction = self.get_transition(
                self.current_state, curr_char, self.cache)
            
            if new_state is None:
                self.rejection_reason = f"No valid transition for ({self.current_state}, {curr_char})"
                break

            self.current_state = new_state
            self.cache = new_cache
            self.tape.write(tape_output)

            if head_direction == RIGHT:
                self.tape.go_right()
            elif head_direction == LEFT:
                self.tape.go_left()

        if self.current_state in self.accepting_states:
            self.print_is_accepted(input_string)
        else:
            self.print_is_rejected(input_string)

    def get_transition(self, state, tape_value, cache_value):
        """
        Get the transition for the given state, tape value, and cache value.
        """
        transition_key = ((state, cache_value), tape_value)
        if transition_key in self.transition_function:
            transition = self.transition_function[transition_key]
            try:
                new_state, new_cache = transition[0]
                tape_output, head_direction = transition[1:]
            except IndexError:
                self.rejection_reason = "Malformed transition in configuration"
                exit("Transition function is not in the correct format")
            return new_state, new_cache, tape_output, head_direction
        else:
            return None, None, None, None

    def print_instant_description(self):
        """
        Print the current state and tape content with custom coloring.
        """
        left_side = self.tape.get_left_side()
        right_side = self.tape.get_right_side()
        current_char = self.tape.get_current()
        state_tuple = self.current_state
        cache_value = self.cache
        
        # Color azul y morado para elementos dentro de []
        formatted_description = (
            f"\t꜔  {left_side} "
            f"{Fore.YELLOW + Style.BRIGHT}[{Fore.MAGENTA}{state_tuple}, {Fore.BLUE}{cache_value}{Fore.YELLOW}]{Style.RESET_ALL} "
            f"{current_char}, {right_side}{Style.RESET_ALL}"
        )
        print(formatted_description)

    def print_is_accepted(self, string: str):
        """
        Print that the input string is accepted.
        """
        print(f"{Fore.GREEN}String: {string} is ACCEPTED by the TM{Style.RESET_ALL}\n")

    def print_is_rejected(self, string: str):
        """
        Print that the input string is rejected.
        """
        rejection_msg = f"\n{self.rejection_reason}\n" if self.rejection_reason else "\n"
        print(f"{Fore.RED}String: {string} is REJECTED{rejection_msg}{Style.RESET_ALL}")

    def print_current_string(self, string: str):
        """
        Print the current input string.
        """
        print(f"{Fore.BLUE}Input String: {string}{Style.RESET_ALL}")


class Node:
    def __init__(self, value):
        """
        Initialize a node with the given value.
        """
        self.char = value
        self.next = None
        self.prev = None


class Tape:
    def __init__(self, string, blank_symbol):
        """
        Initialize the tape with the given string and blank symbol.
        """
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
        """
        Move the tape head to the right.
        """
        if self.current.next is None:
            self._set_next(self.blank_symbol)
        else:
            self.current = self.current.next

    def go_left(self):
        """
        Move the tape head to the left.
        """
        if self.current.prev is None:
            self._set_prev(self.blank_symbol)
        else:
            self.current = self.current.prev

    def write(self, value):
        """
        Write a value to the current tape cell.
        """
        self.current.char = value

    def get_current(self):
        """
        Get the current tape cell value.
        """
        return self.current.char

    def get_left_side(self):
        """
        Get the left side of the tape from the current position.
        """
        left = []
        current = self.current
        while current.prev is not None:
            left.insert(0, current.prev.char)
            current = current.prev
        return ", ".join(left)

    def get_right_side(self):
        """
        Get the right side of the tape from the current position.
        """
        right = []
        current = self.current
        while current.next is not None:
            right.append(current.next.char)
            current = current.next
        return ", ".join(right)

    def _set_initial_node(self, value):
        """
        Set the initial node of the tape.
        """
        self.origin = Node(value)
        self.current = self.origin

    def _set_next(self, value):
        """
        Set the next node of the tape.
        """
        new_node = Node(value)
        self.current.next = new_node
        new_node.prev = self.current
        self.current = new_node
        self.head = self.current

    def _set_prev(self, value):
        """
        Set the previous node of the tape.
        """
        new_node = Node(value)
        self.current.prev = new_node
        new_node.next = self.current
        self.current = new_node
        self.tail = self.current

    def _return_to_origin(self):
        """
        Return the tape head to the origin.
        """
        self.current = self.origin

    def __str__(self):
        """
        Return a string representation of the tape.
        """
        right = self.get_right_side()
        left = self.get_left_side()
        return "[" + left + " >" + self.current.char + ", " + right + "]"


def load_config(filename):
    """
    Load the configuration from the given YAML file.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file {filename} not found.")
    with open(filename, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    return config


def parse_config(config):
    """
    Parse the configuration into a format suitable for the Turing Machine.
    """
    def replace_empty_with_underscore(value):
        return BLANK_SYMBOL if value == 'None' or value is None else str(value)

    parsed_config = {}
    for t in config['delta']:
        initial_state = replace_empty_with_underscore(str(t['params']['initial_state']))
        cache_value = replace_empty_with_underscore(str(t['params'].get('mem_cache_value', BLANK_SYMBOL)))
        new_cache_value = replace_empty_with_underscore(str(t['output'].get('mem_cache_value', BLANK_SYMBOL)))
        tape_input = replace_empty_with_underscore(t['params']['tape_input'])

        state_cache_key = ((initial_state, cache_value), tape_input)
        new_state = replace_empty_with_underscore(str(t['output']['final_state']))
        tape_output = replace_empty_with_underscore(t['output']['tape_output'])
        tape_displacement = replace_empty_with_underscore(t['output']['tape_displacement'])

        tape_values = ((new_state, new_cache_value), tape_output, tape_displacement)
        parsed_config[state_cache_key] = tape_values

    return parsed_config


def get_turing_machine_attr(filename):
    """
    Get the attributes for the Turing Machine from the configuration file.
    """
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
    """
    Main function to run the Turing Machines.
    """
    init()  # Initialize colorama
    
    # Turing machine 1: Recognizer
    print(f"\n{Fore.CYAN}=== RECOGNIZER Machine ==={Style.RESET_ALL}")
    try:
        alphabet, input_symbols, states, initial_state, accepting_states, transition_function, simulation_strings = (
            get_turing_machine_attr('mt_reconocedora.yaml'))

        for string in simulation_strings:
            tm = TuringMachine(alphabet, input_symbols, states, initial_state, accepting_states, transition_function)
            tm.run(string)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    # Turing machine 2: Transformer
    print(f"\n{Fore.CYAN}=== TRANSFORMER Machine ==={Style.RESET_ALL}")
    try:
        alphabet, input_symbols, states, initial_state, accepting_states, transition_function, simulation_strings = (
            get_turing_machine_attr('mt_alteradora.yaml'))

        for string in simulation_strings:
            tm = TuringMachine(alphabet, input_symbols, states, initial_state, accepting_states, transition_function)
            tm.run(string)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()