import numpy as np
import gdsCAD as cad

class ShuntCavity():

    def __init__(self, name, dict_cavity):

        self.name = name
        self.dict_cavity = dict_cavity

        self.layer_bottom = 1
        self.layer_diel = 2
        self.layer_top = 3

        self.cell = cad.core.Cell('RF_CAVITY')

    def gen_cavities(self):

        length = self.dict_cavity['length']
        centerwidth = self.dict_cavity['centerwidth']
        gapwidth = self.dict_cavity['gapwidth']
        shunts = self.dict_cavity['shunts']
        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        holedim = self.dict_cavity['holedim']
        holemarker = self.dict_cavity['holemarker']

        launcherpoints = [(700, 8745+centerwidth/2),
                        (1900, 8745+centerwidth/2),
                        (3100, 8500+centerwidth/2),
                        (3100, 8500-centerwidth/2),
                        (1900, 8255-centerwidth/2),
                        (700, 8255-centerwidth/2)]
        launcher = cad.core.Boundary(launcherpoints)

        launcherleadpoints = [(3100, 8500+centerwidth/2),
                            (3406.2, 8500+centerwidth/2),
                            (3406.2, 8500-centerwidth/2),
                            (3100, 8500-centerwidth/2)]
        launcherlead = cad.core.Boundary(launcherleadpoints)

        shunt1_x1 = 3406.2
        shunt1_y1 = 8290
        shunt1_x2 = shunt1_x1 + 155
        shunt1_y2 = shunt1_y1 + 420
        shunt1_points = [(shunt1_x1, shunt1_y1),(shunt1_x2, shunt1_y2)]
        diel_dx = 47.5
        diel_dy = 120
        shunt1_diel_points = [(shunt1_x1-diel_dx, shunt1_y1-diel_dy),
                            (shunt1_x2+diel_dx, shunt1_y2+diel_dy)]
        shunt_dxy = 5      # 5um overlap
        shunt1_top_points = [(shunt1_x1-diel_dx-shunt_dxy, shunt1_y1-diel_dy-shunt_dxy),
                            (shunt1_x2+diel_dx+shunt_dxy, shunt1_y2+diel_dy+shunt_dxy)]
        shunt1 = cad.shapes.Rectangle(shunt1_points[0],shunt1_points[1])
        shunt1_diel = cad.shapes.Rectangle(shunt1_diel_points[0],shunt1_diel_points[1])
        shunt1_top = cad.shapes.Rectangle(shunt1_top_points[0],shunt1_top_points[1])


        shunt1_lead1_points = [(shunt1_x2,8500+centerwidth/2),
                            (4400, 8500+centerwidth/2),
                            (4400, 8500-centerwidth/2),
                            (shunt1_x2, 8500-centerwidth/2)]
        shunt1_lead1 = cad.core.Boundary(shunt1_lead1_points)


        self.cell.add(launcher)
        self.cell.add(launcherlead)
        self.cell.add(shunt1)
        self.cell.add(shunt1_lead1)


