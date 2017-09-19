import numpy as np
import gdsCAD as cad

# This file only contains method. It shall be used to collect all methods for DC24pin samples to generate bonding pads.
# Maybe move bond testpads from basechip class to here?

def gen_full_array(padgroup):
    '''
    Multiply padgroup cell for ALD JJs and SQUIDs and arrange them along the four sides of a 6x6mm2 chip
    '''
    # Merge objects into cells
    bottom = cad.core.Cell('BOTTOM LAYER')
    bottom.add(padgroup[0]) 
    bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=90))
    bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=180))
    bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=270))

    top = cad.core.Cell('TOP LAYER')
    top.add(padgroup[1]) 
    top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=90))
    top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=180))
    top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=270))

    # Merge all cells
    maincell = cad.core.Cell('MAIN')
    maincell.add(bottom)
    maincell.add(top)
    return maincell
    

def gen_partial(padgroup, loc='s'):
    """
    Generate one padgroup cell at specified loc(ation)
    values for loc: s, e, n, w
    """
    
    # Merge objects into cells
    bottom = cad.core.Cell('BOTTOM LAYER')
    top = cad.core.Cell('TOP LAYER')

    if loc == 's':
        bottom.add(padgroup[0])
        top.add(padgroup[1]) 
    elif loc == 'e':
        bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=90))
        top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=90))
    elif loc == 'n':
        bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=180))
        top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=180))
    elif loc == 'w':
        bottom.add(cad.core.CellReference(padgroup[0], origin=(0,0),rotation=270))
        top.add(cad.core.CellReference(padgroup[1], origin=(0,0),rotation=270))
    else:
        raise ValueError("loc(ation) is invalid. Allowed values are s, e, n, w.")

    # Merge all cells
    maincell = cad.core.Cell('MAIN')
    maincell.add(bottom)
    maincell.add(top)
    return maincell
