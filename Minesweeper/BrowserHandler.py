import os
import time
from selenium import webdriver

from Solvers.LogicSolver import LogicSolver
from MLSolvers.MLSolver import MLSolver
from PrologSolvers.PrologSolver import PrologSolver
from MLSolvers.Model import Model


class BrowserHandler:

    def __init__(self, size, method):
        wins = 0
        games = 30

        driver = webdriver.Firefox()

        if size is 's':
            driver.get("file:///{}/webpage/minesweeperonline.html#beginner".format(os.getcwd()))
        elif size is 'm':
            driver.get("file:///{}/webpage/minesweeperonline.html#intermediate".format(os.getcwd()))
        elif size is 'l':
            driver.get("file:///{}/webpage/minesweeperonline.html".format(os.getcwd()))

        assert 'Minesweeper Online' in driver.title

        model = Model()
        solver = None

        for i in range(games):
            game = driver.find_element_by_id('game')
            height = int(len(game.find_elements_by_class_name('borderlr')) / 2)
            width = int(len(game.find_elements_by_class_name('bordertb')) / 3)

            mines_counter = self.count_mines(game)

            if method is 's':
                solver = LogicSolver(driver, game, height, width, mines_counter)
            elif method is 'm':
                solver = MLSolver(driver, game, height, width, mines_counter, model)
            elif method is 'l':
                solver = PrologSolver(driver, game, height, width, mines_counter)

            if solver.play():
                wins += 1

            # self.save_train_data(logic_solver)
            # self.save_validation_data(logic_solver)

            time.sleep(2.0)
            print(str(i + 1) + '. test - winrate: ' + str(wins / (i + 1) * 100) + '%')
            print("Won: " + str(wins) + ", lost: " + str(i+1-wins))
            driver.find_element_by_id('face').click()

            if self.page_has_loaded(driver):
                continue

        driver.close()
        print('Winrate: ' + str(wins / games * 100) + '%')

    @staticmethod
    def page_has_loaded(driver):
        page_state = driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    @staticmethod
    def count_mines(game):
        mines_counter = int(game.find_element_by_id('mines_hundreds').get_attribute('class')[-1]) * 100
        mines_counter += int(game.find_element_by_id('mines_tens').get_attribute('class')[-1]) * 10
        mines_counter += int(game.find_element_by_id('mines_ones').get_attribute('class')[-1])
        return mines_counter

    @staticmethod
    def save_train_data(logic_solver):
        # with open('data/data.csv', 'a') as file:
        with open('data.csv', 'a') as file:
            data = logic_solver.game_board.train_data
            for i in range(len(data)):
                for j in range(len(data[0])):
                    file.write(str(data[i][j]))
                    file.write(',' if j is not len(data[0]) - 1 else '\n')

    @staticmethod
    def save_validation_data(logic_solver):
        # with open('data/labels.csv', 'a') as file:
        with open('labels.csv', 'a') as file:
            data = logic_solver.game_board.validation_data
            for i in range(len(data)):
                for j in range(len(data[0])):
                    file.write(str(data[i][j]))
                    file.write(',' if j is not len(data[0]) - 1 else '\n')
