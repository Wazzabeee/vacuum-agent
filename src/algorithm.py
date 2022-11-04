"""Search Algorithm."""


class Search:
    """Interface Search Algorithm."""

    def __init__(self, robot) -> None:
        """Initiate algorithm."""
        self.robot = robot

    @staticmethod
    def get_path(path, end) -> list:
        """Return itinerary from start to end."""
        moves = []

        node = (end["x"], end["y"])
        while True:
            previous_node = path[node]

            if not previous_node:
                return moves

            moves.insert(
                0, ("move", (node[0] - previous_node[0], node[1] - previous_node[1]))
            )

            node = previous_node

    def get_neighbours(self, position, visited) -> list:
        """Renvoie les déplacements possibles."""
        moves = []
        if 1 <= position["x"]:
            moves.append((position["x"] - 1, position["y"]))

        if position["x"] < len(self.robot.grille["dirt"]) - 1:
            moves.append((position["x"] + 1, position["y"]))

        if 1 <= position["y"]:
            moves.append((position["x"], position["y"] - 1))

        if position["y"] < len(self.robot.grille["dirt"][0]) - 1:
            moves.append((position["x"], position["y"] + 1))

        return list(set(moves) - visited)

    def search(self):
        """Search Algorithm."""
        raise NotImplementedError


class AStar(Search):
    """Implement A* Search Algorithm."""

    def __init__(self, robot) -> None:
        """Initiate A*."""
        print("A*")
        super().__init__(robot)

    @staticmethod
    def get_h_score(grille, pos) -> float:
        """Return the estimate score from curr node to end node."""
        # Si Jewel sur case : - 50%
        # Si Dirt sur case : - 40%
        # Si Dirt & Jewel adjacents : - 30%
        # Si Jewel adjacent : - 20%
        # Si Dirt adjacent :  - 10%

        if grille["jewel"][pos[0]][pos[1]]:
            return 0.5

        if grille["dirt"][pos[0]][pos[1]]:
            return 0.6

        is_dust_adjacent = False
        is_jewel_adjacent = False

        for move in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            try:
                if grille["jewel"][pos[0] + move[0]][pos[1] + move[1]]:
                    is_jewel_adjacent = True
                if grille["dirt"][pos[0] + move[0]][pos[1] + move[1]]:
                    is_dust_adjacent = True
            except IndexError:
                continue

        if is_jewel_adjacent and is_dust_adjacent:
            return 0.7

        if is_jewel_adjacent:
            return 0.8

        if is_dust_adjacent:
            return 0.9

        return 1

    @staticmethod
    def get_manhattan_distance(start, end) -> int:
        """Return manhattan distance betwen start point and end point."""
        return int(abs(end[0] - start[0]) + abs(end[1] - start[1]))

    def search(self):
        """Algorithme A*."""

        path = {}
        stack = [
            {
                "x": self.robot.position["x"],
                "y": self.robot.position["y"],
                "f": 0,
                "g": 0,
                "h": 0,
            }
        ]
        close = []  # {x coord, y coord, f value, g, h}
        close_bis = set()  # {x coord, y coord}
        path[(self.robot.position["x"], self.robot.position["y"])] = None

        while stack:
            # Get the current node with the least f_value
            current_node = min(
                stack, key=lambda t: t["f"]
            )  # retrieve minimum f value among open list
            simple_node = (current_node["x"], current_node["y"])

            stack.remove(current_node)  # remove current node from open list
            close.append(current_node)  # add current node to closed list
            close_bis.add(simple_node)  # add to closed list (without f,g h values)

            # Check for goal
            if self.robot.grille["jewel"][current_node["x"]][current_node["y"]]:
                actions = self.get_path(
                    path, {"x": current_node["x"], "y": current_node["y"]}
                )
                actions.append(("jewel", (current_node["x"], current_node["y"])))
                self.robot.actions = actions
                return

            if self.robot.grille["dirt"][current_node["x"]][current_node["y"]]:
                actions = self.get_path(
                    path, {"x": current_node["x"], "y": current_node["y"]}
                )
                actions.append(("dirt", (current_node["x"], current_node["y"])))
                self.robot.actions = actions
                return

            # Otherwise generate children
            for neighbour in self.get_neighbours(
                {"x": current_node["x"], "y": current_node["y"]}, close_bis
            ):
                if neighbour in close_bis:
                    continue

                manhanttan_dist = self.get_manhattan_distance(simple_node, neighbour)
                h_score = self.get_h_score(self.robot.grille, neighbour)

                child = {
                    "x": neighbour[0],
                    "y": neighbour[1],
                    "f": manhanttan_dist + h_score,
                    "g": current_node["g"] + manhanttan_dist,
                    "h": h_score,
                }

                # Check if child is already in open list
                for sub_dict in stack:
                    if child["x"] == sub_dict["x"] and child["y"] == sub_dict["y"]:
                        if child["g"] > sub_dict["g"]:
                            continue
                stack.append(child)
                path[neighbour] = (simple_node[0], simple_node[1])

        self.robot.actions = [
            ("stay", (self.robot.position["x"], self.robot.position["y"]))
        ]


class BFS(Search):
    """Implement BFS Search Algorithm."""

    def __init__(self, robot) -> None:
        """Initiate BFS."""
        print("BFS")
        super().__init__(robot)

    def search(self):
        """BFS Algo."""
        path = {}
        visited = set()
        stack = [(self.robot.position["x"], self.robot.position["y"])]
        path[stack[0]] = None

        while stack:
            node = stack.pop(0)
            visited.add(node)
            node = {"x": node[0], "y": node[1]}

            if self.robot.grille["jewel"][node["x"]][node["y"]]:
                actions = self.get_path(path, node)
                actions.append(("jewel", (node["x"], node["y"])))
                self.robot.actions = actions
                return

            if self.robot.grille["dirt"][node["x"]][node["y"]]:
                actions = self.get_path(path, node)
                actions.append(("dirt", (node["x"], node["y"])))
                self.robot.actions = actions
                return

            for neighbour in self.get_neighbours(node, visited):
                stack.append(neighbour)
                path[neighbour] = (node["x"], node["y"])

        self.robot.actions = [
            ("stay", (self.robot.position["x"], self.robot.position["y"]))
        ]
