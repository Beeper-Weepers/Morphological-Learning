class Node:

    def __init__(self, par, depth, name):
        self.parent = par
        self.functions = []  # Consists of tuple (morph, meaning, node)
        # TODO: NOW THAT WE HAVE GRAPHVIZ, DEPTH IS OBSOLETE
        self.depth = depth
        self.name = name

    def addFunction(self, morph, meaning, n):
        self.functions.append([morph, meaning, n])

    def getRecFunc(self):
        return self.functions[len(self.functions) - 1]

    def getParent(self):
        return self.parent


# Transducer is composed of Nodes
class Transducer:

    # Dummy Constructor
    def __init__(self):
        self.leaves = []
        self.branches = []
        self.depth = 0
        self.count = 0
        self.root = Node(None, 0, str(self.count))
        self.count += 1  # For the root node

    def findMatchingNode(self, morpheme, list):
        for i in range(0, len(list)):
            if morpheme == list[i][0]:  # Check Morpheme
                return list[i][2]  # Return Node
        return None

    def addPair(self, word, meaning):
        prevNode = self.root

        # Reserve a list that is used for comparison
        childrenList = prevNode.functions

        currentDepth = 1
        for p in word:
            matchingNode = self.findMatchingNode(p, childrenList)
            # Create a new node
            if matchingNode is None:
                nde = Node(prevNode, currentDepth, str(self.count))
                self.count += 1
                prevNode.addFunction(p, [], nde)
                prevNode = nde
                childrenList = prevNode.functions
            # Update childrenList reference to the match's child list
            else:
                childrenList = matchingNode.functions
                prevNode = matchingNode
            currentDepth += 1

        # Last Node Meaning Tack-On
        nde = Node(prevNode, currentDepth, str(self.count))
        self.count += 1
        prevNode.addFunction("", meaning.split(";"), nde)
        self.leaves.append(prevNode.getRecFunc())
        self.branches.append(prevNode)

        self.depth = max(self.depth, currentDepth)

    # Quasi-Determination Related

    def meaningPush(self, node, meaning):
        # Find function leading to cur. node, then assign cur. meaning to it
        for f in node.parent.functions:
            if f[2] == node:
                f[1] = meaning

        if node.parent.parent is not None:
            # Construction of meaning list
            lst = []
            for f in node.parent.functions:
                lst.append(set(f[1]))

            # Find intersection
            sect = list(lst.pop(0).intersection(*lst))

            # Remove intersections from functions
            for i in sect:
                for f in node.parent.functions:
                    f[1].remove(i)

            # Adding the intersection to the meaning, which is prop.ed downward
            meaning = sect

            # If commonality has something in it, keep propogating
            if meaning:
                self.meaningPush(node.parent, meaning)

    def quasiDetermine(self):
        # Sort the leaves into depth-decreasing order
        self.leaves.sort(key=lambda x: x[2].depth, reverse=True)

        # Propogate meanings down
        for l in self.leaves:
            self.meaningPush(l[2], l[1])
