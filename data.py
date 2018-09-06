import pandas as pd
import scipy as sp
import os.path
import csv
import numpy as np
from astropy import time, coordinates as coo, units as u
import matplotlib
from uncertainties import unumpy

def dat_to_txt(input_file):
    data = pd.read_csv(input_file, sep=" ", usecols=[0,1,2])
    data.columns = ["time", "flux", "error"]
    name, etx = os.path.splitext(input_file)
    np.savetxt(name+".txt", data, delimiter=" ")

def get_data(input):
    data = pd.read_csv(input, sep = " ")
    data.columns = ["time","flux","error"]
    return data.time, data.flux, data.error

def get_flux(input_file, planet_name, epoch):
    with open(input_file) as f:
        reader = csv.reader(f, delimiter = " ", skipinitialspace = True)
        first_row = next(reader)
        num_cols = len(first_row)-1
    data = sp.loadtxt(input_file, unpack = True, delimiter = " ")
    time = data[0]
    star_flux = unumpy.uarray(data[1],data[2])
    refs = []
    mean_refs = []
    i = 3
    while i<=num_cols:
        refs.append(unumpy.uarray(data[i],data[i+1]))
        i = i+2
    for n in range(len(refs[0])):
        items = []
        for j in range(len(refs)):
            items.append(refs[j][n])
        items = np.array(items)
        mean = items.mean()
        mean_refs.append(mean)
    flux_vector = star_flux/mean_refs
    flux = []
    error = []
    for i in range(len(flux_vector)):
        flux.append(flux_vector[i].n)
        error.append(flux_vector[i].s)
    np.savetxt(planet_name + "_" + epoch + ".txt", np.array([time, flux, error]).T, delimiter = " ")

def build_txt(time,flux,error, file_name):
    fmt = "%.10f %.10f %.10f"
    np.savetxt(file_name + ".txt", np.array([time,flux,error]).T, delimiter=" ", fmt=fmt)

def get_bjd_tdb(time_utc, target, obs):

    if target == "WASP19":
        tg = coo.SkyCoord("09:53:40.007","-45:39:33.06", unit=(u.hourangle,u.deg), frame="icrs")
    if target == "WASP18":
        tg = coo.SkyCoord("01:37:25.0332","-45:40:40.373", unit=(u.hourangle,u.deg), frame="icrs")
    if target == "WASP77":
        tg = coo.SkyCoord("02:28:37.2266","-07:03:38.366", unit=(u.hourangle,u.deg), frame="icrs")

    if obs == "lasilla":
        ob = coo.EarthLocation.of_site("La Silla Observatory")
    if obs == "lascampanas":
        ob = coo.EarthLocation.of_site("Las Campanas Observatory")
    if obs == "tololo":
        ob = coo.EarthLocation.of_site("Cerro Tololo Interamerican Observatory")
    if obs == "extra":
        ob = coo.EarthLocation.of_address("Girona, España")

    times = time.Time(time_utc, format="jd", scale="utc", location=ob)
    ltt_bary = times.light_travel_time(tg, ephemeris="jpl")
    bjd_tdb = times.tdb + ltt_bary

    return bjd_tdb.value

def normalize_flux(date, flux):
    """It normalizes the flux by the median of the part without transit"""

    # Compute the mean value of flux
    mean_flux = np.mean(flux)

    # Determinate the points above the mean of the flux
    flux_upper = flux[flux>=mean_flux]
    date_upper = date[flux>=mean_flux]

    # Compute the median of the points above the mean of the flux
    median_flux = np.median(flux_upper)

    # Normalize the flux by the median of the no_transit flux
    norm_flux = flux / median_flux

    return norm_flux

def normalize_flux2(per, a, t0, time, flux):
    """It normalizes the flux by the median of the part without transit"""

    time = np.asarray(time)
    flux = np.asarray(flux)

    # Compute the transit duration
    transit_duration = (per / np.pi) * np.arcsin(1 / a)

    # Compute the half of the transit duration
    half_transit = transit_duration / 2

    # Make a boolean mask for the date array, is True for the transit duration
    mask_transit = (-half_transit <= time) & (time <= half_transit)

    # Make a boolean mask for the date array but now True is for the time without transit
    mask_no_transit = np.logical_not(mask_transit)

    # Get the flux point without transit
    flux_no_transit = flux[mask_no_transit]

    # Compute the median of the flux without transit
    median_flux = np.median(flux_no_transit)

    # Normalize the flux by the median of the no_transit flux
    norm_flux = flux/median_flux

    return norm_flux


#time, flux, error = get_data(".txt")
#time_bjd = get_bjd_tdb(time_utc=time, obs="lascampanas", target="WASP77")
#build_txt(file_name="WASP77b_20161007_bjd", flux=flux,time=time_bjd,error=error)
