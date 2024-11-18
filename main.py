import yaml
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

class Direction(Enum):
    LEFT = 'L'
    RIGHT = 'R'
    STAY = 'S'

@dataclass
class TransitionFunction:
    next_state: str
    write_symbol: str
    direction: Direction

class TuringMachine:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            
        # Validate configuration
        self._validate_config(config)
            
        self.states = set(config['states'])
        self.input_alphabet = set(config['input_alphabet'])
        self.tape_alphabet = set(config['tape_alphabet'])
        self.initial_state = config['initial_state']
        self.final_states = set(config['final_states'])
        self.blank_symbol = config['blank_symbol']
        self.transitions = self._parse_transitions(config['transitions'])
        self.test_strings = config['test_strings']

    def _validate_config(self, config: dict) -> None:
        """Validate the configuration file structure and contents."""
        required_keys = ['states', 'input_alphabet', 'tape_alphabet', 'initial_state',
                        'final_states', 'blank_symbol', 'transitions', 'test_strings']
        
        # Check for required keys
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate relationships between sets
        if not set(config['input_alphabet']).issubset(set(config['tape_alphabet'])):
            raise ValueError("Input alphabet must be subset of tape alphabet")
        
        if config['initial_state'] not in config['states']:
            raise ValueError("Initial state must be in states set")
            
        if not set(config['final_states']).issubset(set(config['states'])):
            raise ValueError("Final states must be subset of states")

    def _parse_transitions(self, transitions: dict) -> Dict[Tuple[str, str], TransitionFunction]:
        parsed = {}
        for transition in transitions:
            current_state = transition['current']
            read_symbol = transition['read']
            
            # Validate transition
            if current_state not in self.states:
                raise ValueError(f"Invalid state in transition: {current_state}")
            if read_symbol not in self.tape_alphabet:
                raise ValueError(f"Invalid symbol in transition: {read_symbol}")
                
            key = (current_state, read_symbol)
            parsed[key] = TransitionFunction(
                transition['next'],
                transition['write'],
                Direction(transition['direction'])
            )
        return parsed

    def simulate(self, input_string: str) -> Tuple[bool, List[str]]:
        # Validate input string
        if not all(c in self.input_alphabet for c in input_string):
            raise ValueError(f"Invalid input string: {input_string}")
            
        # Initialize tape with input string and blanks on both sides
        tape = [self.blank_symbol] * 100
        head_position = 50  # Start in the middle
        
        # Place input string on tape
        for i, symbol in enumerate(input_string):
            tape[head_position + i] = symbol
            
        current_state = self.initial_state
        steps = []
        max_steps = 1000  # Prevent infinite loops
        
        for step in range(max_steps):
            # Create instantaneous description
            id_description = self._create_id(tape, head_position, current_state)
            steps.append(id_description)
            
            # Get current symbol under head
            current_symbol = tape[head_position]
            
            # Look up transition
            transition_key = (current_state, current_symbol)
            if transition_key not in self.transitions:
                steps.append(f"No transition found for state {current_state} and symbol {current_symbol}")
                return False, steps
                
            # Apply transition
            transition = self.transitions[transition_key]
            tape[head_position] = transition.write_symbol
            current_state = transition.next_state
            
            # Move head
            if transition.direction == Direction.RIGHT:
                head_position += 1
            elif transition.direction == Direction.LEFT:
                head_position -= 1
                
            # Check if we've reached a final state
            if current_state in self.final_states:
                steps.append(self._create_id(tape, head_position, current_state))
                return True, steps
                
        steps.append("Maximum steps reached - halting")
        return False, steps

    def _create_id(self, tape: List[str], head_position: int, current_state: str) -> str:
        """Create a visual representation of the current configuration."""
        # Find the bounds of the non-blank portion of the tape
        left_bound = 0
        right_bound = len(tape) - 1
        
        while left_bound < len(tape) and tape[left_bound] == self.blank_symbol:
            left_bound += 1
        while right_bound >= 0 and tape[right_bound] == self.blank_symbol:
            right_bound -= 1
            
        # Ensure we show at least 5 cells on either side of the head
        left_bound = min(left_bound, head_position - 5)
        right_bound = max(right_bound, head_position + 5)
        
        # Create the tape visualization
        tape_segment = tape[left_bound:right_bound + 1]
        head_offset = head_position - left_bound
        
        # Build the string representation
        tape_str = ' '.join(tape_segment)
        head_marker = ' ' * (head_offset * 2) + '↓'
        state_info = f"State: {Fore.GREEN}{current_state}{Style.RESET_ALL}"
        
        return f"{state_info}\n{tape_str}\n{head_marker}"

    def run_all_tests(self):
        print(f"{Fore.CYAN}Starting Turing Machine Simulation...{Style.RESET_ALL}")
        print("="*40)
        
        for i, test_string in enumerate(self.test_strings, 1):
            print(f"\n{Fore.YELLOW}Testing string #{i}: '{test_string}'{Style.RESET_ALL}")
            try:
                accepted, steps = self.simulate(test_string)
                
                print("\nSimulation steps:")
                for step in steps:
                    print(step)
                    time.sleep(0.5)  # Add delay for better visualization
                    
                result = f"{Fore.GREEN}ACCEPTED{Style.RESET_ALL}" if accepted else f"{Fore.RED}REJECTED{Style.RESET_ALL}"
                print(f"\nResult: {result}")
                print("="*40)
                
            except ValueError as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def main():
    try:
        tm = TuringMachine("turing_config.yaml")
        tm.run_all_tests()
    except Exception as e:
        print(f"{Fore.RED}Error loading or running Turing Machine: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()