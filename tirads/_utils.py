def dict_to_bullet(d):
    bullet_points = [f"- {key}: {value}" for key, value in d.items()]
    return '\n'.join(bullet_points)

def yes_no(x):
    if x is True:
        res = "✅" 
    elif x is False:
        res = "❌"
    else:
        res = x
    return res