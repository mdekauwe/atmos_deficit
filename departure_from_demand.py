#!/usr/bin/env python

"""
For each of the Ozflux sites calculate the PET (Milly & Dunne, 2016) to give
an estimate of the demand. Then figure out the departure from this, i.e.
supply (flux LE) - demand (PET).

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (08.11.2017)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.colors as colors

def main(flux_dir, dates, ofname):

    fig = plt.figure(figsize=(9,6))
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(wspace=0.2)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['font.size'] = 12
    plt.rcParams['legend.fontsize'] = 9
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    ax = fig.add_subplot(1,1,1)

    site_list = glob.glob(os.path.join(flux_dir, "*_flux.nc"))
    NUM_COLORS = len(site_list)
    LINE_STYLES = ['solid', 'dashed', 'dashdot', 'dotted']
    NUM_STYLES = len(LINE_STYLES)
    #cm = plt.get_cmap('viridis')
    cm = plt.get_cmap('gist_rainbow')

    for i, fname in enumerate(site_list):
        site = os.path.basename(fname).split("OzFlux")[0]
        ds = xr.open_dataset(fname)
        df = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
        df = df[(df['Qle_qc'] == 1) & (df['Qh_qc'] == 1)]
        df = df.iloc[df.index.indexer_between_time('09:00', '18:00')]
        calc_pet(df)
        get_deficit(df)
        df = df.resample("M").agg("mean")

        lines = ax.plot(df["deficit"], label=site)
        lines[0].set_color(cm(i//NUM_STYLES*float(NUM_STYLES)/NUM_COLORS))
        lines[0].set_linestyle(LINE_STYLES[i%NUM_STYLES])

    ax.axhline(y=0.0, ls="--", color="grey", alpha=0.3)
    ax.set_xlabel("Date")
    ax.set_ylabel("Supply - Demand (W m$^{-2}$)")
    ax.legend(numpoints=1, loc="best", ncol=3)
    ax.set_xlim(dates)
    fig.savefig(ofname, bbox_inches='tight', pad_inches=0.1)


def calc_pet(df):
    """ Energy only PET

    This follows Milly and Dunne but I'm dropping the G bit for now

    Reference:
    ==========
    * Milly & Dunne (2016) Nature Climate Change, DOI: 10.1038/NCLIMATE3046

    """
    df["PET"] = 0.8 * (df.Qh + df.Qle)

def get_deficit(df):
    df["deficit"] = df.Qle - df.PET

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    dates = dt.datetime(2002,1,1), dt.datetime(2011,1,1)
    ofname = "/Users/mdekauwe/Desktop/Atmos_deficit_2002_2011.pdf"
    main(flux_dir, dates, ofname)

    dates = dt.datetime(2011,1,1), dt.datetime(2015,1,1)
    ofname = "/Users/mdekauwe/Desktop/Atmos_deficit_2011_2015.pdf"
    main(flux_dir, dates, ofname)
