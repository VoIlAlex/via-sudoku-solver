import numpy as np
import cv2


class SudokuBoard:
    def __init__(self, width=600):
        self.board = np.ones(shape=(width + 50, width, 3), dtype='uint8') * 255
        self.width = width
        ################
        # drawing grid #
        ################

        # not bold lines
        for i in range(9):
            cv2.line(
                self.board,
                (0, (self.width * i) // 9),
                (self.width, (self.width * i) // 9),
                (0, 0, 0), 1)
        for i in range(9):
            cv2.line(
                self.board,
                ((self.width * i) // 9, 0),
                ((self.width * i) // 9, self.width),
                (0, 0, 0), 1)

        # bold lines
        cv2.line(self.board, (self.width // 3, 0),
                 (self.width // 3, self.width), (0, 0, 0), 5)
        cv2.line(self.board, ((self.width * 2) // 3, 0),
                 ((self.width * 2) // 3, self.width), (0, 0, 0), 5)
        cv2.line(self.board, (0, self.width // 3),
                 (self.width, self.width // 3), (0, 0, 0), 5)
        cv2.line(self.board, (0, (self.width * 2) // 3),
                 (self.width, (self.width * 2) // 3), (0, 0, 0), 5)

        # numbers
        self.nums = np.zeros(shape=(9, 9), dtype='int')
        self.const_nums = np.zeros(shape=(9, 9), dtype='bool_')

        self.selected_cell = None

    def is_correct(self):
        """
        Check whether it's correct 
        to fill <num> into selected
        cell

        Arguments:
            num {int} -- number under consideration
        """

        # go through grid
        for i in range(3):
            for j in range(3):
                numbers = {x: False for x in range(1, 10)}
                offset_i = i * 3
                offset_j = j * 3
                for i_1 in range(3):
                    for j_1 in range(3):
                        cell_value = self.nums[i_1 + offset_i, j_1 + offset_j]
                        # pass empty cells
                        if cell_value == 0:
                            continue
                        # if number repeats
                        if numbers[cell_value] is True:
                            return False
                        numbers[cell_value] = True

        # go through rows
        for i in range(9):
            numbers = {x: False for x in range(1, 10)}
            for j in range(9):
                cell_value = self.nums[i, j]
                # pass empty cells
                if cell_value == 0:
                    continue
                # if number repeats
                if numbers[cell_value] is True:
                    return False
                numbers[cell_value] = True

        # go through columns
        for j in range(9):
            numbers = {x: False for x in range(1, 10)}
            for i in range(9):
                cell_value = self.nums[i, j]
                # pass empty cells
                if cell_value == 0:
                    continue
                # if number repeats
                if numbers[cell_value] is True:
                    return False
                numbers[cell_value] = True

        return True

    '''def fill_random(self, num):
        """
        Fills the board randomly
        Arguments:
            num {int} -- Number of cells to fill
        """
        assert num >= 0 and num <= 81
        filled = 0
        while filled != num:
            # generate random position
            i = np.random.randint(0, 9)
            j = np.random.randint(0, 9)

            # if position is free
            if self.nums[i, j] != 0:
                for num in range(1, 10):
                    self.nums[i, j] = num
                    if self.__fit():
                        break
                else:
                    self.nums[i, j] = 0
                    continue
                filled += 1'''

    def change_mode_of_selected(self):
        if self.selected_cell is None:
            return None
        x = self.selected_cell[0]
        y = self.selected_cell[1]
        self.const_nums[x, y] = not self.const_nums[x, y]

    def fill_random(self, num, max_trials=50):
        """
        Fills the board randomly
        Arguments:
            num {int} -- Number of cells to fill
        """
        assert num >= 0 and num <= 81
        self.clear()
        filled = 0
        total_trials = 0
        trials_to_fill_cell = 0
        while filled != num:
            if trials_to_fill_cell == max_trials:
                trials_to_fill_cell = 0
                filled = 0
                self.clear()
            # generate random position
            i = np.random.randint(0, 9)
            j = np.random.randint(0, 9)
            

            # # if position is free
            # if self.nums[i, j] is not None:
            # find number that's fit

            is_filled = self.nums[i, j]
            trials_to_fill_cell += 1
            trials = 0
            number_to_fill = np.random.randint(1, 9)
            self.nums[i, j] = number_to_fill
            while not self.is_correct():
                number_to_fill = number_to_fill % 9 + 1
                self.nums[i, j] = number_to_fill
                trials += 1
                if trials == 10:
                    self.nums[i, j] = 0
                    break
            else:
                self.const_nums[i, j] = True
                total_trials += trials_to_fill_cell
                filled += 0 if is_filled else 1
                trials_to_fill_cell = 0

    def fill_from_file(self, path_to_board):
        nums = np.zeros_like(self.nums)
        with open(path_to_board) as f:
            for i, line in enumerate(f):
                values = [int(symbol) for symbol in line.rstrip()]
                for j in range(9):
                    if i < 9:
                        self.nums[i, j] = values[j]
                    else:
                        self.const_nums[i % 9, j] = values[j]
        self.selected_cell = None

    def save_to_file(self, path_to_board):
        with open(path_to_board, 'w+') as f:
            for i in range(self.nums.shape[0]):
                line = ''.join(str(num) for num in self.nums[i])
                print(line, file=f)

            for i in range(self.const_nums.shape[0]):
                line = ''.join(str(int(num)) for num in self.const_nums[i])
                print(line, file=f)
        self.selected_cell = None

    def auto_solve(self):
        """
        Automatically solve the Sudoku
        """
        correct_board = None
        positions_stack = []
        # value to continue from
        # for heighest element in stack
        next_value = 1
        while True:
            print('\r[INFO] Filled: {:5}'.format(len(positions_stack)), end='')
            if not (self.nums == 0).any():
                break
            for i in range(9):
                break_cycle = False
                for j in range(9):
                    if self.nums[i, j] != 0:
                        continue
                    for value in range(next_value + 1, 10):
                        self.nums[i, j] = value
                        if self.is_correct():
                            break
                        else:
                            self.nums[i, j] = 0
                    else:  # if there is no possible filler
                        if len(positions_stack) == 0:
                            print('\n[INFO] There is no solution!')
                            return None
                        last_filled = positions_stack[-1]
                        positions_stack = positions_stack[:-1]
                        next_value = self.nums[last_filled[0], last_filled[1]]
                        self.nums[last_filled[0], last_filled[1]] = 0
                        break_cycle = True
                        break

                    positions_stack.append((i, j))
                    next_value = 0
                    break_cycle = True
                    break
                if break_cycle:
                    break

    def numpy(self):
        cell_size = self.width / 9
        board = self.board.copy()

        # const cells
        for i in range(9):
            for j in range(9):
                if self.const_nums[i, j] == True:
                    x = int(j * cell_size)
                    y = int(i * cell_size)
                    cv2.rectangle(
                        board,
                        (x, y),
                        (int(x + cell_size), int(y + cell_size)),
                        (200, 200, 0),
                        -1
                    )

        # display selected cell
        if self.selected_cell is not None:
            x = int(self.selected_cell[1] * cell_size)
            y = int(self.selected_cell[0] * cell_size)
            cv2.rectangle(
                board,
                (x, y),
                (int(x + cell_size), int(y + cell_size)),
                (200, 150, 200),
                -1
            )

        ################
        # drawing grid #
        ################

        # not bold lines
        for i in range(9):
            cv2.line(
                board,
                (0, (self.width * i) // 9),
                (self.width, (self.width * i) // 9),
                (0, 0, 0), 1)
        for i in range(9):
            cv2.line(
                board,
                ((self.width * i) // 9, 0),
                ((self.width * i) // 9, self.width),
                (0, 0, 0), 1)
            # bold lines
        cv2.line(board, (self.width // 3, 0),
                 (self.width // 3, self.width), (0, 0, 0), 5)
        cv2.line(board, ((self.width * 2) // 3, 0),
                 ((self.width * 2) // 3, self.width), (0, 0, 0), 5)
        cv2.line(board, (0, self.width // 3),
                 (self.width, self.width // 3), (0, 0, 0), 5)
        cv2.line(board, (0, (self.width * 2) // 3),
                 (self.width, (self.width * 2) // 3), (0, 0, 0), 5)

        # draw numbers
        for i in range(self.nums.shape[0]):
            for j in range(self.nums.shape[1]):
                if self.nums[i, j] == 0:
                    continue
                # I just tried and tried
                # to make it fit into cell
                # don't touch it!!
                x = int(cell_size // 2 + j * cell_size - 0.15 * cell_size)
                y = int(cell_size // 2 + i * cell_size + 0.18 * cell_size)
                cv2.putText(board, str(self.nums[i, j]), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 0), 2, cv2.LINE_AA)

        # correctess bar
        cv2.line(
            board,
            (0, self.width),
            (self.width, self.width),
            (0, 0, 0),
            5
        )
        color = (0, 255, 0) if self.is_correct() else (0, 0, 255)
        cv2.rectangle(
            board,
            (0, self.width),
            (self.width, self.width + 50),
            color,
            -1
        )

        # winning condition
        if not (self.nums == 0).any() and self.is_correct():
            cv2.putText(board, 'Win!', (self.width // 2, self.width + 35), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 0), 2, cv2.LINE_AA)

        return board

    def select_cell(self, row, col, select_const=False):
        assert 0 <= row < 9
        assert 0 <= col < 9
        # we cannot fill constant cells
        if self.const_nums[row, col] == True and not select_const:
            self.selected_cell = None
            return None
        self.selected_cell = (row, col)

    def fill_into_selected(self, filler):
        """
        Set <filler> into selected cell.
        Note: if it's correct.

        Arguments:
            filler {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        if self.selected_cell is None:
            return None

        # if it's backspace
        if ord(filler) == 8:
            self.nums[self.selected_cell[0], self.selected_cell[1]] = 0
            self.selected_cell = None
            return None

        # convert to integer
        try:
            filler = int(filler)
        except Exception as e:
            print('[INFO] Not supported character!')
            return None

        # check if filler is appropriate
        if not any(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]) == filler):
            return None

        # fill into selected cell
        self.nums[self.selected_cell[0], self.selected_cell[1]] = filler

        # stop selection
        self.selected_cell = None

        print('[INFO] Fitness: {}'.format(self.__fit()))

    def clear(self, keep_const=False):
        for i in range(9):
            for j in range(9):
                if not keep_const or not self.const_nums[i, j]:
                    self.nums[i, j] = 0
        if not keep_const:
            self.const_nums = np.zeros(shape=(9, 9), dtype='bool_')
        self.selected_cell = None
