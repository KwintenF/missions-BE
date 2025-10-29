#!/usr/bin/env python3
"""
Visualize Belgian participation in Operation Inherent Resolve.

Operation Inherent Resolve (OIR) is the U.S. military operation against ISIS
in Iraq and Syria, ongoing since 2014. Belgium contributes through training,
advisory support, and humanitarian demining.

Mission Context (2024-2025):
- Coalition transitioning from combat to advisory role
- Phase 1 (Sep 2024 - Sep 2025): End combat mission in Iraq
- Phase 2 (Sep 2025 - Sep 2026+): Continue counter-ISIS ops in Syria from Iraq bases
- ~2,000 coalition troops (down to ~1,000 in Syria by 2025)
- ~3,000 ISIS fighters remain across Iraq and Syria (scattered, no continuous territory)

INPUT: data/ne_110m_admin_0_countries.geojson, data/globe_locations.json
OUTPUT: maps/inherent_resolve_map.html
"""
import json
import folium
import os


def load_globe_data(filepath='data/globe_locations.json'):
    """Load the extracted globe location data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_country_geojson(cache_file='data/ne_110m_admin_0_countries.geojson'):
    """Load Natural Earth countries GeoJSON from cache."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_inherent_resolve_map(locations, output_file='maps/inherent_resolve_map.html'):
    """
    Create detailed map of Operation Inherent Resolve theater.

    Includes:
    - Belgium's location (Kuwait/Camp Arifjan)
    - Iraq and Syria country polygons
    - Key coalition bases
    - ISIS historical territory context
    - Mission timeline annotations
    """

    # Center on Middle East (Iraq/Syria region)
    m = folium.Map(
        location=[33.5, 43.0],  # Central Iraq
        zoom_start=5,
        tiles='CartoDB positron'
    )

    # Load Natural Earth data
    geojson_data = get_country_geojson()

    # Countries in OIR theater
    oir_countries = {
        'Iraq': {'color': '#ff9999', 'role': 'Primary theater - ISIS defeated 2017, training mission ongoing'},
        'Syria': {'color': '#ffcccc', 'role': 'Active operations - Northeast governorates'},
        'Kuwait': {'color': '#66ccff', 'role': 'Belgium location - Camp Arifjan logistics hub'},
        'Turkey': {'color': '#e6e6e6', 'role': 'Coalition partner - Northern border'},
        'Jordan': {'color': '#e6e6e6', 'role': 'Coalition partner - Al-Tanf support'},
        'Saudi Arabia': {'color': '#e6e6e6', 'role': 'Coalition partner - Regional coordination'},
        'Iran': {'color': '#ffeeee', 'role': 'Regional actor - Influence in Iraq/Syria'},
    }

    # Add country polygons
    for feature in geojson_data['features']:
        country_name = feature['properties'].get('NAME')

        if country_name in oir_countries:
            info = oir_countries[country_name]

            popup_html = f"""
            <div style="width: 250px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">{country_name}</h4>
                <p style="margin: 4px 0; font-size: 11px;">{info['role']}</p>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x, color=info['color']: {
                    'fillColor': color,
                    'color': '#666666',
                    'weight': 1.5,
                    'fillOpacity': 0.5
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.7,
                    'weight': 2.5
                },
                tooltip=country_name,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    # Key coalition bases and locations
    bases = [
        # Iraq training sites
        {
            'name': 'Al-Asad Airbase',
            'coords': [33.7856, 42.4414],
            'country': 'Iraq (Anbar)',
            'role': 'Coalition training base',
            'color': '#0066cc',
            'icon': 'plane'
        },
        {
            'name': 'Erbil',
            'coords': [36.1911, 44.0091],
            'country': 'Iraq (Kurdistan)',
            'role': 'Coalition training site',
            'color': '#0066cc',
            'icon': 'plane'
        },
        {
            'name': 'Taji',
            'coords': [33.5311, 44.2569],
            'country': 'Iraq (Baghdad)',
            'role': 'Coalition training site',
            'color': '#0066cc',
            'icon': 'plane'
        },
        {
            'name': 'Union III',
            'coords': [33.3128, 44.3615],
            'country': 'Iraq (Baghdad)',
            'role': 'CJTF-OIR HQ (as of 2025)',
            'color': '#003399',
            'icon': 'star'
        },
        # Syria sites
        {
            'name': 'Al-Tanf',
            'coords': [33.4933, 38.6167],
            'country': 'Syria (Homs)',
            'role': 'Coalition garrison (SE Syria)',
            'color': '#cc0000',
            'icon': 'plane'
        },
        {
            'name': 'Al-Hasakah Province',
            'coords': [36.5, 40.7],
            'country': 'Syria (NE)',
            'role': 'Active operations zone',
            'color': '#cc0000',
            'icon': 'warning-sign'
        },
        {
            'name': 'Deir ez-Zor Province',
            'coords': [35.0, 40.5],
            'country': 'Syria (NE)',
            'role': 'Active operations zone',
            'color': '#cc0000',
            'icon': 'warning-sign'
        },
        # Kuwait
        {
            'name': 'Camp Arifjan',
            'coords': [29.0833, 48.1000],
            'country': 'Kuwait',
            'role': 'Belgium location - Forward logistics base & CJTF-OIR support',
            'color': '#00aa44',
            'icon': 'home'
        },
    ]

    for base in bases:
        popup_html = f"""
        <div style="width: 220px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">{base['name']}</h4>
            <p style="margin: 4px 0;"><b>Location:</b> {base['country']}</p>
            <p style="margin: 4px 0;"><b>Role:</b> {base['role']}</p>
        </div>
        """

        folium.Marker(
            location=base['coords'],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=base['name'],
            icon=folium.Icon(color='green' if base['color'] == '#00aa44' else
                            'blue' if base['color'] == '#0066cc' else
                            'darkblue' if base['color'] == '#003399' else 'red',
                            icon=base['icon'])
        ).add_to(m)

    # Historical ISIS territory indicator (2014-2017 peak)
    # Simplified polygon showing former ISIS "caliphate" extent
    isis_historical = [
        [36.5, 43.0],  # Mosul area
        [36.0, 41.5],  # Syria-Iraq border
        [35.5, 40.0],  # Raqqa area
        [35.0, 38.5],  # Central Syria
        [34.5, 40.5],  # Deir ez-Zor
        [33.5, 43.5],  # Tikrit area
        [33.0, 44.4],  # Baghdad approaches
        [33.5, 44.0],  # Fallujah area
        [34.5, 43.0],  # Anbar
        [35.5, 42.5],  # Mosul approaches
        [36.5, 43.0],  # Close
    ]

    folium.Polygon(
        locations=isis_historical,
        popup="<b>Historical ISIS Territory (2014-2017)</b><br>Peak caliphate extent - now defeated",
        tooltip="Former ISIS Territory",
        color='#ff0000',
        weight=2,
        fill=False,
        dashArray='10, 10'
    ).add_to(m)

    # Mission timeline annotation box
    timeline_html = '''
    <div style="position: fixed;
                top: 80px; right: 15px; width: 320px;
                background-color: white; border:2px solid #0066cc; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.5;">
    <p style="margin: 0 0 8px 0; font-weight: bold; color: #0066cc;">Operation Inherent Resolve Timeline</p>
    <p style="margin: 4px 0; font-size: 10px;">
        <b>2014:</b> OIR launched - Coalition vs ISIS<br>
        <b>2017:</b> ISIS territorial defeat in Iraq<br>
        <b>2019:</b> ISIS territorial defeat in Syria<br>
        <b>2021:</b> Belgian F-16 operations end<br>
        <b>2024:</b> Belgium training & demining (€1.5M)<br>
        <b>Sep 2024:</b> Phase 1 begins - Iraq transition<br>
        <b>Sep 2025:</b> Phase 2 begins - Syria ops from Iraq<br>
        <b>2026+:</b> Bilateral security partnership
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Current: ~2,000 coalition troops<br>
        ISIS remnants: ~3,000 fighters (scattered)
    </p>
    </div>
    '''

    # Legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 15px; width: 280px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.6;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">Mission Elements</p>
    <p style="margin: 4px 0;">
        <i class="fa fa-home" style="color: green;"></i>
        <b style="color: #00aa44;">Belgium</b> - Kuwait (Camp Arifjan)
    </p>
    <p style="margin: 4px 0;">
        <i class="fa fa-plane" style="color: blue;"></i>
        <b style="color: #0066cc;">Iraq</b> - Training sites
    </p>
    <p style="margin: 4px 0;">
        <i class="fa fa-plane" style="color: red;"></i>
        <b style="color: #cc0000;">Syria</b> - Active operations
    </p>
    <p style="margin: 4px 0;">
        <span style="border: 2px dashed red; padding: 2px 6px;">---</span>
        Former ISIS territory (2014-2017)
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Data sources: CJTF-OIR, DoD IG Reports,<br>
        Washington Institute, PolGeoNow
    </p>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(timeline_html))
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_file)
    print(f" Operation Inherent Resolve map saved to {output_file}")
    return m


if __name__ == "__main__":
    print("=" * 70)
    print("OPERATION INHERENT RESOLVE - Belgian Mission Visualization")
    print("=" * 70)

    print("\nMission Overview:")
    print("  Coalition mission against ISIS in Iraq and Syria (2014-present)")
    print("  Belgium: Training, advisory support, humanitarian demining")
    print("  Location: Kuwait (Camp Arifjan forward logistics base)")
    print("\nCurrent Status (2024-2025):")
    print("  - Transitioning from combat to advisory partnership")
    print("  - ISIS territorial defeat complete (2017-2019)")
    print("  - ~3,000 ISIS fighters remain (no continuous territory)")
    print("  - Coalition: ~2,000 troops → ~1,000 by late 2025")

    print("\n" + "=" * 70)

    locations = load_globe_data()
    create_inherent_resolve_map(locations)

    print("\nNext steps for temporal analysis:")
    print("  1. Historical phase (2014-2019): ISIS rise and territorial defeat")
    print("  2. Stabilization phase (2019-2024): Advisory mission & remnants")
    print("  3. Transition phase (2024-2026): Bilateral partnership")
    print("  4. Future projection (2026+): Long-term security cooperation")
