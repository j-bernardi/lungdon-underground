import os
import pandas as pd


class Station:

    def __init__(self, id, name, line, connected_stations):
        self.id = id
        self.name = name
        self.line = line
        self.connected_stations = connected_stations

class Line:
    def __init__(self, name):
        self.name = name


class Map:

    def __init__(self):

        with open(os.path.join(os.getcwd(), "stations.csv"), "r") as f:
            stations_data = pd.read_csv(f)
        
        with open(os.path.join(os.getcwd(), "lines.csv"), "r") as f:
            lines_data = pd.read_csv(f)
        
        with open(os.path.join(os.getcwd(), "edges.csv"), "r") as f:
            edges_data = pd.read_csv(f)

        # For Line in lines data:
        #    Connect all the stations with that line

        # For stations in stations data
        #    Add to the line
        #    Search all the edges with this station to add the "connected stations"

    def stations_between(self, station1, station2):

        # Assert both stations
        # If not on the same line, return NotImplemented
        pass
