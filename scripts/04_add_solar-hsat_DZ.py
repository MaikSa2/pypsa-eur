import pypsa
import numpy as np
import pandas as pd


eur_file = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"          #Pfad anpassen
output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\fixed_network_2050_reversed_fixed.nc"      #Pfad anpassen

# Netzwerk laden
n = pypsa.Network(eur_file)

import re

# Liste aller DZ-Busse
#dz_buses = n.buses[n.buses.index.str.startswith("DZ")].index

pattern = re.compile(r"^DZ\d \d$")  # z. B. DZ0 0, DZ1 3 usw.
dz_buses = [bus for bus in n.buses.index if pattern.match(bus)]

# Bisherige solar-hsat Generatoren
existing_hsat_buses = n.generators[n.generators.carrier == "solar-hsat"].bus

# Fehlende Buses ermitteln
#missing_buses = dz_buses.difference(existing_hsat_buses)
missing_buses = pd.Index(dz_buses).difference(existing_hsat_buses)

# Generatoren-Dummy-Daten erstellen
new_generators = pd.DataFrame({
    "bus": missing_buses,
    "carrier": "solar-hsat",
    "p_nom": 0.0,
    "p_nom_extendable": True,
    "p_nom_min": 0.0,
    "p_nom_max": 0.0,
    "build_year": 2020,
    "lifetime": 25
}, index=[f"{bus} solar-hsat" for bus in missing_buses])

# In Netz einfügen
n.generators = pd.concat([n.generators, new_generators])

print(f"{len(missing_buses)} neue solar-hsat Generatoren hinzugefügt.")

# Netzwerk speichern
n.export_to_netcdf(output_file)

print(f"Netzwerk erfolgreich gespeichert unter:\n{output_file}")