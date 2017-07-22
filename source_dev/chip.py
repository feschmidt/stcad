import numpy as np
import gdsCAD as cad
import time

class Base_Chip():
	
    """
    This object represent a single chip and can be considered as the parentobject.
    The reference position is 0,0
    """

    def __init__(self, name, xdim, ydim):

        self.name = name
        self.xdim = xdim
        self.ydim = ydim
        self.layer_label = 20
        self.layer_box = 21
        self.layer_ebpgmarker = 22
        self.layer_testpads = 23

        self.cell = cad.core.Cell(name)

        self.make_layout()


    def make_layout(self):
        
        box=cad.shapes.Box((0,0), (self.xdim, self.ydim),
				         width=10, layer =self.layer_box)

        date = time.strftime("%d/%m/%Y")
        #The label is added 100 um on top of the main cell
        label_grid_chip = cad.shapes.LineLabel( self.name + "  " +\
								         date,50,(self.xdim/2.,self.ydim-100),
								         layer=self.layer_label)


        self.cell.add(box)
        self.cell.add(label_grid_chip)


    def add_component(self,cell_obj, pos):
        """
        params cell_obj : cell object to add to maincell
        params pos : tuple of positions
        """
        if pos[0]> self.xdim or pos[0]<0:
            raise ValueError(" component lies out of layout") 

        if pos[1]> self.ydim or pos[1]<0:
            raise ValueError(" component lies out of layout") 

        self.cell.add(cell_obj,origin=pos)

    
    def add_ebpg_marker(self, pos=(1000,1000), size=20, spacing=200):
        '''
        4 marker each 20um rectangular and 200um spaced apart
        params pos : tuple of positions
        '''
        marker = [cad.core.Cell('EBEAM')] * 4
        x = [pos[0], pos[0] + spacing, pos[0] + spacing, pos[0]]
        y = [pos[1], pos[1], pos[1] + spacing, pos[1] + spacing]
        for i in range(4):
            box = cad.shapes.Rectangle((x[i]-size/2,y[i]-size/2),(x[i]+size/2,y[i]+size/2),
                                        layer = self.layer_ebpgmarker)
            marker[0].add(box)
        marker[1] = cad.core.CellReference(marker[0], origin=(self.xdim-2*pos[0]-spacing,0))
        marker[2] = cad.core.CellReference(marker[0], origin=(self.xdim-2*pos[0]-spacing,self.ydim-2*pos[1]-spacing))
        marker[3] = cad.core.CellReference(marker[0], origin=(0,self.ydim-2*pos[1]-spacing))
        self.cell.add(marker)


    def save_to_gds(self, save = True, show = True):
        layout = cad.core.Layout('MAIN_CHIP')
        layout.add(self.cell)
        if save:
            layout.save(self.name + '.gds')
        if show:
            layout.show()


    def add_bond_testpads(self, pos=(1000,1000), dim=(300,300), num=4):
        '''
        value(num) bonding pads with dimension dim (tuple) at position pos (tuple)
        '''
        pads = cad.core.Cell('TESTPADS')
        x = [pos[0], self.xdim-pos[0], self.xdim-pos[0], pos[0]]
        y = [pos[1], pos[1], self.ydim-pos[1], self.ydim-pos[1]]
        for i in range(num):
            box = cad.shapes.Rectangle((x[i]-dim[0]/2,y[i]-dim[1]/2),(x[i]+dim[0]/2,y[i]+dim[1]/2), layer = self.layer_testpads)
            pads.add(box)
        self.cell.add(pads)


    def add_photolitho_marker(self, pos=(3000,3000)):
        marker = cad.core.Cell('PHOTO')
        amarks0 = cad.templates.AlignmentMarks(('A','C'),(1,2))
        amarks = cad.core.CellReference(amarks0).translate(pos)
        marker.add(amarks)
        self.cell.add(amarks)
    
    
    def add_photolitho_vernier(self, pos=(2500,2500)):
        verniers = cad.core.Cell('VERNIER')
        vmarks0 = cad.templates.Verniers(('A','B'),(1,2))
        vmarks = cad.core.CellReference(vmarks0).translate(pos)
        verniers.add(vmarks)
        self.cell.add(verniers)
    
    '''
    # Disabled for now since issue with dxfImport    
    def add_TUlogo(self, pos=(3000,100)):
        # logo is added 100um below bottom edge of chip
        logo = cad.core.DxfImport('examples/TU_Delft_logo_Black.dxf',scale=1.0)
        logo.layer=self.layer_label
        self.cell.add(logo)
    '''
