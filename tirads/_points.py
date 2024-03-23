from ._check import args_check_tirads
from .map import tirads_map_desc, tirads_map_points


def get_tirads_points(composition, echogenicity, shape, margin, echogenic_foci):

    # Validate inputs
    args_check_tirads(composition, echogenicity, shape, margin, echogenic_foci)

    user_selections = {
        "composition": composition,
        "echogenicity": echogenicity,
        "shape": shape,
        "margin": margin,
        "echogenic_foci": echogenic_foci  # This requires special handling due to being a list
    }
    
    points = {}
    
    for category, selection in user_selections.items():
        if category == "echogenic_foci": # Handle multiple selections for echogenic_foci  
            points[category] = sum(tirads_map_points[category][s] for s in selection)
        else:  # Handle single selections
            points[category] = tirads_map_points[category][selection]


    # Return result
    return {
        "points": points,
        "points_tot": sum(points.values()),
        "categories": {
            "composition": composition,
            "echogenicity": echogenicity,
            "shape": shape,
            "margin": margin,
            "echogenic_foci": echogenic_foci
        }
    }
    
if __name__ == "__main__":
    print(get_tirads_points("solid", "hypo", "taller", "irregular", ["none-comet", "punctate"]))

