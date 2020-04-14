import numpy as np
import cv2
from tkinter import Tk, filedialog
from .board import SudokuBoard
import argparse
import os


class Game:
    def __init__(self, board_size, num_to_fill=50, debug=False, random_fills_trials=50):
        """
        Keyword Arguments:
            num_to_fill {int} -- number of cells to fill randomly (default: {50})
        """
        self.board_size = board_size
        self.sudoku_board = SudokuBoard(self.board_size)
        self.num_to_fill = num_to_fill
        self.debug = debug
        self.random_fills_trials = random_fills_trials

        if self.debug:
            print('[INFO] Debugging mode on.')

        self.help_flag = False

    def __mouse_callback(self, event, x, y, *args):
        # cell selection
        if event == cv2.EVENT_LBUTTONUP:
            if self.help_flag:
                self.help_flag = False
                return None
            cell_size = self.board_size // 9
            pos_y = y // cell_size
            pos_x = x // cell_size
            self.sudoku_board.select_cell(
                pos_y, pos_x,
                select_const=self.debug
            )

    def select_board(self):
        root = Tk()
        path_to_board = filedialog.askopenfilename(
            parent=root,
            initialdir=os.getcwd(),
            title='Please select a board',
            filetypes=[('Board files', '.board')]
        )
        root.destroy()

        # if uses canceled selecting
        if path_to_board is None:
            return

        self.sudoku_board.fill_from_file(path_to_board)

    def save_board(self):
        root = Tk()
        path_to_board = filedialog.asksaveasfilename(
            parent=root,
            initialdir=os.getcwd(),
            title='Please select a board',
            filetypes=[('Board files', '.board')]
        )
        root.destroy()

        # if uses canceled selecting
        if path_to_board is None:
            return

        self.sudoku_board.save_to_file(path_to_board)

    def write_help(self, img):
        phantom_board = img
        white_board = np.ones_like(phantom_board) * 255
        help_board = cv2.addWeighted(
            phantom_board, 0.1, white_board, 0.9, 1)

        def next_help_args(text):
            nonlocal help_board
            if not hasattr(next_help_args, 'text_args'):
                next_help_args.text_args = {
                    "img": help_board,
                    "text": None,
                    "org": (5, 5),
                    "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
                    "fontScale": 1,
                    "color": (0, 0, 0),
                    "thickness": 2
                }
            text_args = next_help_args.text_args
            # move position to the bottom
            text_args['org'] = (
                text_args['org'][0], text_args['org'][1] + 30)
            text_args['text'] = text
            return text_args

        cv2.putText(**next_help_args('q - quit'))
        cv2.putText(**next_help_args('a - solve automatically'))
        cv2.putText(**next_help_args('o - open saved board'))
        cv2.putText(**next_help_args('s - save board'))
        cv2.putText(**next_help_args('r - refill board randomly'))
        cv2.putText(**next_help_args('c - make cell constant'))
        cv2.putText(**next_help_args('e - clear board'))
        cv2.putText(**next_help_args('h - help'))

        return help_board

    def main_loop(self):
        cv2.namedWindow('Sudoku')
        cv2.setMouseCallback('Sudoku', self.__mouse_callback)
        self.sudoku_board.fill_random(self.num_to_fill, self.random_fills_trials)
        # main loop starts here
        while True:
            board = self.sudoku_board.numpy()
            if self.help_flag:
                board = self.write_help(board)
            cv2.imshow('Sudoku', board)
            key = cv2.waitKey(10)

            if key != -1 and key != ord('h'):
                self.help_flag = False

            if key == ord('q'):
                break
            elif key == 27:
                self.sudoku_board.selected_cell = None
            elif key == ord('a'):
                self.sudoku_board.auto_solve()
            elif key == ord('o'):
                self.select_board()
            elif key == ord('s'):
                self.save_board()
            elif key == ord('r'):
                self.sudoku_board.clear()
                self.sudoku_board.fill_random(self.num_to_fill)
            # making selected cell constant
            elif key == ord('c') and self.debug:
                self.sudoku_board.change_mode_of_selected()
                continue
            elif key == ord('e'):
                if self.debug:
                    self.sudoku_board.clear()
                else:
                    self.sudoku_board.clear(keep_const=True)
                    continue
            elif key == ord('h'):
                self.help_flag = not self.help_flag

            # trying to fill
            # into selected cell
            if self.sudoku_board.selected_cell is not None:
                try:
                    self.sudoku_board.fill_into_selected(chr(key))
                except Exception as e:
                    pass

        cv2.destroyAllWindows()
