"""Environment."""

from random import randint
from threading import Thread

from board import Board
from config import config
from events import Events
from robot import Robot
from statistique import Stats


class Environment:
    """Environment Class."""

    def __init__(self, line, col, mode) -> None:
        """Création de l'environment."""
        # Dimension de la grille
        self.line = line
        self.col = col

        # Création de la grille
        self.grid = {
            "dirt": [[False for y in range(self.line)] for x in range(self.col)],
            "jewel": [[False for y in range(self.line)] for x in range(self.col)],
        }

        # Initilisation du robot dans son espace
        self.position_robot = {
            "x": randint(0, self.col - 1),
            "y": randint(0, self.line - 1),
        }

        ##### Stats #####
        stats = Stats()
        thread_stats = Thread(target=stats.run)
        thread_stats.daemon = True
        thread_stats.start()

        ##### GUI #####
        self.board = Board(self, stats, mode)

        # On pose aléatoirement un bijoux et une poussière dans la grille
        for objet in ["dirt", "jewel"]:
            self.set_objet(objet, randint(0, self.col - 1), randint(0, self.line - 1))

        self.set_objet("robot", self.position_robot["x"], self.position_robot["y"])

        ##### Event #####
        events = Events(self)
        thread_event = Thread(target=events.run)
        thread_event.daemon = True
        thread_event.start()

        ##### Robot #####
        robot = Robot(self, stats, mode)
        thread_robot = Thread(target=robot.run)
        thread_robot.daemon = True
        thread_robot.start()

        self.board.display()

    def set_objet(self, objet, x, y):
        """Place l'objet dans la grille."""
        if objet != "robot":
            self.grid[objet][x][y] = True

        self.board.display_objet(x, y, objet)

    def unset_objet(self, objet, x, y):
        """Supprime l'objet dans la grille."""
        self.grid[objet][x][y] = False

        self.board.hide_objet(objet, self.position_robot["x"], self.position_robot["y"])

    def move_robot(self, dx, dy):
        """Déplace le robot."""
        self.board.hide_objet(
            "robot", self.position_robot["x"], self.position_robot["y"]
        )
        self.position_robot["x"] += dx
        self.position_robot["y"] += dy
        self.board.display_objet(
            self.position_robot["x"], self.position_robot["y"], "robot"
        )

    def update_stats(self):
        """Update les statisques à afficher."""
        self.board.update_stats()


def main():
    """Entry point."""
    size = config["size"]
    Environment(size["width"], size["heigh"], config["mode"])


if __name__ == "__main__":
    main()
