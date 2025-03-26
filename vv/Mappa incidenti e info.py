from folium.plugins import MarkerCluster

# Crea un oggetto MarkerCluster per raggruppare i marker vicini
marker_cluster = MarkerCluster().add_to(incident_map)

# Aggiungi i marker con colore basato sul tipo di incidente al cluster
for lat, lon, year, incident_type in data:
    icon_color = "green" if incident_type == "Investimento" else "black"
    folium.Marker(
        location=[lat, lon],
        popup=f"Anno: {year}<br>Tipo: {incident_type}<br>({lat}, {lon})",
        icon=folium.Icon(color=icon_color, icon="info-sign")
    ).add_to(marker_cluster)  # Aggiungi i marker al cluster

# Aggiungi un pulsante "Info" con testo descrittivo
info_button = folium.Marker(
    location=[45.53991, 10.23166],  # Posizione del pulsante Info
    icon=folium.DivIcon(
        html=(
            '<button onclick="alert(\'Questa mappa mostra gli incidenti con colori diversi per tipo di evento. '
            'Verde indica gli investimenti, nero altri tipi di incidenti.\')" '
            'style="background-color: lightblue; border: 2px solid black; border-radius: 5px; padding: 5px;">Info</button>'
        )
    )
)
info_button.add_to(incident_map)  # Aggiungi il pulsante alla mappa
