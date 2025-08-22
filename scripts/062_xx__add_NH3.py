import pypsa
import numpy as np
import pandas as pd
import os

# Eingabe- und Ausgabedateien
eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/02/networks/base_s_20___2050.nc" 
#output_file_old = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050_pre05.nc"

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)


#Ammoniak Busse
# Ziel-Busse für neue Ammoniak-Links
new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2", "MA0 0 H2", "MA0 1 H2", "MR6 0 H2", "TN0 0 H2"]

for h2_bus in new_h2_buses:
    # Namen für den neuen Ammonia-Bus generieren
    meoh_bus = h2_bus.replace("H2", "NH3")

    # Referenzbusdaten laden
    ref_bus = n.buses.loc[h2_bus]

    # Neuen Ammonia-Bus hinzufügen
    n.add("Bus",
          meoh_bus,
          carrier="NH3",
          location=ref_bus.location,
          lat=ref_bus.lat,
          lon=ref_bus.lon,
          country=ref_bus.country,
          tag_area=ref_bus.get("tag_area", 0.0),
          tag_substation=ref_bus.get("tag_substation", ""),
          tag_substation_lv=ref_bus.get("tag_substation_lv", ""),
          x=ref_bus.x,
          y=ref_bus.y,
          v_nom=1.0,  # üblich für Flüssigkraftstoffträger
          control="PQ"
    )

## Haber Bosch Links hinzufügen
# Referenz-Link

template_link = n.links.loc["IT0 0 Haber-Bosch"]
candidate_bus1 = n.buses[n.buses.index.str.contains("NH3", case=False)].index

new_links = pd.DataFrame(columns=n.links.columns)

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " Haber-Bosch")

    matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    if not matching_bus1:
        print(f"⚠️ Kein passender NH3-Bus für {h2_bus} gefunden.")
        continue

    electricity_bus = h2_bus.replace(" H2", "")
    hydrogen_bus = h2_bus
    nh3_bus = matching_bus1

    # Link manuell aufbauen, basierend auf template
    new_row = pd.Series(template_link)

    new_row["bus0"] = electricity_bus      # Strom
    new_row["bus1"] = nh3_bus              # NH3
    new_row["bus2"] = hydrogen_bus         # H2
    #new_row["bus3"] = np.nan               # CO2 leer
    #new_row["bus4"] = np.nan
    new_row["efficiency4"] = 1.0

    new_links.loc[link_name] = new_row

n.links = pd.concat([n.links, new_links])



## Shipping Links hinzufügen

NH3_export_buses = ["DZ0 2 NH3", "DZ0 5 NH3", "MA0 0 NH3", "MA0 1 NH3", "MR6 0 NH3", "TN0 0 NH3"]
NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3","IE3 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "NO1 0 NH3", "PT0 0 NH3", "SE1 0 NH3"]
reduced_NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "SE1 0 NH3"]


shipping_distances = {
    # DZ0 2 NH3
    ("DZ0 2 NH3", "BE0 0 NH3"): 4000,
    ("DZ0 2 NH3", "DE0 0 NH3"): 6000,
    ("DZ0 2 NH3", "DK0 0 NH3"): 5500,
    ("DZ0 2 NH3", "ES0 0 NH3"): 500,
    ("DZ0 2 NH3", "FR0 0 NH3"): 1000,
    ("DZ0 2 NH3", "GB2 0 NH3"): 5500,
    ("DZ0 2 NH3", "IE3 0 NH3"): 6000,
    ("DZ0 2 NH3", "IT0 0 NH3"): 750,
    ("DZ0 2 NH3", "NL0 0 NH3"): 4500,
    ("DZ0 2 NH3", "NO1 0 NH3"): 8000,
    ("DZ0 2 NH3", "PT0 0 NH3"): 2000,
    ("DZ0 2 NH3", "SE1 0 NH3"): 8000,

    # DZ0 5 NH3
    ("DZ0 5 NH3", "BE0 0 NH3"): 4100,
    ("DZ0 5 NH3", "DE0 0 NH3"): 6100,
    ("DZ0 5 NH3", "DK0 0 NH3"): 5600,
    ("DZ0 5 NH3", "ES0 0 NH3"): 600,
    ("DZ0 5 NH3", "FR0 0 NH3"): 1100,
    ("DZ0 5 NH3", "GB2 0 NH3"): 5600,
    ("DZ0 5 NH3", "IE3 0 NH3"): 6100,
    ("DZ0 5 NH3", "IT0 0 NH3"): 850,
    ("DZ0 5 NH3", "NL0 0 NH3"): 4600,
    ("DZ0 5 NH3", "NO1 0 NH3"): 8100,
    ("DZ0 5 NH3", "PT0 0 NH3"): 2100,
    ("DZ0 5 NH3", "SE1 0 NH3"): 8100,    

    # MA0 0 NH3
    ("MA0 0 NH3", "BE0 0 NH3"): 4100,
    ("MA0 0 NH3", "DE0 0 NH3"): 6100,
    ("MA0 0 NH3", "DK0 0 NH3"): 5600,
    ("MA0 0 NH3", "ES0 0 NH3"): 600,
    ("MA0 0 NH3", "FR0 0 NH3"): 1200,
    ("MA0 0 NH3", "GB2 0 NH3"): 5600,
    ("MA0 0 NH3", "IE3 0 NH3"): 6100,
    ("MA0 0 NH3", "IT0 0 NH3"): 850,
    ("MA0 0 NH3", "NL0 0 NH3"): 4600,
    ("MA0 0 NH3", "NO1 0 NH3"): 8100,
    ("MA0 0 NH3", "PT0 0 NH3"): 2100,
    ("MA0 0 NH3", "SE1 0 NH3"): 8100,

    # MA0 1 NH3
    ("MA0 1 NH3", "BE0 0 NH3"): 4300,
    ("MA0 1 NH3", "DE0 0 NH3"): 6300,
    ("MA0 1 NH3", "DK0 0 NH3"): 5800,
    ("MA0 1 NH3", "ES0 0 NH3"): 800,
    ("MA0 1 NH3", "FR0 0 NH3"): 1400,
    ("MA0 1 NH3", "GB2 0 NH3"): 5800,
    ("MA0 1 NH3", "IE3 0 NH3"): 6300,
    ("MA0 1 NH3", "IT0 0 NH3"): 1050,
    ("MA0 1 NH3", "NL0 0 NH3"): 4800,
    ("MA0 1 NH3", "NO1 0 NH3"): 8300,
    ("MA0 1 NH3", "PT0 0 NH3"): 2300,
    ("MA0 1 NH3", "SE1 0 NH3"): 8300,

    # MR6 0 NH3
    ("MR6 0 NH3", "BE0 0 NH3"): 4500,
    ("MR6 0 NH3", "DE0 0 NH3"): 6500,
    ("MR6 0 NH3", "DK0 0 NH3"): 6000,
    ("MR6 0 NH3", "ES0 0 NH3"): 1000,
    ("MR6 0 NH3", "FR0 0 NH3"): 1600,
    ("MR6 0 NH3", "GB2 0 NH3"): 6000,
    ("MR6 0 NH3", "IE3 0 NH3"): 6500,
    ("MR6 0 NH3", "IT0 0 NH3"): 1250,
    ("MR6 0 NH3", "NL0 0 NH3"): 5000,
    ("MR6 0 NH3", "NO1 0 NH3"): 8500,
    ("MR6 0 NH3", "PT0 0 NH3"): 2500,
    ("MR6 0 NH3", "SE1 0 NH3"): 8500,

        # TN0 0 NH3
    ("TN0 0 NH3", "BE0 0 NH3"): 4500,
    ("TN0 0 NH3", "DE0 0 NH3"): 6500,
    ("TN0 0 NH3", "DK0 0 NH3"): 6000,
    ("TN0 0 NH3", "ES0 0 NH3"): 700,
    ("TN0 0 NH3", "FR0 0 NH3"): 800,
    ("TN0 0 NH3", "GB2 0 NH3"): 6000,
    ("TN0 0 NH3", "IE3 0 NH3"): 6500,
    ("TN0 0 NH3", "IT0 0 NH3"): 200,
    ("TN0 0 NH3", "NL0 0 NH3"): 5000,
    ("TN0 0 NH3", "NO1 0 NH3"): 8500,
    ("TN0 0 NH3", "PT0 0 NH3"): 2500,
    ("TN0 0 NH3", "SE1 0 NH3"): 8500,
}

euro_per_km = 30 / 2400  # 0.0125 €/MWh/km

marginal_costs_by_distance = {
    (export, import_): round(euro_per_km * km, 2)
    for (export, import_), km in shipping_distances.items()
}




# Leerer DataFrame für neue Links
new_links = pd.DataFrame(columns=n.links.columns)

for (export_bus, import_bus), marginal_cost in marginal_costs_by_distance.items():
    if export_bus not in n.buses.index:
        print(f"⚠️ Export-Bus {export_bus} nicht im Netzwerk.")
        continue
    if import_bus not in n.buses.index:
        print(f"⚠️ Import-Bus {import_bus} nicht im Netzwerk.")
        continue

    link_name = f"{export_bus} to {import_bus} shipping-nh3"

    new_links.loc[link_name] = {
        "bus0": export_bus,
        "bus1": import_bus,
        #"bus2": "co2 atmosphere",
        #"bus3": np.nan,
        #"bus4": np.nan,
        "carrier": "shipping-nh3",
        "efficiency": 1.0,
        "efficiency2": 1.0,
        "efficiency3": 1.0,
        "efficiency4": 1.0,
        "capital_cost": 0.0,
        "marginal_cost": marginal_cost,
        "p_nom": 500000.0,
        "p_nom_extendable": True,
        "p_nom_min": 0.0,
        "p_nom_max": np.inf,
        "p_set": 0.0,
        "p_min_pu": 0.0,
        "p_max_pu": 1.0,
        "committable": False,
        "start_up_cost": 0.0,
        "shut_down_cost": 0.0,
        "min_up_time": 0,
        "min_down_time": 0,
        "up_time_before": 1,
        "down_time_before": 0,
        "ramp_limit_start_up": 1.0,
        "ramp_limit_shut_down": 1.0,
        "reversed": False,
        #"length": np.nan,  # optional: später eintragen
        "terrain_factor": 1.0,
        #"length_original": np.nan,
    }

# Links hinzufügen
n.links = pd.concat([n.links, new_links])





# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre062" + ext

print(n.links["efficiency"].apply(type).value_counts())
n.links["efficiency"] = n.links["efficiency"].astype("float64")
print(n.links["efficiency"].apply(type).value_counts())
# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
