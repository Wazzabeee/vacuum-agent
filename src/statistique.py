"""Statistiques pour apprentisage."""

from copy import deepcopy

from config import config
from simpy.rt import RealtimeEnvironment


class Stats:
    """Class Statistiques."""

    def __init__(self) -> None:
        """Init statistiques."""
        self.rte = RealtimeEnvironment(factor=config["vitesse_simu"])

        self.rte.process(self.stats_event())

        self.freq = 10

        self.clean()

        self.total_stats = {
            "total_dirt_vacuumed": 0,
            "total_energy_consumed": 0,
            "total_jewel_collected": 0,
            "total_error": 0,
            "total_distance": 0,
            "mean_distance": 0,
            "mean_score": 0,
            "best_score": 0,
        }

        self.duree = 0
        self.refresh_rate = config["size"]["width"] + config["size"]["heigh"] - 1

        self.historique = [deepcopy(self.total_stats)]

    def compute_score(self):
        """Calculate the score."""
        self.stats["score"] = (
            10 * self.stats["dirt_vacuumed"]
            + 5 * self.stats["jewel_collected"]
            - self.stats["energy_consumed"]
            - 25 * self.stats["error"]
        )

    def clean(self):
        """Réinitialise les stats temporaires."""
        self.stats = {
            "dirt_vacuumed": 0,
            "energy_consumed": 0,
            "jewel_collected": 0,
            "error": 0,
            "score": 0,
        }

    def archiver(self):
        """Archive les données."""
        tmp = deepcopy(self.total_stats)
        self.historique.append(tmp)

        self.total_stats = {
            "total_dirt_vacuumed": 0,
            "total_energy_consumed": 0,
            "total_jewel_collected": 0,
            "total_error": 0,
            "total_distance": 0,
            "mean_distance": 0,
            "mean_score": 0,
            "best_score": 0,
        }

        self.duree = 0

    def stats_event(self):
        """Stats mainloop."""
        while True:
            yield self.rte.timeout(self.freq)

            self.duree += self.freq  # self.rte.now

            self.compute_score()
            tmp = deepcopy(self.stats)
            self.total_stats["total_dirt_vacuumed"] += tmp["dirt_vacuumed"]
            self.total_stats["total_energy_consumed"] += tmp["energy_consumed"]
            self.total_stats["total_jewel_collected"] += tmp["jewel_collected"]
            self.total_stats["total_error"] += tmp["error"]
            self.total_stats["total_distance"] += (
                tmp["energy_consumed"] - tmp["dirt_vacuumed"] - tmp["jewel_collected"]
            )
            self.total_stats["mean_distance"] = (
                self.freq * self.total_stats["total_distance"] / self.duree
            )
            self.total_stats["mean_score"] = (
                (
                    ((self.duree - self.freq) / self.freq)
                    * self.total_stats["mean_score"]
                    + tmp["score"]
                )
                * self.freq
                / self.duree
            )

            if tmp["score"] > self.total_stats["best_score"]:
                self.total_stats["best_score"] = tmp["score"]
            self.clean()

    def run(self):
        """Lance la simulation."""
        self.rte.run()
