import pypsa
import numpy as np
import pandas as pd
import os

# Eingabe- und Ausgabedateien
eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/01/networks/base_s_20___2050.nc" 
#output_file_old = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050_pre05.nc"

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

#Platzhalter für den relevanten Code
#H2 Pipeline
n.add("Link",
          "Transmed",
          bus0="DZ0 1 H2",
          bus1="IT4 0 H2",
          carrier="H2 pipeline",
          efficiency=1,
          length=2500,
          p_nom_extendable=True,
          lifetime=50,
          )

#Methanol Bus
# Existierenden Bus "DZ3 0" auslesen
ref_bus = n.buses.loc["DZ0 3 H2"]

# Neuen Methanol-Bus mit den gleichen Standortdaten anlegen
n.add("Bus",
          "DZ0 3 MeOH",
          carrier="methanol",
          location=ref_bus.location,
          lat=ref_bus.lat,
          lon=ref_bus.lon,
          country=ref_bus.country,
          tag_area=ref_bus.tag_area,
          tag_substation=ref_bus.tag_substation,
          #tag_substation_lv=ref_bus.tag_substation_lv,
          x=ref_bus.x,
          y=ref_bus.y,
          )

print(n.buses.loc["DZ0 3 H2"])
print(n.buses.loc["DZ0 3 MeOH"])

n.add("Link",
          "DZ0 3 methanolisation",
          bus0="DZ0 3 H2",
          bus1="DZ0 3 MeOH",
          carrier="methanolisation",
          efficiency=0.8787,
          lifetime=20,
          p_nom_extendable=True,
          p_nom_min=0,
          p_nom_max=float('inf'),
          p_min_pu=0.3,
          p_max_pu=1.0,
          capital_cost=76920.16,
          marginal_cost=0.0,
          marginal_cost_quadratic=0.0,
          stand_by_cost=0.0,
          start_up_cost=0.0,
          shut_down_cost=0.0,
          min_up_time=0,
          min_down_time=0,
          ramp_limit_start_up=1.0,
          ramp_limit_shut_down=1.0,
          committable=False,
          reversed=False)

n.add("Link",
          "Shipping Algeria Germany",
          bus0="DZ0 3 MeOH",                 #ist nah an ALgiers im aktuellen Modell
          bus1="EU methanol",
          carrier="shipping",
          efficiency=1,
          #length=2500,
          p_nom_extendable=True,
          lifetime=float('inf'),
          marginal_cost=119.122727,  
          )

# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre05" + ext

# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
