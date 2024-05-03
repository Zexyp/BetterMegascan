class NodeSpawner:
    def __init__(self, tree):
        self.tree = tree

    def create_generic_node(self, type, pos: tuple = None):
        node = self.tree.nodes.new(type=type)
        if pos:
            node.location = pos

        return node

    # order is from node input receiver to input provider node
    def connect_nodes(self, node_a, node_b, in_a: int | str = 0, out_b: int | str = 0):
        return self.tree.links.new(node_a.inputs[in_a], node_b.outputs[out_b])
