# This file generated by Quarto; do not edit by hand.

from __future__ import annotations

from pathlib import Path
from shiny import App, Inputs, Outputs, Session, ui




def server(input: Inputs, output: Outputs, session: Session) -> None:
    from shiny import render, reactive, req
    from shiny.express import input, ui
    import pandas as pd

    # from tirads import TIRADSReport, tirads_map_desc

    # ========================================================================

    width_choices = "400px"

    # ========================================================================

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

    # ========================================================================

    tirads_map_desc = {
        "composition": {
            "cystic": "Cystic or almost completely cystic (0)",
            "spongiform": "Spongiform (0)",
            "mixed": "Mixed cystic and solid (1)",
            "solid": "Solid or almost completely solid (2)"
        },
        "echogenicity": {
            "an": "Anechoic (0)",
            "hyper": "Hyperechoic or Isoechoic (1)",
            "hypo": "Hypoechoic (2)",
            "very-hypo": "Very hypoechoic (3)"
        },
        "shape": {
            "wider": "Wider-than-tall (0)",
            "taller": "Taller-than-wide (3)"
        },
        "margin": {
            "smooth": "Smooth (0)",
            "ill-defined": "Ill-defined (0)",
            "lob-irreg": "Lobulated or Irregular (2)",
            "extra": "Extrathyroidal extension (3)"
        },
        "echogenic_foci": {
            "none-comet": "None or Large comet-tail artifacts (0)",
            "macro-calc": "Macrocalcification (1)",
            "rim-calc": "Rim calcification (2)",
            "punctate": "Punctate echogenic foci (3)"
        }
    }


    tirads_map_points = {
        "composition": {"cystic": 0, "spongiform": 0, "mixed": 1, "solid": 2},
        "echogenicity": {"an": 0, "hyper": 1, "iso": 1, "hypo": 2, "very-hypo": 3},
        "shape": {"wider": 0, "taller": 3},
        "margin": {"smooth": 0, "ill-defined": 0, "lob-irreg": 2, "extra": 3},
        "echogenic_foci": {"none-comet": 0, "macro-calc": 1, "rim-calc": 2, "punctate": 3}
    }


    tirads_map_levels = {
        "TR1": "Benign",
        "TR2": "Not Suspicious",
        "TR3": "Mildly Suspicious",
        "TR4": "Moderately Suspicious",
        "TR5": "Highly Suspicious"
    }

    # ========================================================================

    def args_check_tirads(composition, echogenicity, shape, margin, echogenic_foci):
        tirads_map_categories = {
            "composition": ["cystic", "spongiform", "mixed", "solid"],
            "echogenicity": ["an", "hyper", "iso", "hypo", "very-hypo"],
            "shape": ["wider", "taller"],
            "margin": ["smooth", "ill-defined", "lob-irreg", "extra"],
            "echogenic_foci": ["none-comet", "macro-calc", "rim-calc", "punctate"]
        }
    
        # Check for "echogenic_foci"
        if not isinstance(echogenic_foci, (list, tuple)) or not all(isinstance(item, str) for item in echogenic_foci):
            raise TypeError("echogenic_foci must be a list or tuple of strings")
    
        if composition not in tirads_map_categories["composition"]:
            raise ValueError('Invalid value for composition; must be any of "cystic", "spongiform", "mixed", "solid"')
        if echogenicity not in tirads_map_categories["echogenicity"]:
            raise ValueError('Invalid value for echogenicity; must be any of "an", "hyper", "iso", "hypo", "very-hypo"')
        if shape not in tirads_map_categories["shape"]:
            raise ValueError('Invalid value for shape; must be any of "wider", "taller"')
        if margin not in tirads_map_categories["margin"]:
            raise ValueError('Invalid value for margin; must be any of "smooth", "ill-defined", "lob-irreg", "extra"')
        if not all(f in tirads_map_categories["echogenic_foci"] for f in echogenic_foci):
            raise ValueError('Invalid value(s) in echogenic_foci; muse be in "none-comet", "macro-calc", "rim-calc", "punctate"')
        if len(echogenic_foci) != len(set(echogenic_foci)):
            raise ValueError("Values in echogenic_foci cannot be duplicated")


    # ========================================================================

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

    # ========================================================================

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

    # ========================================================================

    class TIRADSReport:
        def __init__(self, composition, echogenicity, shape, margin, echogenic_foci, size_cm=None):
            # Validate inputs
            args_check_tirads(composition, echogenicity, shape, margin, echogenic_foci)
            pt = get_tirads_points(composition, echogenicity, shape, margin, echogenic_foci)
            lv = get_tirads_levels(composition, echogenicity, shape, margin, echogenic_foci)
            pt_tot = pt["points_tot"]
            # FNA logic
            if pt["points_tot"] < 3: # TR1 or TR2
                should_fna = False
                should_follow = False
            else: # TR3 or more
                should_fna = ((pt_tot == 3 and size_cm >= 2.5) or
                            (4 <= pt_tot <= 6 and size_cm >= 1.5) or
                            (pt_tot >= 7 and size_cm >= 1)) if size_cm is not None else "?"

                # Follow-up logic
                should_follow = ((pt_tot == 3 and size_cm >= 1.5) or
                                (4 <= pt_tot <= 6 and size_cm >= 1) or
                                (pt_tot >= 7 and size_cm >= 0.5)) if size_cm is not None else "?"
        
            desc = {}
            for category, selection in pt["categories"].items():
                if category == "echogenic_foci":
                    ls = [tirads_map_desc[category][x] for x in selection]
                    desc[category] = ", ".join(ls) 
                else:
                    desc[category] = tirads_map_desc[category][selection]
        
        
            self.pt = pt
            self.lv = lv
            self.desc = desc
            self.should_fna = should_fna
            self.should_follow = should_follow
        
        
        # Pretty Printing 
        def __str__(self):
            report_str = f"-- TIRADS Report --\n\n" \
                         f"Level: {self.lv['tr']} ({self.lv['desc']})\n" \
                         f"Total Points: {self.pt['points_tot']}\n\n" \
                         f"Points by Category:\n" \
                         f"{dict_to_bullet(self.pt['points'])}\n\n" \
                         f"Description:\n" \
                         f"{dict_to_bullet(self.desc)}\n\n" \
                         f"Suggested Actions:\n" \
                         f"- FNA: {self.should_fna}\n" \
                         f"- Follow-up: {self.should_follow}"
            return report_str
    
        # Markdown (Summary)
        def to_md_str_summary(self):
            md_str = f"# TIRADS = `{self.lv['tr']}` ({self.lv['desc']})\n" \
                     f"### **Total Points:** {self.pt['points_tot']}\n\n"
            return md_str
    
        # Markdown (Actions)
        def to_md_str_actions(self):
            pt_tot = self.pt["points_tot"]
    
            if (self.should_fna == "?" or self.should_follow == "?") and pt_tot >= 3:
                # Not
                if pt_tot >= 7: # TR5
                    fna = "if ≥ 1 cm"
                    follow = "if ≥ 0.5 cm"
                elif pt_tot >= 4: # TR4
                    fna = "if ≥ 1.5 cm"
                    follow = "if ≥ 1 cm"
                elif pt_tot == 3: # TR3
                    fna = "if ≥ 2.5 cm"
                    follow = "if ≥ 1.5 cm"
            else:
                fna = yes_no(self.should_fna)
                follow = yes_no(self.should_follow)
            
            md_str = f"### Suggested Actions:\n" \
                     f"- FNA: {fna}\n" \
                     f"- Follow-up: {follow}"
                 
            return md_str
    
        # Points as DataFrame
        def get_points_df(self):
            import pandas as pd
        
            df1 = pd.DataFrame({
                "Categories": [k.capitalize().replace("_", " ") for k in tirads_map_desc.keys()],
                "Points": self.desc.values()
            })
            df2 = df1.copy()
            df2.loc[len(df1)] = ["Total", self.pt["points_tot"]]
        
            return df2

    # ========================================================================

    ui.input_radio_buttons(  
            "composition",  
            "Choose one:",  
            tirads_map_desc["composition"],
            width = width_choices
    ) 

    # ========================================================================

    ui.input_radio_buttons(  
            "echogenicity",  
            "Choose one:",  
            tirads_map_desc["echogenicity"],
            width = width_choices
    ) 

    # ========================================================================

    ui.input_radio_buttons(  
            "shape",  
            "Choose one:",  
            tirads_map_desc["shape"],
            width = width_choices
    ) 

    # ========================================================================

    ui.input_radio_buttons(  
            "margin",  
            "Choose one:",  
            tirads_map_desc["margin"],
            width = width_choices
    ) 

    # ========================================================================

    ui.input_checkbox_group(  
        "echogenic_foci",  
        "Choose All That Apply",  
        tirads_map_desc["echogenic_foci"],
        width = width_choices
    )  

    # ========================================================================

    ui.input_numeric("size_cm", None, value=None, min=0)

    # ========================================================================

    @reactive.calc
    def tirads_results():
        req(input.echogenic_foci())
        res = TIRADSReport(
            composition=input.composition(), 
            echogenicity=input.echogenicity(), 
            shape=input.shape(), 
            margin=input.margin(), 
            echogenic_foci= input.echogenic_foci(), 
            size_cm=input.size_cm())
        return res

    # ========================================================================

    @render.ui
    def render_md_summary():
        return ui.markdown(tirads_results().to_md_str_summary())

    # ========================================================================

    @render.data_frame  
    def output_df():
        df = tirads_results().get_points_df()
        return render.DataGrid(df)  

    # ========================================================================

    @render.ui
    def render_md_actions():
        return ui.markdown(tirads_results().to_md_str_actions())

    # ========================================================================



    return None


_static_assets = ["tirads-calc_files","images/tirads-chart.png","images/composition.png","images/echogenicity.png","images/shape.png","images/margin.png","images/echogenic-foci.png","images/cover.png","images/favicon/apple-touch-icon.png","images/favicon/favicon-32x32.png","images/favicon/favicon-16x16.png","images/favicon/site.webmanifest","css/style.css"]
_static_assets = {"/" + sa: Path(__file__).parent / sa for sa in _static_assets}

app = App(
    Path(__file__).parent / "tirads-calc.html",
    server,
    static_assets=_static_assets,
)
