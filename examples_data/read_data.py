"""
read_data.py

This script is to convert to DataFrame the csv data that user can use.
"""
import pandas as pd
production_data = pd.read_csv("../examples_data/production.csv")
pressure_data = pd.read_csv("../examples_data/pressures.csv")
pvt_data = pd.read_csv("../examples_data/pvt.csv")
injection_data = pd.read_csv("../examples_data/injection.csv")
