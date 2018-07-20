from graphviz import Digraph


class TreeDrawer:
    def __init__(self):
        self.gra = Digraph(name='Transducer Visualizer')
        self.gra.edge_attr.update(arrowhead='vee', arrowsize='1')
        self.gra.attr(rankdir='LR')
        self.nodeList = []

    def isBranch(self, node, tree):
        if node in tree.branches:
            return True
        return False

    def propogateNode(self, node, tree):
        if self.isBranch(node, tree):
            self.gra.node(node.name, node.name, shape='doublecircle')
        else:
            self.gra.node(node.name, node.name, shape='circle')
        self.nodeList.append(node.name)
        for f in node.functions:
            if f[0] == "" or not f[1]:
                connec = ""
            else:
                connec = " : "
            if f[2].name not in self.nodeList:
                self.propogateNode(f[2], tree)
            self.gra.edge(node.name, f[2].name,
                          label=f[0] + connec + ';'.join(f[1]))

    def drawTree(self, tree):
        self.gra.node(tree.root.name, tree.root.name, shape='doubleoctagon')
        self.propogateNode(tree.root, tree)
        self.gra.view()
