/**
 * Makes an AJAX call that retrieves data from the input date.
 * This data is then visualized using the addDataToMap function.
 *
 * @param date
 */
function visualize(date) {
    $.ajax({
        dataType: "json",
        url: "Data.php",
        data: {date: date} // Pass in date for database querying
    }).done(function(data){
        mapFunctions.addDataToMap(data);
    });
}

var mapFunctions = (function() {
    var map,
        networkControl,
        networkButtons = [],
        activeLayers = [];

    // Leaflet control for network buttons
    L.Control.NetworkControl = L.Control.extend({
        options: {
            position: 'topleft'
        },

        onAdd: function () {
            var networkBtns = L.DomUtil.create('div', 'btn-group-vertical');
            networkBtns.id = "network-btns";
            return networkBtns;
        }
    });

    // Leaflet control for clearing map
    L.Control.ClearControl = L.Control.extend({
        options: {
            position: 'topright'
        },

        onAdd: function () {
            var clearBtn = L.DomUtil.create('Button', 'clear-btn btn');
            clearBtn.innerHTML = "Clear Map";
            clearBtn.ondblclick = L.DomEvent.stopPropagation;
            clearBtn.onclick = function() {
                // Change each network button's appearance
                networkButtons.forEach(function(btn) {
                    btn.className = "network-btn btn";
                })

                // Remove all active layers
                activeLayers.forEach(function(layer){
                    map.removeLayer(layer);
                });
                activeLayers = [];
            };
            return clearBtn;
        }
    });

    /**
     * Creates map then calls the input callback
     *
     * @param callback
     */
    function createMap(callback) {
        map = new L.Map("map", {
            center: [10, 0],
            zoom: 2,
            minZoom: 2
        }).addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

        // Add clear button
        var clearControl = new L.Control.ClearControl();
        clearControl.addTo(map);

        callback();
    }

    /**
     * Creates the visualizations from the input JSON
     *
     * @param json
     */
    function addDataToMap(json) {
        if(networkControl){
            // Remove all active layers
            activeLayers.forEach(function(layer){
                map.removeLayer(layer);
            });
            activeLayers = [];

            // Remove current network buttons
            map.removeControl(networkControl)
        }
        networkControl = new L.Control.NetworkControl();
        networkControl.addTo(map);

        var networkBtns = L.DomUtil.get("network-btns");

        var networks = json.Networks;
        networks.forEach(function (network) { // Iterate over networks
            var name = network.Name.replace(/\W/g, "").toUpperCase(),
                aggRoutes = network.Aggregate_Routes,
                networkLayer = [],
                aggRouteColor = getLogoColorScale(name, aggRoutes.length),
                icon = getIcon(name);

            if(aggRoutes.length > 0) {
                if (aggRoutes.length == 1 && aggRoutes[0].Destination == "Unknown") {
                    return;
                }
                var splitBtn = L.DomUtil.create("div", "btn-group", networkBtns);

                var networkBtn = L.DomUtil.create("button", "network-btn btn", splitBtn);
                networkBtn.innerHTML = getInnerHTML(name);
                networkBtn.ondblclick = L.DomEvent.stopPropagation;

                var dropdownBtn = L.DomUtil.create("button", "btn dropdown-toggle", splitBtn);
                dropdownBtn.setAttribute("data-toggle", "dropdown");
                dropdownBtn.innerHTML = "<span class= caret-right></span>";
                dropdownBtn.ondblclick = L.DomEvent.stopPropagation;
                dropdownBtn.onclick = (function (b) {
                    var disabled = false;

                    return function () {
                        if (! disabled) {
                            b.blur();
                        }
                    }
                }(dropdownBtn));

                var dropdownMenu = L.DomUtil.create("ul", "network-dropdown dropdown-menu pull-right", splitBtn);
                dropdownMenu.ondblclick = L.DomEvent.stopPropagation;

                var title = document.createElement("li");
                title.style.textAlign = "center";
                title.style.cursor = "default";
                var label = document.createTextNode("Destinations");
                title.appendChild(label);
                dropdownMenu.appendChild(title);

                var divider = document.createElement("li");
                divider.className += "divider";
                dropdownMenu.appendChild(divider);

                // Iterating over aggregate routes
                for (var i = 0; i< aggRoutes.length; i++) {
                    var curr = aggRoutes[i];

                    if (curr.Destination == "Unknown") {
                        continue;
                    }

                    var aggRoute = curr.Aggregate_Route;
                    var ispRTT = curr.ISP_RTT;

                    var aggRouteLayer = new L.layerGroup();

                    var source = new L.latLng(aggRoute[0].lat, aggRoute[0].lng); // Aggregate route source

                    var sourceMarker = L.marker(source, {icon: icon});
                    var sourceName = aggRoute[0].Name ? aggRoute[0].Name : "Unknown";
                    sourceMarker.bindPopup("<b>AS Name:</b> " + sourceName);
                    aggRouteLayer.addLayer(sourceMarker);

                    var dest = new L.latLng(aggRoute[1].lat, aggRoute[1].lng); // Aggregate route destination

                    var aggRoutePoints = [source, dest];
                    var polyline = L.polyline(aggRoutePoints, {snakingSpeed: 100 / ispRTT * 1000})
                        .setStyle({
                            color: aggRouteColor(i + 1),
                            weight: 6.5,
                            opacity: .8
                        });
                    polyline.bindPopup("<b>ISP RTT:</b> " + Math.ceil(ispRTT * 1000) / 1000 + "ms" + "<br>" +
                        "<b>Final RTT: </b>" + Math.ceil(curr.Final_RTT * 1000) / 1000 + "ms");

                    aggRouteLayer.addLayer(polyline);


                    var destMarker = L.marker(dest, {icon: icon});
                    destMarker.bindPopup("<b>AS Name:</b> " + aggRoute[1].Name);
                    aggRouteLayer.addLayer(destMarker);

                    networkLayer.push(aggRouteLayer);

                    var traceroutesLayer = [];

                    var traceroutes = curr.Traceroutes,
                        routesColor = getLogoColorScale(name, traceroutes.length);

                    // Iterating over individual traceroutes
                    for (var j = 0; j < traceroutes.length; j++) {
                        var route = traceroutes[j];
                        if (j != 0 && route.length > 1) {
                            var routes = [];
                            // Iterating over hops in the individual traceroute
                            for (var k = 0; k < route.length - 1; k++) {
                                var hop = route[k]
                                var nextHop = route[k + 1];
                                routes.push({
                                    name: nextHop.Name,
                                    points: [new L.latLng(hop.lat, hop.lng), new L.latLng(nextHop.lat, nextHop.lng)],
                                    RTT: hop.RTT
                                })
                            }

                            var routeLayer = new L.layerGroup(); // Layer group for the individual traceroute

                            // Initial marker
                            var marker = L.marker(routes[0].points[0], {icon: icon});
                            marker.bindPopup("<b>AS Name:</b> " + routes[0].name);
                            routeLayer.addLayer(marker);

                            // Creating route
                            var routeColor = routesColor(j);
                            routes.forEach(function (route) {
                                var polyline = L.polyline(route.points, {snakingSpeed: 100 / route.RTT * 1000})
                                    .setStyle({
                                        weight: 6.5,
                                        color: routeColor,
                                        opacity: .8
                                    });
                                polyline.bindPopup("<b>RTT:</b> " + route.RTT + "ms");
                                routeLayer.addLayer(polyline);

                                var marker = L.marker(route.points[1], {icon: icon});
                                marker.bindPopup("<b>AS Name:</b> " + route.name);
                                routeLayer.addLayer(marker);
                            })
                            traceroutesLayer.push(routeLayer); // Add to layer group for all individual traceroutes
                        }
                    }

                    var subMenu = L.DomUtil.create("li", "dropdown-submenu", dropdownMenu);
                    var label = document.createElement("a");
                    label.innerHTML = curr.Destination;
                    subMenu.appendChild(label);

                    var subMenuDropdown = L.DomUtil.create("ul", "dropdown-menu", subMenu);

                    var aggRouteListEl = document.createElement("li");
                    var aggRouteBtn = document.createElement("a");
                    aggRouteBtn.innerHTML = "Aggregate route";
                    aggRouteBtn.ondblclick = L.DomEvent.stopPropagation;
                    aggRouteBtn.onclick = (function (aggLayer) {
                        return function () {
                            // If the aggregate route is already present, remove it
                            if (map.hasLayer(aggLayer)) {
                                activeLayers.splice(1, activeLayers.indexOf(aggLayer));
                                map.removeLayer(aggLayer)
                            }
                            else {
                                // Add aggregate route to map on click if it is not present
                                activeLayers.push(aggLayer);
                                aggLayer.addTo(map).snakeIn()
                            }
                        }
                    }(aggRouteLayer));
                    aggRouteListEl.appendChild(aggRouteBtn);
                    subMenuDropdown.appendChild(aggRouteListEl);

                    if (traceroutesLayer.length > 0) {
                        var routesListEl = document.createElement("li");
                        var routesBtn = document.createElement("a");
                        routesBtn.innerHTML = "Individual traceroutes";
                        routesBtn.ondblclick = L.DomEvent.stopPropagation;
                        routesBtn.onclick = (function (routeLayer) {
                            return function () {
                                var added = true;
                                for(var i = 0; i < routeLayer.length;i++) {
                                    if(! map.hasLayer(routeLayer[i])){
                                        added = false;
                                        break;
                                    }
                                }

                                if (! added) {
                                    // Animate the individual traceroutes simultaneously
                                    routeLayer.forEach(function (route) {
                                        activeLayers.push(route);
                                        route.addTo(map).snakeIn()
                                    });
                                }
                                else {
                                    // Remove the individual traceroutes
                                    routeLayer.forEach(function (route) {
                                        activeLayers.splice(1, activeLayers.indexOf(route));
                                        map.removeLayer(route)
                                    });
                                }
                            }
                        }(traceroutesLayer));
                        routesListEl.appendChild(routesBtn);
                        subMenuDropdown.appendChild(routesListEl)
                    }
                }

                networkBtn.onclick = (function (l, b) {
                    return function () {
                        var disabled = true;
                        for(var i = 0; i < l.length; i++){
                            if(! map.hasLayer(l[i])) {
                                disabled = false;
                                break;
                            }
                        }

                        if (! disabled) {
                            b.className += " btn-clicked";
                            // Show all of the network's aggregate routes
                            l.forEach(function (layer) {
                                if (! map.hasLayer(layer)) {
                                    activeLayers.push(layer);
                                    layer.addTo(map).snakeIn()
                                }
                            });
                        }
                        else {
                            b.blur();
                            b.className = "network-btn btn";
                            // Remove all of the network's aggregate routes
                            l.forEach(function (layer) {
                                activeLayers.splice(1, activeLayers.indexOf(layer));
                                map.removeLayer(layer)
                            });
                        }
                    }
                }(networkLayer, networkBtn));

                networkButtons.push(networkBtn)
            }
        });
    }

    return {
        createMap: createMap,
        addDataToMap: addDataToMap
    };
})();

/**
 * Retrieves the icon for the input network
 *
 * @param networkName
 * @returns Icon
 */
function getIcon(networkName){
    var markerURL;

    if (networkName.indexOf("COX") != -1) {
        markerURL = "Images/blue-marker.png"
    }
    else if (networkName.indexOf("COMCAST") != -1) {
        markerURL = "Images/yellow-marker.png"
    }
    else if (networkName.indexOf("CHARTER") != -1) {
        markerURL = "Images/grey-marker.png"
    }
    else if (networkName.indexOf("VERIZON") != -1) {
        markerURL = "Images/red-marker.png"
    }
    else if(networkName.indexOf("CENTURYLINK") != -1) {
        markerURL = "Images/green-marker.png"
    }
    else if(networkName.indexOf("ATT") != -1) {
        markerURL = "Images/blue-marker.png"
    }
    else if(networkName.indexOf("ALTICE") != -1) {
        markerURL = "Images/violet-marker.png"
    }
    else if(networkName.indexOf("MEDIACOM") != -1) {
        markerURL = "Images/red-marker.png"
    }

    return new L.Icon({
        iconUrl: markerURL,
        shadowUrl: "Images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
}

