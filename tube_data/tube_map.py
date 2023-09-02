import os
import pickle
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class Station:

    def __init__(self, id: int, name: str, lines: set, connected_stations: set = None):
        self.id = id
        self.name = name
        self.lines = lines
        self.connected_stations = connected_stations or set()

class Line:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.stations_on_line = set()


class Map:

    def __init__(self):
        """Maybe will be needed for lookups"""

        this_filepath = os.path.dirname(os.path.abspath(__file__))
        datastore_path = os.path.join(this_filepath, "datastore")
        line_data_path = os.path.join(datastore_path, "lines.pickle")
        stations_data_path = os.path.join(datastore_path, "stations.pickle")
        name_map_data_path = os.path.join(datastore_path, "namemap.pickle")

        if os.path.exists(datastore_path):
            with open(stations_data_path, "rb") as f:
                self.stations = pickle.load(f)
            
            with open(line_data_path, "rb") as f:
                self.lines = pickle.load(f)

            with open(name_map_data_path, "rb") as f:
                self.station_name_lookup = pickle.load(f)

            return

        self.lines = {}
        self.stations = {}
        self.station_name_lookup = {}  # Map name to ID

        print("Reading stations")
        with open(os.path.join(this_filepath, "stations.csv"), "r") as f:
            stations_data = pd.read_csv(f)
        
        print("Reading lines")
        with open(os.path.join(this_filepath, "lines.csv"), "r") as f:
            lines_data = pd.read_csv(f)

        print("Reading edges")
        with open(os.path.join(this_filepath, "edges.csv"), "r") as f:
            edges_data = pd.read_csv(f)


        print("LINES")
        print(lines_data.head())
        print("STATIONS")
        print(stations_data.head())
        print("EDGES")
        print(edges_data.head())

        for _, line_row in lines_data.iterrows():
            self.lines[line_row["line"]] = Line(
                id=line_row["line"], name=line_row["name"])

        for temp_i, station_row in stations_data.iterrows():
            self.station_name_lookup[station_row["name"]] = station_row["id"]

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

            station_object = Station(
                id=station_row["id"],
                name=station_row["name"],
                lines=line_objects,
                connected_stations=None,
            )

            self.stations[station_row["id"]] = station_object

            for line_i in line_idxs_on_station:
                self.lines[line_i].stations_on_line.add(station_object)
        
        for _, edge_row in edges_data.iterrows():
            s1 = self.stations[edge_row["station1"]]
            s2 = self.stations[edge_row["station2"]]
            assert len(s1.lines.union(s2.lines)) > 0
            s1.connected_stations.add(s2)
            s2.connected_stations.add(s1)

        os.makedirs(datastore_path)
        
        with open(stations_data_path, "wb") as f:
            pickle.dump(self.stations, f)
            
        with open(line_data_path, "wb") as f:
            pickle.dump(self.lines, f)

        with open(name_map_data_path, "wb") as f:
            pickle.dump(self.station_name_lookup, f)
    
    def stations_between(self, station1_name, station2_name):
        """Takes stations as names"""
        # Assert both stations

        station1_id = self.station_name_lookup[station1_name]
        station1 = self.stations[station1_id]

        station2_id = self.station_name_lookup[station2_name]
        station2 = self.stations[station2_id]

        assert len(station1.lines.union(station2.lines)) > 0, (
            f"{station1_name} & {station2_name} not on same line")

        paths = []
        # TODO - traverse all paths til you find it
