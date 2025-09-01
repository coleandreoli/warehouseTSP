import numpy as np
import pandas as pd
import networkx as nx
from .simulation.simulation import Simulation


class Grid:
	"""Constructs a graph from a 2D grid and solves path and TSP problems using NetworkX.

	Navigable nodes are grid cells with value 1. Nodes connect to their west and north neighbors,
	with edge weights scaled by the provided factor. The class offers methods to validate graph
	connectivity, convert between grid positions and node indices, compute shortest paths, approximate
	a TSP route for given nodes, and visualize the grid and routes for debugging.

	Attributes:
	        grid (np.ndarray): 2D array representing the grid (1 indicates a pathway).
	        scale (int or float): Factor to scale edge weights.
	        G (nx.Graph): Graph built from the grid.
	"""

	def __init__(self, grid, scale=1):
		self.grid = grid
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

	def validate(self) -> bool:
		if nx.is_connected(self.G):
			return True
		else:
			return False

	def pos2node(self, pos: tuple) -> int:
		return pos[1] * self.grid.shape[1] + pos[0]

	def node2pos(self, node: int) -> tuple:
		return (node // self.grid.shape[1], node % self.grid.shape[1])

	def find_path(self, start: int, end: int):
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

	def tsp(self, pickup_node: list, nodes: list, debug: bool = False):
		tsp = nx.approximation.traveling_salesman_problem
		pickup_list = pickup_node + nodes
		try:
			tsp_route = tsp(self.G, nodes=pickup_list)
		except KeyError as e:
			print(
				f"Route optimization failed: One or more pickup locations are not found in the current grid overlay. "
				f"This may be due to a mismatch between the pickup list and the warehouse layout. Missing node: {str(e)}"
			)
		pickup_order = list(dict.fromkeys(node for node in tsp_route if node in pickup_list))[1:]
		if debug:
			tsp_distance = sum(self.G[u][v]["weight"] for u, v in zip(tsp_route, tsp_route[1:]))
			return pickup_order, tsp_route, tsp_distance
		else:
			return (pickup_order, None, None)

	def _plot(self, tsp_route: list[int] | None = None) -> None:
		"""Debug plot of the grid and (optional) TSP route."""
		import matplotlib.pyplot as plt

		plt.imshow(self.grid, cmap="gray")
		plt.grid(True)

		if tsp_route:
			# node2pos(wp) returns a (row:int, col:int) tuple
			coords: list[tuple[int, int]] = [self.node2pos(wp) for wp in tsp_route]
			rows, cols = zip(*coords)  # unzip into two sequences of ints
			plt.plot(cols, rows, "r-")  # x = cols, y = rows

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
