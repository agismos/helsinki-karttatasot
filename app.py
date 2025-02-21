from flask import Flask, render_template, request, jsonify
import requests
from pyproj import Transformer

app = Flask(__name__)

WFS_URL = "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"

def transform_coordinates(geometry):
    """ Muuntaa EPSG:3879 → EPSG:4326 """
    transformer = Transformer.from_crs("EPSG:3879", "EPSG:4326", always_xy=True)

    if geometry["type"] == "Point":
        x, y = geometry["coordinates"]
        lon, lat = transformer.transform(x, y)
        return {"type": "Point", "coordinates": [lon, lat]}

    elif geometry["type"] == "LineString":
        return {
            "type": "LineString",
            "coordinates": [list(transformer.transform(x, y)) for x, y in geometry["coordinates"]]
        }

    elif geometry["type"] == "Polygon":
        return {
            "type": "Polygon",
            "coordinates": [
                [list(transformer.transform(x, y)) for x, y in ring]
                for ring in geometry["coordinates"]
            ]
        }
    
    return geometry  # Palautetaan alkuperäinen, jos tyyppiä ei tunnisteta

def get_wfs_layer(layer_name, bbox):
    """ Hakee ja muuntaa WFS-rajapinnan GeoJSON-datan rajaamalla alueen """
    params = {
        "SERVICE": "WFS",
        "VERSION": "1.1.0",
        "REQUEST": "GetFeature",
        "TYPENAME": layer_name,
        "MAXFEATURES": 1000,
        "OUTPUTFORMAT": "json",
        "BBOX": bbox + ",EPSG:4326"  # Lisätään BBOX-parametri
    }
    response = requests.get(WFS_URL, params=params)
    if response.status_code == 200:
        geojson_data = response.json()

        # Muunnetaan jokaisen kohteen koordinaatit
        for feature in geojson_data.get("features", []):
            feature["geometry"] = transform_coordinates(feature["geometry"])

        return geojson_data

    return {"error": "WFS-haku epäonnistui"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_layer", methods=["POST"])
def get_layer():
    """ API-endpoint WFS-tason hakemiseen vain näkyvältä alueelta """
    data = request.json
    layer_name = data.get("layer_name")
    bbox = data.get("bbox")

    if not layer_name or not bbox:
        return jsonify({"error": "Layer name or BBOX missing"}), 400
    
    geojson_data = get_wfs_layer(layer_name, bbox)
    return jsonify(geojson_data)

if __name__ == "__main__":
    app.run(debug=True)
