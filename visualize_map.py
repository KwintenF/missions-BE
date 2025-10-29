#!/usr/bin/env python3
"""
Create simple map visualizations of Belgian military mission locations.

INPUT: data/globe_locations.json, data/ne_110m_admin_0_countries.geojson, data/baltic_sea_extracted.geojson
"""
import json
import folium
import requests
from collections import Counter


# Country coordinates (approximate centers)
COUNTRY_COORDS = {
    "Romania": (45.9432, 24.9668),
    "Baltic Sea": (58.0, 20.0),
    "Lithuania": (55.1694, 23.8813),
    "Latvia": (56.8796, 24.6032),
    "Estonia": (58.5953, 25.0136),
    "Dem. Rep. Congo": (-4.0383, 21.7587),
    "Benin": (9.3077, 2.3158),
    "Mali": (17.5707, -3.9962),
    "Burkina Faso": (12.2383, -1.5616),
    "Niger": (17.6078, 8.0817),
    "Kuwait": (29.3117, 47.4818),
}


def load_globe_data(filepath='data/globe_locations.json'):
    """Load the extracted globe location data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_country_geojson(cache_file='data/ne_110m_admin_0_countries.geojson'):
    """
    Fetch Natural Earth world countries GeoJSON data.
    Downloads once and caches locally to avoid repeated network requests.
    """
    import os

    if os.path.exists(cache_file):
        print(f"Loading Natural Earth data from cache: {cache_file}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
        print(f"Downloading Natural Earth countries GeoJSON (first time)...")
        response = requests.get(url)
        data = response.json()

        print(f"Saving to cache: {cache_file}")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        return data


def create_interactive_map(locations, output_file='maps/missions_map.html'):
    """Create an interactive Folium map with full country polygons."""
    import os

    m = folium.Map(location=[30, 15], zoom_start=3, tiles='CartoDB positron')

    location_to_name = {
        "Romania": "Romania",
        "Lithuania": "Lithuania",
        "Latvia": "Latvia",
        "Estonia": "Estonia",
        "Dem. Rep. Congo": "Dem. Rep. Congo",  # Natural Earth uses same name
        "Benin": "Benin",
        "Mali": "Mali",
        "Burkina Faso": "Burkina Faso",
        "Niger": "Niger",
        "Kuwait": "Kuwait",
    }

    country_missions = {}
    for loc in locations:
        country = loc['Location']
        if country in location_to_name and country != "Baltic Sea":
            natural_earth_name = location_to_name[country]
            country_missions[natural_earth_name] = {
                'name': country,
                'mission': loc['Title'],
                'link': loc['Link']
            }

    mission_colors = {
        'Missies op de oostflank van Europa': '#3388ff',
        'Missies in Afrika': '#00cc66',
        'Missie Inherent Resolve': '#ff4444'
    }

    geojson_data = get_country_geojson()

    # Load extracted Baltic Sea polygon
    baltic_sea_path = 'data/baltic_sea_extracted.geojson'
    if os.path.exists(baltic_sea_path):
        with open(baltic_sea_path, 'r', encoding='utf-8') as f:
            baltic_sea_data = json.load(f)
    else:
        baltic_sea_data = None

    for feature in geojson_data['features']:
        country_name = feature['properties'].get('NAME')

        if country_name in country_missions:
            mission_info = country_missions[country_name]
            mission = mission_info['mission']
            color = mission_colors.get(mission, '#cccccc')

            popup_html = f"""
            <div style="width: 220px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">{mission_info['name']}</h4>
                <p style="margin: 4px 0;"><b>Mission:</b><br>{mission}</p>
                <a href="https://www.mil.be{mission_info['link']}" target="_blank">More info</a>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': '#333333',
                    'weight': 1.5,
                    'fillOpacity': 0.6
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.8,
                    'weight': 3
                },
                tooltip=mission_info['name'],
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)
        elif country_name == 'Belgium':
            # Belgium - home country in green
            popup_html = """
            <div style="width: 200px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">Belgium</h4>
                <p style="margin: 4px 0;">Home country</p>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': '#28a745',
                    'color': '#1e7e34',
                    'weight': 2,
                    'fillOpacity': 0.7
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.9,
                    'weight': 3
                },
                tooltip='Belgium (Home)',
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

    # Add Baltic Sea as part of Eastern Flank
    for loc in locations:
        if loc['Location'] == "Baltic Sea" and baltic_sea_data:
            popup_html = f"""
            <div style="width: 220px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">Baltic Sea</h4>
                <p style="margin: 4px 0;"><b>Mission:</b><br>{loc['Title']}</p>
                <a href="https://www.mil.be{loc['Link']}" target="_blank">More info</a>
            </div>
            """

            folium.GeoJson(
                baltic_sea_data,
                style_function=lambda x: {
                    'fillColor': '#3388ff',  # Same as Eastern Flank
                    'color': '#1a66cc',
                    'weight': 2,
                    'fillOpacity': 0.6
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.8,
                    'weight': 3
                },
                tooltip="Baltic Sea (Eastern Flank)",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 200px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:12px; padding: 12px; line-height: 1.6;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">Mission Categories</p>
    <p style="margin: 4px 0;">
        <span style="display:inline-block; width:20px; height:15px;
                     background-color:#28a745; border:1px solid #1e7e34;"></span>
        Belgium (Home)
    </p>
    <p style="margin: 4px 0;">
        <span style="display:inline-block; width:20px; height:15px;
                     background-color:#3388ff; border:1px solid #333;"></span>
        Eastern Flank
    </p>
    <p style="margin: 4px 0;">
        <span style="display:inline-block; width:20px; height:15px;
                     background-color:#00cc66; border:1px solid #333;"></span>
        Africa
    </p>
    <p style="margin: 4px 0;">
        <span style="display:inline-block; width:20px; height:15px;
                     background-color:#ff4444; border:1px solid #333;"></span>
        Inherent Resolve
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_file)
    print(f"Interactive map saved to {output_file}")
    return m


def create_text_summary(locations):
    """Create a simple text summary of mission locations."""

    print("\n=== BELGIAN MILITARY MISSIONS - GEOGRAPHICAL SUMMARY ===\n")

    # Group by mission category
    by_category = {}
    for loc in locations:
        title = loc['Title']
        country = loc['Location']

        if title not in by_category:
            by_category[title] = []
        by_category[title].append(country)

    # Print summary
    for mission_title, countries in by_category.items():
        print(f"\n{mission_title}:")
        print(f"  Countries: {', '.join(set(countries))}")
        print(f"  Total locations: {len(countries)}")

    print(f"\n\nTOTAL MISSION LOCATIONS: {len(locations)}")
    print(f"UNIQUE COUNTRIES: {len(set(loc['Location'] for loc in locations))}")

    # Regional breakdown
    print("\n=== REGIONAL BREAKDOWN ===")
    regions = {
        'Europe': ['Romania', 'Baltic Sea', 'Lithuania', 'Latvia', 'Estonia'],
        'Africa': ['Dem. Rep. Congo', 'Benin', 'Mali', 'Burkina Faso', 'Niger'],
        'Middle East': ['Kuwait']
    }

    for region, region_countries in regions.items():
        count = sum(1 for loc in locations if loc['Location'] in region_countries)
        print(f"{region}: {count} locations")


if __name__ == "__main__":
    # Load data
    locations = load_globe_data()

    # Create text summary
    create_text_summary(locations)

    # Create interactive map
    print("\n" + "="*60)
    print("Creating interactive map...")
    create_interactive_map(locations)
    print("\nOpen data/missions_map.html in a web browser to view the map")
