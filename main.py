from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
import yaml
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
class Configuration:
    """Represents the current configuration of the Turing Machine"""
    state: str
    head_position: int
    tape: List[str]

@dataclass
class TransitionRule:
    """Represents a single transition rule"""
    next_state: str
    write_symbol: str
    direction: Direction

class TuringMachine:
    def __init__(self, config_file: str):
        """Initialize Turing Machine from YAML configuration"""
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        # Basic components
        self.states = set(config['states'])
        self.input_alphabet = set(config['input_alphabet'])
        self.tape_alphabet = set(config['tape_alphabet'])
        self.initial_state = config['initial_state']
        self.final_states = set(config['final_states'])
        self.blank_symbol = config['blank_symbol']
        self.transitions = self._parse_transitions(config['transitions'])
        self.test_strings = config.get('test_strings', [])

    def _parse_transitions(self, transitions: List[dict]) -> Dict[Tuple[str, str], TransitionRule]:
        """Parse transition rules from configuration"""
        rules = {}
        for t in transitions:
            key = (t['current'], t['read'])
            rules[key] = TransitionRule(
                t['next'],
                t['write'],
                Direction(t['direction'])
            )
        return rules

    def _create_initial_tape(self, input_string: str) -> List[str]:
        """Create initial tape configuration with input string"""
        # Add padding on both sides
        padding = [self.blank_symbol] * 50
        tape = padding + list(input_string) + padding
        return tape

    def _get_displayable_tape(self, tape: List[str], head_pos: int) -> str:
        """Create a visual representation of the tape"""
        # Find bounds of non-blank portion
        left = max(0, head_pos - 10)
        right = min(len(tape), head_pos + 11)
        
        display = []
        for i in range(left, right):
            if i == head_pos:
                display.append(f"{Fore.GREEN}[{tape[i]}]{Style.RESET_ALL}")
            else:
                display.append(tape[i])
        
        return " ".join(display)

    def run(self, input_string: str) -> Tuple[bool, List[str]]:
        """Run the Turing Machine on an input string"""
        # Validate input
        if not all(c in self.input_alphabet for c in input_string):
            raise ValueError(f"Invalid input string: {input_string}")

        # Initialize configuration
        tape = self._create_initial_tape(input_string)
        head_pos = 50  # Start at beginning of input
        current_state = self.initial_state
        steps = []

        print(f"\n{Fore.CYAN}Starting simulation for input: {input_string}{Style.RESET_ALL}")
        
        max_steps = 1000  # Prevent infinite loops
        step_count = 0

        while step_count < max_steps:
            # Record current configuration
            current_config = f"Step {step_count}: State {current_state}\n"
            current_config += self._get_displayable_tape(tape, head_pos)
            steps.append(current_config)
            
            # Check if in final state
            if current_state in self.final_states:
                print(f"{Fore.GREEN}String accepted in state: {current_state}{Style.RESET_ALL}")
                return True, steps

            # Get current symbol and transition
            current_symbol = tape[head_pos]
            transition_key = (current_state, current_symbol)

            if transition_key not in self.transitions:
                print(f"{Fore.RED}No transition found for state {current_state} and symbol {current_symbol}{Style.RESET_ALL}")
                return False, steps

            # Apply transition
            transition = self.transitions[transition_key]
            tape[head_pos] = transition.write_symbol
            current_state = transition.next_state

            # Move head
            if transition.direction == Direction.RIGHT:
                head_pos += 1
            elif transition.direction == Direction.LEFT:
                head_pos -= 1

            step_count += 1
            time.sleep(0.2)  # Add delay for visualization

        print(f"{Fore.RED}Maximum steps reached{Style.RESET_ALL}")
        return False, steps

    def run_all_tests(self):
        """Run all test strings from configuration"""
        print(f"{Fore.CYAN}Starting Turing Machine tests...{Style.RESET_ALL}")
        print("="*50)

        for test_string in self.test_strings:
            print(f"\n{Fore.YELLOW}Testing string: {test_string}{Style.RESET_ALL}")
            try:
                accepted, steps = self.run(test_string)
                for step in steps:
                    print(step)
                    print("-"*50)
                
                result = f"{Fore.GREEN}ACCEPTED{Style.RESET_ALL}" if accepted else f"{Fore.RED}REJECTED{Style.RESET_ALL}"
                print(f"\nResult for {test_string}: {result}")
                print("="*50)
                
            except ValueError as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def main():
    try:
        # Probar MT Reconocedora
        print("\n=== MT Reconocedora ===")
        tm_reconocedora = TuringMachine("mt_reconocedora.yaml")
        tm_reconocedora.run_all_tests()

        # Probar MT Alteradora
        print("\n=== MT Alteradora ===")
        tm_alteradora = TuringMachine("mt_alteradora.yaml")
        tm_alteradora.run_all_tests()

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()