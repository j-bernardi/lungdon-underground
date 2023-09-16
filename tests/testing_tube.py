import pandas as pd
from api.tube_data.tube_map import Map

if __name__ == "__main__":
    map = Map()
    line_name = "Circle Line"  # has to end in 'Line'

    print("LINES:", map.lines)

    path = map.stations_between("Aldgate", "King's Cross St. Pancras", line_name)
    vals = map.get_pm25_of_path(path, line_name)

    print(path)
    print(vals)
    print(f"{sum(vals) / len(vals):.2f}")
