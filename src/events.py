"""Events."""

from random import randint, random

from config import config
from simpy.rt import RealtimeEnvironment


class Events:
    """Real-Time Simulation."""

    def __init__(self, env) -> None:
        """Création des évènements."""
        self.rte = RealtimeEnvironment(factor=config["vitesse_simu"])

        self.rte.process(self.dirt_event())
        self.rte.process(self.jewel_event())

        self.environment = env

    def run(self):
        """Lance la simulation."""
        self.rte.run()

    def jewel_event(self):
        """Jewels generator."""
        while True:

            yield self.rte.timeout(
                config["jewel"]["pause"] + config["jewel"]["freq"] * random()
            )

            self.environment.set_objet(
                "jewel",
                randint(0, self.environment.line - 1),
                randint(0, self.environment.col - 1),
            )

    def dirt_event(self):
        """Dirt generator."""
        while True:

            yield self.rte.timeout(
                config["dirt"]["pause"] + config["dirt"]["freq"] * random()
            )

            self.environment.set_objet(
                "dirt",
                randint(0, self.environment.line - 1),
                randint(0, self.environment.col - 1),
            )
