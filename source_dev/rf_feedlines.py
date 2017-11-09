import numpy as np
import gdsCAD as cad
import utilities as utils


class Feedline():
    """
    Class for RF transmission feedline
    """

    def __init__(self, name, dict_feedline, feedline=True):

        self.name = name
        self.dict_feedline = dict_feedline

        
        self.lfeedline = self.dict_feedline['length']
        self.feedwidth = self.dict_feedline['feedwidth']

        self.gapwidth = self.dict_feedline['gapwidth']
        self.curved = self.dict_feedline['curved']
        self.orientation = self.dict_feedline['orientation']
        self.layer = self.dict_feedline['layer']
        
        self.feedline = feedline    # additional option to omit feedlines if set to False
            
        # hard coded parameters of the feedline
        self.lf_spacing = 0.5e3
        self.launchw = 0.5e3
        self.launchl = 0.4e3
        self.taperl = 0.5e3

        self.gen_params_launcher()

    def gen_feedline(self):

        self.main_cell = cad.core.Cell('MAIN CELL')
        self.cell = cad.core.Cell('RF_FEED')

        if self.curved == True:
            feedline_cpw = self.gen_curved_feeline()
            launcher1 = self.put_launcher((-self.lfeedline / 2. - self.feedwidth / 2,
                                           self.lf_spacing + self.feedwidth / 2.), 'down')
            launcher2 = self.put_launcher((self.lfeedline / 2. + self.feedwidth / 2,
                                           self.lf_spacing + self.feedwidth / 2.), 'down')

        else:
            feedline_cpw = self.gen_cpw_feedline()
            launcher1 = self.put_launcher((-self.lfeedline / 2., 0), 'right')
            launcher2 = self.put_launcher((self.lfeedline / 2., 0), 'left')

        if self.feedline:
            self.cell.add(feedline_cpw)
        self.cell.add(launcher1)
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
            # feedline_cpw = cad.utils.rotate(feedline_cpw, 90)
            # launcher1 = cad.utils.rotate(launcher1, 90)
            # launcher2 = cad.utils.rotate(launcher2, 90)

        return self.main_cell



    def gen_cpw_feedline(self):
        """
        Generate feedline
        """

        feedwidth = self.feedwidth
        gapwidth = self.gapwidth
        lfeedline = self.lfeedline

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
        lfeedline = self.lfeedline
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

    def gen_params_launcher(self):

        self.dict_launcher = {}
        self.dict_launcher['feedwidth'] = self.feedwidth
        self.dict_launcher['launchw'] = self.launchw
        self.dict_launcher['launchl'] = self.launchl
        self.dict_launcher['taperl'] = self.taperl
        self.dict_launcher['launchgap'] = 200
        self.dict_launcher['gapwidth'] = self.gapwidth

    def put_launcher(self, pos, dir='right'):
        """
        Generate launchers. If config==hor, it creates a horizontal feedline, if config==vert the launchers are at the top of the chip and the feedline bends down.
        """

        startpoint = 0
        transl = pos
        feedwidth = self.dict_launcher['feedwidth']
        launchw = self.dict_launcher['launchw']
        launchl = self.dict_launcher['launchl']
        taperl = self.dict_launcher['taperl']
        gapwidth = self.dict_launcher['gapwidth']
        launchgap = self.dict_launcher['launchgap']

        launchpoints_top = [(startpoint, feedwidth / 2.),
                            (startpoint - taperl, taperl / 2.),
                            (startpoint - taperl - launchl, launchw / 2.),
                            (startpoint - taperl - launchl, 0),
                            (startpoint - taperl - launchl - launchgap, 0),
                            (startpoint - taperl - launchl -
                             launchgap, launchw / 2. + launchgap),
                            (startpoint - taperl, launchw / 2. + launchgap),
                            (startpoint, feedwidth / 2. + gapwidth)]

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
    
    

