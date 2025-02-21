let map = L.map('map').setView([60.1699, 24.9384], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
}).addTo(map);

let layerGroup = L.layerGroup().addTo(map);

function loadLayer() {
    fetch('/get_layer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layer_name: 'avoindata:YLRE_Katu_ja_viherosat_eiliikenne_alue' })
    })
    .then(response => response.json())
    .then(data => {
        console.log("GeoJSON Features:", data.features);

        if (data.features) {
            let geoJsonLayer = L.geoJSON(data, {
                onEachFeature: function (feature, layer) {
                    if (feature.properties) {
                        layer.bindPopup("Tunniste: " + feature.id);
                    }
                }
            });
            layerGroup.clearLayers();
            layerGroup.addLayer(geoJsonLayer);
        } else {
            alert("Virhe ladattaessa tasoa.");
        }
    })
    .catch(error => console.error('Fetch error:', error));
}
