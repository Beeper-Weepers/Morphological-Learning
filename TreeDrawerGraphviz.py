from graphviz import Digraph


class TreeDrawer:
    def __init__(self):
        self.gra = Digraph(name='Transducer Visualizer')
        self.gra.edge_attr.update(arrowhead='vee', arrowsize='1')

    def propogateNode(self, node, tree):
        self.gra.node(node.name, node.name)
        self.gra.edge(node.parent.name, node.name, constraint='false')
        for x in node.functions:
            self.propogateNode(x[2], tree)

    def drawTree(self, tree):
        self.gra.node(tree.root.name, tree.root.name)
        for x in tree.root.functions:
            self.propogateNode(x[2], tree)
        self.gra.render('Output/TransducerVisualizer.gv', view=True)
