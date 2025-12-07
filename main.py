import json
from collections import defaultdict

from flask import Flask, render_template, request
import folium
from folium.plugins import HeatMap
from idna.idnadata import joining_types

from pyschema import Case
from pydantic import TypeAdapter

from test import coords

Cases = TypeAdapter(list[Case])

cvg = Cases.validate_json(open("2024_cases_cvg.json").read())
print("cases loaded")

short_map = json.load(open("short_map_relevant.json"))
#print(short_map)
weights = json.load(open("entry_weights.json"))

#print(weights)
import networkx

def tree():
    return defaultdict(tree)

def insert_path(root, path, case_id=None):
    node = root
    for step in path:
        node = node[step]
        if case_id is not None:
            node.setdefault("_cases", []).append(case_id)
    return root


root = tree()

for c in cvg:
    #print([d.text for d in c.docket])
    path = ["Filing"]+list(reversed([short_map.get(d.text) for d in c.docket if weights.get(d.text,0) > 1]))

    insert_path(root, path, case_id=c)


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


def get_subtree(tree, path_parts):
    """Descend into the nested dictionaries following path_parts."""
    node = tree
    for part in path_parts:
        if part not in node:
            return None
        node = node[part]
    return node


@app.route("/map/", defaults={"path": ""})
@app.route("/map/<path:path>")
def test(path):
    parts = [p for p in path.split("/") if p]

    subtree = get_subtree(root, parts)
    if subtree is None:
        return

    # ----- Breadcrumbs -----
    breadcrumbs = [("Home", "/map/")]

    for i in range(len(parts)):
        prefix = parts[:i + 1]
        st = get_subtree(root, prefix)
        breadcrumbs.append((
            f"{len(st['_cases'])} {prefix[-1]}",
            "/map/" + "/".join(prefix)
        ))

    # ---- Build child links ----
    children = sorted([
        (f"{len(subtree[key]['_cases'])} {key}", "/map/" + "/".join(parts + [key]), len(subtree[key]['_cases']))
        for key in subtree.keys()
        if key != "_cases"
    ], key=lambda x:x[2], reverse=True)

    if len(subtree["_cases"]) > 1:
        coords = [c.location for c in subtree["_cases"] if c.location is not None]
    else:
        coords = [c.location for c in cvg if c.location is not None]
        
    m = folium.Map(location=[coords[0][0], coords[0][1]], zoom_start=11, tiles="OpenStreetMap")

    # Add heatmap layer
    HeatMap(coords, radius=10, blur=20, max_zoom=1).add_to(m)

    # Render map to HTML string
    map_html = m._repr_html_()  # or m.get_root().render()

    return render_template("map.html", map_html=map_html, breadcrumbs=breadcrumbs,
        children=children,)

    return jsonify({
        "path": parts,
        "breadcrumbs": breadcrumbs,
        "children": children
    })

    # Example list of coordinate pairs: [(lat, lon), ...]
    if len(valid_nodes) > 1:
        cs = d["cases"]
        coords = [c.location for c in cs if c.location is not None]
    else:
        coords = [c.location for c in cvg if c.location is not None]
    #print(coords)
    # Create base map centered roughly around the points
    m = folium.Map(location=[coords[0][0], coords[0][1]], zoom_start=11, tiles="OpenStreetMap")

    # Add heatmap layer
    HeatMap(coords, radius=10, blur=20, max_zoom=1).add_to(m)

    # Render map to HTML string
    map_html = m._repr_html_()  # or m.get_root().render()

    return render_template("map.html", map_html=map_html, items=valid_nodes, next=next )
