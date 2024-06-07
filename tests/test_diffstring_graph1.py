import pytest
from .filegraph import GRAPH_PY
from jarvisportal.diffstr import applydiff


diffperfect = """             self.edges[to_node].append((from_node, weight))
 
+    def display_graph(self):
+        display_str = ""
+        for node in self.nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in self.edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()
+
     def dijkstra(self, start, end):
"""

diffok1 = """
             self.edges[to_node].append((from_node, weight))
 
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()
+
     def dijkstra(self, start, end):
"""

diffok2 = """
 self.edges[to_node].append((from_node, weight))
 
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()
+
     def dijkstra(self, start, end):
"""

diffok3 = """
 self.edges[to_node].append((from_node, weight))
+
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()
+
     def dijkstra(self, start, end):
"""

diffok4 = """
 self.edges[to_node].append((from_node, weight))
+
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()
 
     def dijkstra(self, start, end):
"""

diffok5 = """
 self.edges[to_node].append((from_node, weight))
+
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()

     def dijkstra(self, start, end):
"""

diffok6 = """
self.edges[to_node].append((from_node, weight))
+
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()

    def dijkstra(self, start, end):
"""

diffbad = """
self.edges[to_node].append((from_node,weight))
+
+    def display_graph(self):
+        display_str = ""
+        for node in the nodes:
+            connections = ", ".join([f"{neighbor} ({weight})" for neighbor, weight in the edges[node]])
+            display_str += f"Node {node}: {connections}"
+        return display_str.strip()

    def dijkstra(self, start, end):
"""


def test_applydiff_diffperfect_start_15():
    result = applydiff(GRAPH_PY, 15, diffperfect)
    assert "def display_graph" in result


def test_applydiff_diffperfect_start_14():
    result = applydiff(GRAPH_PY, 15, diffperfect)
    assert "def display_graph" in result


def test_applydiff_diffperfect_start_12():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 12, diffperfect)


def test_applydiff_diffperfect_start_16():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 16, diffperfect)


# @pytest.mark.parametrize("diffok", [diffok1, diffok2, diffok3, diffok4, diffok5, diffok6])
@pytest.mark.parametrize("diffok", [diffok1, diffok2, diffok3, diffok4, diffok5, diffok6])
def test_applydiff_diffok_start_15(diffok):
    result = applydiff(GRAPH_PY, 15, diffok)
    assert "def display_graph" in result


@pytest.mark.parametrize("diffok", [diffok1, diffok2, diffok3, diffok4, diffok5, diffok6])
def test_applydiff_diffok_start_14(diffok):
    result = applydiff(GRAPH_PY, 14, diffok)
    assert "def display_graph" in result


@pytest.mark.parametrize("diffok", [diffok1, diffok2, diffok3, diffok4, diffok5, diffok6])
def test_applydiff_diffok_start_12(diffok):
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 12, diffok)


@pytest.mark.parametrize("diffok", [diffok1, diffok2, diffok3, diffok4, diffok5, diffok6])
def test_applydiff_diffok_start_16(diffok):
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 16, diffok)


def test_applydiff_diffbad_start_15():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 15, diffbad)


def test_applydiff_diffbad_start_14():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 14, diffbad)


def test_applydiff_diffbad_start_12():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 12, diffbad)


def test_applydiff_diffbad_start_16():
    with pytest.raises(ValueError):
        applydiff(GRAPH_PY, 16, diffbad)
