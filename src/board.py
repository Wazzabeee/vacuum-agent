"""GUI."""

import tkinter as tk

from PIL import Image, ImageTk


class Board:
    """GUI Class."""

    def __init__(self, env, stats, mode="not-informed") -> None:
        """Création GUI."""
        self.perf = stats

        self.canva_size = {
            "width": int(800 / env.col),
            "heigh": int(800 / env.line),
        }

        self.window = tk.Tk()
        self.window.title("Robot Aspirateur - " + mode)
        self.window.iconbitmap(f"../data/robot_vacuum_icon.ico")

        frame = tk.Frame(
            self.window,
            bg="black",
            height=self.canva_size["heigh"] * env.col,
            width=self.canva_size["width"] * env.line,
        )
        frame.pack(side=tk.LEFT)

        perf_frame = tk.Frame(self.window)
        perf_frame.pack(side=tk.RIGHT)

        stats_lbl = tk.Label(
            perf_frame, text="Statistiques", font=("Helvetica", 18, "bold"), width=20
        )
        stats_lbl.pack()

        self.stats = {
            "energy_consumed": None,
            "dirt_vacuumed": None,
            "jewel_collected": None,
            "error": None,
            "score": None,
        }

        for label in self.stats:
            self.stats[label] = tk.Label(
                perf_frame, text=f"{label} : {self.perf.stats[label]:.2f}"
            )
            self.stats[label].pack()

        total_stats_lbl = tk.Label(
            perf_frame, text="Total Statistiques", font=("Helvetica", 18, "bold")
        )
        total_stats_lbl.pack()

        self.total_stats = {
            "total_dirt_vacuumed": None,
            "total_energy_consumed": None,
            "total_jewel_collected": None,
            "total_error": None,
            "total_distance": None,
            "mean_distance": None,
            "mean_score": None,
            "best_score": None,
        }

        for label in self.total_stats:
            self.total_stats[label] = tk.Label(
                perf_frame, text=f"{label} : {self.perf.total_stats[label]:.2f}"
            )
            self.total_stats[label].pack()

        self.duree_lbl = tk.Label(
            perf_frame,
            text=f"Temps : {self.perf.duree:.2f} s",
            font=("Helvetica", 12, "bold"),
        )
        self.duree_lbl.pack()

        self.refresh_rate_lbl = tk.Label(
            perf_frame,
            text=f"Refresh Rate : {self.perf.refresh_rate} s",
            font=("Helvetica", 12, "bold"),
        )
        self.refresh_rate_lbl.pack()

        self.image = {"blank": None, "dirt": None, "jewel": None, "robot": None}

        for name in self.image:
            self.image[name] = self.load(
                name,
                int(self.canva_size["width"] / 2),
                int(self.canva_size["heigh"] / 2),
            )

        self.board = [
            [{"dirt": None, "jewel": None, "robot": None} for _ in range(env.line)]
            for _ in range(env.col)
        ]

        for x in range(env.col):
            for y in range(env.line):
                grid_canv = tk.Canvas(
                    frame,
                    height=self.canva_size["heigh"],
                    width=self.canva_size["width"],
                    bg="white",
                )
                grid_canv.grid(row=y, column=x, padx=2.5, pady=2.5)

                self.board[x][y]["dirt"] = tk.Canvas(
                    grid_canv,
                    bg="white",
                    heigh=self.canva_size["heigh"] / 2,
                    width=self.canva_size["width"] / 2,
                )
                self.board[x][y]["dirt"].grid(row=0, column=0)
                self.board[x][y]["dirt"].create_image(
                    self.canva_size["width"] / 4,
                    self.canva_size["heigh"] / 4,
                    image=self.image["blank"],
                )
                self.board[x][y]["dirt"].image = self.image["blank"]

                self.board[x][y]["jewel"] = tk.Canvas(
                    grid_canv,
                    bg="white",
                    heigh=self.canva_size["heigh"] / 2,
                    width=self.canva_size["width"] / 2,
                )
                self.board[x][y]["jewel"].grid(row=0, column=1)
                self.board[x][y]["jewel"].create_image(
                    self.canva_size["width"] / 4,
                    self.canva_size["heigh"] / 4,
                    image=self.image["blank"],
                )
                self.board[x][y]["jewel"].image = self.image["blank"]

                self.board[x][y]["robot"] = tk.Canvas(
                    grid_canv,
                    bg="white",
                    heigh=self.canva_size["heigh"] / 2,
                    width=self.canva_size["width"] / 2,
                )
                self.board[x][y]["robot"].grid(row=1, column=0, columnspan=2)
                self.board[x][y]["robot"].create_image(
                    self.canva_size["width"] / 4,
                    self.canva_size["heigh"] / 4,
                    image=self.image["blank"],
                )
                self.board[x][y]["robot"].image = self.image["blank"]

    @staticmethod
    def load(name, width_size, heigh_size) -> ImageTk:
        """Charge une image."""
        img = Image.open(f"../data/{name}.webp")
        img = img.resize((width_size, heigh_size), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def display_objet(self, x, y, objet):
        """Affiche l'image."""
        self.board[x][y][objet].create_image(
            self.canva_size["width"] / 4,
            self.canva_size["heigh"] / 4,
            image=self.image[objet],
        )
        self.board[x][y][objet].image = self.image[objet]

    def hide_objet(self, objet, x, y):
        """Cacher l'image."""
        self.board[x][y][objet].create_image(
            self.canva_size["width"] / 4,
            self.canva_size["heigh"] / 4,
            image=self.image["blank"],
        )
        self.board[x][y][objet].image = self.image["blank"]

    def update_stats(self):
        """Update les stats."""
        for label in self.stats:
            self.stats[label].configure(text=f"{label} : {self.perf.stats[label]:.2f}")

        for label in self.total_stats:
            self.total_stats[label].configure(
                text=f"{label} : {self.perf.total_stats[label]:.2f}"
            )

        self.duree_lbl.configure(
            text=f"Temps : (x{len(self.perf.historique)}) {self.perf.duree:.2f} s"
        )

        self.refresh_rate_lbl.configure(
            text=f"Refresh Rate : {self.perf.refresh_rate} s"
        )

    def display(self):
        """Lance le GUI."""
        self.window.mainloop()
