import folium
from folium.plugins import HeatMap
import random

# Example list of coordinate pairs: [(lat, lon), ...]
coords = [
    (52.5200, 13.4050),
    (52.5201, 13.4052),
    (52.5199, 13.4048),
    # your many more points...
]
coords = [(random.random()+52, random.random()+13) for _ in range(10000)]

# Create base map centered roughly around the points
m = folium.Map(location=[coords[0][0], coords[0][1]], zoom_start=12, tiles="OpenStreetMap")

# Add heatmap layer
HeatMap(coords, radius=15, blur=10, max_zoom=1).add_to(m)

# Save as HTML
m.save("heatmap_view.html")
