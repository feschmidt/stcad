import numpy as np
import gdsCAD as cad
from . import utilities as utils


class Feedline():
    """
    Class for RF transmission feedline
    """

    def __init__(self, name, dict_feedline, feedline=True):

        self.name = name

        self.lf_spacing = 500.
        self.launchw = 500.
        self.launchl = 400.
        self.taperl = 500.

        self.launchgapx = 400
        self.launchgapy = 200

        self.feedline = feedline    # additional option to omit feedlines if set to False

        for key,val in list(dict_feedline.items()):
            setattr(self,key,val)

    def gen_feedline(self,left=True,right=True):

        self.main_cell = cad.core.Cell('MAIN CELL')
        self.cell = cad.core.Cell('RF_FEED')

        if self.curved == True:
            feedline_cpw = self.gen_curved_feeline()
            launcher1 = self.put_launcher((-self.length / 2. - self.feedwidth / 2,
                                           self.lf_spacing + self.feedwidth / 2.), 'down')
            launcher2 = self.put_launcher((self.length / 2. + self.feedwidth / 2,
                                           self.lf_spacing + self.feedwidth / 2.), 'down')

        else:
            feedline_cpw = self.gen_cpw_feedline()
            launcher1 = self.put_launcher((-self.length / 2., 0), 'right')
            launcher2 = self.put_launcher((self.length / 2., 0), 'left')

        if self.feedline:
            self.cell.add(feedline_cpw)
        if left:
            self.cell.add(launcher1)
        if right:
            self.cell.add(launcher2)



        if self.orientation == 'left':
            opper_cell = cad.core.CellReference(self.cell,rotation = -90)
            self.main_cell.add(opper_cell)

        elif self.orientation == 'right':
            opper_cell = cad.core.CellReference(self.cell,rotation = 90)
            self.main_cell.add(opper_cell)
       
        elif self.orientation == 'down':
            opper_cell = cad.core.CellReference(self.cell,rotation = 180)
            self.main_cell.add(opper_cell)

        else:
            self.main_cell.add(self.cell)

        return self.main_cell



    def gen_cpw_feedline(self):
        """
        Generate feedline
        """

        feedwidth = self.feedwidth
        gapwidth = self.gapwidth
        lfeedline = self.length

        feedpoints = [(-lfeedline / 2., feedwidth / 2.),
                      (lfeedline / 2., feedwidth / 2.),
                      (lfeedline / 2., feedwidth / 2. + gapwidth),
                      (-lfeedline / 2., feedwidth / 2. + gapwidth)]

        feedline1 = cad.core.Boundary(feedpoints,layer = self.layer)
        feedline2 = cad.utils.reflect(feedline1, 'x')

        feedlist = cad.core.Elements([feedline1, feedline2])
        return feedlist

    def gen_curved_feeline(self):

        feedwidth = self.feedwidth
        gapwidth = self.gapwidth
        lfeedline = self.length
        lf_spacing = self.lf_spacing

        feedpoints_up = [(-lfeedline / 2., feedwidth / 2. + lf_spacing),
                         (-lfeedline / 2., feedwidth / 2.),
                         (lfeedline / 2., feedwidth / 2.),
                         (lfeedline / 2., feedwidth / 2. + lf_spacing),
                         (lfeedline / 2. - gapwidth, feedwidth / 2. + lf_spacing),
                         (lfeedline / 2. - gapwidth, feedwidth / 2. + gapwidth),
                         (-lfeedline / 2. + gapwidth, feedwidth / 2. + gapwidth),
                         (-lfeedline / 2. + gapwidth, feedwidth / 2. + lf_spacing)]

        feedpoints_below = [(-lfeedline / 2. - feedwidth, feedwidth / 2. + lf_spacing),
                            (-lfeedline / 2. - feedwidth, -feedwidth / 2.),
                            (lfeedline / 2. + feedwidth, -feedwidth / 2.),
                            (lfeedline / 2. + feedwidth,
                             feedwidth / 2. + lf_spacing),
                            (lfeedline / 2. + feedwidth + gapwidth,
                             feedwidth / 2. + lf_spacing),
                            (lfeedline / 2. + feedwidth +
                             gapwidth, -feedwidth / 2. - gapwidth),
                            (-lfeedline / 2. - feedwidth -
                             gapwidth, -feedwidth / 2. - gapwidth),
                            (-lfeedline / 2. - feedwidth - gapwidth, feedwidth / 2. + lf_spacing)]

        dict_corners1 = {}
        dict_corners1['BL1'] = 1
        dict_corners1['BR2'] = 2
        dict_corners1['BR5O'] = 5
        dict_corners1['BL6O'] = 6

        dict_corners2 = {}
        dict_corners2['BL1O'] = 1
        dict_corners2['BR2O'] = 2
        dict_corners2['BR5'] = 5
        dict_corners2['BL6'] = 6

        feedline1 = cad.core.Boundary(feedpoints_up,layer = self.layer)
        feedline2 = cad.core.Boundary(feedpoints_below)
        radius = 0.5
        feedline1 = utils.make_rounded_edges(feedline1, radius, dict_corners1)
        feedline2 = utils.make_rounded_edges(feedline2, radius, dict_corners2)

        feedlist = cad.core.Elements([feedline1, feedline2])
        return feedlist


    def put_launcher(self, pos, dir='right'):
        """
        Generate launchers. If config==hor, it creates a horizontal feedline, if config==vert the launchers are at the top of the chip and the feedline bends down.
        """
        
        launchpoints_top = [(0, self.feedwidth / 2.),
                            (- self.taperl, self.launchw / 2.),
                            (- self.taperl - self.launchl, self.launchw / 2.),
                            (- self.taperl - self.launchl, 0),
                            (- self.taperl - self.launchl - self.launchgapx, 0),
                            (- self.taperl - self.launchl -
                             self.launchgapx, self.launchw / 2. + self.launchgapy),
                            (- self.taperl, self.launchw / 2. + self.launchgapy),
                            (0, self.feedwidth / 2. + self.gapwidth)]

        launcher1 = cad.core.Boundary(launchpoints_top,layer = self.layer)
        launcher2 = cad.utils.reflect(launcher1, 'x')

        launcherlist = cad.core.Elements([launcher1, launcher2])

        if dir == 'left':
            launcherlist = cad.utils.reflect(launcherlist, 'y')

        if dir == 'down':
            launcherlist = cad.utils.rotate(launcherlist, -90)

        if dir == 'up':
            launcherlist = cad.utils.rotate(launcherlist, 90)

        launcherlist = cad.utils.translate(launcherlist, pos)

        return launcherlist
    
    

