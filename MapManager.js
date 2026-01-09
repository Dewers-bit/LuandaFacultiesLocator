class MapManager {
    constructor(mapId, onMarkerClick) {
        this.map = null;
        this.markers = [];
        this.onMarkerClick = onMarkerClick; // Callback for click handling
        this.initMap(mapId);
    }

    initMap(mapId) {
        // Center on Luanda
        this.map = L.map(mapId, {
            zoomControl: false // We can add it back in a better position if needed
        }).setView([-8.839988, 13.289437], 13);

        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);

        // Dark map style using CartoDB Dark Matter
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(this.map);
    }

    addMarkers(institutions) {
        // Clear existing
        this.markers.forEach(m => this.map.removeLayer(m));
        this.markers = [];

        institutions.forEach(inst => {
            const marker = L.marker([inst.latitude, inst.longitude]);

            // Add White Label (Tooltip)
            marker.bindTooltip(inst.name, {
                permanent: true,
                direction: 'bottom',
                className: 'map-label', // This class is styled in CSS to be white
                offset: [0, 10]
            });

            // Handle Click -> Show Info Card
            marker.on('click', () => {
                this.map.setView(marker.getLatLng(), 15);
                if (this.onMarkerClick) this.onMarkerClick(inst);
            });

            marker.addTo(this.map);
            this.markers.push({ id: inst.id, marker });
        });
    }

    focusMarker(id) {
        const target = this.markers.find(m => m.id === id);
        if (target) {
            this.map.setView(target.marker.getLatLng(), 16);
            // Trigger the click logic visually to show info
            target.marker.fire('click');
        }
    }
}
