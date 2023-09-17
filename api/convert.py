# TODO data in here. Maybe colour, and definitely formula parameters
# TODO create a standard data structure
MEAN_KEY = "MEAN"
MEDIAN_KEY = "MEDIAN"
MAX_KEY = "MAX"
TYPE_KEY = "TYPE"

# omit max
EXPECTED_KEYS = [MEAN_KEY, MEDIAN_KEY, TYPE_KEY]

TUBE_VAL = "Tube"
AMBIENT_VAL = "Ambient"

# Hardcoded overall keys
AVERAGE_TUBE_ITEM_KEY = "London Underground Overall"
ROADSIDE_ITEM_KEY = "Ambient Roadside"
URBAN_BACKGROUND_ITEM_KEY = "Ambient Background"

# All units in microgrammes per m3
# Source [1]: https://www.sciencedirect.com/science/article/pii/S0160412019313649?via%3Dihub

# TODO use the actual data instead of Options! From api.tube_map import Map
#  Get every tube stop passed through, and average the data

AMBIENT_DATA = {
    AVERAGE_TUBE_ITEM_KEY: {
        TYPE_KEY: AMBIENT_VAL,
        MEAN_KEY: 88,  # [1]
        MEDIAN_KEY: 28  # [1]
    },
    URBAN_BACKGROUND_ITEM_KEY: {
        TYPE_KEY: AMBIENT_VAL,
        MEAN_KEY: 19,  # [1]  TODO figure out what this was
        MEDIAN_KEY: 14  # [1]
    },
    ROADSIDE_ITEM_KEY: {
        TYPE_KEY: AMBIENT_VAL,
        MEAN_KEY: 22,  # [1]
        MEDIAN_KEY: 14  # [1]
    },
}

# Breathing 22. microgrammes per metre-cubed PM2.5, for a whole day, is 1 cigarette
PM25_VAL_ALL_DAY_FOR_ONE_CIGARETTE = 22.
# Therefore spending all day on a tube at a certain PM25 value is
CIGARETTES_FOR_ALL_DAY_TUBE = lambda tube_val: tube_val / PM25_VAL_ALL_DAY_FOR_ONE_CIGARETTE

# Validate
for k, item in AMBIENT_DATA.items():
    for expected_key in EXPECTED_KEYS:
        assert expected_key in item.keys(), (
            f"Expected key {expected_key} not found in {k}: {item}")


def conversion_formula(tube_path: list, minutes_spent: str):

    # TODO could be integral of time at each station
    tube_mean_exposure = sum(tube_path) / len(tube_path)
    cycle_mean_exposure = AMBIENT_DATA[ROADSIDE_ITEM_KEY][MEAN_KEY]
    urban_mean_exposure = AMBIENT_DATA[URBAN_BACKGROUND_ITEM_KEY][MEAN_KEY]

    mins = float(minutes_spent)

    frac_mins = mins / (24. * 60.)

    result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(tube_mean_exposure) * frac_mins

    cycle_result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(cycle_mean_exposure) * frac_mins
    urban_result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure) * frac_mins
    all_day_result = CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure)
    rest_of_day_result_cigs = ((24. * 60. - mins) / (24. * 60.)) * CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure)

    extra_detail = ""
    return result_cigs, cycle_result_cigs, urban_result_cigs, all_day_result, rest_of_day_result_cigs, extra_detail