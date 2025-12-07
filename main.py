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

cvg = Cases.validate_json(open("2024_cases_cvg_head.json").read())
print("cases loaded")

short_map = json.load(open("short_map_relevant.json"))
#print(short_map)
weights = json.load(open("entry_weights.json"))

#print(weights)
import networkx

G = networkx.DiGraph()

data = {}

for c in cvg:
    #print([d.text for d in c.docket])
    path = ["Filing"]+list(reversed([short_map.get(d.text) for d in c.docket if weights.get(d.text,0) > 1]))+[None]
    d = data
    for el in path:
        if el not in d:
            d[el] = {"children":{}, "cases":[c.case_number]}
        else:
            d[el]["cases"].append(c.case_number)
            pass
        d = d[el]["children"]
            #d[el][]

    for pos, (fr,to) in enumerate(zip(path, path[1:])):
        #print(pos, fr, to)
        frstr = f"{pos} ~ {fr}"
        tostr = f"{pos+1} ~ {to}"
        if G.has_edge(frstr, tostr):
            G[frstr][tostr]["cases"].append(c)
        else:
            G.add_edge(frstr, tostr, cases=[c])

print("data", json.dumps(data, indent=2))
for edge in G.edges:
    #print(edge, G[edge[0]][edge[1]]["cases"], hash(edge[0])%100000000)
    pass
    #break


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

    # --- 1. Read query parameter ---
    nodes_param = request.args.get("nodes", "")
    #print("raw val", nodes_param)
    node_list = [n.strip() for n in nodes_param.split("::") if n.strip()]
    #print("raw list", node_list)
    # --- 2. Validate nodes exist in graph ---
    valid_nodes = []

    for n in node_list:
        if n in G.nodes:
            valid_nodes.append(n)

    if not len(valid_nodes):
        valid_nodes = ['0 ~ Filing']
    #print("vn", valid_nodes)

    next = sorted([(len(G[e[0]][e[1]]["cases"]), e[1]) for e in G.out_edges(valid_nodes[-1])], reverse=True)

    # Example list of coordinate pairs: [(lat, lon), ...]
    if len(valid_nodes) > 1:
        cs = G[valid_nodes[-2]][valid_nodes[-1]]["cases"]
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
