import copy
from math import floor

from Minesweeper.Board import Board
from selenium.webdriver.firefox.webdriver import WebDriver
import numpy as np


class MLSolver:

    def __init__(self, driver: WebDriver, game: WebDriver, height, width, mines_counter, model):
        self.game_board = Board(driver, game, height, width, mines_counter)
        self.model = model

    def play(self):
        self.game_board.send_left_click(floor(self.game_board.height / 2), floor(self.game_board.width / 2))
        self.game_board.update_fields()

        while self.game_board.game.find_element_by_id('face').get_attribute("class") == 'facesmile':
            self.search_outline_fields()

        return True if self.game_board.game.find_element_by_id('face').get_attribute('class') == 'facewin' else False

    def search_outline_fields(self):
        prediction_board = np.zeros([self.game_board.height, self.game_board.width], dtype=float)
        outline_fields = self.game_board.neighbours_of_mines
        mines_coordinates = [list(), list()]

        # for field in outline_fields:
        for i in range(len(outline_fields)):
            prediction_board = self.generate_prediction_board(outline_fields[i].y, outline_fields[i].x,
                                                              prediction_board)

        coord = np.where(prediction_board == np.amax(prediction_board))
        # where zwraca array zw wsp. y i drugi array ze wsp. x
        mines_coordinates[0].extend(coord[0])
        mines_coordinates[1].extend(coord[1])

        # zerowanie wartosci pola, na ktorym wykryto mine
        prediction_board[mines_coordinates[0][0]][mines_coordinates[1][0]] = 0

        # gdyby byly dwa pola o takiej samej wartosci (ew. gdy bez prawdopodobienstw):
        for i in range(len(mines_coordinates[0])):
            if self.game_board.board[mines_coordinates[0][i]][mines_coordinates[1][i]].game_class == 'square blank':
                self.game_board.send_right_click(mines_coordinates[0][i], mines_coordinates[1][i])

        for field in outline_fields:
            self.game_board.check_field_neighbours(field.y, field.x)

    def generate_prediction_board(self, y, x, prediction_board):
        matrix_size = 4
        predict_data = []
        coord = []

        for y_shift in range(matrix_size):
            for x_shift in range(matrix_size):
                vector = []
                for j in range(y - y_shift, y + matrix_size - y_shift):
                    if 0 <= j < len(self.game_board.board):
                        for i in range(x - x_shift, x + matrix_size - x_shift):
                            if 0 <= i < len(self.game_board.board[0]):
                                vector.append(copy.copy(self.game_board.board[j][i].mine_neighbours))

                if len(vector) == matrix_size * matrix_size:
                    predict_data.append(vector)
                    coord.append([y - y_shift, x - x_shift])

        # prediction_board = self.predict_mines(predict_data, coord, prediction_board)
        prediction_board = self.predict_mines_probabilities(predict_data, coord, prediction_board)

        return prediction_board

    def predict_mines(self, data, coord, prediction_board):
        y_mine, x_mine = self.locate_mines(data)

        for i in range(len(coord)):
            if y_mine[i] != -1:
                prediction_board[y_mine[i] + coord[i][0]][x_mine[i] + coord[i][1]] += 1

        return prediction_board

    def locate_mines(self, data):
        labels = self.model.make_prediction(data)

        matrix_size = 4

        x = [label % matrix_size if label != 16 else -1 for label in labels]
        y = [int(label / matrix_size) if label != 16 else -1 for label in labels]

        return np.asarray(y), np.asarray(x)

    def predict_mines_probabilities(self, data, coord, prediction_board):
        probabilities = self.model.make_probabilities_prediction(data)

        matrix_size = 4

        for i in range(len(probabilities)):
            for k in range(len(probabilities[0]) - 1):  # na ostatniej pozycji prawdopodobienstwo braku miny
                prediction_board[int(k / matrix_size) + coord[i][0]][k % matrix_size + coord[i][1]] += probabilities[i][
                    k]

        return prediction_board
