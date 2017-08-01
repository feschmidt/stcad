import numpy as np
import gdsCAD as cad

class HangerCavity():
    '''
    Class for RF cavity hangers inductively coupled to a transmission feedline
    '''
    def __init__(self, name, dict_cavity):

        self.name = name
        self.dict_cavity = dict_cavity

        self.layer_bottom = 1

        self.cell = cad.core.Cell('RF_CAVITY')

        self.length = self.dict_cavity['length']
        self.couplinglength = self.dict_cavity['couplinglength']
        self.centerwidth = self.dict_cavity['centerwidth']
        self.gapwidth = self.dict_cavity['gapwidth']
        
        self.launchx = -4.9e3
        self.launchy = 3.5e3
        
        self.launchw = 500
        self.launchpad = 400
        self.taperl = 500
    
    
    def gen_full(self):
        
        launcher = self.gen_launcher()
        for i in range(len(launcher)):
            self.cell.add(launcher[i])
            
        feedline = self.gen_feedline()
        self.cell.add(feedline[0])
        self.cell.add(feedline[1])
        
        feedline_bottom = feedline[2]   # extract y-coordinate of bottom of feedline
        length0 = self.length
        for xx, length in enumerate([length0,length0-430,length0-830,length0-1.2e3]):
            hanger = self.gen_hanger(length,(-3.3e3+xx*1.8e3,feedline_bottom))
            for i in range(len(hanger)):
                self.cell.add(hanger[i])
        
        
    def gen_launcher(self, hor=True, feedwidth = 50, gapwidth = 25):
        """
        Generate launchers. If config==hor, it creates a horizontal feedline, if config==vert the launchers are at the top of the chip and the feedline bends down.
        """
        
        print 'Generating launchers'
        center_x = self.launchx
        center_y = self.launchy
        launchw = self.launchw
        launchpad = self.launchpad
        taperl = self.taperl
        
        launchgap = 200
        
        if hor==True:
            launchpoints_top = [(center_x,center_y),
                            (center_x,center_y+launchw/2),
                            (center_x+launchpad,center_y+launchw/2),
                            (center_x+launchpad+taperl,center_y+feedwidth/2),
                            (center_x+launchpad+taperl,center_y+feedwidth/2+gapwidth),
                            (center_x+launchpad,center_y+launchw/2+launchgap),
                            (center_x-launchgap,center_y+launchw/2+launchgap),
                            (center_x-launchgap,center_y)]
            launcher_top = cad.core.Boundary(launchpoints_top)
            launcher_bot = cad.utils.reflect(launcher_top,'x',origin=(0,center_y))
            launcher2_top = cad.utils.reflect(launcher_top,'y',origin=(0,0))
            launcher2_bot = cad.utils.reflect(launcher_bot,'y',origin=(0,0))
        
        return (launcher_top,launcher_bot,launcher2_top,launcher2_bot)
        
    
    def gen_feedline(self, feedwidth = 50, gapwidth = 25):
        """
        Generate feedline
        """
        
        print 'Generating feedline'
        center_x = self.launchx
        center_y = self.launchy
        launchpad = self.launchpad
        taperl = self.taperl
            
        feedpoints = [(center_x+launchpad+taperl,center_y+feedwidth/2+gapwidth),
                    (-(center_x+launchpad+taperl),center_y+feedwidth/2+gapwidth),
                    (-(center_x+launchpad+taperl),center_y+feedwidth/2),
                    (center_x+launchpad+taperl,center_y+feedwidth/2)]
        feedline1 = cad.core.Boundary(feedpoints)
        feedline2 = cad.utils.reflect(feedline1,'x',origin=(0,center_y))
        
        return (feedline1,feedline2,center_y-feedwidth/2-gapwidth)
    
    
    def gen_hanger(self, length, pos, couplinglength = 610, couplinggap = 10, centerwidth = 4, gapwidth = 20, radius = 100):
        """
        Generate hanger of length=length at pos=(x0,y1) with inductive coupling
        """
        
        print 'Generating hanger of length ' + str(length)
        x0 = pos[0]
        y0 = pos[1] - couplinggap
        radius_hanger = radius - gapwidth - centerwidth/2
        restlength = length - couplinglength - 2*np.pi*radius_hanger/4
         
        hangerpoints_1 = [(x0,y0),
                        (x0 + couplinglength,y0),
                        (x0 + couplinglength,y0-gapwidth),
                        (x0, y0-gapwidth)]
        hangerpoints_2 = [(x0 + couplinglength + radius, y0 - radius),
                        (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                        (x0+couplinglength+radius-2*gapwidth-centerwidth,y0-radius-restlength-gapwidth),
                        (x0+couplinglength+radius-2*gapwidth-centerwidth,y0-radius),
                        (x0+couplinglength+radius-gapwidth-centerwidth,y0-radius),
                        (x0+couplinglength+radius-gapwidth-centerwidth,y0-radius-restlength),
                        (x0+couplinglength+radius-gapwidth,y0-radius-restlength),
                        (x0+couplinglength+radius-gapwidth,y0-radius)]
        hanger1 = cad.core.Boundary(hangerpoints_1)
        hanger2 = cad.core.Boundary(hangerpoints_2)
        hanger3 = cad.utils.reflect(hanger1,'x',origin=(0,y0-gapwidth-centerwidth/2))
        
        radius1 = radius                
        curve1 = cad.shapes.Disk((x0+couplinglength,y0-radius1), radius=radius, inner_radius=radius1-gapwidth, initial_angle=90,final_angle=0)
        
        radius2 = radius-gapwidth-centerwidth
        curve2 = cad.shapes.Disk((x0+couplinglength,y0-gapwidth-centerwidth-radius2), radius=radius2, inner_radius=radius2-gapwidth, initial_angle=90,final_angle=0)
            
        return (hanger1,hanger2,hanger3,curve1,curve2)
        
    '''
        
        
        
        
        self.shuntheight = 420
        self.shuntlength = 155
        self.top_dx = 32.5
        self.top_dy = 106
        self.diel_dxy = 5 

        self.r0 = 150
        self.top_cv = 8350
        self.bot_cv = 7600 #7594
        # bot_cv should be the main variable depending on length of cavity. However, for this
        # we need to restructure the creation of the meandering

    # gen_full with two gen_cavity, each with own centerwidth
    # afterwards add elements in gen_full
    def gen_full(self):
        """
        First creates the center conductor with gapwidth = 0
        Second creates the space around the conductor, finite gapwidth
        Add everything together. Finally, in LayoutBeamer do P-XOR
        """

        cavity_nogap = self.gen_cavities(gapwidth=0)
        cavity_gap = self.gen_cavities(gapwidth=self.gapwidth)

        for cavity in [cavity_nogap, cavity_gap]:
            for i in range(len(cavity)):
                self.cell.add(cavity[i])

    def gen_cavities(self,gapwidth=0):
        

        length = self.length
        centerwidth = self.centerwidth + 2*gapwidth
        shunts = self.shunts

        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        center = self.center

        # Create first launcher
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend
        if gapwidth!=0:
            x1_launcher = 0#-500
            y1_launcher = 230
        else:
            x1_launcher = 700
            y1_launcher = 0  

        launcherpoints = [(x1_launcher, center+(launcherwidth+centerwidth)/2+y1_launcher),
                        (1900, center+(launcherwidth+centerwidth)/2+y1_launcher),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2-y1_launcher),
                        (x1_launcher, center-(launcherwidth+centerwidth)/2-y1_launcher)]
        launcher = cad.core.Boundary(launcherpoints)

        # Create first shunt
        shunt1 = self.gen_shunt((llstart,self.llength),0,gap=gapwidth)

        # Cavity length starts here
        startx0 = shunt1[5]
        stopx0 = startx0 + self.dict_cavity['lead1']-gapwidth
        
        shunt1_cavity_points = [(startx0,center),(stopx0,center)]
        start_cavity = cad.core.Path(shunt1_cavity_points,centerwidth)

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
        
        # Calculate cavity length
        A = (stopx0-startx0) + 2*np.pi*r0 * 2 + (top_cv-bot_cv) * 4
        endx0 = stopx0+r0*8
        endx = length - (A - endx0) - gapwidth
        # without any curves: cav_straight = endx - startx0
        
        # Do the wiggles
        curve1 = cad.shapes.Disk((stopx0,top_cv),radius,inner_radius=inner_radius,initial_angle=90,
            final_angle=0)
        curve1_lead = cad.core.Path([(stopx0+r0, top_cv),(stopx0+r0,bot_cv)],centerwidth)
        curve2 = cad.shapes.Disk((stopx0+r0*2,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve2_lead = cad.core.Path([(stopx0+r0*3,bot_cv),(stopx0+r0*3,top_cv)],centerwidth)
        curve3 = cad.shapes.Disk((stopx0+r0*4,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=0)
        curve3_lead = cad.core.Path([(stopx0+r0*5,top_cv),(stopx0+r0*5,bot_cv)],centerwidth)
        curve4 = cad.shapes.Disk((stopx0+r0*6,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve4_lead = cad.core.Path([(stopx0+r0*7,bot_cv),(stopx0+r0*7,top_cv)],centerwidth)
        curve5 = cad.shapes.Disk((endx0,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=90)
        final_lead = cad.core.Path([(endx0,center),(endx,center)],centerwidth)

        # Create hole at the end
        holex0 = endx
        holedim = self.holedim
        holemarker = self.holemarker
        if gapwidth!=0:
            # Add hole for gJJ
            gJJ_box = cad.shapes.Rectangle((holex0, center-holedim[1]/2),(holex0+holedim[0],center+holedim[1]/2))
            # Add marker for gJJ
            if holemarker == True:
                gJJ_marker = cad.core.Cell('gJJ_marker')
                box1=cad.shapes.Rectangle((holex0+5,center+40),(holex0+10,center+45))
                box2=cad.shapes.Rectangle((holex0+10,center+35),(holex0+15,center+40))
                gJJ_marker.add(box1)
                gJJ_marker.add(box2)
                gJJ_marker.add(cad.utils.reflect(box1,'x',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box2,'x',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box1,'y',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box2,'y',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.rotate(box1,180,center=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.rotate(box2,180,center=(holex0+holedim[0]/2,center)))
        endhole = holex0+holedim[0]

        # Create second shunt (optional)
        if shunts==2:
            leadout = 125
            shunt2 = self.gen_shunt((endhole,70),leadout,gap=gapwidth)
            self.endshunt = shunt2[5]
        else:
            self.endshunt = endhole
        
        # Create second launcher
        launcher2 = cad.utils.reflect(launcher,'y',origin=(5e3,5e3))
        holex0 = endx
        holedim = self.holedim
        launcher2 = cad.utils.translate(launcher2,(self.endshunt-(10e3-llstart),0))   
        # For future: fix second shunt. For length adjustments make meandering longer or shorter,
        # and center it. For now this is sufficient.
        
        # Create cavity
        cavity1 = [cad.core.Elements()] * 3
        # Add all elements with layer 1
        for toadd in [launcher, shunt1[0], shunt1[1], shunt1[4],
                    start_cavity, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead,
                    launcher2]:
            toadd.layer = self.layer_bottom
            cavity1[0].add(toadd)

        # Complete shunt
        if gapwidth == 0:    
            # Add all elements with layer 2
            for toadd in [shunt1[2]]:
                toadd.layer = self.layer_diel
                cavity1[1].add(toadd)

            # Add all elements with layer 3
            for toadd in [shunt1[3]]:
                toadd.layer = self.layer_top
                cavity1[2].add(toadd)

        # Add second shunt (optional)
        if shunts==2:
            for toadd in [shunt2[0], shunt2[1], shunt2[4]]:
                toadd.layer = self.layer_bottom
                cavity1[0].add(toadd)
            if gapwidth == 0:
                for toadd in [shunt2[2]]:
                    toadd.layer = self.layer_diel
                    cavity1[0].add(toadd)
                for toadd in [shunt2[3]]:
                    toadd.layer = self.layer_top
                    cavity1[0].add(toadd)

        # Add hole and marker for graphene
        if gapwidth != 0:
            cavity1[0].add(gJJ_box)
            if holemarker == True:
                for toadd in gJJ_marker:
                    gJJ_marker.layer = self.layer_bottom
                    cavity1[0].add(toadd)
                # gJJ marker are missing from cavity2 ??
        
        
        # Create second cavity as mirrored version of first one
        cavity2 = [cad.utils.reflect(cavity1[i],'x',origin=(5e3,5e3)) for i in range(len(cavity1))]
        
        return (cavity1, cavity2)
        

    def gen_shunt(self,leadin,leadout,gap=0):
        
        # Connect in to shunt
        startx_in = leadin[0]   # x-coordinate
        stopx_in = startx_in+leadin[1]-gap
        leadpoints_in = [(startx_in, self.center),(stopx_in,self.center)]
        lead_in = cad.core.Path(leadpoints_in,self.centerwidth+2*gap)

        # Create shunt
        shuntheight = self.shuntheight + 2*gap
        shuntlength = self.shuntlength + 2*gap
        shunt_x1 = stopx_in
        shunt_y1 = self.center - shuntheight/2
        shunt_x2 = shunt_x1 + shuntlength
        shunt_y2 = shunt_y1 + shuntheight
        shunt_points = [(shunt_x1, shunt_y1),(shunt_x2, shunt_y2)]

        top_dx = self.top_dx
        top_dy = self.top_dy
        shunt_top_points = [(shunt_x1-top_dx, shunt_y1-top_dy),
                            (shunt_x2+top_dx, shunt_y2+top_dy)]

        diel_dxy = self.diel_dxy
        shunt_diel_points = [(shunt_x1-top_dx-diel_dxy, shunt_y1-top_dy-diel_dxy),
                            (shunt_x2+top_dx+diel_dxy, shunt_y2+top_dy+diel_dxy)]
        
        shunt = cad.shapes.Rectangle(shunt_points[0],shunt_points[1])
        shunt_diel = cad.shapes.Rectangle(shunt_diel_points[0],shunt_diel_points[1])
        shunt_top = cad.shapes.Rectangle(shunt_top_points[0],shunt_top_points[1])

        # Connect shunt to out
        startx_out = shunt_x2
        stopx_out = startx_out + leadout
        leadpoints_out = [(startx_out, self.center),(stopx_out,self.center)]
        lead_out = cad.core.Path(leadpoints_out,self.centerwidth+2*gap)

        return (lead_in, shunt, shunt_diel, shunt_top, lead_out, stopx_out)

    '''

