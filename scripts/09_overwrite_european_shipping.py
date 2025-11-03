import pypsa
import numpy as np
import pandas as pd
import os
import re

from aa_shipping_variables import shipping_distances_eur, get_cost
from aa_run_variables import eur_file

# Eingabe- und Ausgabedateien
#eur_file = r"/home/student_01/Student_Folders/Maik/pypsa-eur/resources/04/networks/base_s_20___2050.nc" 
#output_file_old = r"C:\Users\maiks\pypsa-eur\resources\networks\base_s_39_Co2L0.00_Co2L0.00_2050_pre05.nc"

# Netzwerke laden
n = pypsa.Network(eur_file)
n_copy = pypsa.Network(eur_file)

#Platzhalter für den relevanten Code

new_cost_links = [
    "methanol transport BE0 0 -> GB2 0",
    "methanol transport DE0 0 -> GB2 0", 
    "methanol transport DE0 0 -> NO1 0", 
    "methanol transport DE0 0 -> SE1 0", 
    "methanol transport DK0 0 -> GB2 0", 
    "methanol transport DK0 0 -> NO1 0",
    "methanol transport DK0 0 -> SE1 0",
    "methanol transport DK1 0 -> SE1 0",
    "methanol transport FR0 0 -> GB2 0",
    "methanol transport FR0 0 -> IE3 0",
    "methanol transport GB2 0 -> GB3 0",
    "methanol transport GB2 0 -> IE3 0",
    "methanol transport GB2 0 -> NL0 0",
    "methanol transport GB2 0 -> NO1 0",
    "methanol transport NL0 0 -> NO1 0",
    "methanol transport GB2 0 -> BE0 0",
    "methanol transport GB2 0 -> DE0 0", 
    "methanol transport NO1 0 -> DE0 0",
    "methanol transport SE1 0 -> DE0 0", 
    "methanol transport GB2 0 -> DK0 0", 
    "methanol transport NO1 0 -> DK0 0",
    "methanol transport SE1 0 -> DK0 0",
    "methanol transport SE1 0 -> DK1 0",
    "methanol transport GB2 0 -> FR0 0",
    "methanol transport IE3 0 -> FR0 0",
    "methanol transport GB3 0 -> GB2 0",
    "methanol transport IE3 0 -> GB2 0",
    "methanol transport NL0 0 -> GB2 0",
    "methanol transport NO1 0 -> GB2 0",
    "methanol transport NO1 0 -> NL0 0",
    ]

marginal_costs_by_distance = {
    (export, import_): get_cost(km, "Methanol") * km if km is not None else None
    for (export, import_), km in shipping_distances_eur.items()
}

for link_name in new_cost_links:
    # Busnamen aus dem Link-String extrahieren
    match = re.match(r"methanol transport ([A-Z0-9 ]+) -> ([A-Z0-9 ]+)", link_name)
    if not match:
        print(f"⚠️ Konnte Busnamen nicht parsen: {link_name}")
        continue

    bus0, bus1 = match.groups()
    pair = (bus0, bus1)

    # Nachschauen, ob es einen Eintrag im Dict gibt
    if pair not in marginal_costs_by_distance:
        print(f"⚠️ Kein Eintrag im marginal_costs_by_distance für {pair}")
        continue

    value = marginal_costs_by_distance[pair]

    # Wenn der Link existiert, marginal_cost setzen
    if link_name in n.links.index:
        n.links.loc[link_name, "marginal_cost"] = value
        print(f"✅ {link_name}: marginal_cost = {value:.4f} €/MWh")
    else:
        print(f"❌ Link nicht im Netzwerk gefunden: {link_name}")

for i, row in n.buses[n.buses.index.str.contains("H2")].iterrows():
    if pd.isna(row["location"]) or row["location"] == "":
        n.buses.at[i, "location"] = i[:5]

### Methanol Transport via Land in Maghreb region
def create_network_topology(
    n, prefix, carriers=["DC"], connector=" -> ", bidirectional=True
):
    """
    Create a network topology from transmission lines and link carrier
    selection.

    Parameters
    ----------
    n : pypsa.Network
    prefix : str
    carriers : list-like
    connector : str
    bidirectional : bool, default True
        True: one link for each connection
        False: one link for each connection and direction (back and forth)

    Returns
    -------
    pd.DataFrame with columns bus0, bus1, length, underwater_fraction
    """

    ln_attrs = ["bus0", "bus1", "length"]
    lk_attrs = ["bus0", "bus1", "length", "underwater_fraction"]
    lk_attrs = n.links.columns.intersection(lk_attrs)
    #print(lk_attrs)

    candidates = pd.concat(
        [n.lines[ln_attrs], n.links.loc[n.links.carrier.isin(carriers), lk_attrs]]
    ).fillna(0)
    #print("candidates before:", candidates)
    
    # base network topology purely on location not carrier
    candidates["bus0"] = candidates.bus0.map(n.buses.location)
    candidates["bus1"] = candidates.bus1.map(n.buses.location)

    positive_order = candidates.bus0 < candidates.bus1
    candidates_p = candidates[positive_order]
    swap_buses = {"bus0": "bus1", "bus1": "bus0"}
    candidates_n = candidates[~positive_order].rename(columns=swap_buses)
    candidates = pd.concat([candidates_p, candidates_n])
    #print("candidates after:", candidates)

    def make_index(c):
        return prefix + c.bus0 + connector + c.bus1

    topo = candidates.groupby(["bus0", "bus1"], as_index=False).mean()
    #print("topo:", topo)
    topo.index = topo.apply(make_index, axis=1)

    if not bidirectional:
        topo_reverse = topo.copy()
        topo_reverse.rename(columns=swap_buses, inplace=True)
        topo_reverse.index = topo_reverse.apply(make_index, axis=1)
        topo = pd.concat([topo, topo_reverse])
        print("bidirectional")

    return topo

methanol_transport = create_network_topology(
            n, "methanol transport ", carriers=["H2 pipeline"],  
            bidirectional=False
        )

links_to_drop = [
    "methanol transport  -> ",
    "methanol transport MA0 1 -> ES0 0",
    "methanol transport TN0 0 -> IT0 0",
    "methanol transport ES0 0 -> DZ0 5",
    "methanol transport ES0 0 -> MA0 1",
    "methanol transport IT0 0 -> TN0 0",
    "methanol transport DZ0 5 -> ES0 0",
]

methanol_transport = methanol_transport.drop(index=links_to_drop, errors="ignore")


n.add(
            "Link",
            methanol_transport.index,
            bus0=methanol_transport.bus0 + " methanol",
            bus1=methanol_transport.bus1 + " methanol",
            p_nom_extendable=True,
            p_nom=5e4,
            length=methanol_transport.length,
            marginal_cost= 0.0146 #methanol_options["transport_cost"]
            * methanol_transport.length,
            carrier="methanol transport",
        )

### Oil Transport added
oil_transport = create_network_topology(
            n, "oil transport ", carriers=["H2 pipeline"],  
            bidirectional=False
        )

links_to_drop = [
    "oil transport  -> ",
    "oil transport MA0 1 -> ES0 0",
    "oil transport TN0 0 -> IT0 0",
    "oil transport ES0 0 -> DZ0 5",
    "oil transport ES0 0 -> MA0 1",
    "oil transport IT0 0 -> TN0 0",
    "oil transport DZ0 5 -> ES0 0",
]

oil_transport = oil_transport.drop(index=links_to_drop, errors="ignore")

n.add(
            "Link",
            oil_transport.index,
            bus0=oil_transport.bus0 + " oil",
            bus1=oil_transport.bus1 + " oil",
            p_nom_extendable=True,
            p_nom=5e4,
            length=oil_transport.length,
            marginal_cost= 0.0067 #methanol_options["transport_cost"]
            * oil_transport.length,
            carrier="oil transport",
        )

###Oil Shipping in Europe overwritten
new_cost_links_oil = [link.replace("methanol", "oil") for link in new_cost_links]

marginal_costs_by_distance = {
    (export, import_): get_cost(km, "Blue Crude") * km if km is not None else None
    for (export, import_), km in shipping_distances_eur.items()
}

"""
def replace_shipping_link_costs(
        
):
    for link_name in new_cost_links:
        # Busnamen aus dem Link-String extrahieren
        match = re.match(r"methanol transport ([A-Z0-9 ]+) -> ([A-Z0-9 ]+)", link_name)
        if not match:
            print(f"⚠️ Konnte Busnamen nicht parsen: {link_name}")
            continue

        bus0, bus1 = match.groups()
        pair = (bus0, bus1)

        # Nachschauen, ob es einen Eintrag im Dict gibt
        if pair not in marginal_costs_by_distance:
            print(f"⚠️ Kein Eintrag im marginal_costs_by_distance für {pair}")
            continue

        value = marginal_costs_by_distance[pair]

        # Wenn der Link existiert, marginal_cost setzen
        if link_name in n.links.index:
            n.links.loc[link_name, "marginal_cost"] = value
            print(f"✅ {link_name}: marginal_cost = {value:.4f} €/MWh")
        else:
            print(f"❌ Link nicht im Netzwerk gefunden: {link_name}")
        
        return 
"""

for link_name in new_cost_links_oil:
    # Busnamen aus dem Link-String extrahieren
    match = re.match(r"oil transport ([A-Z0-9 ]+) -> ([A-Z0-9 ]+)", link_name)
    if not match:
        print(f"⚠️ Konnte Busnamen nicht parsen: {link_name}")
        continue

    bus0, bus1 = match.groups()
    pair = (bus0, bus1)

    # Nachschauen, ob es einen Eintrag im Dict gibt
    if pair not in marginal_costs_by_distance:
        print(f"⚠️ Kein Eintrag im marginal_costs_by_distance für {pair}")
        continue

    value = marginal_costs_by_distance[pair]

    # Wenn der Link existiert, marginal_cost setzen
    if link_name in n.links.index:
        n.links.loc[link_name, "marginal_cost"] = value
        print(f"✅ {link_name}: marginal_cost = {value:.4f} €/MWh")
    else:
        print(f"❌ Link nicht im Netzwerk gefunden: {link_name}")

for i, row in n.buses[n.buses.index.str.contains("H2")].iterrows():
    if pd.isna(row["location"]) or row["location"] == "":
        n.buses.at[i, "location"] = i[:5]

### Ammonia Transport added
ammonia_transport = create_network_topology(
            n, "ammonia transport ", carriers=["H2 pipeline"],  
            bidirectional=False
        )

links_to_drop = [
    "ammonia transport  -> ",
    "ammonia transport MA0 1 -> ES0 0",
    "ammonia transport TN0 0 -> IT0 0",
    "ammonia transport ES0 0 -> DZ0 5",
    "ammonia transport ES0 0 -> MA0 1",
    "ammonia transport IT0 0 -> TN0 0",
    "ammonia transport DZ0 5 -> ES0 0",
]

ammonia_transport = ammonia_transport.drop(index=links_to_drop, errors="ignore")

n.add(
            "Link",
            ammonia_transport.index,
            bus0=ammonia_transport.bus0 + " NH3",
            bus1=ammonia_transport.bus1 + " NH3",
            p_nom_extendable=True,
            p_nom=5e4,
            length=ammonia_transport.length,
            marginal_cost=  0.0247 #ChatGPT Annahme, mit Aufwandfaktor von 1.2#0.0067 #methanol_options["transport_cost"]
            * ammonia_transport.length,
            carrier="ammonia transport",
        )

###Ammonia Shipping in Europe overwritten
new_cost_links_ammonia = [link.replace("methanol", "ammonia") for link in new_cost_links]

marginal_costs_by_distance = {
    (export, import_): get_cost(km, "Ammoniak") * km if km is not None else None
    for (export, import_), km in shipping_distances_eur.items()
}

for link_name in new_cost_links_ammonia:
    # Busnamen aus dem Link-String extrahieren
    match = re.match(r"ammonia transport ([A-Z0-9 ]+) -> ([A-Z0-9 ]+)", link_name)
    if not match:
        print(f"⚠️ Konnte Busnamen nicht parsen: {link_name}")
        continue

    bus0, bus1 = match.groups()
    pair = (bus0, bus1)

    # Nachschauen, ob es einen Eintrag im Dict gibt
    if pair not in marginal_costs_by_distance:
        print(f"⚠️ Kein Eintrag im marginal_costs_by_distance für {pair}")
        continue

    value = marginal_costs_by_distance[pair]

    # Wenn der Link existiert, marginal_cost setzen
    if link_name in n.links.index:
        n.links.loc[link_name, "marginal_cost"] = value
        print(f"✅ {link_name}: marginal_cost = {value:.4f} €/MWh")
    else:
        print(f"❌ Link nicht im Netzwerk gefunden: {link_name}")

# Suffix "_old" einfügen
base, ext = os.path.splitext(eur_file)
eur_file_old = base + "_pre09" + ext

# Neues Netzwerk speichern
n.export_to_netcdf(eur_file)

#Altes Netzwerk speichern
n_copy.export_to_netcdf(eur_file_old)

print(f"European Shipping costs overwritten, Methanol and Oil Transport by Truck enabled and Network saved as :\n{eur_file}")
