import os
import pypsa
import pandas as pd
import math

from aa_run_variables import eur_file
# === Parameter ===
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" #r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050.nc"
#alg_file = r"/home/student_01/Student_Folders/Maik/elec_s_16_ec_lcopt_3h_manual.nc" #r"/home/student_01/Student_Folders/Maik/pypsa-earth/networks/01/elec_s_10_ec_lcopt_1h.nc" #r"C:\Users\maiks\pypsa-earth\networks\NoSectorNetwork\elec_s_6_ec_lcopt_Co2L0.00.nc"
#output_file = "merged_europe_algeria_2050.nc"

# === Netzwerke laden ===
n_eur = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)
n_eur_copy = pypsa.Network(eur_file)
"""
links_to_remove = [
    "H2 pipeline DZ0 0-MA0 2",
    "H2 pipeline DZ0 0-MA0 2-reversed",
    "H2 pipeline DZ0 5-MA0 2",
    "H2 pipeline DZ0 5-MA0 2-reversed"
]

for link in links_to_remove:
    if link in n_eur.links.index:
        n_eur.remove("Link", link)
"""
keywords = ["kerosene for aviation", "shipping methanol"]  # ggf. erweitern

# Maske: Finde Loads, deren Namen eines der Keywords enthalten
mask = n_eur.loads.index.to_series().apply(
    lambda x: any(k in x for k in keywords)
)

# Gefundene Loads auflisten (zur Kontrolle)
print("Zu entfernende Loads:")
print(n_eur.loads.index[mask])

# Entfernen
n_eur.mremove("Load", n_eur.loads.index[mask])

# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre012_remove_H2_network" + ext

#output_file = r"C:\Users\maiks\pypsa-eur\resources\networks\merged_network_2050.nc"
n_eur.export_to_netcdf(eur_file)
n_eur_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk ohne H2-Netzwerk in Nordafrika erfolgreich gespeichert unter: {eur_file}")