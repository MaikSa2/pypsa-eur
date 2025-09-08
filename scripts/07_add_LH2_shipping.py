import pypsa
import numpy as np
import pandas as pd
import os

from aa_shipping_variables import shipping_distances, get_cost
from aa_run_variables import eur_file

# Eingabe- und Ausgabedateien
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" 
#output_file_old = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050_pre05.nc"

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

#Platzhalter für den relevanten Code

new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2", "MA0 0 H2", "MA0 1 H2", "MR6 0 H2", "TN0 0 H2"]

shipping_distances_h2 = {
    (k[0].replace("NH3", "H2"), k[1].replace("NH3", "H2")): v
    for k, v in shipping_distances.items()
}

marginal_costs_by_distance = {
    (export, import_): get_cost(km, "H2-flüssig") * km if km is not None else None
    for (export, import_), km in shipping_distances_h2.items()
}


##Shipping Links hinzufügen

for (export_bus, import_bus), marginal_cost in marginal_costs_by_distance.items():
    if export_bus not in n.buses.index:
        print(f"⚠️ Export-Bus {export_bus} nicht im Netzwerk.")
        continue
    if import_bus not in n.buses.index:
        print(f"⚠️ Import-Bus {import_bus} nicht im Netzwerk.")
        continue

    link_name = f"{export_bus} to {import_bus} shipping-lh2"

    n.add(
        "Link",
        link_name,
        bus0=export_bus,
        bus1=import_bus,
        #bus2="co2 atmosphere",  # falls gewünscht, sonst weglassen
        #bus3=np.nan,
        #bus4=np.nan,
        carrier="shipping-lh2",
        efficiency=1.0,
        efficiency2=1.0,
        efficiency3=1.0,
        efficiency4=1.0,
        capital_cost=0.0,
        marginal_cost=marginal_cost,
        p_nom=500000.0,
        p_nom_extendable=True,
        p_nom_min=0.0,
        p_nom_max=np.inf,
        p_set=0.0,
        p_min_pu=0.0,
        p_max_pu=1.0,
        committable=False,
        start_up_cost=0.0,
        shut_down_cost=0.0,
        min_up_time=0,
        min_down_time=0,
        up_time_before=1,
        down_time_before=0,
        ramp_limit_start_up=1.0,
        ramp_limit_shut_down=1.0,
        reversed=False,
        #length=np.nan,  # falls notwendig
        terrain_factor=1.0,
        #length_original=np.nan,
    )


# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre07" + ext

# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk mit LH2-Shipping erfolgreich gespeichert unter:\n{eur_file}")
