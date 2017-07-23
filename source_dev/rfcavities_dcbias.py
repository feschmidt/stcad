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

        self.length = self.dict_cavity['length']
        self.centerwidth = self.dict_cavity['centerwidth']
        self.gapwidth = self.dict_cavity['gapwidth']
        self.shunts = self.dict_cavity['shunts']
        self.holedim = self.dict_cavity['holedim']
        self.holemarker = self.dict_cavity['holemarker']

        self.center = 8500
        self.launcherwidth = 490
        self.llstart = 3100     # x coordinate of launcher lead start
        self.llend = 3400       # x coordinate of launcher lead end
        self.shuntheight = 420
        self.shuntlength = 155
        self.r0 = 150
        self.top_cv = 8350
        self.bot_cv = 7594

    def gen_cavities(self):

        length = self.length
        centerwidth = self.centerwidth
        gapwidth = self.gapwidth
        shunts = self.shunts

        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        center = self.center
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend      
        launcherpoints = [(700, center+(launcherwidth+centerwidth)/2),
                        (1900, center+(launcherwidth+centerwidth)/2),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2),
                        (700, center-(launcherwidth+centerwidth)/2)]
        launcher = cad.core.Boundary(launcherpoints)

        launcherleadpoints = [(llstart, center),(llend,center)]
        launcherlead = cad.core.Path(launcherleadpoints,centerwidth)

        shunt1_x1 = llend
        shuntheight = self.shuntheight
        shuntlength = self.shuntlength
        shunt1_y1 = center-shuntheight/2
        shunt1_x2 = shunt1_x1 + shuntlength
        shunt1_y2 = shunt1_y1 + shuntheight
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

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
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

        
        # Create cavity
        cavity1 = [cad.core.Elements()] * 3
        # Add all elements with layer 1
        for toadd in [launcher, launcherlead, shunt1, shunt1_lead1, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead]:
            toadd.layer = self.layer_bottom
            cavity1[0].add(toadd)

        # Add all elements with layer 2
        for toadd in [shunt1_diel]:
            toadd.layer = self.layer_diel
            #cavity1[1].add(toadd)

        # Add all elements with layer 3
        for toadd in [shunt1_top]:
            toadd.layer = self.layer_top
            #cavity1[2].add(toadd)
        
        # Create second cavity as mirrored versio of first one
        cavity2 = [cad.utils.reflect(cavity1[i],'x',origin=(5000,5000)) for i in range(3)]
        
        self.cell.add(cavity1[0])
        self.cell.add(cavity2[0])
        
    
    def gen_full(self):

        length = self.length
        centerwidth = self.centerwidth + 2*self.gapwidth
        gapwidth = self.gapwidth
        shunts = self.shunts

        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        center = self.center
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend      
        launcherpoints = [(0, center+(launcherwidth+centerwidth)/2+230),
                        (1900, center+(launcherwidth+centerwidth)/2+230),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2-230),
                        (0, center-(launcherwidth+centerwidth)/2-230)]
        launcher = cad.core.Boundary(launcherpoints)

        launcherleadpoints = [(llstart, center),(llend - self.gapwidth,center)]
        launcherlead = cad.core.Path(launcherleadpoints,centerwidth)

        shuntheight = self.shuntheight + 2*self.gapwidth
        shuntlength = self.shuntlength + 2*self.gapwidth
        shunt1_x1 = llend - self.gapwidth
        shunt1_y1 = center - shuntheight/2
        shunt1_x2 = shunt1_x1 + shuntlength
        shunt1_y2 = shunt1_y1 + shuntheight
        shunt1_points = [(shunt1_x1, shunt1_y1),(shunt1_x2, shunt1_y2)]
        
        shunt1 = cad.shapes.Rectangle(shunt1_points[0],shunt1_points[1])

        # Cavity length starts here
        startx0 = self.dict_cavity['startx0']      # originally 4400
        if startx0 < shunt1_x2:
            raise ValueError('End of shunt: ' + str(shunt1_x2),
                'Begin of cavity: ' + str(startx0),
                'Cavity cannot begin before end of shunt!')
        shunt1_lead1_points = [(shunt1_x2,center),(startx0,center)]
        shunt1_lead1 = cad.core.Path(shunt1_lead1_points,centerwidth)

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
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
        final_lead = cad.core.Path([(endx0,center),(endx - self.gapwidth,center)],centerwidth)

        # Add hole for gJJ
        holex0 = endx - self.gapwidth
        holedim = self.holedim
        holemarker = self.holemarker
        gJJ_box = cad.shapes.Rectangle((holex0, center-holedim[1]/2),(holex0+holedim[0],center+holedim[1]/2))
        if holemarker == True:
            gJJ_marker = [cad.core.Elements()] * 4
            #for i in range(2):
            box1 = cad.shapes.Rectangle((holex0+5,center+40),(holex0+10,center+45))
            box2 = cad.shapes.Rectangle((holex0+10,center+35),(holex0+15,center+40))
            gJJ_marker[0].add(box1)
            gJJ_marker[0].add(box2)
            gJJ_marker[1] = cad.utils.reflect(gJJ_marker[0],'x',origin=(holex0+holedim[0]/2,center))
            gJJ_marker[2] = cad.utils.reflect(gJJ_marker[0],'y',origin=(holex0+holedim[0]/2,center))
            gJJ_marker[3] = cad.utils.reflect(gJJ_marker[1],'y',origin=(holex0+holedim[0]/2,center))

        # Create cavity
        cavity1 = cad.core.Elements()
        # Add all elements with layer 1
        for toadd in [launcher, launcherlead, shunt1, shunt1_lead1, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead,
                    gJJ_box, gJJ_marker[0], gJJ_marker[1], gJJ_marker[2], gJJ_marker[3]]:
            toadd.layer = self.layer_bottom
            cavity1.add(toadd)
        
        # Create second cavity as mirrored versio of first one
        cavity2 = cad.utils.reflect(cavity1,'x',origin=(5000,5000))
        
        self.cell.add(cavity1)
        self.cell.add(cavity2)
    

