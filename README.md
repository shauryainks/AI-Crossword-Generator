# AI Crossword

This project implements an AI crossword generator using Constraint Satisfaction Problem (CSP) techniques. The crossword generator is capable of creating new crossword puzzles given the structure and word bank provided.

## Directory Structure

- **assets:** This directory contains fonts used for rendering crossword assignments.
- **data:** This directory contains structure files (`structure0.txt`, `structure1.txt`, and `structure2.txt`) representing crossword structures and word files (`words0.txt`, `words1.txt`, and `words2.txt`) containing words to be used for generating crosswords.
- **crossword.py:** This file contains the implementation of classes `Variable` and `Crossword`, representing crossword variables and the crossword puzzle itself, respectively.
- **generate.py:** This file implements the crossword generator using CSP techniques. It contains the `CrosswordCreator` class, which encapsulates methods for enforcing node and arc consistency, solving the CSP, and generating the crossword.

## How to Use

To generate a crossword, run `generate.py` with the following command-line arguments:

```bash
python generate.py <structure> <words> [output]
```

- `<structure>`: Path to the structure file containing the crossword layout.
- `<words>`: Path to the word bank file containing a list of words to use in the crossword puzzle.
- `[output]` (optional): Path to save the generated crossword image. If not provided, the crossword will be printed to the terminal.

## Files Description

- **crossword.py:** This file contains two classes:
  - `Variable`: Represents a variable in the crossword puzzle grid. It stores information such as starting point, direction, and length of the word.
  - `Crossword`: Represents the crossword puzzle itself. It initializes the crossword structure, vocabulary list, variables, and computes overlaps between variables.

- **generate.py:** This file implements the `CrosswordCreator` class, which encapsulates methods for solving the CSP problem to generate crosswords:
  - `__init__`: Initializes the crossword generator with the provided crossword structure and word bank.
  - `letter_grid`: Returns a 2D array representing a given assignment.
  - `print`: Prints the crossword assignment to the terminal.
  - `save`: Saves the crossword assignment to an image file.
  - `solve`: Enforces node and arc consistency, and then solves the CSP to generate the crossword.
  - `enforce_node_consistency`: Updates the domains such that each variable is node-consistent.
  - `revise`: Makes variable `x` arc consistent with variable `y`.
  - `ac3`: Updates the domains such that each variable is arc consistent.
  - `assignment_complete`: Checks if the assignment is complete (all variables are assigned).
  - `consistent`: Checks if the assignment is consistent.
  - `order_domain_values`: Orders domain values based on their impact on neighboring variables.
  - `select_unassigned_variable`: Selects an unassigned variable not already part of the assignment.
  - `backtrack`: Using Backtracking Search, takes a partial assignment and returns a complete assignment if possible.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- This project is inspired by artificial intelligence and constraint satisfaction problem techniques.
- The crossword generator algorithm is adapted from [MIT 6.034: Artificial Intelligence](http://web.mit.edu/6.034/wwwbob/csp.py).
