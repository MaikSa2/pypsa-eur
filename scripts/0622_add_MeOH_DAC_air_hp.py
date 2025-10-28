import pypsa
import numpy as np
import pandas as pd
import os
import xarray as xr

from aa_shipping_variables import shipping_distances, get_cost
from aa_run_variables import eur_file

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

#Methanol Busse
# Ziel-Busse für neue Methanoliliserungs-Links
new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2","DZ0 0 H2", "DZ0 1 H2","DZ0 3 H2", "DZ0 4 H2",#"DZ1 0 H2", 
                "DZ5 0 H2", "MA0 0 H2", "MA0 1 H2","MA0 2 H2", #"MA4 0 H2", 
                "MR6 0 H2", "MR2 0 H2","MR3 0 H2", "TN0 0 H2"]

for h2_bus in new_h2_buses:
    # Namen für den neuen methanol-Bus generieren
    meoh_bus = h2_bus.replace("H2", "methanol")

    # Referenzbusdaten laden
    ref_bus = n.buses.loc[h2_bus]

    # Neuen Methanol-Bus hinzufügen
    n.add("Bus",
          meoh_bus,
          carrier="methanol",
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

### Methanol Stores hinzufügen
# Template-Store-Daten holen
template_link = n.stores.loc["IT0 0 methanol Store"]

for h2_bus in new_h2_buses:
    # Namen für den exisitierenden MEOH Bus generieren
    meoh_bus = h2_bus.replace("H2", "methanol")

    # Falls der Store noch nicht existiert:
    if meoh_bus not in n.stores.index:
        # Store hinzufügen, basierend auf den Template-Werten
        n.add(
            "Store",
            meoh_bus,
            bus=meoh_bus,  # muss bereits im Netzwerk existieren!
            carrier=template_link.carrier,
            e_nom=template_link.e_nom,
            e_min_pu=template_link.e_min_pu,
            e_max_pu=template_link.e_max_pu,
            e_cyclic=template_link.e_cyclic,
            capital_cost=template_link.capital_cost,
            marginal_cost=template_link.marginal_cost,
            e_nom_extendable = template_link.e_nom_extendable
        )

#Urban central heat Busse
# Ziel-Busse für neue Urban Central heat Busse
#new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2", "MA0 0 H2", "MA0 1 H2", "MR6 0 H2", "TN0 0 H2"]

### Heat Busse hinzufügen
for h2_bus in new_h2_buses:
    # Namen für den neuen methanol-Bus generieren
    heat_bus = h2_bus.replace("H2", "urban central heat")

    # Referenzbusdaten laden
    ref_bus = n.buses.loc[h2_bus]

    # Neuen Heat-Bus hinzufügen
    n.add("Bus",
          heat_bus,
          carrier="urban central heat",
          location=ref_bus.location,     #wird hier schon beim H2 Bus nicht richtig eingefügt. Könnte evtl. für Plots später wichtig werden
          lat=ref_bus.lat,
          lon=ref_bus.lon,
          country=ref_bus.country,
          #tag_area=ref_bus.get("tag_area", 0.0),
          #tag_substation=ref_bus.get("tag_substation", ""),
          #tag_substation_lv=ref_bus.get("tag_substation_lv", ""),
          x=ref_bus.x,
          y=ref_bus.y,
          #v_nom=1.0,  # üblich für Flüssigkraftstoffträger
          #control="PQ",
          unit="MWh_th"
    ) 

### CO2 Busse hinzufügen
for h2_bus in new_h2_buses:
    # Namen für den neuen co2-Bus generieren
    co2_bus = h2_bus.replace("H2", "co2 stored")

    # Referenzbusdaten laden
    ref_bus = n.buses.loc[h2_bus]

    # Neuen CO2 Bus hinzufügen
    n.add("Bus",
          co2_bus,
          carrier="co2 stored",
          location=ref_bus.location,     #wird hier schon beim H2 Bus nicht richtig eingefügt. Könnte evtl. für Plots später wichtig werden
          lat=ref_bus.lat,
          lon=ref_bus.lon,
          country=ref_bus.country,
          x=ref_bus.x,
          y=ref_bus.y,
          unit="t_co2"
    ) 

### CO2 Stores hinzufügen
# Template-Store-Daten holen
template_link = n.stores.loc["IT0 0 co2 stored"]

for h2_bus in new_h2_buses:
    # Namen für den neuen CO2-Bus generieren
    co2_bus = h2_bus.replace("H2", "co2 stored")

    # Falls der Store noch nicht existiert:
    if co2_bus not in n.stores.index:
        # Store hinzufügen, basierend auf den Template-Werten
        n.add(
            "Store",
            co2_bus,
            bus=co2_bus,  # muss bereits im Netzwerk existieren!
            carrier=template_link.carrier,
            e_nom=template_link.e_nom,
            e_min_pu=template_link.e_min_pu,
            e_max_pu=template_link.e_max_pu,
            e_cyclic=template_link.e_cyclic,
            capital_cost=template_link.capital_cost,
            marginal_cost=template_link.marginal_cost,
            e_nom_extendable = template_link.e_nom_extendable
        )

### Neue low voltage Busse hinzufügen
for h2_bus in new_h2_buses:
    # Namen für den neuen methanol-Bus generieren
    heat_bus = h2_bus.replace("H2", "low voltage")

    # Referenzbusdaten laden
    ref_bus = n.buses.loc[h2_bus]

    # Neuen Heat-Bus hinzufügen
    n.add("Bus",
          heat_bus,
          carrier="low voltage",
          location=ref_bus.location,     #wird hier schon beim H2 Bus nicht richtig eingefügt. Könnte evtl. für Plots später wichtig werden
          lat=ref_bus.lat,
          lon=ref_bus.lon,
          country=ref_bus.country,
          #tag_area=ref_bus.get("tag_area", 0.0),
          #tag_substation=ref_bus.get("tag_substation", ""),
          #tag_substation_lv=ref_bus.get("tag_substation_lv", ""),
          x=ref_bus.x,
          y=ref_bus.y,
          #v_nom=1.0,  # üblich für Flüssigkraftstoffträger
          #control="PQ",
          unit="MWh_el"
    ) 

## Low voltage Links hinzufügen
# Referenz-Link
template_link = n.links.loc["IT0 0 electricity distribution grid"]
#candidate_bus1 = n.buses[n.buses.index.str.contains("low voltage", case=False)].index

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " electricity distribution grid")

    #matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    #if not matching_bus1:
        #print(f"⚠️ Kein passender Heat-Bus für {h2_bus} gefunden.")
        #continue

    elec_bus = h2_bus.replace(" H2", "")
    lv_bus = h2_bus.replace(" H2", " low voltage")
    #electricity_bus = h2_bus.replace(" H2", "")
    #hydrogen_bus = h2_bus
    #meoh_bus = matching_bus1

    # Link-Daten aus Template kopieren und anpassen
    data = template_link.copy()

    data["bus0"] = elec_bus #allgemeiner Bus um Gas zu beziehen
    data["bus1"] = lv_bus  #Heat_bus wo alles reinkommt
    data["bus2"] = np.nan  #der Gas boiler emittiert CO2
    # Falls du weitere Busse hinzufügen willst, z.B. bus3, bus4:
    data["bus3"] = np.nan #None 
    data["bus4"] = np.nan
    #data["efficiency2"] = 0.198

    # Link einzeln hinzufügen
    n.add("Link", name=link_name, **data.to_dict())

## air heat pump Links hinzufügen
# Referenz-Link
template_link = n.links.loc["IT0 0 urban central air heat pump"]
#candidate_bus1 = n.buses[n.buses.index.str.contains("urban central heat", case=False)].index

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " urban central air heat pump")

    #matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    #if not matching_bus1:
        #print(f"⚠️ Kein passender Heat-Bus für {h2_bus} gefunden.")
        #continue

    lv_bus = h2_bus.replace(" H2", " low voltage")
    heat_bus = h2_bus.replace(" H2", " urban central heat")
    #electricity_bus = h2_bus.replace(" H2", "")
    #hydrogen_bus = h2_bus
    #meoh_bus = matching_bus1

    # Link-Daten aus Template kopieren und anpassen
    data = template_link.copy()

    data["bus0"] = lv_bus #"EU gas" #allgemeiner Bus um Gas zu beziehen
    data["bus1"] = heat_bus  #Heat_bus wo alles reinkommt
    #data["bus2"] = "co2 atmosphere"  #der Gas boiler emittiert CO2
    # Falls du weitere Busse hinzufügen willst, z.B. bus3, bus4:
    data["bus3"] = np.nan #None 
    data["bus4"] = np.nan
    #data["efficiency2"] = 0.198

    # Link einzeln hinzufügen
    n.add("Link", name=link_name, **data.to_dict())


### Zeitabhängige Effizienzen

cop_profiles_file = r"/home/student_01/Student_Folders/Maik/cop_profiles_air_hp_maghreb.nc"
cop = xr.open_dataarray(cop_profiles_file)

cop_pd = (
    cop#.sel(
        #heat_system=heat_system.system_type.value,
        #heat_source=heat_source,
        #name=nodes,
    #)
    .to_pandas()
    .reindex(index=n.snapshots)
)

###Zeitabhängigkeiten der Links ermöglichen
for h2_bus in new_h2_buses:
    link = h2_bus.replace(" H2", " urban central air heat pump")

    if hasattr(n.links_t, "p0") and link not in n.links_t.p0.columns:
        n.links_t.p0[link] = 0.0

    if hasattr(n.links_t, "p1") and link not in n.links_t.p1.columns:
        n.links_t.p1[link] = 0.0

    if hasattr(n.links_t, "efficiency") and link not in n.links_t.efficiency.columns:
        n.links_t.efficiency[link] = 0.0

print("Neue Links in links_t hinzugefügt.")

# Ausgangsliste (ohne Suffix in cop_pd)
#new_h2_buses = ["DZ0 2 H2", "DZ0 5 H2","DZ0 0 H2", "DZ0 1 H2","DZ0 3 H2", "DZ0 4 H2","DZ1 0 H2", "DZ5 0 H2", "MA0 0 H2", "MA0 1 H2","MA0 2 H2", "MA4 0 H2", "MR6 0 H2", "MR2 0 H2","MR3 0 H2", "TN0 0 H2"]
new_buses =    ["DZ0 2", "DZ0 5", "DZ0 0", "DZ0 1","DZ0 3", "DZ0 4", "DZ1 0", "DZ5 0", "MA0 0", "MA0 1", "MA0 2", "MA4 0", "MR6 0", "MR2 0", "MR3 0", "TN0 0"]
suffix = "urban central air heat pump"

# Mapping: Spaltenname in cop_pd  ->  Spaltenname in n.links_t.efficiency
#rename_map = {bus: bus.replace("H2", suffix) for bus in new_h2_buses}
rename_map = {
    bus: (bus + " " + suffix) if not bus.endswith(suffix) else bus
    for bus in new_buses
}

# 1) Spalten in cop_pd umbenennen
cop_pd_renamed = cop_pd.rename(columns=rename_map)

# 2) Zeitindex sauber an die Snapshots ausrichten
#cop_pd_renamed = cop_pd_renamed.reindex(index=n.snapshots)

# 3) Nur Spalten überschreiben, die es in n.links_t.efficiency wirklich gibt
target_cols = [c for c in cop_pd_renamed.columns if c in n.links_t.efficiency.columns]

# 4) Werte rüberkopieren (zeitabhängig)
n.links_t.efficiency[target_cols] = cop_pd_renamed[target_cols]



## DAC Links hinzufügen
# Referenz-Link
template_link = n.links.loc["IT0 0 urban central DAC"]
#candidate_bus1 = n.buses[n.buses.index.str.contains("co2 stored", case=False)].index

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " urban central DAC")

    #matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    #if not matching_bus1:
        #print(f"⚠️ Kein passender co2-Bus für {h2_bus} gefunden.")
        #continue

    heat_bus = h2_bus.replace(" H2", " urban central heat")
    co2_stored_bus = h2_bus.replace(" H2", " co2 stored")
    electricity_bus = h2_bus.replace(" H2", "")
    #hydrogen_bus = h2_bus
    #meoh_bus = matching_bus1

    # Link-Daten aus Template kopieren und anpassen
    data = template_link.copy()

    data["bus0"] = electricity_bus #" #hydrogen_bus      # H2
    data["bus1"] = heat_bus  #meoh_bus              # methanol
    data["bus2"] = "co2 atmosphere"  
    data["bus3"] = co2_stored_bus 
    data["bus4"] = np.nan
    #data["efficiency2"] = 0.198

    # Link einzeln hinzufügen
    n.add("Link", name=link_name, **data.to_dict()) #overwrite=True

## Methanolisierungs-Links hinzufügen
# Referenz-Link
template_link = n.links.loc["IT0 0 methanolisation"]
candidate_bus1 = n.buses[n.buses.index.str.contains("methanol", case=False)].index

for h2_bus in new_h2_buses:
    region_prefix = h2_bus.split()[0][:2]
    link_name = h2_bus.replace(" H2", " methanolisation")

    #matching_bus1 = next((b for b in candidate_bus1 if b.startswith(region_prefix)), None)
    #if not matching_bus1:
        #print(f"⚠️ Kein passender Methanol-Bus für {h2_bus} gefunden.")
        #continue

    electricity_bus = h2_bus.replace(" H2", "")
    hydrogen_bus = h2_bus
    #meoh_bus = matching_bus1
    meoh_bus = h2_bus.replace(" H2", " methanol")
    co2_stored_bus = h2_bus.replace(" H2", " co2 stored")

    # Link-Daten aus Template kopieren und anpassen
    data = template_link.copy()

    data["bus0"] = hydrogen_bus      # H2
    data["bus1"] = meoh_bus              # methanol
    data["bus2"] = electricity_bus         # H2
    # Falls du weitere Busse hinzufügen willst, z.B. bus3, bus4:
    data["bus3"] = co2_stored_bus #angepasst auf die lokalen co2 stored-Busse
    data["bus4"] = np.nan
    #data["efficiency4"] = 1.0

    # Link einzeln hinzufügen
    n.add("Link", name=link_name, **data.to_dict())


## Shipping Links hinzufügen

#NH3_export_buses = ["DZ0 2 NH3", "DZ0 5 NH3", "MA0 0 NH3", "MA0 1 NH3", "MR6 0 NH3", "TN0 0 NH3"]
#NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3","IE3 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "NO1 0 NH3", "PT0 0 NH3", "SE1 0 NH3"]
#reduced_NH3_import_buses = ["BE0 0 NH3", "DE0 0 NH3", "DK0 0 NH3", "ES0 0 NH3", "FR0 0 NH3", "GB2 0 NH3", "IT0 0 NH3", "NL0 0 NH3", "SE1 0 NH3"]

shipping_distances_meoh = {
    (k[0].replace("NH3", "methanol"), k[1].replace("NH3", "methanol")): v
    for k, v in shipping_distances.items()
}

#euro_per_km = 30 / 2400  # 0.0125 €/MWh/km
#euro_per_km = 1.87 / 1200 #0.0016 €/MWh/km
#euro_per_km = 0.3 / 4000  # 0.000075 €/MWh/km
#euro_per_km = 0.0010 #pi mal Daumen dazwischen interpoliert

marginal_costs_by_distance = {
    (export, import_): get_cost(km, "Methanol") * km if km is not None else None
    for (export, import_), km in shipping_distances_meoh.items()
}
'''
#Just linear cost assumption
marginal_costs_by_distance = {
    (export, import_): round(euro_per_km * km, 2)
    for (export, import_), km in shipping_distances_meoh.items()
}
'''

##Shipping Links hinzufügen

for (export_bus, import_bus), marginal_cost in marginal_costs_by_distance.items():
    if export_bus not in n.buses.index:
        print(f"⚠️ Export-Bus {export_bus} nicht im Netzwerk.")
        continue
    if import_bus not in n.buses.index:
        print(f"⚠️ Import-Bus {import_bus} nicht im Netzwerk.")
        continue

    link_name = f"{export_bus} to {import_bus} shipping-meoh"

    n.add(
        "Link",
        link_name,
        bus0=export_bus,
        bus1=import_bus,
        #bus2="co2 atmosphere",  # falls gewünscht, sonst weglassen
        #bus3=np.nan,
        #bus4=np.nan,
        carrier="shipping-meoh",
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
eur_file_old = base + "_pre062_meoh_DAC_air_hp" + ext

print(n.links["efficiency"].apply(type).value_counts())
n.links["efficiency"] = n.links["efficiency"].astype("float64")
print(n.links["efficiency"].apply(type).value_counts())
# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"Script 0622_add_MeOH_DAC_air_hp.py carried out")
print(f"Netzwerk erfolgreich gespeichert unter:\n{eur_file}")
