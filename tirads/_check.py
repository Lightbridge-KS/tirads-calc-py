def args_check_tirads(composition, echogenicity, shape, margin, echogenic_foci):
    tirads_map_categories = {
        "composition": ["cystic", "spongiform", "mixed", "solid", "undetermined"],
        "echogenicity": ["an", "hyper", "iso", "hypo", "very-hypo", "undetermined"],
        "shape": ["wider", "taller"],
        "margin": ["undetermined", "smooth", "ill-defined", "lob-irreg", "extra"],
        "echogenic_foci": ["none-comet", "macro-calc", "rim-calc", "punctate"]
    }
    
    # Check for "echogenic_foci"
    if not isinstance(echogenic_foci, (list, tuple)) or not all(isinstance(item, str) for item in echogenic_foci):
        raise TypeError("echogenic_foci must be a list or tuple of strings")
    
    if composition not in tirads_map_categories["composition"]:
        raise ValueError('Invalid value for composition; must be any of "cystic", "spongiform", "mixed", "solid", "undetermined')
    if echogenicity not in tirads_map_categories["echogenicity"]:
        raise ValueError('Invalid value for echogenicity; must be any of "an", "hyper", "iso", "hypo", "very-hypo", "undetermined"')
    if shape not in tirads_map_categories["shape"]:
        raise ValueError('Invalid value for shape; must be any of "wider", "taller"')
    if margin not in tirads_map_categories["margin"]:
        raise ValueError('Invalid value for margin; must be any of "undetermined", "smooth", "ill-defined", "lob-irreg", "extra"')
    if not all(f in tirads_map_categories["echogenic_foci"] for f in echogenic_foci):
        raise ValueError('Invalid value(s) in echogenic_foci; muse be in "none-comet", "macro-calc", "rim-calc", "punctate"')
    if len(echogenic_foci) != len(set(echogenic_foci)):
        raise ValueError("Values in echogenic_foci cannot be duplicated")

