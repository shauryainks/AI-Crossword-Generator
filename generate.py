import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)

        Parameters:
        - self: The instance of the class containing this method.

        Algorithm:
        - Iterate through each variable in self.domains.
        - For each variable, iterate through its domain values.
        - If the length of a domain value doesn't match the variable's length, remove it from the domain.
        """

        for v in self.domains:
            for x in list(self.domains[v]):
                if len(x) != v.length:
                    # Remove any values inconsistent with the variable's unary constraints
                    self.domains[v].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Parameters:
        - self: The instance of the class containing this method.
        - x: The variable to be made arc consistent.
        - y: The variable with which `x` is to be made arc consistent.

        Returns:
        - True if a revision was made to the domain of `x`;
        - False if no revision was made.

        Algorithm:
        - Initialize a variable `revise_check` to track if a revision is made.
        - Initialize a list `items_to_remove` to store values to be removed from `self.domains[x]`.
        - Iterate through each value in the domain of variable `x`.
        - Check if there exists any corresponding value for `y` in `self.domains[y]`.
        - If no corresponding value is found, add the value to `items_to_remove` and set `revise_check` to 1.
        - Remove the values in `items_to_remove` from the domain of `x`.
        - If any value is removed, return True; otherwise, return False.
        """

        revise_check = 0  # Initialize a variable to track if a revision is made
        # Initialize a list to store values to be removed from self.domains[x]
        items_to_remove = []

        if self.crossword.overlaps[x, y] is not None:
            for X in self.domains[x]:
                any_match = 0
                for Y in self.domains[y]:
                    x_location = self.crossword.overlaps[x, y][0]
                    y_location = self.crossword.overlaps[x, y][1]
                    if X[x_location] == Y[y_location]:
                        any_match += 1
                if any_match == 0:
                    items_to_remove.append(X)
                    revise_check = 1

            # Remove the values in items_to_remove from the domain of x
            for i in items_to_remove:
                self.domains[x].remove(i)
                revise_check = 1

        # If any value is removed, return True; otherwise, return False
        if revise_check != 0:
            return True
        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with the initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Parameters:
        - self: The instance of the class containing this method.
        - arcs: Optional. The initial list of arcs to make consistent.

        Returns:
        - True if arc consistency is enforced and no domains are empty;
        - False if one or more domains end up empty.

        Algorithm:
        - If `arcs` is None, initialize the queue with all arcs.
        - Otherwise, use `arcs` as the initial queue.
        - While the queue is not empty:
            - Remove an arc from the queue.
            - Apply the revise operation to the removed arc.
            - If domain reduction occurs:
                - If the domain of any variable becomes empty, return False.
                - Add arcs involving the revised variable to the queue.
        - If no domain becomes empty, return True.
        """

        if arcs is None:
            # If arcs is None, initialize the queue with all arcs
            queue = []
            for variable1 in self.domains:
                for variable2 in self.crossword.neighbors(variable1):
                    queue.append((variable1, variable2))
        else:
            # Otherwise, use arcs as the initial queue
            queue = arcs

        # While the queue is not empty
        while len(queue) > 0:
            remov = queue.pop(0)
            x, y = remov[0], remov[1]

            # Apply the revise operation to the removed arc
            if self.revise(x, y):
                # If domain reduction occurs
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        # Add arcs involving the revised variable to the queue
                        queue.append((z, x))

        # If no domain becomes empty, return True
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.

        Parameters:
        - self: The instance of the class containing this method.
        - assignment: A dictionary representing the current assignment.

        Returns:
        - True if assignment is complete, False otherwise.

        Algorithm:
        - Iterate through each variable in the crossword.
        - If any variable is not in the assignment, return False.
        - If all variables are in the assignment, return True.
        """

        # Iterate through each variable in the crossword
        for var in self.crossword.variables:
            # If any variable is not in the assignment, return False
            if var not in assignment:
                return False

        # If all variables are in the assignment, return True
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.

        Parameters:
        - self: The instance of the class containing this method.
        - assignment: A dictionary representing the current assignment.

        Returns:
        - True if assignment is consistent, False otherwise.

        Algorithm:
        - Iterate through each variable and its assigned word in the assignment.
        - Check if the length of the assigned word matches the length of the variable and there are no empty spaces.
        - Check if the assigned word conflicts with neighboring variables' assigned words.
        - If any inconsistency is found, return False.
        - If no inconsistency is found, return True.
        """

        # Iterate through each variable and its assigned word in the assignment
        for variable, word in assignment.items():
            # Check if the length of the assigned word matches the length of the variable and there are no empty spaces
            if (word and len(word) != variable.length) or "_" in word:
                return False

        # Check consistency between neighboring variables' assigned words
        for var in self.crossword.variables:
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if var in assignment and neighbor in assignment:
                    # Check if the characters at overlapping positions of the assigned words match
                    if assignment[var][self.crossword.overlaps[var, neighbor][0]] != assignment[neighbor][self.crossword.overlaps[var, neighbor][1]]:
                        return False

        # If no inconsistency is found, return True
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.

        Parameters:
        - self: The instance of the class containing this method.
        - var: The variable for which domain values are to be ordered.
        - assignment: A dictionary representing the current assignment.

        Returns:
        - word_list: A list of values in the domain of `var`, ordered by their impact on neighboring variables.

        Algorithm:
        - Initialize an empty list to store word-value pairs.
        - Iterate through each word in the domain of `var`.
        - Calculate the cost of each word based on how many values they rule out for neighboring variables.
        - Append each word and its associated cost to the word_list.
        - Sort the word_list based on the cost.
        - Extract the words from the sorted word_list and return them.
        """

        word_list = []  # Initialize an empty list to store word-value pairs

        # Iterate through each word in the domain of `var`
        for word in self.domains[var]:
            cost_word = 0

            # Iterate through neighbors of `var`
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue

                # Calculate the cost of the word based on its impact on neighboring variables
                x_index, y_index = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[x_index] != neighbor_word[y_index]:
                        cost_word += 1

            # Append each word and its associated cost to the word_list
            word_list.append((word, cost_word))

        # Sort the word_list based on the cost
        word_list = sorted(word_list, key=lambda tup: tup[1])

        # Extract the words from the sorted word_list and return them
        word_list = [tup[0] for tup in word_list]
        return word_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.

        Parameters:
        - self: The instance of the class containing this method.
        - assignment: A dictionary representing the current assignment.

        Returns:
        - min_variable: The selected unassigned variable.

        Algorithm:
        - Initialize min_values to a very large number.
        - Iterate through each variable in the crossword's variables.
        - If the variable is not in the current assignment:
            - Check if the number of remaining values in its domain is less than the current minimum.
            - Update min_values and min_variable accordingly.
        - If min_values is not None, return min_variable.
        """

        min_values = 99999999999  # Initialize min_values to a very large number
        min_variable = None

        # Iterate through each variable in the crossword's variables
        for variable in self.crossword.variables:
            if variable not in assignment:  # If the variable is not assigned
                # Check if the number of remaining values in its domain is less than the current minimum
                if len(self.domains[variable]) < min_values:
                    # Update min_values and min_variable accordingly
                    min_values = len(self.domains[variable])
                    min_variable = variable

        # If min_values is not None, return min_variable
        if min_values != None:
            return min_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        Parameters:
        - self: The instance of the class containing this method.
        - assignment: A dictionary representing the current partial assignment.

        Returns:
        - assignment: A complete assignment if possible; otherwise, None.

        Algorithm:
        - Check if the assignment is complete (all variables are assigned).
        - If complete, return the assignment.
        - Select an unassigned variable.
        - Try each value in the domain of the selected variable.
        - If a value is consistent with the assignment, recursively call backtrack with the updated assignment.
        - If a complete assignment is found, return it.
        - If no assignment is possible, return None.
        """

        # Check if assignment is complete
        if len(assignment) == len(self.crossword.variables):
            return assignment

        # Try a new variable
        var = self.select_unassigned_variable(assignment)

        # Try each value in the domain of the selected variable
        for value in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Check consistency of new assignment
            if self.consistent(new_assignment):
                # Recursively call backtrack with the updated assignment
                result = self.backtrack(new_assignment)
                # If a complete assignment is found, return it
                if result is not None:
                    return result
        # If no assignment is possible, return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
