// 🗺️ Initialize Leaflet map
let map = L.map('map').setView([0, 0], 13);

// 🌍 Load OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data © OpenStreetMap contributors'
}).addTo(map);

// 🚌 Initial Bus Marker
let busMarker = L.marker([0, 0], {
  icon: L.icon({
    iconUrl: "https://maps.google.com/mapfiles/kml/shapes/bus.png",
    iconSize: [32, 32],
    iconAnchor: [16, 32]
  })
}).addTo(map);

// 📍 User’s Alert Marker
let alertMarker = null;
let alertLocation = null; // stores [lat, lng]

// 📍 Center map to current user location
navigator.geolocation.getCurrentPosition(
  (position) => {
    const userLat = position.coords.latitude;
    const userLng = position.coords.longitude;

    map.setView([userLat, userLng], 14);

    // ✅ User Location Marker (green pin)
    const userIcon = L.icon({
      iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
      iconSize: [30, 30],
      iconAnchor: [15, 30],
    });

    L.marker([userLat, userLng], { icon: userIcon })
      .addTo(map)
      .bindPopup("📍 You are here");
  },
  (error) => {
    alert("⚠️ Location access denied.");
    console.error(error);
    map.setView([12.9716, 77.5946], 13); // fallback to Bangalore
  }
);

// 🖱️ Set alert location on map click
map.on("click", function (e) {
  // Remove old alert marker
  if (alertMarker) {
    map.removeLayer(alertMarker);
  }

  alertLocation = [e.latlng.lat, e.latlng.lng];

  alertMarker = L.marker(alertLocation)
    .addTo(map)
    .bindPopup("📍 Alert set here")
    .openPopup();

  alert("✅ Alert set at:\nLat: " + alertLocation[0].toFixed(5) + "\nLng: " + alertLocation[1].toFixed(5));
});

// 🔁 Load Route Dropdown Options
function populateRouteDropdown() {
  fetch('/get_routes')
    .then(res => res.json())
    .then(routes => {
      const dropdown = document.getElementById("route_no");
      dropdown.innerHTML = '<option value="">-- Select Route --</option>';
      routes.forEach(route => {
        const opt = document.createElement("option");
        opt.value = route.route_no;
        opt.textContent = route.route_no;
        dropdown.appendChild(opt);
      });
    })
    .catch(err => {
      console.error("❌ Failed to load route dropdown:", err);
    });
}

// 📦 Optional Helpers (for admin/department panel)
function loadRoutes() {
  // Expected to be implemented in department.html (already exists)
}
function loadBuses() {
  // Expected to be implemented in department.html (already exists)
}

// 🔁 Auto-call on page load
window.onload = () => {
  if (typeof loadRoutes === 'function') loadRoutes();
  if (typeof loadBuses === 'function') loadBuses();
  if (document.getElementById("route_no")) populateRouteDropdown();
};

// 🚀 Ready for extension: You can add periodic bus location updates, alert triggering, etc.
