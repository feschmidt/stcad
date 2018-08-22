import numpy as np
import gdsCAD as cad
from .objects import CPW
from .chip import Base_Chip
from .fillet import fillet

#################################
# This file enables connecting the (left) center pin of a CPW to the ground plane via a graphene Josephson junction.
# The junction is covered by a dielectric and a top-gate, that is connected to the right CPW center pin, leading to the gate line.
# should be adjusted such that the leads actually end at the junction because then they can also be filleted and no secondary processing (LayoutBeamer) is needed
#################################

def calc_theta(points):
    """
    return the angle theta of vector points
    """
    (x0,y0),(x1,y1) = points
    try:
        theta = np.arctan((y1-y0)/(x1-x0)) # fails for vertical structures
    except ZeroDivisionError:
        theta = np.pi/2
    return theta

def calc_length(points):
    """
    return the length of the array points
    """
    (x0,y0),(x1,y1) = points
    return np.sqrt((y1-y0)**2+(x1-x0)**2)

def calc_center(points,vec=0):
    """
    return the center value (or vector if vec=1) of array points
    """
    (x0,y0),(x1,y1) = points
    val1, val2 = (x1+x0)/2.,(y1+y0)/2.
    if not vec:
        return np.array([val1, val2])
    else:
        return np.array([(0,0),(val1,val2)])

def finishpts(X0,Y0,Z1,Z2,gcenter,xbox,ybox,finish):
    """
    docstring for finishpts
    """
    if finish==1:
        cppts = [[X0,Y0],Z1,gcenter,Z2,[X0+xbox,Z2[1]]]
    elif finish==2:
        cppts = [[X0,Y0],Z1,gcenter,Z2,[Z2[0],Y0+ybox/2]]
    elif finish==3:
        cppts = [[X0,Y0],Z1,gcenter,Z2,[X0,Z2[1]]]
    elif finish==4:
        cppts = [[X0,Y0],Z1,gcenter,Z2,[Z2[0],Y0-ybox/2]]
    return cppts

def sincospts(center,theta,dx,dy,ortn=1,start=1):
    """
    docstring for sincospts
    """
    if ortn==1:
        pts = [[center[0]+dx*np.sin(theta),center[1]-dy*np.cos(theta)],[center[0]-dx*np.sin(theta),center[1]+dy*np.cos(theta)]]
    elif ortn==2:
        pts = [[center[0]-dx*np.cos(theta),center[1]-dy*np.sin(theta)],[center[0]+dx*np.cos(theta),center[1]+dy*np.sin(theta)]]
    if start==1:
        return pts
    elif start==2:
        return pts[::-1]

def path_to_boundary(points,dx,dy,ortn=1,start=1):
    """
    Converts a path with endpoints points and width 2*dx=2*dy to a polygon with four corners
    """
    (x0,y0),(x1,y1) = points
    center = calc_center(points)#/2
    theta = calc_theta(points)
    newpoints = points
    top = sincospts(newpoints[0],theta,dx,dy,ortn,start)
    bottom = sincospts(newpoints[1],theta,dx,dy,ortn,start)
    if theta<0:
        finalpoints = top + bottom[::-1]
    else:
        finalpoints = bottom + top[::-1]
    return finalpoints

def rottheta(points,theta,center=1):
    """
    Rotate an array of points by angle theta
    if center=1, then rotate with respect to array center; else w.r.t. (0,0)
    """
    Rth = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    if center:
        return Rth.dot(np.array(points)-calc_center(points))#Rth.dot(np.array(points)-calc_center(points))+calc_center(points)
    else:
        return Rth.dot(np.array(points))

def add_extensions(gcenter,dist,theta,start):
    """
    docstring for add_extensions
    """
    if isinstance(dist,list):
        dist1,dist2=dist[0],dist[1]
    else:
        dist1,dist2 = dist,dist
    if start==2:
        Z1 = (gcenter[0]+dist1*np.sin(theta),gcenter[1]-dist1*np.cos(theta))
        Z2 = (gcenter[0]-dist2*np.sin(theta),gcenter[1]+dist2*np.cos(theta))
    elif start==1:
        dist1,dist2 = dist2,dist1
        Z2 = (gcenter[0]+dist1*np.sin(theta),gcenter[1]-dist1*np.cos(theta))
        Z1 = (gcenter[0]-dist2*np.sin(theta),gcenter[1]+dist2*np.cos(theta))
    return [Z1,Z2]

def add_endbox(cppts,S,finish):
    """
    Adds and extra box at the end of the grounding graphene lead
    """
    if finish==1:
        endboxpts = ((cppts[-1][0],cppts[-1][1]-S/2),(cppts[-1][0]+S/2,cppts[-1][1]+S/2))
    elif finish==2:
        endboxpts = ((cppts[-1][0]-S/2,cppts[-1][1]+S/2),(cppts[-1][0]+S/2,cppts[-1][1]))
    elif finish==3:
        endboxpts = ((cppts[-1][0],cppts[-1][1]-S/2),(cppts[-1][0]-S/2,cppts[-1][1]+S/2))
    elif finish==4:
        endboxpts = ((cppts[-1][0]-S/2,cppts[-1][1]-S/2),(cppts[-1][0]+S/2,cppts[-1][1]))
    return endboxpts

def add_extrapts(cppts,jjwidth,finish,which=2,endwidth=None):
    """
    Widen grounding graphene lead towards the end
    """
    if endwidth==None:
        endwidth = 5*jjwidth
    if which==2:
        if finish==2 or finish==4:
            extrapts2 = [[cppts[-2][0]-jjwidth/2,cppts[-2][1]],[cppts[-2][0]+jjwidth/2,cppts[-2][1]],[cppts[-1][0]+endwidth,cppts[-1][1]],[cppts[-1][0]-endwidth,cppts[-1][1]]]
        else:
            extrapts2 = [[cppts[-2][0],cppts[-2][1]-jjwidth/2],[cppts[-2][0],cppts[-2][1]+jjwidth/2],[cppts[-1][0],cppts[-1][1]+endwidth],[cppts[-1][0],cppts[-1][1]-endwidth]]
        return extrapts2


#################################


class gJJ_layout():
    '''
    Parameters to be edited by user:
    - flakepos (x0,y0,x1,y1)
    - start (1 or 2)
    - gatestart (1 or 2)
    '''

    def __init__(self,name,dict_gjj):

        self.name = name
        self.maincell = cad.core.Cell('gJJ MAINCELL')

        # layer assignment
        self.lylead = 10
        # self.lyhole = 100   # for SQUID hole
        self.lygraphene = 111
        self.lyshape = 11
        self.lydiel = 12
        self.lygate = 13
        self.lybox = 1

        # basic geometry
        self.gJJbox = (80,70)
        self.Pos0 = (3399, 3500)
        self.CPWpars = (12,5)
        
        self.S, self.W = 12, 5 # has to match CPW centerpin and gap
        self.start = 1 # 1 or 2
        self.gatestart = 2 # 1 or 2
        self.dist = 2.0  # extension of straight lead part
        self.dofillet = 1
        self.filletradius = 0.1
        self.cornerfill = 1

        # gJJ parameters
        self.flakepos = [(3430,3475),(3431,3478)]
        self.JJ = [0.3,0.3]
        self.dx = 0.5
        self.dy = self.dx
        self.dw = 0.5
        self.leadwidth = 1.0

        for key,val in list(dict_gjj.items()):
            setattr(self,key,val)

        # Assign parameters for better readibility
        self.xbox, self.ybox = self.gJJbox
        self.X0, self.Y0 = self.Pos0

        (x0,y0),(x1,y1) = self.flakepos
        if x0>x1:
            raise ValueError('Flake has to have x0<x1 !')

        self.width = calc_length(self.flakepos)
        self.gcenter = calc_center(self.flakepos)
        self.theta = calc_theta(self.flakepos)
        print("Location of graphene:",self.flakepos)
        print("Location of graphene JJ center:",self.gcenter)
        print("Rotation angle theta (deg):",self.theta*180/np.pi)

        # Lead parameters
        if y1>self.Y0: # if flake above center of box
            self.finish = 2
        else:
            self.finish = 4

        # JJ parameters
        self.jjlength,self.jjwidth = self.JJ
        print("Junction length x width (um):",self.jjlength,"x",self.jjwidth)
        print("Flake width x JJlength (um):",self.width,"x",self.jjlength)

    
    def generate(self,short=False,xreflect=False,rotation=None,mask=False,showflake=True):
        self.cell = cad.core.Cell('gJJ CELL')

        if short:
            print("\n*******************")
            print("WARNING: short=True! This will create a short to ground!")
            print("*******************\n")
        leads = self.generate_leads(gcenter=self.gcenter,theta=self.theta,jjlength=self.jjlength,jjwidth=self.jjwidth,dx=self.dx,dy=self.dy,dw=self.dw,dist=self.dist,short=short)
        topgate = self.generate_topgate(theta=self.theta,jjlength=self.jjlength,jjwidth=self.jjwidth,dx=self.dx,dy=self.dy,dw=self.dw,dist=self.dist)
        if mask:
            etchmask = self.generate_etchmask(theta=self.theta,jjlength=self.jjlength,jjwidth=self.jjwidth,dx=self.dx,dy=self.dy,dw=self.dw,dist=self.dist)
            self.cell.add(etchmask)

        for toadd in [leads,topgate]:
            self.cell.add(toadd)

        if xreflect or rotation: # this mirrors the cell at the y axis
            # calculate cell center
            x0, y0 = 0, (self.cell.bounding_box[0][1]+self.cell.bounding_box[1][1]) #-(self.cell.bounding_box[0][0]+self.cell.bounding_box[1][0])/2
            self.maincell.add(cad.core.CellReference(self.cell,origin=(x0,y0),rotation=rotation,x_reflection=xreflect))        
        else:
            self.maincell.add(self.cell)
        if showflake:
            self.maincell.add(cad.core.Path(self.flakepos,width=1,layer=99))

        return self.maincell


    def generate_leads(self,gcenter,theta,jjlength,jjwidth,dx,dy,dw,dist,short):
        # Add the graphene leads
        leadcell = cad.core.Cell('gJJ_LEADS')

        gjjpts = sincospts(center=gcenter,theta=theta,dx=jjlength/2,dy=jjlength/2,ortn=1)
        gjj0 = cad.core.Path(gjjpts,width=jjwidth,layer=self.lygraphene)
        # gjj = cad.core.Path(gjjpts,width=self.leadwidth,layer=self.lyhole)
        
        # calculate where the leads should end
        normflakepos = (self.flakepos - calc_center(self.flakepos))/calc_length(self.flakepos) + calc_center(self.flakepos)
        if self.start==1:
            p2bstart = 2
        else:
            p2bstart = 1
        leadboxpts = path_to_boundary(points=normflakepos,dx=self.JJ[0]/2,dy=self.JJ[0]/2,ortn=1,start=p2bstart)
        leadboxpts2 = path_to_boundary(points=normflakepos,dx=1.75*dist,dy=1.75*dist,ortn=1,start=p2bstart)

        if not short:
            leadcell.add(gjj0)
            # leadcell.add(gjj)

        self.gbarpts = sincospts(center=gcenter,theta=theta,dx=dw+jjlength/2,dy=dw+jjlength/2,ortn=2)
        # gbar = cad.core.Path(self.gbarpts,width=jjlength+dw,layer=self.lyhole)
        # if not short:
        #     leadcell.add(gbar)
        
        Z1, Z2 = add_extensions(gcenter,[dist,1.5*dist],theta,self.start)
        cppts = finishpts(self.X0,self.Y0,Z1,Z2,self.gcenter,self.xbox,self.ybox,self.finish)

        pin = self.leadwidth # jjwidth
        gndgap = self.W
        # cp = CPW(cppts,pin=pin,turn_radius=0.001,layer=self.lylead,writegaps=False)
        cp = cad.core.Path(cppts,width=pin,layer=self.lylead)
        # print("cp.points:",cp.points,"end")
        # leadcell.add(cp)

        # Add circles at possibly narrow corners of leads
        if self.cornerfill:
            [leadcell.add(cad.shapes.Disk(thepoint,radius=self.leadwidth/2,layer=self.lylead)) for thepoint in [cppts[1],cppts[-2]]]
        # Make leads wider for lower resistance
        # first cpw towards JJ
        self.extrapts1 = [
            [self.X0-self.S,self.Y0+self.S/2],
            [self.X0-self.S,self.Y0-self.S/2],
            [self.X0,self.Y0-self.S/2]
            ]\
            +[sincospts(center=cppts[1],theta=theta,dx=self.leadwidth/2,dy=self.leadwidth/2,ortn=2,start=self.start)[0]]\
            +[leadboxpts[3]]\
            +[leadboxpts[0]]\
            +[sincospts(center=cppts[1],theta=theta,dx=self.leadwidth/2,dy=self.leadwidth/2,ortn=2,start=self.start)[1]]\
            +[[self.X0,self.Y0+self.S/2]
            ]
        # then JJ towards ground
        self.extrapts2 = add_extrapts(cppts=cppts,jjwidth=self.leadwidth,endwidth=self.S/2,finish=self.finish,which=2)
        self.extrapts3 = [leadboxpts[1]]+[leadboxpts[2]]+[leadboxpts2[2]]+[leadboxpts2[1]]
        endboxpts = add_endbox(cppts=cppts,S=self.S,finish=self.finish)
        endbox = cad.shapes.Rectangle(endboxpts[0],endboxpts[1],layer=self.lylead)
        leadcell.add(endbox)
        for extrapts in [self.extrapts1,self.extrapts2,self.extrapts3]:
            if self.dofillet:
                extra = cad.core.Boundary(fillet(extrapts,radius=self.filletradius),layer=self.lylead)
            else:
                extra = cad.core.Boundary(extrapts,layer=self.lylead)
            leadcell.add(extra)

        return leadcell


    def generate_topgate(self,theta,jjlength,jjwidth,dx,dy,dw,dist):
        # Add top gate
        gatecell = cad.core.Cell('gJJ_GATE')
        
        topdielwidth = jjlength+2*dw
        topdiel = cad.core.Path(self.gbarpts,width=topdielwidth,layer=self.lydiel)
        gatecell.add(topdiel)

        gatepts1 = add_extensions(self.gcenter,[3*dist,self.leadwidth/2],theta=self.theta+np.pi/2,start=self.gatestart) # jjwidth/2+dx/2
        gatepts1 = [[self.X0+self.xbox,self.Y0]] + gatepts1
        topgatewidth = topdielwidth-dw
        # topgate1 = CPW(gatepts1,pin=topgatewidth,turn_radius=0.001,layer=self.lygate,writegaps=False)
        topgate1 = cad.core.Path(gatepts1,width=topgatewidth,layer=self.lygate)
        gatecell.add(topgate1)
        gatepts2 = [[self.X0+self.xbox+self.S,self.Y0-self.S/2],[self.X0+self.xbox,self.Y0-self.S/2]]+sincospts(center=gatepts1[1],theta=theta,dx=topgatewidth/2,dy=topgatewidth/2,ortn=1)+[[self.X0+self.xbox,self.Y0+self.S/2],[self.X0+self.xbox+self.S,self.Y0+self.S/2]]
        topgate2 = cad.core.Boundary(gatepts2,layer=self.lygate)
        gatecell.add(topgate2)

        return gatecell


    def generate_etchmask(self,theta,jjlength,jjwidth,dx,dy,dw,dist):
        # Generate etch mask on layer=self.lyshape
        etchcell = cad.core.Cell('ETCHMASK')

        # etchpts = [[self.X0,self.Y0-self.ybox/2],[self.X0+self.xbox/2,self.Y0-self.ybox/2],[self.X0+self.xbox/2,self.Y0],[self.X0,self.Y0]]
        etchpts = [self.extrapts2[0],self.extrapts2[-1],[self.X0,self.Y0-self.ybox/2],self.extrapts1[2],self.extrapts1[3]]
        etchcell.add(cad.core.Boundary(etchpts,layer=self.lyshape))

        return etchcell


    def gen_label(self,pos):
        #
        labelcell = cad.core.Cell('gJJ_LABEL')
        lblstrng = 'W,L={},{}um'.format(self.jjwidth,self.jjlength)
        label = cad.shapes.LineLabel(lblstrng,80,
                                     (pos[0],pos[1]),line_width=5,layer=self.lylead)
        labelcell.add(label)
        return labelcell



if __name__ == '__main__':
    chipsize = 10e3
    chip = Base_Chip('GJJ_GUIDING_TEST',chipsize,chipsize,label=False)
    # dict_gJJ = {}
    dict_gJJ = {'Pos0':[3267,-3500],
            'JJ':[0.3,0.3],
            'gJJbox':[70,80],
            'flakepos':(3300,-3510,3305,-3500)}
    gJJinit = gJJ_layout(name='test',dict_gjj=dict_gJJ)
    # print(gJJinit.maincell.bounding_box)
    gJJ = gJJinit.generate(rotation=0,xreflect=0)
    # print(gJJinit.maincell.bounding_box)
    chip.add_component(gJJ, (0,0))

    chip.save_to_gds(show=False, save=True,loc='')

####################
# # Add the ground plane
# # Note: maybe better to do this post-topgate deposition to avoid huge capacitance to ground?
# gndpts1 = [(X0+xbox,Y0+ybox/2),(X0,Y0+ybox/2),(X0,Y0+gap+gndgap)]
# gndpts2 = [(X0+xbox,Y0-ybox/2),(X0,Y0-ybox/2),(X0,Y0-gap-gndgap)]
# for i,(xx,yy) in enumerate(cppts):
#     k=1
#     if i==0 or i==len(cppts)-1:
#         k=0
#     if start==1:
#         gndpts1.append((xx-k*gndgap,yy+gndgap))
#         gndpts2.append((xx+k*gndgap,yy-gndgap))
#     elif start==2:
#         gndpts1.append((xx+gndgap,yy+k*gndgap))
#         gndpts2.append((xx+k*gndgap,yy-gndgap))
# gndplane1 = cad.core.Boundary(gndpts1,layer=lylead)
# gndplane2 = cad.core.Boundary(gndpts2,layer=lylead)
# chip.add_component(gndplane1)
# chip.add_component(gndplane2)