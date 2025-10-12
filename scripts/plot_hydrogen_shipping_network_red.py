# SPDX-FileCopyrightText: Contributors to PyPSA-Eur <https://github.com/pypsa/pypsa-eur>
#
# SPDX-License-Identifier: MIT
"""
Creates map of optimised hydrogen network, storage and selected other
infrastructure.
"""

import logging

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import pypsa
from pypsa.plot import add_legend_circles, add_legend_lines, add_legend_patches

from scripts._helpers import configure_logging, retry, set_scenario_config
from scripts.make_summary import assign_locations
from scripts.plot_power_network import load_projection

logger = logging.getLogger(__name__)

def project_paths(ax, paths_lonlat):
    """
    Wandelt ein dict von lon/lat-Pfaden in projizierte x/y-Pfade um.
    """
    paths_xy = {}
    for name, pts in paths_lonlat.items():
        arr = np.asarray(pts, float)
        xy = ax.projection.transform_points(ccrs.PlateCarree(), arr[:,0], arr[:,1])
        paths_xy[name] = [(float(x), float(y)) for x, y in xy[:, :2]]
    return paths_xy

@retry
def plot_h2_map(n, regions):
    # if "H2 pipeline" not in n.links.carrier.unique():
    #     return

    assign_locations(n)

    h2_storage = n.stores.query("carrier == 'ammonia store'")
    regions["NH3"] = (
        h2_storage.rename(index=h2_storage.bus.map(n.buses.location))
        .e_nom_opt.groupby(level=0)
        .sum()
        .div(1e6)
    )  # TWh
    regions["NH3"] = regions["NH3"].where(regions["NH3"] > 0.01)

    bus_size_factor = 1e5
    linewidth_factor = 5e2
    # MW below which not drawn
    line_lower_threshold = 25 #750/1e2

    # Drop non-electric buses so they don't clutter the plot
    n.buses.drop(n.buses.index[n.buses.carrier != "AC"], inplace=True)

    carriers =  ["H2 Electrolysis", "H2 Fuel Cell"]              #  "H2 Electrolysis", "H2 Fuel Cell"

    elec = n.links[n.links.carrier.isin(carriers)].index

    bus_sizes = (
        n.links.loc[elec, "p_nom_opt"].groupby([n.links["bus0"], n.links.carrier]).sum()
        / bus_size_factor
    )

    # make a fake MultiIndex so that area is correct for legend
    bus_sizes.rename(index=lambda x: x.replace(" H2", ""), level=0, inplace=True)
    # drop all links which are not H2 pipelines
    n.links.drop(
        n.links.index[~n.links.carrier.str.contains("shipping-lh2")], inplace=True
    )

    h2_new = n.links[n.links.carrier == "shipping-lh2"]
    #h2_retro = n.links[n.links.carrier == "H2 pipeline retrofitted"]
    h2_total = h2_new.p_nom_opt
    #print(h2_total)
    link_widths_total = h2_total / linewidth_factor
    #print(link_widths_total)

    #n.links.rename(index=lambda x: x.split("-2")[0], inplace=True)
    # group links by summing up p_nom values and taking the first value of the rest of the columns
    other_cols = dict.fromkeys(n.links.columns.drop(["p_nom_opt", "p_nom"]), "first")
    n.links = n.links.groupby(level=0).agg(
        {"p_nom_opt": "sum", "p_nom": "sum", **other_cols}
    )

    link_widths_total = link_widths_total.reindex(n.links.index).fillna(0.0)
    link_widths_total[n.links.p_nom_opt < line_lower_threshold] = 0.0

    #retro = n.links.p_nom_opt.where(
    #    n.links.carrier == "H2 pipeline retrofitted", other=0.0
    #)
    #link_widths_retro = retro / linewidth_factor
    #link_widths_retro[n.links.p_nom_opt < line_lower_threshold] = 0.0

    n.links.bus0 = n.links.bus0.str.replace(" H2", "")
    n.links.bus1 = n.links.bus1.str.replace(" H2", "")

    regions = regions.to_crs(proj.proj4_init)

    fig, ax = plt.subplots(figsize=(7, 6), subplot_kw={"projection": proj})

    color_h2_pipe = "#b3f3f4"
    color_retrofit = "#499a9c"

    bus_colors = {"H2 Electrolysis": "#ff29d9", "H2 Fuel Cell": "#805394"}
   #print(link_widths_total)
   #print(n.links)
    
   #test_paths = {
   #"MR6 0 NH3 to DE0 0 NH3 shipping-nh3": [
    #   (-15.98, 18.08),   # Nouakchott
    #   (-9.14, 38.72),    # Lissabon
    #   (8.11, 53.52),     # Wilhelmshaven
   #]
   #}

   #fig, ax = plt.subplots(subplot_kw={"projection": ccrs.EqualEarth()})

    # Vorher projizieren:
   #proj_paths = project_paths(ax, test_paths)
        
    n.plot(
        geomap=True,
        bus_sizes=bus_sizes,
        bus_colors=bus_colors,
        link_colors=color_h2_pipe,
        link_widths=link_widths_total,
        branch_components=["Link"],
        ax=ax,
   #    paths=proj_paths,
        **map_opts,
    )

    #n.plot(
    #    geomap=True,
    #    bus_sizes=0,
    #    link_colors=color_retrofit,
    #    link_widths=link_widths_retro,
    #    branch_components=["Link"],
    #    ax=ax,
    #    **map_opts,
    #)

   #regions.plot(
    #   ax=ax,
     #  column="NH3",
     #  cmap="Blues",
     #  linewidths=0,
     #  legend=True,
     #  vmax=0.4,
     #  vmin=0,
       #legend_kwds={
       #    "label": "Hydrogen Storage [TWh]",
       #    "shrink": 0.7,
       #    "extend": "max",
       #},
   #)

    sizes = [100, 50]
    labels = [f"{s} MW" for s in sizes]
    sizes = [s / bus_size_factor  *2  for s in sizes]

    legend_kw = dict(
        loc="upper left",
        bbox_to_anchor=(0, 1),
        labelspacing=0.8,
        handletextpad=0,
        frameon=False,
    )

    add_legend_circles(
        ax,
        sizes,
        labels,
        srid=n.srid,
        patch_kw=dict(facecolor="lightgrey"),
        legend_kw=legend_kw,
    )

    sizes = [300, 100]
    labels = [f"{s} MW" for s in sizes]
    scale = 1e1 / linewidth_factor
    sizes = [s * scale for s in sizes]

    legend_kw = dict(
        loc="upper left",
        bbox_to_anchor=(0.23, 1),
        frameon=False,
        labelspacing=0.8,
        handletextpad=1,
    )

    add_legend_lines(
        ax,
        sizes,
        labels,
        patch_kw=dict(color="lightgrey"),
        legend_kw=legend_kw,
    )

    colors = [bus_colors[c] for c in carriers] + [color_h2_pipe]
    labels = carriers + ["LH2 shipping"]

    legend_kw = dict(
        loc="upper left",
        bbox_to_anchor=(0, 1.13),
        ncol=2,
        frameon=False,
    )

    add_legend_patches(ax, colors, labels, legend_kw=legend_kw)

    ax.set_facecolor("white")

    fig.savefig(snakemake.output.map, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    if "snakemake" not in globals():
        from scripts._helpers import mock_snakemake

        snakemake = mock_snakemake(
            "plot_hydrogen_network",
            opts="",
            clusters="37",
            sector_opts="4380H-T-H-B-I-A-dist1",
        )

    configure_logging(snakemake)
    set_scenario_config(snakemake)

    n = pypsa.Network(snakemake.input.network)

    regions = gpd.read_file(snakemake.input.regions).set_index("name")

    #map_opts = snakemake.params.plotting["map"]
    map_opts = {
    "boundaries": [-25, 20,15, 71]  # [minx, maxx, miny, maxy]
    }

    if map_opts["boundaries"] is None:
        map_opts["boundaries"] = regions.total_bounds[[0, 2, 1, 3]] + [-1, 1, -1, 1]

    proj = load_projection(snakemake.params.plotting)

    plot_h2_map(n, regions)
