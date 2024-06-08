class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def add_node(self, value):
        self.nodes.add(value)
        if value not in self.edges:
            self.edges[value] = []

    def add_edge(self, from_node, to_node, weight):
        if from_node in self.nodes and to_node in self.nodes:
            self.edges[from_node].append((to_node, weight))
            self.edges[to_node].append((from_node, weight))

    def dijkstra(self, start, end):
        import heapq
        queue = []
        heapq.heappush(queue, (0, start))
        distances = {node: float('infinity') for node in self.nodes}
        distances[start] = 0
        shortest_path = {}

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.edges[current_node]:
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(queue, (distance, neighbor))
                    shortest_path[neighbor] = current_node

        path = []
        while end:
            path.append(end)
            end = shortest_path.get(end)
        path.reverse()
        return path