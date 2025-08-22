import pypsa
import numpy as np
import pandas as pd
import os


eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/02/networks/base_s_20___2050.nc"        #Pfad anpassen
#output_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/networks/base_s_39_Co2L0.50_Co2L0.50_2050_solar-hsat.nc"      #Pfad anpassen

# Netzwerk laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

import re

# === Nordafrikanische Länder-Kürzel ===
countries = ["DZ", "MA", "MR", "TN"]

# === Alle passenden Busse extrahieren ===
pattern = re.compile(r"^(" + "|".join(countries) + r")\d \d$")
target_buses = [bus for bus in n.buses.index if pattern.match(bus)]

# === Bereits existierende solar-hsat Generatoren (nach Bus) ===
existing_hsat_buses = n.generators[n.generators.carrier == "solar-hsat"].bus

# === Fehlende Busse für solar-hsat bestimmen ===
missing_buses = pd.Index(target_buses).difference(existing_hsat_buses)

# === Neue Generatoren erstellen ===
new_generators = pd.DataFrame({
    "bus": missing_buses,
    "carrier": "solar-hsat",
    "p_nom": 0.0,
    "p_nom_extendable": True,
    "p_nom_min": 0.0,
    "p_nom_max": 0.0,  # <- Wird später angepasst, wenn Potenziale bekannt sind
    "build_year": 2020,
    "lifetime": 25
}, index=[f"{bus} solar-hsat" for bus in missing_buses])

# === Neue Generatoren hinzufügen ===
n.generators = pd.concat([n.generators, new_generators])

print(f"{len(missing_buses)} neue solar-hsat Generatoren hinzugefügt für: {', '.join(countries)}")

# === Sicherung des alten Netzwerks ===
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre04" + ext

# === Netzwerk speichern ===
n.export_to_netcdf(eur_file)
n_copy.export_to_netcdf(eur_file_old)

print(f"Modifiziertes Netzwerk gespeichert unter:\n{eur_file}")
print(f"Backup gespeichert unter:\n{eur_file_old}")
