from graphs import RatePerWell

production_file = "data_for_tests/full_example_1/production.csv"
pressure_file = "data_for_tests/full_example_1/pressures.csv"
pvt_file = "data_for_tests/full_example_1/pvt.csv"

figura = RatePerWell(production_file, pressure_file, pvt_file)
print(figura)

