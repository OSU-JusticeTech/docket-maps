import json

from flask import Flask, render_template
import folium
from folium.plugins import HeatMap

from pyschema import Case
from pydantic import TypeAdapter

Cases = TypeAdapter(list[Case])

cvg = Cases.validate_json(open("2024_cases_cvg_head.json").read())

print("cases loaded")

geo = json.load(open("case_geo_2024.json"))

for c in cvg:
    if c.case_number in geo:
        c.location = tuple(map(float,reversed(geo[c.case_number])))
    else:
        pass
        #print("missing", c.case_number)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/map")
def test():
    # Example list of coordinate pairs: [(lat, lon), ...]
    coords = [c.location for c in cvg if c.location is not None]
    #print(coords)
    # Create base map centered roughly around the points
    m = folium.Map(location=[coords[0][0], coords[0][1]], zoom_start=11, tiles="OpenStreetMap")

    # Add heatmap layer
    HeatMap(coords, radius=10, blur=20, max_zoom=1).add_to(m)

    # Render map to HTML string
    map_html = m._repr_html_()  # or m.get_root().render()

    return render_template("map.html", map_html=map_html)
