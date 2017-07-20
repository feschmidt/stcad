import numpy as np
import gdsCAD as cad

class BaseChip():

    def __init__(self, l=6000, name = 'CHIP'):  # base layer: 6mm x 6mm

        self.length = l
        self.gridname = name
        self.layer_box = 0
        self.chip = cad.core.Layout(name)

    def base_chip(self):

        l = self.length
        grid = cad.core.Cell(self.gridname)
        box = cad.shapes.Box((-l/2,-l/2), (l/2,l/2), width = 50, layer = self.layer_box)
        grid.add(box)
        self.chip.add(grid)
        return self.chip

    def gen_full_array(self, padgroup, marker = True, vernier = True, testpads = True,
                    ebeam = True):

        # Merge objects into cells
        bottom = [cad.core.Cell('BOTTOM LAYER')] * 4
        bottom[0].add(padgroup[0]) 
        bottom[1] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=90)
        bottom[2] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=180)
        bottom[3] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=270)

        top = [cad.core.Cell('TOP LAYER')] * 4
        top[0].add(padgroup[1])
        top[1] = cad.core.CellReference(top[0], origin=(0,0),rotation=90)
        top[2] = cad.core.CellReference(top[0], origin=(0,0),rotation=180)
        top[3] = cad.core.CellReference(top[0], origin=(0,0),rotation=270)

        # Merge all cells
        maincell = cad.core.Cell('MAIN')
        maincell.add(bottom)
        maincell.add(top)
        
        # Alignment marks, verniers and test pads
        if marker:
            amarks = cad.templates.AlignmentMarks(('A','C'),(1,2))
            maincell.add(amarks)
        if vernier:
            verniers0 = cad.templates.Verniers(('A','B'),(1,2))
            verniers = cad.core.CellReference(verniers0).translate([-500,-500])
            maincell.add(verniers)
        if testpads:
            pads = self.bond_testpads()
            maincell.add(pads)
        if ebeam:
            emarks = self.ebpg_marker()
            maincell.add(emarks)

        # Create a layout and add the cell
        # Maybe this is the problem??
        self.layout = cad.core.Layout('LIBRARY')
        self.chip.add(maincell)
        return self.chip

    def bond_testpads(self, l = 300, w = 300):

        pads = cad.core.Cell('TESTPADS')
        l = 300     # l from above is instance. How to convert to int or float?
        w = 300
        s = 2100
        x = [s * xi for xi in [-1, 1, 1, -1]]
        y = [s * yi for yi in [-1, -1, 1, 1]]
        for i in range(len(x)):
            box = cad.shapes.Rectangle((x[i]-l/2,y[i]-l/2),(x[i]+l/2,y[i]+w/2), layer = 1)
            pads.add(box)
        return pads

    def ebpg_marker(self):

        marker = [cad.core.Cell('EBEAM')] * 4
        size = 20
        x = [-2000, -1800, -1800]
        y = [-1800, -1800, -2000]
        for i in range(len(x)):
            box = cad.shapes.Rectangle((x[i]-size/2,y[i]-size/2),
                                    (x[i]+size/2,y[i]+size/2), layer = 1)
            marker[0].add(box)
        marker[1] = cad.core.CellReference(marker[0], origin=(0,0),rotation=90)
        marker[2] = cad.core.CellReference(marker[0], origin=(0,0),rotation=180)
        marker[3] = cad.core.CellReference(marker[0], origin=(0,0),rotation=270)
        return marker

    def save_to_gds(self, chip, layout, name = 'testjunctions', save = True,
                    show = True):

        chip.add(layout)
        if save:
            chip.save(name + '.gds')
        if show:
            chip.save(name + '.png')
            chip.show()

