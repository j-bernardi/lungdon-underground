import numpy as np
import matplotlib.pyplot as plt


markers = {
    "Annual target": 5,  # https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines
    "WHO 24h target": 15,  # https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines
}

legend = ["WHO 2021 limits"]

custom_colors = ['blue', 'green', 'orange', 'purple', 'red']  # Add or remove colors as needed

station_medians = {
    "Victoria line,\nmedian station": (308.00, "skyblue"),
    # "Piccadilly": (104.00, "blue"),
    # "Northern line,\nmedian station": (232.50, "black"),
    "Circle line,\nmedian station": (18.00, "yellow"),
    # "Jubilee": (39.00, "gray"),
    # "District": (15.00, "green"),
    # "Bakerloo": (173.00, "brown"),
    # "Metropolitan": (28.00, "purple"),
    # "Docklands Light Railway": (4.00, "skyblue"),
    "Central line,\nmedian station": (57.00, "red"),
    # "Hammersmith & City": (22.00, "pink"),
    "London,\nMarylebone Road,\nAnnual Avg\n(2021)": (11, "gray"),  # https://www.westminster.gov.uk/media/document/air-quality-report-2021
    # "Edinburgh,\nAnnual Avg\n(2022)": (6, "gray"),  # https://www.statista.com/statistics/1299076/pm25-emissions-selected-cities-in-united-kingdom/
    "Stockwell Station\nMax PM2.5": (639, "black"),
}

tube = {
    "elemental carbon": 0.07,
    "organic carbon": 0.11,
    "iron base": 0.47,
    "metallic and\nmineral oxides": 0.14,
    "silicone dioxide\n(suspected)": 0.11,
    "other (unknown)": 0.10,
}
roadside = {
    "elemental carbon": 0.11,
    "organic carbon": 0.26,
    "iron base": 0.06,
    "ammonium\nsulphate": 0.24,
    "ammonium\n& sodium nitrate": 0.21,
    "salts": 0.07,
    "other": 0.05,
}

def pie_charts():

    sorted_tube = tube  #  {k: v for k, v in sorted(tube.items(), key=lambda item: item[0])}
    sorted_roadside =  roadside  # {k: v for k, v in sorted(roadside.items(), key=lambda item: item[0])}
    print(sorted_tube)
    print(sorted_roadside)

    unique_labels = set(list(sorted_tube.keys()) + list(sorted_roadside.keys()))
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(unique_labels)))
    color_map = {label: color for label, color in zip(sorted(unique_labels), colors)}

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Create pie chart for Tube
    tube_labels = list(sorted_tube.keys())
    tube_colors = [color_map[label] for label in tube_labels]
    tube_wedges, tube_texts, tube_autotexts = axes[0].pie(
        list(sorted_tube.values()), labels=tube_labels, autopct='%1.1f%%', 
        pctdistance=0.85, colors=tube_colors, startangle=90)
    axes[0].set_title('Tube PM 2.5 Composition', fontsize=18)

    # Increase the size and move text further to the edge
    for text in tube_texts + tube_autotexts:
        text.set_fontsize(14)
        # text.set_horizontalalignment('right')

    # Create pie chart for Roadside
    roadside_labels = list(sorted_roadside.keys())
    roadside_colors = [color_map.get(label, (0, 0, 0, 0)) for label in roadside_labels]
    roadside_wedges, roadside_texts, roadside_autotexts = axes[1].pie(
        list(sorted_roadside.values()),
        labels=roadside_labels,
        autopct='%1.1f%%', 
        pctdistance=0.85,
        colors=roadside_colors,
        startangle=90
    )
    axes[1].set_title('Roadside PM2.5 Composition', fontsize=18)
    
    # Increase the size and move text further to the edge
    for text in roadside_texts + roadside_autotexts:
        text.set_fontsize(14)
        # text.set_horizontalalignment('right')

    # Create a legend from unique labels
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[label]) for label in sorted(unique_labels)]
    fig.legend(handles, sorted(unique_labels), loc='center left', bbox_to_anchor=(1, 0.5))

    plt.subplots_adjust(wspace=0.5)  # Adjust the horizontal spacing between subplots

    plt.savefig("images/rename_pie_to_keep.png")
    plt.show()


def plot_bars():
    # Sort the station_medians dictionary by value
    sorted_station_medians = {k: v for k, v in sorted(station_medians.items(), key=lambda item: item[1][0])}

    # Create the column chart
    stations = list(sorted_station_medians.keys())
    medians = list(v[0] for v in sorted_station_medians.values())
    colors = list(v[1] for v in sorted_station_medians.values())
    plt.figure(figsize=(12, 8))
    bars = plt.bar(stations, medians, color=colors)

    # Add horizontal lines and annotations for the markers
    for i, (marker_label, marker_value) in enumerate(markers.items()):
        plt.axhline(y=marker_value, color='red', linestyle='--')
        plt.text(
            bars[-1].get_x() + bars[1].get_x() * 1.1 - bars[0].get_x(),
            marker_value + (11 * -1 if i == 0 else 0),
            f'{marker_label}',
            verticalalignment='bottom',
            fontsize=16,
            # horizontalalignment='right',
            # rotation=-15,
        )

    # Annotate the bars with their respective median values
    for i, bar in enumerate(bars):
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            38 if i in (0, 1) else bar.get_height() + 20,
            f'{bar.get_height()}',
            ha='center', va='top', color='black', fontsize=16)

    # Labels and Title
    plt.ylabel('PM2.5 Concentration (ug/m3)', fontsize=18, labelpad=15)
    # plt.xlabel('Stations')
    plt.title('PM2.5 Concentration on the London Underground', fontsize=18, y=1.05)
    # Move the title away from the axes


    # Rotate x labels for better visibility
    plt.xticks(rotation=0, fontsize=14)  #, ha='right')
    plt.yticks(fontsize=14)
    plt.tick_params(axis='x', which='major', pad=5)

    # Hide spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Show the plot
    plt.savefig("images/rename_to_keep.png")
    plt.show()

if __name__ == "__main__":
    plot_bars()
    # pie_charts()
