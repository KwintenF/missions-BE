#!/usr/bin/env python3
"""
Visualize Belgian military missions in Africa.

Belgian forces operate across multiple African countries focusing on:
- Security cooperation and training (Benin)
- Embassy protection (Mali, Burkina Faso, Niger)
- Equipment support and training (DRC)
- Counter-terrorism in the Sahel
- Anti-piracy in the Gulf of Guinea

Mission Context (2024-2025):
- European Peace Facility (EPF) in DRC through December 2027
- Bilateral partnerships with Benin (25+ years)
- Diplomatic protection detachments (DAS) in Sahel countries
- 3D approach: Diplomacy, Development, Defense

INPUT: data/ne_110m_admin_0_countries.geojson
OUTPUT: maps/african_missions_map.html
"""
import json
import folium
import os


def get_country_geojson(cache_file='data/ne_110m_admin_0_countries.geojson'):
    """Load Natural Earth countries GeoJSON from cache."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_african_missions_map(output_file='maps/african_missions_map.html'):
    """
    Create detailed map of Belgian military missions in Africa.

    Includes:
    - Countries with Belgian military presence
    - Belgian embassy locations (with security detachments)
    - Key operational sites in DRC
    - Gulf of Guinea (piracy threat zone)
    - Sahel region (terrorism threat zone)
    """

    # Center on West/Central Africa
    m = folium.Map(
        location=[10.0, 10.0],  # Central West Africa
        zoom_start=4,
        tiles='CartoDB positron'
    )

    # Load Natural Earth data
    geojson_data = get_country_geojson()

    # Countries with Belgian military presence
    african_missions = {
        'Dem. Rep. Congo': {
            'color': '#ff6666',
            'role': 'EPF mission - Equipment support & training at Camp Lwama (Kindu)',
            'personnel': '~10 military',
            'mission': 'European Peace Facility'
        },
        'Benin': {
            'color': '#66cc66',
            'role': 'Bilateral partnership - Training National Guard, maritime security',
            'personnel': 'Training missions',
            'mission': 'Security cooperation (25+ years)'
        },
        'Mali': {
            'color': '#ffcc66',
            'role': 'Embassy security detachment (DAS) - Diplomatic protection',
            'personnel': 'Security detachment',
            'mission': 'Diplomatic protection'
        },
        'Burkina Faso': {
            'color': '#ffcc66',
            'role': 'Embassy security detachment (DAS) - Diplomatic protection',
            'personnel': 'Security detachment',
            'mission': 'Diplomatic protection'
        },
        'Niger': {
            'color': '#ffcc66',
            'role': 'Embassy security detachment (DAS) - Diplomatic protection',
            'personnel': 'Security detachment',
            'mission': 'Diplomatic protection'
        },
    }

    # Add country polygons
    for feature in geojson_data['features']:
        country_name = feature['properties'].get('NAME')

        if country_name in african_missions:
            info = african_missions[country_name]

            popup_html = f"""
            <div style="width: 280px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">{country_name}</h4>
                <p style="margin: 4px 0;"><b>Mission:</b> {info['mission']}</p>
                <p style="margin: 4px 0;"><b>Personnel:</b> {info['personnel']}</p>
                <p style="margin: 4px 0; font-size: 11px;">{info['role']}</p>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x, color=info['color']: {
                    'fillColor': color,
                    'color': '#333333',
                    'weight': 2,
                    'fillOpacity': 0.6
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.8,
                    'weight': 3
                },
                tooltip=country_name,
                popup=folium.Popup(popup_html, max_width=320)
            ).add_to(m)

    # Belgian embassies with security detachments
    embassies = [
        {
            'name': 'Belgian Embassy Kinshasa',
            'coords': [-4.3276, 15.3136],
            'country': 'DRC',
            'role': 'Embassy with security support',
            'color': '#cc0000',
            'icon': 'home'
        },
        {
            'name': 'Belgian Embassy Bamako',
            'coords': [12.6392, -8.0029],
            'country': 'Mali',
            'role': 'Embassy with DAS security detachment',
            'color': '#cc0000',
            'icon': 'home'
        },
        {
            'name': 'Belgian Embassy Ouagadougou',
            'coords': [12.3714, -1.5197],
            'country': 'Burkina Faso',
            'role': 'Embassy with DAS security detachment',
            'color': '#cc0000',
            'icon': 'home'
        },
        {
            'name': 'Belgian Embassy Niamey',
            'coords': [13.5116, 2.1254],
            'country': 'Niger',
            'role': 'Embassy with DAS security detachment',
            'color': '#cc0000',
            'icon': 'home'
        },
    ]

    for embassy in embassies:
        popup_html = f"""
        <div style="width: 220px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">{embassy['name']}</h4>
            <p style="margin: 4px 0;"><b>Location:</b> {embassy['country']}</p>
            <p style="margin: 4px 0;"><b>Role:</b> {embassy['role']}</p>
        </div>
        """

        folium.Marker(
            location=embassy['coords'],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=embassy['name'],
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)

    # Operational sites in DRC
    drc_sites = [
        {
            'name': 'Kindu',
            'coords': [-2.9578, 25.9224],
            'country': 'DRC (Maniema Province)',
            'role': 'EPF project oversight center (through Dec 2027)',
            'color': '#0066cc',
            'icon': 'plane'
        },
        {
            'name': 'Camp Lwama',
            'coords': [-2.95, 25.95],  # Near Kindu
            'country': 'DRC (near Kindu)',
            'role': '31 Brigade equipment & infrastructure support',
            'color': '#0066cc',
            'icon': 'plane'
        },
    ]

    for site in drc_sites:
        popup_html = f"""
        <div style="width: 240px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">{site['name']}</h4>
            <p style="margin: 4px 0;"><b>Location:</b> {site['country']}</p>
            <p style="margin: 4px 0;"><b>Role:</b> {site['role']}</p>
        </div>
        """

        folium.Marker(
            location=site['coords'],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=site['name'],
            icon=folium.Icon(color='blue', icon=site['icon'])
        ).add_to(m)
    '''
    # Gulf of Guinea - Piracy threat zone
    gulf_of_guinea_area = [
        [4.0, -5.0],   # Ivory Coast coast
        [4.5, 3.0],    # Benin coast
        [3.5, 8.5],    # Nigeria coast
        [0.0, 9.0],    # Cameroon coast
        [-2.0, 8.0],   # Gabon coast
        [-3.0, 3.0],   # Congo coast
        [-2.0, -2.0],  # Open water
        [2.0, -8.0],   # Open water
        [4.0, -5.0],   # Close
    ]

    folium.Polygon(
        locations=gulf_of_guinea_area,
        popup="<b>Gulf of Guinea</b><br>Maritime security operations - Piracy & smuggling threat zone",
        tooltip="Gulf of Guinea (Piracy Threat)",
        color='#0066cc',
        weight=2,
        fill=True,
        fillColor='#0066cc',
        fillOpacity=0.15,
        dashArray='5, 5'
    ).add_to(m)
    

    # Add label for Gulf of Guinea
    folium.Marker(
        location=[2.0, 2.0],
        icon=folium.DivIcon(html=f"""
            <div style="font-size: 10px; color: #0066cc; font-weight: bold;
                        background-color: white; padding: 2px 5px;
                        border: 1px solid #0066cc; border-radius: 3px;">
                Gulf of Guinea<br><span style="font-size: 8px;">(Piracy Zone)</span>
            </div>
        """)
    ).add_to(m)
    '''

    '''
    # Sahel Region - Terrorism threat zone
    sahel_region_area = [
        [18.0, -5.0],   # Mauritania
        [18.0, 16.0],   # Chad
        [12.0, 16.0],   # Chad south
        [12.0, -5.0],   # Mali south
        [18.0, -5.0],   # Close
    ]

    folium.Polygon(
        locations=sahel_region_area,
        popup="<b>Sahel Region</b><br>Counter-terrorism operations - Support to regional forces",
        tooltip="Sahel Region (Terrorism Threat)",
        color='#cc6600',
        weight=2,
        fill=True,
        fillColor='#cc6600',
        fillOpacity=0.15,
        dashArray='5, 5'
    ).add_to(m)

    # Add label for Sahel
    folium.Marker(
        location=[15.5, 5.0],
        icon=folium.DivIcon(html=f"""
            <div style="font-size: 10px; color: #cc6600; font-weight: bold;
                        background-color: white; padding: 2px 5px;
                        border: 1px solid #cc6600; border-radius: 3px;">
                Sahel Region<br><span style="font-size: 8px;">(Terrorism Threat)</span>
            </div>
        """)
    ).add_to(m)
    '''

    # Mission overview annotation box
    overview_html = '''
    <div style="position: fixed;
                top: 80px; right: 15px; width: 320px;
                background-color: white; border:2px solid #cc6600; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.5;">
    <p style="margin: 0 0 8px 0; font-weight: bold; color: #cc6600;">Belgian Missions in Africa</p>
    <p style="margin: 4px 0; font-size: 10px;">
        <b style="color: #ff6666;">DRC:</b> European Peace Facility (EPF)<br>
        → Equipment & training for 31 Brigade<br>
        → Camp Lwama (Kindu) operations<br>
        → Through December 2027<br><br>

        <b style="color: #66cc66;">Benin:</b> Bilateral Partnership<br>
        → 25+ years of cooperation<br>
        → National Guard training<br>
        → Maritime security (Gulf of Guinea)<br><br>

        <b style="color: #ffcc66;">Mali, Burkina Faso, Niger:</b><br>
        → Embassy security detachments (DAS)<br>
        → Diplomatic protection<br>
        → Evacuation coordination<br><br>

        <b>Sahel:</b> 3D Approach (Diplomacy, Development, Defense)
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
        <span style="background-color: #ff6666; padding: 2px 8px; border-radius: 3px;">■</span>
        <b>DRC</b> - EPF equipment & training
    </p>
    <p style="margin: 4px 0;">
        <span style="background-color: #66cc66; padding: 2px 8px; border-radius: 3px;">■</span>
        <b>Benin</b> - Bilateral partnership
    </p>
    <p style="margin: 4px 0;">
        <span style="background-color: #ffcc66; padding: 2px 8px; border-radius: 3px;">■</span>
        <b>Sahel</b> - Embassy security (DAS)
    </p>
    <p style="margin: 4px 0;">
        <i class="fa fa-home" style="color: red;"></i>
        Belgian Embassies
    </p>
    <p style="margin: 4px 0;">
        <i class="fa fa-plane" style="color: blue;"></i>
        Operational sites (DRC)
    </p>
    <p style="margin: 4px 0;">
        <span style="border: 2px dashed #0066cc; padding: 2px 6px;">---</span>
        Gulf of Guinea (piracy)
    </p>
    <p style="margin: 4px 0;">
        <span style="border: 2px dashed #cc6600; padding: 2px 6px;">---</span>
        Sahel (terrorism)
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Data source: Belgian Defence<br>
        (mil.be/nl/onze-missies/missies-in-afrika)
    </p>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(overview_html))
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_file)
    print(f" African missions map saved to {output_file}")
    return m


if __name__ == "__main__":
    print("=" * 70)
    print("BELGIAN MILITARY MISSIONS IN AFRICA - Visualization")
    print("=" * 70)

    print("\nMission Overview:")
    print("  Three primary mission types across 5 countries")
    print("  1. Equipment support & training (DRC)")
    print("  2. Bilateral security cooperation (Benin)")
    print("  3. Embassy security detachments (Mali, Burkina Faso, Niger)")

    print("\nKey Operations:")
    print("  DRC - European Peace Facility (EPF)")
    print("    • Camp Lwama (Kindu): Equipment support for 31 Brigade")
    print("    • Mission duration: Through December 2027")
    print("    • Personnel: ~10 military")
    print("\n  Benin - Bilateral Partnership")
    print("    • 25+ years of cooperation")
    print("    • National Guard training")
    print("    • Maritime security in Gulf of Guinea")
    print("\n  Sahel Countries (Mali, Burkina Faso, Niger)")
    print("    • Diplomatic protection detachments (DAS)")
    print("    • Embassy security")
    print("    • Evacuation coordination capability")

    print("\nThreat Environments:")
    print("  • Gulf of Guinea: Piracy and maritime smuggling")
    print("  • Sahel Region: Terrorist activity and instability")

    print("\n" + "=" * 70)

    create_african_missions_map()

    print("\nNext visualizations to create:")
    print("  1. DRC detailed map - EPF operations and infrastructure")
    print("  2. Sahel detailed map - Security cooperation across region")
    print("\nNote: These will be separate Python visualization files.")
