class Node:

    def __init__(self, par, depth, name):
        self.parent = par
        self.functions = []  # Consists of tuple (morph, meaning, node)
        # TODO: NOW THAT WE HAVE GRAPHVIZ, DEPTH IS OBSOLETE
        self.depth = depth
        self.name = name

    def addFunction(self, morph, meaning, n):
        self.functions.append([morph, meaning, n])

    # Get most recent function
    def getRecFunc(self):
        return self.functions[len(self.functions) - 1]

    def getParent(self):
        return self.parent


# Transducer is composed of Nodes
class Transducer:

    def __init__(self):
        self.leaves = []
        self.branches = []
        self.depth = 0
        self.count = 0
        self.root = Node(None, 0, str(self.count))
        self.count += 1  # For the root node

    # Used to find the [2] portion of a node func. where [0] and [1] are known
    def findMatchingNode(self, morpheme, list):
        for i in range(0, len(list)):
            if morpheme == list[i][0]:  # Check Morpheme
                return list[i][2]  # Return Node
        return None

    # Productive simple p.-subseq. construction function
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

    # Recursive function used to push meanings back for quasi-determinization
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

    # Productive function used to quasi-determine a p.-subseq. transducer
    def quasiDetermine(self):
        # Sort the leaves into depth-decreasing order
        self.leaves.sort(key=lambda x: x[2].depth, reverse=True)

        # Propogate meanings down
        for l in self.leaves:
            self.meaningPush(l[2], l[1])

    # Merge-Tail Minimization Related

    # Recursive function used to populate a list with node segements
    def gatherSegments(self, n, lst):
        if len(n.functions) >= 2:
            lst.append(n)
        for f in n.functions:
            self.gatherSegments(f[2], lst)

    # Recursive function used to check tail congruency
    def areCongruent(self, s1, s2):
        s1FLen = len(s1.functions)

        # Function lists must be same length
        if s1FLen == len(s2.functions):
            # Terminating procedure conditional
            if s1FLen == 0:
                return True

            # Congruency check
            for i in range(0, s1FLen):
                if (s1.functions[i][0] == s2.functions[i][0] and
                        s1.functions[i][1] == s2.functions[i][1]):
                    pass
                else:
                    return False
        else:
            return False

        # If congruency succeeds, then recurse the function onto children nodes
        for i in range(0, s1FLen):
            if not self.areCongruent(s1.functions[i][2], s2.functions[i][2]):
                return False

        return True

    def purgeTails(self, node):
        for f in node.functions:
            self.purgeTails(f[2])
        del node.functions[:]
        del node

    # Productive function used to merge all congruent tails in an FSM
    def mergeTails(self):
        # Segment List
        segmLst = []

        # Gather all the segmenting nodes (besides the first one)
        curN = self.root
        while len(curN.functions) < 2:
            curN = curN.functions[0][2]

        for f in curN.functions:
            self.gatherSegments(f[2], segmLst)

        # Check for trail congruency among segments
        for s1 in segmLst:
            for s2 in segmLst:
                # Check for congruency
                if s1 != s2 and self.areCongruent(s1, s2):
                    # Delete one of the branches and reassign functions
                    par = s2.parent
                    self.purgeTails(s2)
                    for x in range(len(par.functions)):
                        if par.functions[x][2] == s2:
                            par.functions[x][2] = s1
                            print(s1.name)
                            print(s2.name)
                    return
