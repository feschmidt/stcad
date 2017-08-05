    
    def gen_hanger(self, length, pos, coupling='capacitive', couplinglength = 610, couplinggap = 10, centerwidth = 4, gapwidth = 20, radius = 100):
        """
        Generate hanger of length=length at pos=(x0,y1) with inductive coupling
        """
        
        print 'Generating hanger of length ' + str(length) + ' with '+coupling+' coupling'
        x0 = pos[0]
        y0 = pos[1] - couplinggap
        radius_hanger = radius - gapwidth - centerwidth/2
        restlength = length - couplinglength - 2*np.pi*radius_hanger/4
         
        if coupling == 'inductive':
            hangerpoints_1 = [(x0,y0),
                            (x0 + couplinglength,y0),
                            (x0 + couplinglength,y0-gapwidth),
                            (x0, y0-gapwidth)]
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
                            
        if coupling == 'capacitive':
            hangerpoints_1 = [(x0,y0),
                            (x0 + couplinglength,y0),
                            (x0 + couplinglength,y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth-centerwidth/2),
                            (x0, y0-gapwidth-centerwidth/2)]
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
        hanger1 = cad.core.Boundary(hangerpoints_1)
        hanger2 = cad.core.Boundary(hangerpoints_2)
        hanger3 = cad.utils.reflect(hanger1,'x',origin=(0,y0-gapwidth-centerwidth/2))
        hanger4 = cad.utils.reflect(hanger2,'y',origin=(x0+couplinglength+radius-gapwidth-centerwidth/2,0))
        
        radius1 = radius                
        curve1 = cad.shapes.Disk((x0+couplinglength,y0-radius1), radius=radius, inner_radius=radius1-gapwidth, initial_angle=90,final_angle=0)
        
        radius2 = radius-gapwidth-centerwidth
        curve2 = cad.shapes.Disk((x0+couplinglength,y0-gapwidth-centerwidth-radius2), radius=radius2, inner_radius=radius2-gapwidth, initial_angle=90,final_angle=0)
            
        return (hanger1,hanger2,hanger3,hanger4,curve1,curve2)
        




       
        
        # feedline_bottom = feedline[2]   # extract y-coordinate of bottom of feedline
        # length0 = self.length
        # for xx, length in enumerate([length0,length0-430,length0-830,length0-1.2e3]):
        #     hanger = self.gen_hanger(length,(-3.3e3+xx*1.8e3,feedline_bottom),coupling=self.coupling)
        #     for i in range(len(hanger)):
        #         self.cell.add(hanger[i])
        
                self.coupling = self.dict_feedline[
            'coupling']    # inductive, capacitive

                    self.couplinglength = self.dict_feedline['couplinglength']