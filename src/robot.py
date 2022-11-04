"""Robot."""

from copy import deepcopy

from algorithm import BFS, AStar
from config import config
from simpy.rt import RealtimeEnvironment


class Sensor:
    """Capteur."""

    def __init__(self, env, robot) -> None:
        """Création du/des capteur(s)."""
        self.environment = env
        self.robot = robot

    def observe_environment(self):
        """Récupère les données d'environnement."""
        self.robot.grille = deepcopy(self.environment.grid)
        self.robot.position = deepcopy(self.environment.position_robot)


class Effector:
    """Action sur l'environnement."""

    def __init__(self, env, robot) -> None:
        """Création de l'effecteur."""
        self.environment = env
        self.robot = robot

    def move(self, dx, dy):
        """Déplace le robot."""
        self.environment.move_robot(dx, dy)
        self.robot.perf.stats["energy_consumed"] += 1

    def vacuum(self, x, y):
        """Aspire une pousière."""
        self.robot.perf.stats["energy_consumed"] += 1

        if self.environment.grid["dirt"][x][y]:
            self.environment.unset_objet("dirt", x, y)
            self.robot.perf.stats["dirt_vacuumed"] += 1

        if self.environment.grid["jewel"][x][y]:
            self.environment.unset_objet("jewel", x, y)
            self.robot.perf.stats["error"] += 1

    def collect(self, x, y):
        """Ramasse un objet."""
        self.robot.perf.stats["energy_consumed"] += 1

        if self.environment.grid["jewel"][x][y]:
            self.environment.unset_objet("jewel", x, y)
            self.robot.perf.stats["jewel_collected"] += 1

    def stay_put(self):
        """Ne fait rien."""

    def execute(self):
        """Execute l'action dans la liste."""
        try:
            action = self.robot.actions.pop(0)

            if action[0] == "dirt":
                x, y = action[1]
                self.vacuum(x, y)
            elif action[0] == "jewel":
                x, y = action[1]
                self.collect(x, y)
            elif action[0] == "move":
                dx, dy = action[1]
                self.move(dx, dy)
        except IndexError:
            self.stay_put()
        finally:
            self.robot.perf.compute_score()
            self.environment.update_stats()

        return len(self.robot.actions) > 0


class Robot:
    """Agent intelligent."""

    EPSILLON = config["learning"]["epsillon"]

    def __init__(self, env, stats, mode) -> None:
        """Création du robot."""
        self.rte = RealtimeEnvironment(factor=config["vitesse_simu"])

        self.rte.process(self.robot_event())

        # Capteur(s)
        self.capteur = Sensor(env, self)

        # Algo de Recherche
        self.algo = AStar(self) if mode == "informed" else BFS(self)

        # Actionneur(s)
        self.actionneur = Effector(env, self)

        self.has_strategy = False
        self.grille = []
        self.position = {}
        self.actions = []
        self.perf = stats
        self.learning_mvt = None

    def get_mvt(self, refresh_rate):
        """Retourne le mouvement de la courbe."""
        if len(self.perf.historique) < 2:
            self.learning_mvt = "down"
            return refresh_rate

        print("Current mean_score")
        print(self.perf.total_stats["mean_score"])
        print("Preivous mean_score")
        print(self.perf.historique[-1]["mean_score"])

        diff = (
            self.perf.total_stats["mean_score"] - self.perf.historique[-1]["mean_score"]
        )

        if diff**2 <= self.EPSILLON:
            return refresh_rate

        if (self.learning_mvt == "up" and diff > 0) or (
            self.learning_mvt == "down" and diff < 0
        ):
            self.learning_mvt = "up"
            return min(
                max(2, int(refresh_rate * 4 / 3)),
                len(self.grille["dirt"]) + len(self.grille["dirt"][0]) - 1,
            )

        if (self.learning_mvt == "up" and diff < 0) or (
            self.learning_mvt == "down" and diff > 0
        ):
            self.learning_mvt = "down"
            return max(int(refresh_rate * 2 / 3), 1)

        # Impossible
        return refresh_rate

    def robot_event(self):
        """Robot mainloop."""
        iteration = 0
        refresh_rate = config["size"]["width"] + config["size"]["heigh"] - 1
        while True:

            yield self.rte.timeout(1)
            iteration += 1

            # Apprentisage
            if (iteration - 1) != 0 and (iteration - 1) % config["learning"][
                "learning_period"
            ] == 0:
                refresh_rate = self.get_mvt(refresh_rate)
                self.perf.refresh_rate = refresh_rate

                print(f"New refreshing rate is {refresh_rate}")

                self.perf.archiver()  # Archive stats

            # Sensor
            self.capteur.observe_environment()

            # Modifier l'état
            if not (
                any(any(x) for x in self.grille["dirt"])
                or any(any(x) for x in self.grille["jewel"])
            ):
                print("Mission Accomplished !")
                self.actionneur.execute()
                continue

            # Choisir une action
            if (iteration % refresh_rate == 0) | (not self.has_strategy):
                self.algo.search()
                self.has_strategy = True

            # Effectuer l'action
            self.has_strategy = self.actionneur.execute()

    def run(self):
        """Lance la simulation."""
        self.rte.run()
