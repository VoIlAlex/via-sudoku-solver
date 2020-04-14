"""

This problem was asked by Dropbox.

Sudoku is a puzzle where you're given 
a partially-filled 9 by 9 grid with digits.
The objective is to fill the grid with the 
constraint that every row, column, and box 
(3 by 3 subgrid) must contain all of the 
digits from 1 to 9.

Implement an efficient sudoku solver.

"""
import numpy as np
import cv2
from tkinter import Tk, filedialog
import os
import click
import sys

from via_sudoku_solver.game import Game

@click.command()
@click.option('-d', '--debug', is_flag=True, help="Debug mode.")
@click.option('-s', '--size', help='Size of the board (px)', default=600)
@click.option('-f', '--filled', type=int, help='Number of filled cells.', default=30)    
@click.option('-r', '--random-trials', type=int, help='Number of trials to fill cell before refresh (stops freezing).', default=50)
def cli(debug, size, filled, random_trials):
    Game(
        board_size=size,
        num_to_fill=filled,
        debug=debug,
        random_fills_trials=random_trials
    ).main_loop()

if __name__ == "__main__":
    cli()
