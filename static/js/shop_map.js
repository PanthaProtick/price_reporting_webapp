// Initialize a Leaflet map, allow user to click to place a marker,
// and sync the marker position into hidden form fields `lat` and `lon`.
(function () {
  function qs(id) { return document.getElementById(id); }

  const map = L.map('map').setView([0, 0], 2);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  let marker = null;

  function setMarker(latlng) {
    if (marker) {
      marker.setLatLng(latlng);
    } else {
      marker = L.marker(latlng, { draggable: true }).addTo(map);
      marker.on('dragend', function (e) {
        const p = e.target.getLatLng();
        qs('lat').value = p.lat.toFixed(6);
        qs('lon').value = p.lng.toFixed(6);
      });
    }
    qs('lat').value = latlng.lat.toFixed(6);
    qs('lon').value = latlng.lng.toFixed(6);
  }

  map.on('click', function (e) {
    setMarker(e.latlng);
  });

  // Try to center map on user's location if available
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (pos) {
      const latlng = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      map.setView(latlng, 13);
    }, function () { /* ignore errors */ });
  }

  // Prevent form submission if lat/lon not set
  const form = qs('shop-form');
  if (form) {
    form.addEventListener('submit', function (ev) {
      if (!qs('lat').value || !qs('lon').value) {
        ev.preventDefault();
        alert('Please click on the map to set the shop location before submitting.');
      }
    });
  }
})();
