from typing import Set


def get_input_with_validation(message: str, valid_inputs: Set[str]) -> str:
    input_str = input(message)
    while input_str not in valid_inputs:
        input_str = input(f'Invalid input! Please try again. {message}')
    return input_str
