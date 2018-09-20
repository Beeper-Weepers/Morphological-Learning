from tkinter import filedialog
import TransducerTree
import TreeDrawerGraphviz
from tkinter import Tk


def main():
    # Prompt for filename
    Tk().withdraw()
    trnFilePath = filedialog.askopenfilename()
    Tk().destroy()

    # Open provided file and take data from it
    try:
        trainFile = open(trnFilePath, "r")
    except IOError:
        exit()   # Silent Close
    trainFileContents = trainFile.readlines()
    trainFile.close()

    trans = TransducerTree.Transducer()

    # Split data and shunt to Transducer for real processing work
    for ln in trainFileContents:
        # Remove endline
        ln = ln.replace('\n', '')

        # Split into pair and feed to transducer
        if ln.strip() != "":
            tempPair = ln.split("\t")
            trans.addPair(tempPair[0], tempPair[1])

    # Quasi-Determinization
    trans.quasiDetermine()

    # Merge paradigms (Hay wrapper functions for performing min procs on paras)
    trans.mergeParadigms()

    # Minimization
    trans.mergeTails(trans.root)
    trans.morphemeBoundaries(trans.root)
    trans.removeAccOverlap(trans.root)

    # Draw Tree
    drawer = TreeDrawerGraphviz.TreeDrawer()
    drawer.drawTree(trans)


if __name__ == "__main__":
    main()
