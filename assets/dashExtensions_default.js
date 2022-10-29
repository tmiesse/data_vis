window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://www.freeiconspng.com/uploads/thunderstorm-icon-29.png`,
                iconSize: [30, 30]
            });
            return L.marker(latlng, {
                icon: flag
            });
        }
    }
});