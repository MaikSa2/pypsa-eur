import yaml
from pathlib import Path

# Config laden
with open(r"/home/student_01/Student_Folders/Maik/pypsa-eur/config/config_a5.yaml") as f:  # Pfad anpassen
    config = yaml.safe_load(f)

prefix = config["run"]["prefix"]

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parent.parent 

eur_file =(REPO_ROOT  / "resources" / prefix / "networks" / "base_s_20__3h_2050.nc").resolve()
   #print(config)
print(type(config))
print(prefix)
print(eur_file)



   #eur_file =  r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/a3_base_shipping/networks/base_s_20__3h_2050.nc" #r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/06/networks/base_s_2___2050.nc"


