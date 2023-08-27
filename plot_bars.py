import matplotlib.pyplot as plt

# All units in microgrammes per m3
# Source: https://www.sciencedirect.com/science/article/pii/S0160412019313649?via%3Dihub
data = {
    "London Underground": {"mean": 88, "median": 28},
    "Ambient Background": {"mean": 19, "median": 14},
    "Roadside (central London)": {"mean": 22, "median": 14},
    "LU District line (shallow)": {"mean": None, "median": 4},
    "LU Victoria line (deep)": {"mean": None, "median": 361, "max": 885},
}
