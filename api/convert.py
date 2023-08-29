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

# TODO use the actual data instead of Options! From tube_data.tube_map import Map
#  Get every tube stop passed through, and average the data

OPTIONS = {
    "District line": {
        TYPE_KEY: TUBE_VAL,
        MEAN_KEY: 6,  # Guess based on median
        MEDIAN_KEY: 4  # [1]
    },
    "Victoria": {
        TYPE_KEY: TUBE_VAL,
        MEAN_KEY: 450,  # Guess based on median and max
        MEDIAN_KEY: 361,  # [1]
        MAX_KEY: 885,  # [1]
    },
    "Northern": {
        TYPE_KEY: TUBE_VAL,
        MEAN_KEY: 350,  # Guess based on [1]
        MEDIAN_KEY: 300,
    },
    "Picadilly": {
        TYPE_KEY: TUBE_VAL,
        MEAN_KEY: 250,  # Guess based on [1]
        MEDIAN_KEY: 200,  # Guess based on mean
    },
    "Hammersmith and City": {
        TYPE_KEY: TUBE_VAL,
        MEAN_KEY: 6,  # Guess based on median
        MEDIAN_KEY: 4,  # Guess based on [1]
    },
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
for k, item in OPTIONS.items():
    for expected_key in EXPECTED_KEYS:
        assert expected_key in item.keys(), (
            f"Expected key {expected_key} not found in {k}: {item}")


def conversion_formula(tube_line, minutes_spent):

    if not tube_line:
        return f"Invalid tube line (empty)"
    elif tube_line not in OPTIONS:
        return f"Invalid option {tube_line}"

    try:
        mins = float(minutes_spent)
    except:
        return "Invalid minutes: must be integer"
    
    data_item = OPTIONS[tube_line]

    extra_detail = ""

    if data_item[MEAN_KEY] is None:
        assert data_item[TYPE_KEY] == TUBE_VAL
        tube_mean_exposure = OPTIONS[AVERAGE_TUBE_ITEM_KEY][MEAN_KEY]
        extra_detail += "used default value as no data found"
    else:
        tube_mean_exposure = data_item[MEAN_KEY]

    cycle_mean_exposure = OPTIONS[ROADSIDE_ITEM_KEY][MEAN_KEY]
    urban_mean_exposure = OPTIONS[URBAN_BACKGROUND_ITEM_KEY][MEAN_KEY]

    frac_mins = mins / (24. * 60.)

    result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(tube_mean_exposure) * frac_mins
    cycle_result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(cycle_mean_exposure) * frac_mins
    holiday_result_cigs = CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure) * frac_mins
    all_day_result = CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure)
    rest_of_day_result_cigs = ((24. * 60. - mins) / (24 * 60)) * CIGARETTES_FOR_ALL_DAY_TUBE(urban_mean_exposure)

    return result_cigs, cycle_result_cigs, holiday_result_cigs, all_day_result, rest_of_day_result_cigs, extra_detail
