import os
import pickle
import pandas as pd

from collections import deque

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

TUBE_DATA_PATH = "tube_data"


class Station:

    def __init__(self, id: int, name: str, lines: set, pm25_values: dict, connected_stations: set = None):
        self.id = id
        self.name = name
        self.lines = lines
        # Map {line_name: pm25_value} as different platforms have different values
        self.pm25_values = pm25_values
        self.connected_stations = connected_stations or set()

class Line:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.stations_on_line = set()


class Map:

    def __init__(self, debug=False):
        """Maybe will be needed for lookups"""

        datastore_path = os.path.join(TUBE_DATA_PATH, "datastore")
        line_data_path = os.path.join(datastore_path, "lines.pickle")
        stations_data_path = os.path.join(datastore_path, "stations.pickle")
        station_name_map_data_path = os.path.join(datastore_path, "station_namemap.pickle")
        line_name_map_data_path = os.path.join(datastore_path, "line_namemap.pickle")

        if os.path.exists(datastore_path):
            with open(stations_data_path, "rb") as f:
                self.stations = pickle.load(f)
            
            with open(line_data_path, "rb") as f:
                self.lines = pickle.load(f)

            with open(station_name_map_data_path, "rb") as f:
                self.station_name_id_lookup = pickle.load(f)
            
            with open(line_name_map_data_path, "rb") as f:
                self.line_name_to_id_lookup = pickle.load(f)

            return

        self.lines = {}
        self.stations = {}
        self.station_name_id_lookup = {}  # Map name to ID
        self.line_name_to_id_lookup = {}  # Map name to ID

        with open(os.path.join(TUBE_DATA_PATH, "stations.csv"), "r") as f:
            stations_data = pd.read_csv(f)
    
        with open(os.path.join(TUBE_DATA_PATH, "lines.csv"), "r") as f:
            lines_data = pd.read_csv(f)

        with open(os.path.join(TUBE_DATA_PATH, "edges.csv"), "r") as f:
            edges_data = pd.read_csv(f)
        
        with open(os.path.join(TUBE_DATA_PATH, "pm25_per_station_line.csv"), "r") as f:
            pm25_data = pd.read_csv(f)

        if debug:
            print("LINES")
            print(lines_data.head())
            print("STATIONS")
            print(stations_data.head())
            print("EDGES")
            print(edges_data.head())
            print("PM25")
            print(pm25_data.head())

        # Add all the lines to the object
        for _, line_row in lines_data.iterrows():

            self.line_name_to_id_lookup[line_row["name"]] = line_row["line"]

            self.lines[line_row["line"]] = Line(
                id=line_row["line"],
                name=line_row["name"]
            )

        for temp_i, station_row in stations_data.iterrows():
            self.station_name_id_lookup[station_row["name"]] = station_row["id"]

            relevant_edges = edges_data[
                (edges_data["station1"] == station_row["id"])
                | (edges_data["station2"] == station_row["id"])
            ]

            line_idxs_on_station = relevant_edges["line"].unique()
            line_objects = {self.lines[x] for x in line_idxs_on_station}

            assert len(line_idxs_on_station) == station_row["total_lines"], (
                f"{temp_i}: For {station_row['name']} found line idxs: {line_idxs_on_station}, "
                f"expected total: {station_row['total_lines']}."
                f"\nLines are {[l.name for l in line_objects]}"
            )

            # TODO index this on lines instead! Currently pm25 data is missing some rows, so we should try to fix it 
            station_pm25s = pm25_data[pm25_data["station"] == station_row["name"]]
            station_pm25_dict = {}
            for _, pm25_row in station_pm25s.iterrows():

                # Make keys match the tube map data (merging 2 sources)
                matching_line_key = pm25_row["line"] + (
                    " Line" if pm25_row["line"] != "Docklands Light Railway" else "")

                assert matching_line_key in [l.name for l in self.lines.values()], (
                    f"{matching_line_key} not in {[l.name for l in self.lines.values()]}")

                station_pm25_dict[matching_line_key] = pm25_row["pm25"]

            station_object = Station(
                id=station_row["id"],
                name=station_row["name"],
                lines=line_objects,
                pm25_values=station_pm25_dict,
                connected_stations=None,
            )

            self.stations[station_row["id"]] = station_object

            for line_i in line_idxs_on_station:
                self.lines[line_i].stations_on_line.add(station_object)

        for _, edge_row in edges_data.iterrows():
            s1 = self.stations[edge_row["station1"]]
            s2 = self.stations[edge_row["station2"]]
            assert len(s1.lines.intersection(s2.lines)) > 0
            s1.connected_stations.add(s2)
            s2.connected_stations.add(s1)

        os.makedirs(datastore_path)
        
        with open(stations_data_path, "wb") as f:
            pickle.dump(self.stations, f)
            
        with open(line_data_path, "wb") as f:
            pickle.dump(self.lines, f)

        with open(station_name_map_data_path, "wb") as f:
            pickle.dump(self.station_name_id_lookup, f)
        
        with open(line_name_map_data_path, "wb") as f:
            pickle.dump(self.line_name_to_id_lookup, f)
    
    def stations_between(self, station1_name, station2_name, station1_line_name):
        """Takes stations as names"""
        # Assert both stations

        station1_id = self.station_name_id_lookup[station1_name]
        station1 = self.stations[station1_id]

        station2_id = self.station_name_id_lookup[station2_name]
        station2 = self.stations[station2_id]

        assert station1_line_name in [l.name for l in station1.lines], (
            f"{station1_line_name} not at station {station1_name}, {[l.name for l in station1.lines]}"
        )

        assert len(station1.lines.intersection(station2.lines)) > 0, (
            f"{station1_name} & {station2_name} not on same line")

        visited = set()
        queue = deque([[station1]])

        while queue:
            path = queue.popleft()
            current_station = path[-1]

            if current_station.id in visited:
                continue

            for next_station in current_station.connected_stations:
                if station1_line_name not in [line.name for line in next_station.lines]:
                    continue
                new_path = list(path)
                new_path.append(next_station)
                queue.append(new_path)

                if next_station.id == station2.id:
                    return [station.name for station in new_path]  # or station.id if you want the IDs

            visited.add(current_station.id)

        return None  # Return None if no path exists

    def get_time_of_path(self, path, line_name):
        """Get full journey time of the user

        Returns: journey time underground in minutes
        """

        walkdown = 2
        waittime = 3
        walkup = 2

        # Assume 2 mins per stop
        journeytime = sum([2 for _ in range(len(path))])

        return walkdown + waittime + journeytime + walkup
    
    def get_pm25_of_path(self, path, line_name):
        """ path is names

        # TODO integrate this with minutes
        # multiply walkdown + waittime 
        # divide by total mins
        """
        vals = []

        for station_id in path:

            station = self.stations[self.station_name_id_lookup[station_id]]

            assert line_name in station.pm25_values, (
                f"{line_name} not in {station.name} dict: {station.pm25_values}"
            )

            vals.append(station.pm25_values[line_name])

        return vals
