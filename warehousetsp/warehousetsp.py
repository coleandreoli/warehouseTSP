import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from .simulation.simulation import Simulation


class Grid:
    def __init__(self, grid, waypoints, scale=1):
        self.grid = grid
        self.waypoints = waypoints
        self.scale = scale
        self.G = nx.Graph()
        self.make_graph()

    def make_graph(self):
        x_shape = self.grid.shape[1]
        for n, pos in enumerate(np.ndindex(self.grid.shape)):
            x = pos[1]
            y = pos[0]
            if self.grid[pos] == 1:
                self.G.add_node(n, pos=(x, -y))
                # Add edged to north and west neighbors if pathway
                if x > 0 and self.grid[y, x - 1] == 1:
                    self.G.add_edge(n, n - 1, weight=self.scale)
                if y > 0 and self.grid[y - 1, x] == 1:
                    north_neighbor = n - x_shape
                    self.G.add_edge(n, north_neighbor, weight=self.scale)

    def validate(self):
        if nx.is_connected(self.G):
            return True
        else:
            return False

    def pos2node(self, pos: tuple):
        return pos[1] * self.grid.shape[1] + pos[0]

    def node2pos(self, node: int):
        return (node // self.grid.shape[1], node % self.grid.shape[1])

    def find_path(self, start, end, model: str = "dijkstra", node=False):
        if node:
            start = start
            end = end
        else:
            start = self.pos2node(self.waypoints[start])
            end = self.pos2node(self.waypoints[end])
        if model == "astar":

            def heuristic(a, b):
                x1, y1 = self.G.nodes[a]["pos"]
                x2, y2 = self.G.nodes[b]["pos"]
                return np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))

            path = nx.astar_path(
                self.G, start, end, heuristic=heuristic, weight="weight"
            )
        elif model == "dijkstra":
            try:
                path = nx.shortest_path(self.G, start, end)
            except nx.NetworkXNoPath:
                print("No path found between the given nodes.")
                path = []
            except nx.NodeNotFound as e:
                print(f"Error: {e}")
                path = []
            except Exception as e:
                print(f"Unexpected error: {e}")
                path = []

        distance = sum(self.G[u][v]["weight"] for u, v in zip(path, path[1:]))
        return path, distance

    def tsp(self, pickup_node: list, nodes: list):
        tsp = nx.approximation.traveling_salesman_problem
        pickup_list = pickup_node + nodes
        tsp_route = tsp(self.G, nodes=pickup_list)
        tsp_distance = sum(
            self.G[u][v]["weight"] for u, v in zip(tsp_route, tsp_route[1:])
        )

        seen = set()
        pickup_order = []

        for node in tsp_route:
            if node in pickup_list and node not in seen:
                pickup_order.append(node)
                seen.add(node)

        return tsp_route, tsp_distance, pickup_order

    def plot(self, path: list = None):
        plt.imshow(self.grid, cmap="gray")
        plt.grid(True)

        for key, (x, y) in self.waypoints.items():
            plt.plot(x, y, "go")
            # plt.text(x, y, key, fontsize=12, ha="right")
        if path:
            # Plot the path
            path_coords = [self.node2pos(wp) for wp in path]
            path_coords = np.array(path_coords)
            plt.plot(path_coords[:, 1], path_coords[:, 0], "r-")
        plt.show()

    def plot_graph(self):
        pos = nx.get_node_attributes(self.G, "pos")
        nx.draw(
            self.G,
            pos=pos,
            with_labels=True,
            node_size=200,
            node_color="lightblue",
            edge_color="gray",
        )
        plt.show()


class Dispatch:
    def __init__(self, wos, wh):
        """Generates Pick lists depending on time, location, and bin"""
        self.wos = wos
        self.wh = wh
        self.sim = Simulation(wh)

    def fifo(self):
        pass

    def lifo(self):
        pass

    def deplete_max_bins(self, items: list):
        pl = []
        for item in items:
            bin = self.sim.get_highest_bin(item)
            pl.append({"bin": bin, "item": item})
        return pl

    def deplete_min_bins(self):
        pass

    def shortest_path(self):
        pass
