#!/usr/bin/env python3
"""
Visualize NATO Alliance member countries with historical context.

NATO (North Atlantic Treaty Organization) formed in 1949 as a collective
defense alliance. The map distinguishes between:
- Original/Cold War members (joined before 1989)
- Post-Cold War expansion members (joined 1989 or later)

The year 1989 marks the fall of the Berlin Wall.

Historical Context:
- 1949: NATO founded with 12 members
- 1952-1982: Gradual expansion (Greece, Turkey, W. Germany, Spain)
- 1989: Fall of Berlin Wall
- 1999-2024: Major Eastern European expansion (16 new members)
- Current: 32 member states (as of 2024 with Sweden)

INPUT: data/geojson/ne_110m_admin_0_countries.geojson
OUTPUT:  maps/nato_alliance_map.html
"""
import json
import folium


def get_country_geojson(cache_file='data/geojson/ne_110m_admin_0_countries.geojson'):
    """Load Natural Earth countries GeoJSON from cache."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_nato_alliance_map(output_file='maps/nato_alliance_map.html'):
    """
    Create map of NATO alliance with historical membership context.

    Colors:
    - Dark blue: Original/Cold War members (before 1989)
    - Light blue: Post-Cold War expansion (1989 and after)
    """

    # Center on North Atlantic region
    m = folium.Map(
        location=[50.0, 15.0],  # Central Europe
        zoom_start=3,
        tiles='CartoDB positron'
    )

    # Load Natural Earth data
    geojson_data = get_country_geojson()

    # NATO member countries with accession dates
    # Note: Using country names as they appear in Natural Earth GeoJSON
    nato_members = {
        # Original members (1949) - Dark blue
        'Belgium': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Canada': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Denmark': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'France': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Iceland': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Italy': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Luxembourg': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Netherlands': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Norway': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'Portugal': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'United Kingdom': {'year': 1949, 'era': 'original', 'color': '#003399'},
        'United States of America': {'year': 1949, 'era': 'original', 'color': '#003399'},

        # Cold War expansion (before 1989) - Dark blue
        'Greece': {'year': 1952, 'era': 'cold_war', 'color': '#003399'},
        'Turkey': {'year': 1952, 'era': 'cold_war', 'color': '#003399'},
        'Germany': {'year': 1955, 'era': 'cold_war', 'color': '#003399'},  # West Germany initially
        'Spain': {'year': 1982, 'era': 'cold_war', 'color': '#003399'},

        # Post-Cold War expansion (1989+) - Light blue
        'Czechia': {'year': 1999, 'era': 'post_cold_war', 'color': '#6699cc'},  # Czech Republic
        'Hungary': {'year': 1999, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Poland': {'year': 1999, 'era': 'post_cold_war', 'color': '#6699cc'},

        'Bulgaria': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Estonia': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Latvia': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Lithuania': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Romania': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Slovakia': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Slovenia': {'year': 2004, 'era': 'post_cold_war', 'color': '#6699cc'},

        'Albania': {'year': 2009, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Croatia': {'year': 2009, 'era': 'post_cold_war', 'color': '#6699cc'},

        'Montenegro': {'year': 2017, 'era': 'post_cold_war', 'color': '#6699cc'},
        'North Macedonia': {'year': 2020, 'era': 'post_cold_war', 'color': '#6699cc'},

        'Finland': {'year': 2023, 'era': 'post_cold_war', 'color': '#6699cc'},
        'Sweden': {'year': 2024, 'era': 'post_cold_war', 'color': '#6699cc'},
    }

    # Add country polygons
    for feature in geojson_data['features']:
        country_name = feature['properties'].get('NAME')

        if country_name in nato_members:
            info = nato_members[country_name]

            era_text = {
                'original': 'Founding Member (1949)',
                'cold_war': 'Cold War Era Member',
                'post_cold_war': 'Post-Cold War Expansion'
            }[info['era']]
            if country_name == 'Germany':
                popup_html = f"""
            <div style="width: 260px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">(West) {country_name}</h4>
                <p style="margin: 4px 0;"><b>Joined NATO:</b> {info['year']}</p>
                <p style="margin: 4px 0;"><b>Era:</b> {era_text}</p>
            </div>
            """
            else:
                popup_html = f"""
            <div style="width: 260px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">{country_name}</h4>
                <p style="margin: 4px 0;"><b>Joined NATO:</b> {info['year']}</p>
                <p style="margin: 4px 0;"><b>Era:</b> {era_text}</p>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x, color=info['color']: {
                    'fillColor': color,
                    'color': '#000000',
                    'weight': 1.5,
                    'fillOpacity': 0.7
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.9,
                    'weight': 2.5
                },
                tooltip=f"{country_name} ({info['year']})",
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    # NATO Headquarters marker
    folium.Marker(
        location=[50.8799, 4.4258],  # Brussels, Belgium
        popup="""
        <div style="width: 220px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">NATO Headquarters</h4>
            <p style="margin: 4px 0;"><b>Location:</b> Brussels, Belgium</p>
            <p style="margin: 4px 0;"><b>Since:</b> 1967 (moved from Paris)</p>
        </div>
        """,
        tooltip="NATO HQ - Brussels",
        icon=folium.Icon(color='darkblue', icon='star')
    ).add_to(m)

    # Historical timeline box
    timeline_html = '''
    <div style="position: fixed;
                top: 80px; right: 15px; width: 320px;
                background-color: white; border:2px solid #003399; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.5;">
    <p style="margin: 0 0 8px 0; font-weight: bold; color: #003399;">NATO Expansion Timeline</p>
    <p style="margin: 4px 0; font-size: 10px;">
        <b style="color: #003399;">Before 1989 (Cold War Era):</b><br>
        • 1949: 12 founding members<br>
        • 1952: Greece, Turkey<br>
        • 1955: West Germany<br>
        • 1982: Spain<br>
        <b>Total: 16 members by 1989</b><br><br>

        <b style="color: #6699cc;">After 1989 (Post-Cold War):</b><br>
        • 1999: Czech Rep., Hungary, Poland<br>
        • 2004: 7 Eastern European states<br>
        • 2009: Albania, Croatia<br>
        • 2017: Montenegro<br>
        • 2020: North Macedonia<br>
        • 2023: Finland<br>
        • 2024: Sweden<br>
        <b>Total: 32 members as of 2024</b>
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Article 5: Collective defense - attack on<br>
        one is attack on all (invoked once: 9/11)
    </p>
    </div>
    '''

    # Legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 15px; width: 280px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.6;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">NATO Alliance</p>
    <p style="margin: 4px 0;">
        <span style="background-color: #003399; padding: 2px 12px; border-radius: 3px;">■</span>
        <b>Before 1989</b> - Original & Cold War members (16)
    </p>
    <p style="margin: 4px 0;">
        <span style="background-color: #6699cc; padding: 2px 12px; border-radius: 3px;">■</span>
        <b>After 1989</b> - Post-Cold War expansion (16)
    </p>
    <p style="margin: 4px 0;">
        <i class="fa fa-star" style="color: darkblue;"></i>
        NATO Headquarters (Brussels)
    </p>
    <p style="margin: 8px 0 4px 0; font-size: 10px; color: #333;">
        <b>Belgium's Role:</b><br>
        • Founding member (1949)<br>
        • Hosts NATO HQ since 1967<br>
        • Active contributor to missions
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Data source: NATO official records<br>
        32 member states as of 2024
    </p>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(timeline_html))
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_file)
    print(f" NATO alliance map saved to {output_file}")
    return m


if __name__ == "__main__":
    print("=" * 70)
    print("NATO ALLIANCE - Historical Membership Visualization")
    print("=" * 70)

    print("\nAlliance Overview:")
    print("  NATO (North Atlantic Treaty Organization)")
    print("  Collective defense alliance founded 1949")
    print("  Current membership: 32 countries (as of 2024)")

    print("\nMembership Eras:")
    print("  BEFORE 1989 (Cold War Era) - Dark Blue:")
    print("    • 1949: Belgium, Canada, Denmark, France, Iceland, Italy,")
    print("            Luxembourg, Netherlands, Norway, Portugal, UK, USA")
    print("    • 1952: Greece, Turkey")
    print("    • 1955: West Germany (unified Germany in 1990)")
    print("    • 1982: Spain")
    print("    Total: 16 members by 1989")

    print("\n  AFTER 1989 (Post-Cold War Expansion) - Light Blue:")
    print("    • 1999: Czech Republic, Hungary, Poland")
    print("    • 2004: Bulgaria, Estonia, Latvia, Lithuania, Romania,")
    print("            Slovakia, Slovenia")
    print("    • 2009: Albania, Croatia")
    print("    • 2017: Montenegro")
    print("    • 2020: North Macedonia")
    print("    • 2023: Finland")
    print("    • 2024: Sweden")
    print("    Total: 16 new members since 1989")

    print("\nKey Facts:")
    print("  • Article 5: Collective defense principle")
    print("  • Invoked once in history: September 12, 2001 (after 9/11)")
    print("  • HQ: Brussels, Belgium (since 1967)")
    print("  • Belgium: Founding member and host nation")

    print("\n" + "=" * 70)

    create_nato_alliance_map()

    print("\nMap Features:")
    print("  - Dark blue: Pre-1989 members (Cold War era)")
    print("  - Light blue: Post-1989 members (expansion era)")
    print("  - Focus: US-European-Eurasia region")
    print("  - Interactive tooltips with accession dates")
