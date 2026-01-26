from typing import List, Type, Tuple, Any, Dict, Optional, Union
from .base_action import *
import random

NodeSpec = Union[BaseAction, Tuple[str, BaseAction]]  # allow auto-naming or explicit id
PathSpec = Union[Tuple[str, List[NodeSpec]], List[NodeSpec]]  # allow auto-naming or explicit id
Edge = Tuple[str, str, Optional[str]]

THEMES = {
    "basic": {
        "background_color": "#FFFFFF",
        "fill_color": "#E8E8E8",
        "outline_color": "#000000",
        "font_color": "#000000",
        "font_name": "Arial",
        "font_size": "10",
        "margin": "0,0",
        "padding":  "1.0,0.5",
    },
}

class BaseComposeAction(BaseAction):
    """
    Base Compose Action

    It is a directed graph
    """
    type: str = "base_compose_action"
    # arguments: Dict[str, Any] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._nodes: Dict[str, BaseAction] = {}
        self._edges: List[Edge] = []
        self._node_groups: Dict[str, Any] = {}

        self._start_node = DummyAction(name=self.type + '_start_node')
        self._end_node = DummyAction(name=self.type + '_end_node')

        self.add_node(self._start_node)
        self.add_node(self._end_node)

    @property
    def num_nodes(self):
        return len(self._nodes)

    @property
    def num_edges(self):
        return len(self._edges)

    def add_node(self, action: BaseAction):
        node_id = action.id
        self._nodes[node_id] = action

    def add_nodes(self, actions: List[BaseAction]):
        for action in actions:
            self.add_node(action)

    def add_edge(self, node_1: BaseAction, node_2: BaseAction, label=None):
        edge = (node_1.id, node_2.id, label)
        if edge not in self._edges:
            self._edges.append(edge)

    def incoming(self, node: BaseAction):
        """Returns nodes connecting to the given node (or list of nodes)."""
        nodes = node if isinstance(node, list) else [node]
        node_ids = [node.id for node in nodes]
        # Find edges incoming to this group but not outgoing from it
        incoming = [self._nodes[e[0]] for e in self._edges
                    if e[1] in node_ids and e[0] not in node_ids]
        return incoming

    def outgoing(self, node, edge_name_pref: Optional[str] = None):
        """Returns nodes connecting out of the given node (or list of nodes)."""
        nodes = node if isinstance(node, list) else [node]
        node_ids = [node.id for node in nodes]
        # Find edges outgoing from this group but not incoming to it
        if edge_name_pref is not None:
            outgoing_pref = [self._nodes[e[1]] for e in self._edges
                        if e[0] in node_ids and e[1] not in node_ids and edge_name_pref in e[2]]
            if len(outgoing_pref) > 0:
                return outgoing_pref
        outgoing = [self._nodes[e[1]] for e in self._edges
                    if e[0] in node_ids and e[1] not in node_ids]
        return outgoing

    def add_path(self, name: str, path: PathSpec):
        prev = self._start_node
        for node_entry in path:
            if isinstance(node_entry, tuple):
                node_desp, node = node_entry
            else:
                node = node_entry
            if isinstance(node, BaseComposeAction):
                self.add_nodes(node._nodes.values())
                self._edges.extend(node._edges)
                self.add_edge(prev, node._start_node, name)
                prev = node._end_node
            else:
                self.add_node(node)
                self.add_edge(prev, node, name)
                prev = node
        self.add_edge(prev, self._end_node, name)

    def find_leaf_node(self, exclude_end_node: bool = True):
        leaf_nodes = set()
        def dfs_helper(node, leaf_nodes):
            if len(self.outgoing(node)) == 0:
                if (exclude_end_node and not self.is_end_node(node, strict=True)) \
                    or not exclude_end_node:
                    leaf_nodes.add(node)
                return
            
            for node_out in self.outgoing(node):
                dfs_helper(node_out, leaf_nodes)

        dfs_helper(self._start_node, leaf_nodes)
        return leaf_nodes

    def append_path(self, name: str, path: PathSpec):
        """
        Append a path to connected to the leaf nodes.
        Note: it is designed to be not connect the end_node.
        """
        leaf_nodes = self.find_leaf_node()

        prev = None
        for i, node_entry in enumerate(path):
            if isinstance(node_entry, tuple):
                node_desp, node = node_entry
            else:
                node = node_entry
            if i == 0:
                if isinstance(node, BaseComposeAction):
                    self.add_nodes(node._nodes.values())
                    self._edges.extend(node._edges)
                    for leaf_node in leaf_nodes:
                        self.add_edge(leaf_node, node._start_node, name)
                    prev = node._end_node
                else:
                    self.add_node(node)
                    for leaf_node in leaf_nodes:
                        self.add_edge(leaf_node, node, name)
                    prev = node
            else:
                if isinstance(node, BaseComposeAction):
                    self.add_nodes(node._nodes.values())
                    self._edges.extend(node._edges)
                    self.add_edge(prev, node._start_node, name)
                    prev = node._end_node
                else:
                    self.add_node(node)
                    self.add_edge(prev, node, name)
                    prev = node
    
    def commit_end_node(self):
        """
        Connect all leaf nodes to the _end_node.
        """
        leaf_nodes = self.find_leaf_node()
        for leaf_node in leaf_nodes:
            self.add_edge(leaf_node, self._end_node)

    def append_graph(self, graph_description: str = None, graph: BaseAction = None):
        """
        Add a graph to connected to the leaf nodes and add edges to the _end_node.
        """
        leaf_nodes = self.find_leaf_node()
        self._node_groups[graph_description] = {}

        if isinstance(graph, BaseComposeAction):
            self._node_groups[graph_description] = graph._nodes
            self.add_nodes(graph._nodes.values())
            self._edges.extend(graph._edges)
            for leaf_node in leaf_nodes:
                self.add_edge(leaf_node, graph._start_node)
        elif isinstance(graph, BaseAction):
            self._node_groups[graph_description] = {graph.id: graph}
            self.add_node(graph)
            for leaf_node in leaf_nodes:
                self.add_edge(leaf_node, graph)
        else:
            raise ValueError("graph must be a BaseAction or BaseComposeAction")

    def build_dot(self, vertical=True, display_node_groups=False) -> "Digraph":
        """
        Generate a GraphViz Dot graph.
        If verbose, then draw more detailed info as well as groups.
        Returns a GraphViz Digraph object.
        """
        from graphviz import Digraph
        import random
        import html

        def escape_html(text):
            """Escape special characters for HTML labels in Graphviz."""
            return html.escape(str(text))

        dot = Digraph()
        
        dot.attr("graph", 
                bgcolor=THEMES["basic"]["background_color"],
                color=THEMES["basic"]["outline_color"],
                fontsize=THEMES["basic"]["font_size"],
                fontcolor=THEMES["basic"]["font_color"],
                fontname=THEMES["basic"]["font_name"],
                margin=THEMES["basic"]["margin"],
                rankdir="TB" if vertical else "LR",
                pad=THEMES["basic"]["padding"])

        dot.attr("edge", style="solid", 
                color=THEMES["basic"]["outline_color"],
                fontsize=THEMES["basic"]["font_size"],
                fontcolor=THEMES["basic"]["font_color"],
                fontname=THEMES["basic"]["font_name"])

        # Set color for node based on their group
        node_colors = dict()
        for node in self._nodes.values():
            node_colors[node.id] = list()

        if display_node_groups:
            for node_group in self._node_groups.values():
                # Generate light colors by constraining RGB values to 180-255 range
                # This ensures good contrast with dark text
                r = random.randint(120, 255)
                g = random.randint(120, 255)
                b = random.randint(120, 255)
                color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
                for node in node_group.values():
                    node_colors[node.id].append(color)

        for node_id in node_colors:
            if len(node_colors[node_id]) == 0:
                node_colors[node_id].append(THEMES["basic"]["fill_color"])

        for node in self._nodes.values():
            color = ":".join(node_colors[node.id])
            if self.is_start_node(node):
                dot.attr("node", shape="ellipse", 
                        style="filled", margin="0,0",
                        fillcolor=THEMES["basic"]["fill_color"] if self.is_start_node(node, strict=True) else color,
                        color=THEMES["basic"]["outline_color"],
                        fontsize=THEMES["basic"]["font_size"],
                        fontname=THEMES["basic"]["font_name"])
                label = "<tr><td cellpadding='6'>{}</td></tr>".format(escape_html(node.name))
                label = "<<table border='0' cellborder='0' cellpadding='0'>" + label + "</table>>"
                dot.node(str(node.id), label)
            elif self.is_end_node(node):
                dot.attr("node", shape="doubleoctagon", 
                        style="filled", margin="0,0",
                        fillcolor=THEMES["basic"]["fill_color"] if self.is_end_node(node, strict=True) else color,
                        color=THEMES["basic"]["outline_color"],
                        fontsize=THEMES["basic"]["font_size"],
                        fontname=THEMES["basic"]["font_name"])
                label = "<tr><td cellpadding='6'>{}</td></tr>".format(escape_html(node.name))
                label = "<<table border='0' cellborder='0' cellpadding='0'>" + label + "</table>>"
                dot.node(str(node.id), label)
            else:
                dot.attr("node", shape="box", 
                        style="filled", margin="0,0",
                        fillcolor=color,
                        color=THEMES["basic"]["outline_color"],
                        fontsize=THEMES["basic"]["font_size"],
                        fontcolor=THEMES["basic"]["font_color"],
                        fontname=THEMES["basic"]["font_name"])
                label = ""
                if node.name:
                    label += "<tr><td>{}</td></tr>".format(escape_html(node.name))
                label += "<tr><td cellpadding='6'>{}</td></tr>".format(escape_html(node.arguments_str))
                label = "<<table border='0' cellborder='0' cellpadding='0'>" + label + "</table>>"
                dot.node(str(node.id), label)

        for a, b, label in self._edges:
            if isinstance(label, (list, tuple)):
                label = "x".join([str(l or "?") for l in label])
            dot.edge(str(a), str(b), label)
        return dot    

    def is_start_node(self, node: BaseAction, strict=False):
        if strict:
            return node.id == self._start_node.id
        else:
            return True if node.name.endswith("start_node") else False

    def is_end_node(self, node: BaseAction, strict=False):
        if strict:
            return node.id == self._end_node.id
        else:
            return True if node.name.endswith("end_node") else False 

    def is_executable_action(self, node: BaseAction) -> bool:
        return node.__class__.__name__ in EXECUTABLE_ACTIONS

    def step(self, seed: Optional[int] = None, edge_name_pref: Optional[str] = None) -> Optional["BaseAction"]:
        """
        Depth-first walk along one path:
        - Start from _start_node if traversal not initialized.
        - At each step, pick exactly one outgoing edge.
          * If multiple exist, choose randomly.
        - Return the next *executable* action (including the end_node).
        - Stop when _end_node is reached.
        """
        if not hasattr(self, "_cur_node"):
            # first call
            if seed is not None:
                self._rng = random.Random(seed)
            else:
                self._rng = random.Random()
            self._cur_node = self._start_node

        # If we already finished, stop
        if self._cur_node is None:
            return None

        # Advance to the next node
        outgoing_nodes = self.outgoing(self._cur_node, edge_name_pref=edge_name_pref)
        if not outgoing_nodes:
            # dead end, stop traversal
            self._cur_node = None
            return None

        if len(outgoing_nodes) > 1:
            self._rng.shuffle(outgoing_nodes)

        # Pick the next branch
        self._cur_node = outgoing_nodes[0]

        # If end_node, return None and stop traversal afterwards
        if self.is_end_node(self._cur_node, strict=True):
            node = self._cur_node
            self._cur_node = None
            return node

        # Return if this is an executable action
        if self.is_executable_action(self._cur_node):
            return self._cur_node

        # If not executable (dummy, wrapper, etc.), recurse until we find one or end
        return self.step(seed=seed, edge_name_pref=edge_name_pref)

    def visualize_graph(self, filename: str = None, directory: str = ".", 
                  format: str = "pdf", view: bool = False,
                  vertical: bool = True, display_node_groups: bool = True):
        """
        Visualize the graph using GraphViz.
        Saves to a file and optionally opens it.
        """
        dot = self.build_dot(vertical=vertical, display_node_groups=display_node_groups)
        dot.render(
            filename=self.__class__.__name__ if filename is None else filename,          # base filename (no extension)
            directory=directory,
            format=format,
            view=view
        )