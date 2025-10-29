#!/usr/bin/env python3
"""
Visualize current NATO and EU membership.

Shows overlap between NATO (North Atlantic Treaty Organization) and
European Union membership as of 2024.

Three categories:
- Both NATO and EU members
- EU only (not NATO)
- NATO only (not EU)

Current status:
- NATO: 32 member states
- EU: 27 member states
- Both: 23 member states

INPUT: data/ne_110m_admin_0_countries.geojson
OUTPUT: maps/nato_eu_membership_map.html
"""
import json
import folium


def get_country_geojson(cache_file='data/ne_110m_admin_0_countries.geojson'):
    """Load Natural Earth countries GeoJSON from cache."""
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_nato_eu_map(output_file='maps/nato_eu_membership_map.html'):
    """
    Create map showing NATO and EU membership overlap.

    Colors:
    - Purple: Both NATO and EU members
    - Blue: NATO only
    - Yellow: EU only
    """

    # Center on Europe
    m = folium.Map(
        location=[50.0, 15.0],  # Central Europe
        zoom_start=3,
        tiles='CartoDB positron'
    )

    # Load Natural Earth data
    geojson_data = get_country_geojson()

    # Current NATO members (32)
    nato_members = {
        # Original members
        'Belgium', 'Canada', 'Denmark', 'France', 'Iceland', 'Italy',
        'Luxembourg', 'Netherlands', 'Norway', 'Portugal', 'United Kingdom',
        'United States of America',
        # Cold War expansion
        'Greece', 'Turkey', 'Germany', 'Spain',
        # Post-Cold War expansion
        'Czechia', 'Hungary', 'Poland',
        'Bulgaria', 'Estonia', 'Latvia', 'Lithuania', 'Romania',
        'Slovakia', 'Slovenia',
        'Albania', 'Croatia',
        'Montenegro', 'North Macedonia',
        'Finland', 'Sweden'
    }

    # Current EU members (27) - as of 2024
    eu_members = {
        # Founding 6 (1957)
        'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg', 'Netherlands',
        # 1973 expansion
        'Denmark', 'Ireland',
        # 1980s expansion
        'Greece', 'Spain', 'Portugal',
        # 1995 expansion
        'Austria', 'Finland', 'Sweden',
        # 2004 expansion
        'Cyprus', 'Czechia', 'Estonia', 'Hungary', 'Latvia', 'Lithuania',
        'Poland', 'Slovakia', 'Slovenia',
        # Note: Malta is EU member but not visible in 110m Natural Earth dataset (too small)
        # 2007 expansion
        'Bulgaria', 'Romania',
        # 2013 expansion
        'Croatia'
        # Note: UK left EU in 2020 (Brexit)
    }

    # Categorize countries
    both_nato_eu = nato_members.intersection(eu_members)
    nato_only = nato_members - eu_members
    eu_only = eu_members - nato_members

    # Define colors and information
    country_info = {}

    for country in both_nato_eu:
        country_info[country] = {
            'category': 'Both NATO & EU',
            'color': '#9933cc',  # Purple
            'details': 'Member of both NATO and European Union'
        }

    for country in nato_only:
        country_info[country] = {
            'category': 'NATO Only',
            'color': '#0066cc',  # Blue
            'details': 'NATO member, not in European Union'
        }

    for country in eu_only:
        country_info[country] = {
            'category': 'EU Only',
            'color': '#ffcc00',  # Yellow
            'details': 'European Union member, not in NATO'
        }

    # Add country polygons
    for feature in geojson_data['features']:
        country_name = feature['properties'].get('NAME')

        if country_name in country_info:
            info = country_info[country_name]

            popup_html = f"""
            <div style="width: 260px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0;">{country_name}</h4>
                <p style="margin: 4px 0;"><b>Status:</b> {info['category']}</p>
                <p style="margin: 4px 0; font-size: 11px;">{info['details']}</p>
            </div>
            """

            folium.GeoJson(
                feature,
                style_function=lambda x, color=info['color']: {
                    'fillColor': color,
                    'color': '#333333',
                    'weight': 1.5,
                    'fillOpacity': 0.7
                },
                highlight_function=lambda x: {
                    'fillOpacity': 0.9,
                    'weight': 2.5
                },
                tooltip=f"{country_name} - {info['category']}",
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    # NATO HQ marker
    folium.Marker(
        location=[50.8799, 4.4258],  # Brussels, Belgium
        popup="""
        <div style="width: 220px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">NATO Headquarters</h4>
            <p style="margin: 4px 0;"><b>Location:</b> Brussels, Belgium</p>
        </div>
        """,
        tooltip="NATO HQ - Brussels",
        icon=folium.Icon(color='darkblue', icon='star', prefix='fa')
    ).add_to(m)

    # EU HQ marker
    folium.Marker(
        location=[50.8467, 4.3525],  # Brussels, Belgium (EU institutions)
        popup="""
        <div style="width: 220px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 8px 0;">EU Headquarters</h4>
            <p style="margin: 4px 0;"><b>Location:</b> Brussels, Belgium</p>
            <p style="margin: 4px 0; font-size: 10px;">European Commission & Council</p>
        </div>
        """,
        tooltip="EU HQ - Brussels",
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(m)

    # Overview box
    overview_html = f'''
    <div style="position: fixed;
                top: 80px; right: 15px; width: 300px;
                background-color: white; border:2px solid #9933cc; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.5;">
    <p style="margin: 0 0 8px 0; font-weight: bold; color: #9933cc;">NATO & EU Membership (2024)</p>
    <p style="margin: 4px 0; font-size: 10px;">
        <b style="color: #9933cc;">Both NATO & EU:</b> {len(both_nato_eu)} countries<br>
        → Most European NATO members<br>
        → Includes Belgium (hosts both HQs)<br><br>

        <b style="color: #0066cc;">NATO Only:</b> {len(nato_only)} countries<br>
        → Includes USA, Canada, UK<br>
        → Turkey, Albania, North Macedonia<br>
        → Iceland, Norway, Montenegro<br><br>

        <b style="color: #ffcc00;">EU Only:</b> {len(eu_only)} countries<br>
        → Ireland, Austria (neutral states)<br>
        → Cyprus (island nation)<br>
        → Note: Malta not visible at this scale<br>
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Total NATO: {len(nato_members)} members<br>
        Total EU: {len(eu_members)} visible (27 total incl. Malta)
    </p>
    </div>
    '''

    # Legend with counts
    legend_html = f'''
    <div style="position: fixed;
                bottom: 50px; right: 15px; width: 280px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:11px; padding: 12px; line-height: 1.6;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">Membership Categories</p>
    <p style="margin: 4px 0;">
        <span style="background-color: #9933cc; padding: 2px 12px; border-radius: 3px; color: white;">■</span>
        <b>Both NATO & EU</b> ({len(both_nato_eu)} countries)
    </p>
    <p style="margin: 4px 0;">
        <span style="background-color: #0066cc; padding: 2px 12px; border-radius: 3px; color: white;">■</span>
        <b>NATO Only</b> ({len(nato_only)} countries)
    </p>
    <p style="margin: 4px 0;">
        <span style="background-color: #ffcc00; padding: 2px 12px; border-radius: 3px;">■</span>
        <b>EU Only</b> ({len(eu_only)} countries)
    </p>
    <p style="margin: 8px 0 4px 0; border-top: 1px solid #ccc; padding-top: 8px;">
        <i class="fa fa-star" style="color: darkblue;"></i> NATO HQ (Brussels)<br>
        <i class="fa fa-star" style="color: orange;"></i> EU HQ (Brussels)
    </p>
    <p style="margin: 8px 0 0 0; font-size: 9px; color: #666;">
        Belgium: Member of both alliances<br>
        and hosts both headquarters
    </p>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(overview_html))
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_file)
    print(f"✓ NATO-EU membership map saved to {output_file}")
    return m, both_nato_eu, nato_only, eu_only


if __name__ == "__main__":
    print("=" * 70)
    print("NATO & EU MEMBERSHIP - Current Status (2024)")
    print("=" * 70)

    nato_members = {
        'Belgium', 'Canada', 'Denmark', 'France', 'Iceland', 'Italy',
        'Luxembourg', 'Netherlands', 'Norway', 'Portugal', 'United Kingdom',
        'United States of America', 'Greece', 'Turkey', 'Germany', 'Spain',
        'Czechia', 'Hungary', 'Poland', 'Bulgaria', 'Estonia', 'Latvia',
        'Lithuania', 'Romania', 'Slovakia', 'Slovenia', 'Albania', 'Croatia',
        'Montenegro', 'North Macedonia', 'Finland', 'Sweden'
    }

    eu_members = {
        'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg', 'Netherlands',
        'Denmark', 'Ireland', 'Greece', 'Spain', 'Portugal', 'Austria',
        'Finland', 'Sweden', 'Cyprus', 'Czechia', 'Estonia', 'Hungary',
        'Latvia', 'Lithuania', 'Poland', 'Slovakia', 'Slovenia',
        'Bulgaria', 'Romania', 'Croatia'
        # Note: Malta excluded (too small for 110m scale map)
    }

    both = nato_members.intersection(eu_members)
    nato_only = nato_members - eu_members
    eu_only = eu_members - nato_members

    print(f"\nMembership Statistics:")
    print(f"  Total NATO members: {len(nato_members)}")
    print(f"  Total EU members: {len(eu_members)} visible (27 total, Malta not shown)")
    print(f"  Both NATO & EU: {len(both)}")
    print(f"  NATO only: {len(nato_only)}")
    print(f"  EU only: {len(eu_only)}")

    print(f"\nBoth NATO & EU ({len(both)} countries):")
    print(f"  {', '.join(sorted(both))}")

    print(f"\nNATO Only ({len(nato_only)} countries):")
    print(f"  {', '.join(sorted(nato_only))}")

    print(f"\nEU Only ({len(eu_only)} countries):")
    print(f"  {', '.join(sorted(eu_only))}")

    print("\nKey Notes:")
    print("  • Belgium hosts both NATO and EU headquarters in Brussels")
    print("  • UK left EU in 2020 (Brexit) but remains in NATO")
    print("  • Ireland and Austria maintain military neutrality (EU only)")
    print("  • Cyprus and Malta: EU only (Malta too small for this map scale)")
    print("  • Turkey, Albania, North Macedonia: NATO but not EU")
    print("  • Most EU members are also in NATO")

    print("\n" + "=" * 70)

    create_nato_eu_map()

    print("\nVisualization complete!")
