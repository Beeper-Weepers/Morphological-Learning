import tkinter as tk
import math


class TreeDrawer:
    w = 1024
    h = 768
    r = 16
    xl = 64  # Stands for X length
    yl = 156  # Stands for Y length

    def __init__(self):
        # Initializes a tkinter window ready for the transducer
        root = self.root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", exit)
        self.root.title("Transducer Visualizer")
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h)
        self.canvas.pack()
        # Center window (just another way Tkinter shows its clunkiness...)
        root.eval('tk::PlaceWindow %s center' %
                  root.winfo_pathname(root.winfo_id()))

    def createCircle(self, x, y):
        return self.canvas.create_oval(x-self.r, y-self.r, x+self.r, y+self.r,
                                       fill="white")

    def isBranch(self, node, tree):
        if node in tree.branches:
            return True
        return False

    def propogateNode(self, node, x, y, spacing, tree):
        sz = len(node.functions)
        i = 0

        # DepthMod causes the y dist to decrease between nodes as tree expands
        dep = tree.depth
        depthMod = max((dep - spacing), dep / 3.0) / dep
        depthMod **= 2.5

        # Add to spacing if the line isn't straight
        if sz > 1:
            spacing += 1

        for f in node.functions:
            # Calculate points of next node and arc flip
            xx = x + self.xl
            yy = y + (i * self.yl - (sz - 1) * self.yl / 2) * depthMod
            d = -10

            # Calculatees new final point on circumference of child circle
            baseAng = math.atan2(yy - y, xx - x)
            xn = xx - self.r * 1 * math.cos(baseAng)
            yn = yy - self.r * 1 * math.sin(baseAng)

            # Calculates perp. bisec. of the arc (as an intermediate point)
            # Could go without this if only basic lines and not arcs were used
            t = math.atan2(yn - y, xn - x)
            xC = (x + xn) / 2 + d * math.cos(t)
            yC = (y + yn) / 2 - d * math.sin(t)

            # Draw Arc
            self.canvas.create_line((x, y), (xC, yC), (xn, yn), smooth=True,
                                    arrow="last")
            # Draw morph + meaning text
            if y == yy:
                self.canvas.create_text(xC + 12, yC - 28,
                                        text=f[0]+":"+';'.join(f[1]),
                                        anchor="nw")
            else:
                self.canvas.create_text(xC + 6, yC - 8,
                                        text=f[0]+":"+';'.join(f[1]),
                                        anchor="w")

            # Recurse function
            self.propogateNode(f[2], xx, yy, spacing, tree)
            i += 1

        # Double circle for output nodes
        if self.isBranch(node, tree):
            self.r *= 1.1
            self.createCircle(x, y)
            self.r /= 1.1
        # Generate basic circle and morpheme text
        self.createCircle(x, y)

    # Calls the recursive function and initializes the main loop
    def drawTree(self, tree):
        # Draw root special box
        xp = self.r * 2
        yp = self.h / 2
        self.canvas.create_rectangle(xp - self.r, yp - self.r, xp + self.r,
                                     yp + self.r)
        # Call recursive drawing function (draws every node)
        self.propogateNode(tree.root, xp, yp, 0.0, tree)
        self.root.mainloop()
