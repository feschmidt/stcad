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

        center = 8500
        launcherpoints = [(700, 8745+centerwidth/2),
                        (1900, 8745+centerwidth/2),
                        (3100, center+centerwidth/2),
                        (3100, center-centerwidth/2),
                        (1900, 8255-centerwidth/2),
                        (700, 8255-centerwidth/2)]
        launcher = cad.core.Boundary(launcherpoints)

        launcherleadpoints = [(3100, center),(3406.2,center)]
        launcherlead = cad.core.Path(launcherleadpoints,centerwidth)

        shunt1_x1 = 3406.2
        shunt1_y1 = 8290
        shunt1_x2 = shunt1_x1 + 155
        shunt1_y2 = shunt1_y1 + 420
        shunt1_points = [(shunt1_x1, shunt1_y1),(shunt1_x2, shunt1_y2)]

        top_dx = 32.5
        top_dy = 106
        shunt1_top_points = [(shunt1_x1-top_dx, shunt1_y1-top_dy),
                            (shunt1_x2+top_dx, shunt1_y2+top_dy)]

        diel_dxy = 5      # 5um overlap
        shunt1_diel_points = [(shunt1_x1-top_dx-diel_dxy, shunt1_y1-top_dy-diel_dxy),
                            (shunt1_x2+top_dx+diel_dxy, shunt1_y2+top_dy+diel_dxy)]
        
        shunt1 = cad.shapes.Rectangle(shunt1_points[0],shunt1_points[1])
        shunt1_diel = cad.shapes.Rectangle(shunt1_diel_points[0],shunt1_diel_points[1])
        shunt1_top = cad.shapes.Rectangle(shunt1_top_points[0],shunt1_top_points[1])

        # Cavity length starts here
        startx0 = self.dict_cavity['startx0']      # originally 4400
        if startx0 < shunt1_x2:
            raise ValueError('End of shunt: ' + str(shunt1_x2),
                'Begin of cavity: ' + str(startx0),
                'Cavity cannot begin before end of shunt!')
        shunt1_lead1_points = [(shunt1_x2,center),(startx0,center)]
        shunt1_lead1 = cad.core.Path(shunt1_lead1_points,centerwidth)

        r0 = 150
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = 8350
        bot_cv = 7594
        #end = 6820
        #base_length = (startx0-shunt1_x2) + 2*np.pi*r0 * 2 + (top_cv-bot_cv) * 4 + (end-5600)
        #print base_length
        A = (startx0-shunt1_x2) + 2*np.pi*r0 * 2 + (top_cv-bot_cv) * 4
        endx0 = startx0+r0*8
        endx = length - (A - endx0)

        curve1 = cad.shapes.Disk((startx0,top_cv),radius,inner_radius=inner_radius,initial_angle=90,
            final_angle=0)
        curve1_lead = cad.core.Path([(startx0+r0, top_cv),(startx0+r0,bot_cv)],centerwidth)
        curve2 = cad.shapes.Disk((startx0+r0*2,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve2_lead = cad.core.Path([(startx0+r0*3,bot_cv),(startx0+r0*3,top_cv)],centerwidth)
        curve3 = cad.shapes.Disk((startx0+r0*4,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=0)
        curve3_lead = cad.core.Path([(startx0+r0*5,top_cv),(startx0+r0*5,bot_cv)],centerwidth)
        curve4 = cad.shapes.Disk((startx0+r0*6,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve4_lead = cad.core.Path([(startx0+r0*7,bot_cv),(startx0+r0*7,top_cv)],centerwidth)
        curve5 = cad.shapes.Disk((endx0,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=90)
        final_lead = cad.core.Path([(endx0,center),(endx,center)],centerwidth)

        # Add all elements with layer 1
        for toadd in [launcher, launcherlead, shunt1, shunt1_lead1, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead]:
            toadd.layer = 1
            self.cell.add(toadd)

        # Add all elements with layer 2
        for toadd in [shunt1_diel]:
            toadd.layer = 2
            self.cell.add(toadd)

        # Add all elements with layer 3
        for toadd in [shunt1_top]:
            toadd.layer = 3
            self.cell.add(toadd)

        '''
        # Create second cavity
        # Doesn't work: RuntimeError: maximum recursion depth exceeded while calling a Python object
        cavity1 = self.cell
        cavity2 = cad.core.CellReference(cavity1,x_reflection=False)
        self.cell.add(cavity2)
        '''
        '''
        # Create second cavity
        # Doesn't work: ValueError: operands could not be broadcast together with shapes (16) (2)
        cavity1 = self.cell
        cavity2 = cad.utils.reflect(cavity1, 'x', origin=(5000,5000))
        self.cell.add(cavity2)
        '''




