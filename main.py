import yaml
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time

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
            
        self.states = set(config['states'])
        self.input_alphabet = set(config['input_alphabet'])
        self.tape_alphabet = set(config['tape_alphabet'])
        self.initial_state = config['initial_state']
        self.final_states = set(config['final_states'])
        self.blank_symbol = config['blank_symbol']
        self.transitions = self._parse_transitions(config['transitions'])
        self.test_strings = config['test_strings']

    def _parse_transitions(self, transitions: dict) -> Dict[Tuple[str, str], TransitionFunction]:
        parsed = {}
        for transition in transitions:
            current_state = transition['current']
            read_symbol = transition['read']
            key = (current_state, read_symbol)
            parsed[key] = TransitionFunction(
                transition['next'],
                transition['write'],
                Direction(transition['direction'])
            )
        return parsed

    def simulate(self, input_string: str) -> Tuple[bool, List[str]]:
        # Initialize tape with input string and blanks on both sides
        tape = [self.blank_symbol] * 100  # Add blanks to the left
        head_position = 50  # Start in the middle
        
        # Place input string on tape
        for i, symbol in enumerate(input_string):
            tape[head_position + i] = symbol
            
        current_state = self.initial_state
        steps = []
        max_steps = 1000  # Prevent infinite loops
        
        for _ in range(max_steps):
            # Create instantaneous description
            id_description = self._create_id(tape, head_position, current_state)
            steps.append(id_description)
            
            # Get current symbol under head
            current_symbol = tape[head_position]
            
            # Look up transition
            transition_key = (current_state, current_symbol)
            if transition_key not in self.transitions:
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
                
        return False, steps

    def _create_id(self, tape: List[str], head_position: int, current_state: str) -> str:
        # Create a visual representation of the current configuration
        tape_str = ''.join(tape[head_position-10:head_position+11])
        head_marker = ' ' * 10 + '↓'
        return f"State: {current_state}\n{tape_str}\n{head_marker}"

    def run_all_tests(self):
        print("Starting Turing Machine Simulation...")
        print("=====================================")
        
        for i, test_string in enumerate(self.test_strings, 1):
            print(f"\nTesting string #{i}: '{test_string}'")
            accepted, steps = self.simulate(test_string)
            
            print("\nSimulation steps:")
            for step in steps:
                print(step)
                time.sleep(0.5)  # Add delay for better visualization
                
            print("\nResult:", "ACCEPTED" if accepted else "REJECTED")
            print("=====================================")

def main():
    # Example usage
    tm = TuringMachine("turing_config.yaml")
    tm.run_all_tests()


main()