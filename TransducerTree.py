from itertools import combinations


class Node:

    def __init__(self, par, depth, name):
        self.parent = par
        self.functions = []  # Consists of list (morph, meaning, node)
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

    # MINIMIZATION RELATED

    # Merge-Tail Minimization Related

    # Recursive function used to populate a list with node segements
    # Also deletes null morphemes
    def gatherSegments(self, n, lst):
        if len(n.functions) >= 2:
            lst.append(n)
        elif not n.functions:
            # Check if parent function is null
            toAppend = n
            for i in range(len(n.parent.functions)):
                if (n.parent.functions[i][2] == n and
                        n.parent.functions[i][0] == "" and
                        not n.parent.functions[i][1]):
                    # If so, delete and assign parent to lst
                    toAppend = n.parent
                    del n.parent.functions[i]
                    del n
            lst.append(toAppend)
            return
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
                if not (s1.functions[i][0] == s2.functions[i][0] and
                        s1.functions[i][1] == s2.functions[i][1]):
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
        i1Range = range(len(segmLst) - 1)
        for i1 in i1Range:
            i2Range = range(i1 + 1, len(segmLst))  # Look into it self checking
            for i2 in i2Range:
                s1 = segmLst[i1]
                s2 = segmLst[i2]
                # Check for congruency
                if s1 != s2 and self.areCongruent(s1, s2):
                    # Delete one of the branches and reassign functions
                    par = s2.parent  # Unsure about parent stability
                    self.purgeTails(s2)
                    parRng = range(len(par.functions))
                    for x in parRng:
                        inst = par.functions[x][2]
                        del inst
                        if par.functions[x][2] == s2:
                            par.functions[x][2] = s1

    # Introducing morpheme boudaries (node-function minimization)

    def morphemeBoundaries(self, n):
        for f in n.functions:
            cur = f[2]
            while len(cur.functions) == 1:
                nextCur = cur.functions[0][2]
                f[0] += cur.functions[0][0]
                f[2] = nextCur
                del cur
                cur = nextCur

        for f in n.functions:
            self.morphemeBoundaries(f[2])

    # Removes accidental or partial overlap in form

    def removeAccOverlap(self, n):
        merged = False
        for i in range(len(n.functions)):
            f = n.functions[i]
            if not f[1]:
                merged = True
                morphBase = f[0]

                # Append child node functions to node
                for fc in f[2].functions:  # Function child loop
                    n.functions.insert(0, [morphBase + fc[0], fc[1], fc[2]])
                    i += 1
                # Clean up and delete
                inst = n.functions[i][2]
                del inst
                n.functions.pop(i)
                i -= 1
        if merged:
            self.removeAccOverlap(n)
        else:
            for f in n.functions:
                self.removeAccOverlap(f[2])

    # Modified prefix-segmenting quasi-determination

    # Helper function to assist with morpheme intersections

    def findIntersection(self, strList):
        maxRange = range(len(min(strList, key=len)))
        for i in maxRange:
            if not all(st[i] == strList[0][i] for st in strList):
                return i - 1
        return i

    # Main function of prefix segmenting

    def prefixDetermine(self):

        # Meaning grouping

        meaningLst = []  # each item in format [[INTSEC], [FUNCS], [POSITIONS]]

        funcSz = len(self.root.functions)
        rtfs = self.root.functions
        # Function comparison level (over all functions in root)
        for f1 in range(0, funcSz - 1):

            # Get meaning combinations (may be bad because iterable conversion)
            meanCombs = []  # Meaning combinations
            meanLast = len(rtfs[f1][1])
            for x in range(meanLast, 0, -1):
                tempCombos = combinations(rtfs[f1][1], x)
                for y in tempCombos:
                    meanCombs.append(list(y))

            for f2 in range(f1 + 1, funcSz):
                for m in meanCombs:

                    # Checking if the meaning + f2 already exists in an item
                    alreadyPres = False
                    for tI in meaningLst:
                        if tI[0] == m and rtfs[f2] in tI[1]:
                            alreadyPres = True
                            break
                    if alreadyPres:
                        continue

                    poses = []
                    # Subset check
                    comboSz = 0
                    for m1 in m:
                        comboSz += 1
                        for m2 in range(0, len(rtfs[f2][1])):
                            if m1 == rtfs[f2][1][m2]:
                                poses.append(m2)
                                break
                    # Checking if the subset exists and then deletion
                    if comboSz == len(poses):
                        # Check if this intersection is in [x][1] of meaningLst
                        found = False
                        for x in meaningLst:
                            if m == x[0]:
                                x[1].append(rtfs[f2])
                                found = True
                                break
                        # If not, create a new intersection category
                        if not found:
                            meaningLst.append([m, [rtfs[f1], rtfs[f2]]])

        # print(*meaningLst)

        # Morpheme extraction based on meaning

        for group in meaningLst:
            # Build a "basket" for morphemes and then a basket for rt functions
            morphLst = []
            for s in group[1]:
                morphLst.append(s[0])

            # Grab an intersection
            intersectIndex = self.findIntersection(morphLst) + 1

            # If no intersection, don't do anything
            if intersectIndex == 0:
                continue

            # Create new node
            nde = Node(self.root, 1, str(self.count))
            self.count += 1

            # Give node new functions
            for func in group[1]:
                for meaning in group[0]:
                    func[1].remove(meaning)
                nde.addFunction(func[0][intersectIndex:], func[1], func[2])

            # Delete old nodes from root
            fI = 0
            while fI < len(rtfs):
                try:
                    fun = rtfs[fI]
                    val = group[1].index(fun)
                    del rtfs[fI]
                    del group[1][val]
                except ValueError:
                    fI += 1
                    pass

            # Connect the new node to the root
            self.root.addFunction(morphLst[0][:intersectIndex], group[0], nde)

        pass
