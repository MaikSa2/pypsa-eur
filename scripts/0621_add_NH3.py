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


#Ammoniak Busse
# Ziel-Busse für neue Ammoniak-Links
#new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2", "MA0 0 H2", "MA0 1 H2", "MR6 0 H2", "TN0 0 H2"]
new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2","DZ0 0 H2", "DZ0 1 H2","DZ0 3 H2", "DZ0 4 H2",#"DZ1 0 H2", 
                "DZ5 0 H2", "MA0 0 H2", "MA0 1 H2","MA0 2 H2", #"MA4 0 H2", 
                "MR6 0 H2", "MR2 0 H2","MR3 0 H2", "TN0 0 H2"]

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

### Ammonia Stores hinzufügen
# Template-Store-Daten holen
template_store = n.stores.loc["IT0 0 NH3 ammonia store"]

for h2_bus in new_h2_buses:
    # Namen für den exisitierenden MEOH Bus generieren
    nh3_bus = h2_bus.replace("H2", "NH3")

    # Falls der Store noch nicht existiert:
    if nh3_bus not in n.stores.index:
        # Store hinzufügen, basierend auf den Template-Werten
        n.add(
            "Store",
            nh3_bus + " ammonia store",
            bus=nh3_bus,  # muss bereits im Netzwerk existieren!
            carrier=template_store.carrier,
            e_nom=template_store.e_nom,
            e_min_pu=template_store.e_min_pu,
            e_max_pu=template_store.e_max_pu,
            e_cyclic=template_store.e_cyclic,
            capital_cost=template_store.capital_cost,
            marginal_cost=template_store.marginal_cost,
            e_nom_extendable = template_store.e_nom_extendable,
            lifetime = template_store.lifetime
        )

## Haber Bosch Links hinzufügen
# Referenz-Link
template_link = n.links.loc["IT0 0 Haber-Bosch"]
candidate_bus1 = n.buses[n.buses.index.str.contains("NH3", case=False)].index

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " Haber-Bosch")

    #matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    #if not matching_bus1:
    #    print(f"⚠️ Kein passender NH3-Bus für {h2_bus} gefunden.")
    #    continue

    electricity_bus = h2_bus.replace(" H2", "")
    hydrogen_bus = h2_bus
    nh3_bus = h2_bus.replace(" H2", " NH3")  #matching_bus1

    # Link-Daten aus Template kopieren und anpassen
    data = template_link.copy()

    data["bus0"] = electricity_bus      # Strom
    data["bus1"] = nh3_bus              # NH3
    data["bus2"] = hydrogen_bus         # H2
    # Falls du weitere Busse hinzufügen willst, z.B. bus3, bus4:
    data["bus3"] = np.nan #None 
    # data["bus4"] = np.nan
    data["efficiency4"] = 1.0

    # Link einzeln hinzufügen
    n.add("Link", name=link_name, **data.to_dict())



## Shipping Links hinzufügen

#NH3_export_buses = ["DZ0 2 NH3", "DZ0 5 NH3", "MA0 0 NH3", "MA0 1 NH3", "MR6 0 NH3", "TN0 0 NH3"]
#NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3","IE3 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "NO1 0 NH3", "PT0 0 NH3", "SE1 0 NH3"]
#reduced_NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "SE1 0 NH3"]

#euro_per_km = 30 / 2400  # 0.0125 €/MWh/km
'''
marginal_costs_by_distance = {
    (export, import_): round(euro_per_km * km, 2)
    for (export, import_), km in shipping_distances.items()
}
'''
marginal_costs_by_distance = {
    (export, import_): get_cost(km, "Ammoniak") * km if km is not None else None
    for (export, import_), km in shipping_distances.items()
}


##Shipping Links hinzufügen

for (export_bus, import_bus), marginal_cost in marginal_costs_by_distance.items():
    if export_bus not in n.buses.index:
        print(f"⚠️ Export-Bus {export_bus} nicht im Netzwerk.")
        continue
    if import_bus not in n.buses.index:
        print(f"⚠️ Import-Bus {import_bus} nicht im Netzwerk.")
        continue

    link_name = f"{export_bus} to {import_bus} shipping-nh3"

    n.add(
        "Link",
        link_name,
        bus0=export_bus,
        bus1=import_bus,
        #bus2="co2 atmosphere",  # falls gewünscht, sonst weglassen
        #bus3=np.nan,
        #bus4=np.nan,
        carrier="shipping-nh3",
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
eur_file_old = base + "_pre0621_NH3" + ext

print(n.links["efficiency"].apply(type).value_counts())
n.links["efficiency"] = n.links["efficiency"].astype("float64")
print(n.links["efficiency"].apply(type).value_counts())
# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Script 0621_add_NH3-py carried out")
print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
