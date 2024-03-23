from .map import tirads_map_levels
from ._check import args_check_tirads
from ._points import get_tirads_points

def get_tirads_levels(composition, echogenicity, shape, margin, echogenic_foci):
    
    # Validate inputs
    args_check_tirads(composition, echogenicity, shape, margin, echogenic_foci)
    
    pt = get_tirads_points(composition, echogenicity, shape, margin, echogenic_foci)
    
    # TR 
    if pt["points_tot"] >= 7:
        tr = "TR5"
    elif pt["points_tot"] >= 4:
        tr = "TR4"
    elif pt["points_tot"] == 3:
        tr = "TR3"
    elif pt["points_tot"] == 2 or pt["points_tot"] == 1: # 1 point is not defined in TI-RADS category, but here, I give TR2.
        tr = "TR2"
    elif pt["points_tot"] == 0:
        tr = "TR1"
    else:
        tr = "Undefined"
    
    return {
        "tr": tr, # TR
        "desc": tirads_map_levels[tr] # Description
    }