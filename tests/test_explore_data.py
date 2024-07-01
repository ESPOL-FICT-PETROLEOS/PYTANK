from graphs import RatePerWell

production_file = "../pytank/resources/data_csv/production.csv"
pressure_file = "../pytank/resources/data_csv/pressures.csv"
pvt_file = "../pytank/resources/data_csv/pvt.csv"

figura = RatePerWell(production_file, pressure_file, pvt_file)
print(figura)
