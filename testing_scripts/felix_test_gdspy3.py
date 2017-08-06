import numpy
import gdspy

layer = {'cross': 20, 'pad': 21, 'amark': 22, 'text': 23, 'elec':24, 'tmp': 50, 'bigtmp': 51}

def my_or(l): # boolean "or", which will flatten our structs.
    v = 0
    for a in l:
        if a != 0: v = 1
    return v

# boolean xor
def my_xor(l): return (sum(l)%2)

def makecross(width=2, length=10):
    plist = []
    cross = gdspy.Cell('cross')
    plist = [gdspy.Rectangle((4, 0), (6, 10)).points,
    	gdspy.Rectangle((0, 4), (10, 6)).points]
    return cross.add(gdspy.fast_boolean(plist[0],plist[1], 'or'))

supercross = gdspy.Cell('supercross')
supercross.add(gdspy.CellArray(makecross(), 2, 2, (50, 50), (0, 0)))

supercross.add(gdspy.CellReference(makecross(), (10, 20), 35))

def makecross(width=2, length=10):
    plist = []
    cross = gdspy.Cell('cross'+repr(width)+repr(length))
    plist.append([gdspy.Rectangle(layer['tmp'], (-width/2, -5), (width/2, 5))])#.points])
    plist.append([gdspy.Rectangle(layer['tmp'], (0, 4), (10, -width/2))])#.points])
    return cross.add(gdspy.boolean(layer['tmp'], plist, my_or))

for i in range(2):
    for j in range(2):
        c = makecross(width=2*i, length=10*j)
        supercross.add(gdspy.CellReference(c, (i*100, j*100), 0))

supercross.add(gdspy.Text('Hello world', (20, -10)))

def save(fname=None):
    import sys
    ## Create a file to save the GDSII stream.
    fname = fname or os.path.abspath(os.path.dirname(os.sys.argv[0])) + os.sep + sys.argv[0][:-3]
    out = open(fname + '.gds', 'wb')
    ## Write the GDSII stream in the file with all created cells (by default).
    ## The units we used are set to micrometers and the precision to nanometers.
    gdspy.gds_print(out, unit=1.0e-6, precision=1.0e-9)
    out.close()
    print 'Sample gds file saved: ' + fname + '.gds'

save('superlayout')