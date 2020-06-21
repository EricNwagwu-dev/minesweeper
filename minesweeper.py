import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #Add the current move to moves made set
        self.moves_made.add(cell)

        #We made the move so we can assume it's safe
        self.mark_safe(cell)

        #Gets all adjacents cells and makes a sentence
        adjCells = []
        for i in range(cell[0]-1,cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if i >= 0 and j >= 0 and i < self.height and j < self.width and not (i,j) in self.safes:
                    if (i,j) in self.mines:
                        count -= 1
                    else:
                        adjCells.append((i,j))
        
        #Adds new sentence to knowledge
        newSentence = Sentence(adjCells,count)
        #print(f"Number of unknown bombs touching {cell}: {count}")
        #print(f"List of undetermined cells: {newSentence.cells}")
        self.knowledge.append(newSentence)
        #This reevaluates our knowledge
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            for safe in safes:
                 self.mark_safe(safe)
            mines = sentence.known_mines()
            for mine in mines:
                self.mark_mine(mine)
        #print(f"List of undetermined cells after re: {newSentence.cells}")
        print(f"List of mines: {self.mines}")
        #This creates new sentences based on other sentences
        newKnowledge = [] #Contains all the new knowledge sentences we can deduce
        for sentence in self.knowledge:
            if sentence.cells == set():#If we find a sentence that is empty
                self.knowledge.remove(sentence)#remove it from the knowledge base, we have no use for it
            for otherSentence in self.knowledge:
                if otherSentence.cells == set():#If we find another sentence that is empty
                    self.knowledge.remove(otherSentence)#remove it from the knowledge base, we have no use for it
                if sentence.cells != set() and otherSentence.cells != set() and sentence != otherSentence:#The none of the sentences are empty and they are different
                    setA = sentence.cells #creates a setA
                    setB = otherSentence.cells#creates a setB
                    setAC = sentence.count#keep track of mines in setA
                    setBC = otherSentence.count#keep track of mines in setB
                    if len(setA)  > len(setB) and setB <= setA:#if setA has more elements and setB is it's subset
                        self.knowledge.remove(sentence)#remove setA from the knowledge base because with knowledge acquired it doesn't tell us enough
                        newKnowledge.append(Sentence(set(setA -setB),setAC - setBC))#take the difference of setA and setB and make a new sentence
                    elif len(setB)  > len(setA) and setA <= setB:#if setB has more elements and setA is it's subset
                        self.knowledge.remove(otherSentence)#remove setB from the knowledge base because with knowledge acquired it doesn't tell us enough
                        newKnowledge.append(Sentence(set(setB - setA),setBC - setAC))#take the difference of setB and setA and make a new sentence
        #print(f"New knowledege: {newKnowledge}")
        self.knowledge.extend(newKnowledge)#add all the new knowledge acquired to knowledge base
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for x in self.safes:
            if not x in self.moves_made:
                print(f"{x} is a safe move...")
                return x
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        randSet = []
        for i in range(self.height):
            for j in range(self.width):
                if not (i,j) in self.mines and not (i,j) in self.moves_made:
                    randSet.append((i,j))
        if randSet:
            return random.choice(randSet)
        return None