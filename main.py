import yaml
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from colorama import Fore, Style, init

init(autoreset=True)

@dataclass
class TuringMachineConfig:
    states: Set[str]
    initial_state: str
    final_states: Set[str]
    input_alphabet: Set[str]
    tape_alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Dict[str, str]]
    test_strings: List[str]
    name: str

class TuringMachine:
    def __init__(self, config_file: str, machine_type: str):
        self.config = self._parse_yaml_config(config_file, machine_type)

    def _parse_yaml_config(self, config_file: str, machine_type: str) -> TuringMachineConfig:
        try:
            with open(config_file, 'r') as file:
                raw_config = yaml.safe_load(file)
            
            return TuringMachineConfig(
                name=machine_type,
                states=set(raw_config['q_states']['q_list']),
                initial_state=raw_config['q_states']['initial'],
                final_states=set(raw_config['q_states']['final']) if isinstance(raw_config['q_states']['final'], list) else {raw_config['q_states']['final']},
                input_alphabet=set(raw_config.get('alphabet', [])),
                tape_alphabet=set(raw_config.get('tape_alphabet', [])),
                transitions=self._extract_transitions(raw_config),
                test_strings=raw_config.get('simulation_strings', [])
            )
        except Exception as e:
            print(f"{Fore.RED}Error reading configuration file {config_file}: {e}{Style.RESET_ALL}")
            raise

    def _extract_transitions(self, config):
        transitions = {}
        for rule in config.get('delta', []):
            key = (rule['params']['initial_state'], rule['params']['tape_input'])
            transitions[key] = {
                'next_state': rule['output']['final_state'],
                'write_symbol': rule['output']['tape_output'],
                'direction': rule['output']['tape_displacement']
            }
        return transitions

    def run(self, input_string: str):
        tape = list(input_string) + ['_']
        head_pos = 0
        current_state = self.config.initial_state
        steps = []

        print(f"\n{Fore.CYAN}=== {self.config.name.upper()} Machine ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Current String: {input_string}{Style.RESET_ALL}")

        while True:
            x_markers = ', '.join(['X'] * head_pos)
            steps.append(f"         →  {x_markers} [{Fore.BLUE}{current_state}{Style.RESET_ALL}, {Fore.MAGENTA}{tape[head_pos]}{Style.RESET_ALL}] {', '.join(tape[head_pos:])}")
            
            transition_key = (current_state, tape[head_pos])
            if transition_key not in self.config.transitions:
                steps.append(f"{Fore.RED}No valid transition for {transition_key}{Style.RESET_ALL}")
                break

            transition = self.config.transitions[transition_key]
            tape[head_pos] = transition['write_symbol']
            current_state = transition['next_state']

            if transition['direction'] == 'R':
                head_pos += 1
                if head_pos == len(tape):
                    tape.append('_')
            elif transition['direction'] == 'L':
                head_pos = max(head_pos - 1, 0)

        # Print all steps
        for step in steps:
            print(step)

        result = current_state in self.config.final_states
        result_color = Fore.GREEN if result else Fore.RED
        result_message = 'ACCEPTED' if result else 'REJECTED'
        print(f"\nThe String: {input_string} is {result_color}{result_message}{Style.RESET_ALL} by the TM")
        print("="*50)

        return result, steps

    def run_all_tests(self):
        print(f"{Fore.CYAN}Running tests for {self.config.name} Machine{Style.RESET_ALL}")
        for test_string in self.config.test_strings:
            self.run(test_string)

def main():
    # Recognizer Machine
    tm_recognizer = TuringMachine("mt_reconocedora.yaml", "Recognizer")
    tm_recognizer.run_all_tests()

    # Transformer Machine
    tm_transformer = TuringMachine("mt_alteradora.yaml", "Transformer")
    tm_transformer.run_all_tests()

if __name__ == "__main__":
    main()
