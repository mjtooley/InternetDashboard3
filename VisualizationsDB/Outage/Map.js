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
    var color,
        map,
        stateData = {},
        ASN_Data = {},
        networkControl,
        activeLayers = [];

    // Leaflet control for network buttons
    L.Control.NetworkControl = L.Control.extend({
        options: {
            position: "topleft"
        },

        onAdd: function () {
            var networkBtns = L.DomUtil.create("div", "btn-group-vertical");
            networkBtns.id = "network-btns";
            return networkBtns;
        }
    });

    /**
     * Creates map then calls the input callback
     *
     * @param callback
     */
    function createMap(callback) {
        color = d3.scale.linear().domain([0,100])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#ff0000"), d3.rgb("#008000")]);

        map = new L.Map("map", {
            center: [37.8, -106.9],
            zoom: 4,
            minZoom: 3
        }).addLayer(new L.TileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"));

        // SVG overlay for coloring states
        var svg = d3.select(map.getPanes().overlayPane)
            .append("svg");

        var g = svg.append("g")
            .attr("class", "leaflet-zoom-hide")
            .attr("opacity", .4)
            .attr("fill", "#F2EEE8");

        // Info box
        var infoBox,
            info = L.control();
        info.onAdd = function () {
            infoBox = L.DomUtil.create("div", "info");
            // update();
            return infoBox;
        };

        // Function for updating info box
        info.update = function (d) {
            var message;
            if(d) {
                var state = d.properties.NAME;
                message = "<b>" + state + "</b><br />";
                var percentUp = Math.round((stateData[state].up/stateData[state].total)*100);
                if (! isNaN(percentUp)){
                    message += percentUp + "% of probes up";
                }
                else{
                    message += "No data available";
                }
            }
            else{
                message = "Hover over a state";
            }
            infoBox.innerHTML = "<h4>Network Outage</h4>" + message;
        };
        info.addTo(map);

        // Color legend
        var colorLegend = L.control({position: "bottomright"});
        colorLegend.onAdd = function () {
            var div = L.DomUtil.create("div", "info legend"),
                grades = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
            for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    "<i style= background:" + color(grades[i]) + "></i>" +
                    grades[i] + "% <br>";
            }
            return div;
        };
        colorLegend.addTo(map);

        // Marker legend
        var markerLegend = L.control({position: "bottomright"});
        markerLegend.onAdd = function () {
            var div = L.DomUtil.create("div", "info legend");
            div.innerHTML += "<img src = Images/red-marker.png width = 20 height = ><img> Probe down<br>";
            div.innerHTML += "<img src = Images/green-marker.png width = 20 height = 20><img> Probe up";
            return div;
        };
        markerLegend.addTo(map);

        // Creating overlay
        d3.json("us-states.json", function (error, collection) {
            if (error){ throw error }

            var feature = g.selectAll("path")
                .data(collection.features)
                .enter()
                .append("path")
                .attr("id", function(d) { return d.properties.NAME.replace(/\W/g, ""); })
                .on("mouseover", function(d) {
                    d3.select(this)
                        .attr("class", "hoverState");
                    info.update(d);
                })
                .on("mouseout", function() {
                    d3.select(this)
                        .attr("class", null);
                    info.update();
                });

            // Initializing stateData dictionary
            collection.features.forEach(function(feature) {
                stateData[feature.properties.NAME] = {
                    total: 0,
                    up: 0
                }
            });

            // Reposition the SVG to cover features on zoom
            function projectPoint(x, y) {
                var point = map.latLngToLayerPoint(new L.LatLng(y, x));
                this.stream.point(point.x, point.y);
            }
            var transform = d3.geo.transform({point: projectPoint});
            var path = d3.geo.path()
                .projection(transform);
            function reset() {
                var bounds = path.bounds(collection),
                    topLeft = bounds[0],
                    bottomRight = bounds[1];

                svg.attr("width", bottomRight[0] - topLeft[0])
                    .attr("height", bottomRight[1] - topLeft[1])
                    .style("left", topLeft[0] + "px")
                    .style("top", topLeft[1] + "px");

                g.attr("transform", "translate(" + -topLeft[0] + "," + -topLeft[1] + ")");

                feature.attr("d", path);
            }
            map.on("viewreset", reset);
            reset();

            callback();
        });
    }

    /**
     * Adds the probes for the input AS to the map and updates the map
     *
     * @param AS_Number
     */
    function addASN(AS_Number) {
        var currASN_Data = ASN_Data[AS_Number];
        var states = Object.keys(currASN_Data);
        for (var i=0;i<states.length;i++) {
            var state = states[i];

            stateData[state].total += ASN_Data[AS_Number][state].total;
            var stateTotal =  stateData[state].total;

            stateData[state].up += ASN_Data[AS_Number][state].up;
            var stateUp =  stateData[state].up;

            var percentUp = Math.round((stateUp/stateTotal)*100);

            var stateColor = isNaN(percentUp) ? "#F2EEE8" : color(percentUp);
            d3.select("path#" + state.replace(/\W/g, ""))
                .style("fill", stateColor);
        }
    }

    /**
     * Removes the probes for the input AS from the map and updates the map
     *
     * @param AS_Number
     */
    function removeASN(AS_Number){
        var currASN_Data = ASN_Data[AS_Number];
        var states = Object.keys(currASN_Data);
        for (var i=0;i<states.length;i++) {
            var state = states[i];

            stateData[state].total -= ASN_Data[AS_Number][state].total;
            var stateTotal =  stateData[state].total;

            stateData[state].up -= ASN_Data[AS_Number][state].up;
            var stateUp =  stateData[state].up;

            var percentUp = Math.round((stateUp/stateTotal)*100);

            var stateColor = isNaN(percentUp) ? "#F2EEE8" : color(percentUp);
            d3.select("path#" + state.replace(/\W/g, ""))
                .style("fill", stateColor)
        }
    }

    /**
     * Creates the visualizations from the input JSON
     *
     * @param json
     */
    function addDataToMap(json){
        if(networkControl){
            map.removeControl(networkControl); // Remove old network control buttons
            activeLayers.forEach(function(layer) {
                map.removeLayer(layer); // Remove old markers
            })
        }
        networkControl = new L.Control.NetworkControl();
        networkControl.addTo(map);

        // Reset state color
        d3.selectAll("path")
            .style("fill", "#F2EEE8");

        // Reset state data
        Object.keys(stateData).forEach(function(state) {
            stateData[state] = {
                total: 0,
                up: 0
            };
        });

        ASN_Data = {}; // Reset
        // Reset
        var Network_Groups = {},
            AS_list = json.AS_List;

        // Creating a dictionary entry for each network and adding all ASNs to the ASN_Data dictionary
        for (var i=0;i<AS_list.length;i++){
            var currNetwork = AS_list[i],
                AS_Groups ={},
                ASNs = currNetwork.ASN;
            for(var j=0;j<ASNs.length;j++){
                var currASN = ASNs[j];
                AS_Groups[currASN] = new L.LayerGroup(); // Dictionary entry for each network is a dictionary of its ASNs
                ASN_Data[currASN] = {}; // Creating dictionary entry for each ASN in ASN_Data
            }
            Network_Groups[currNetwork.Name] = AS_Groups;
        }

        var probes = json.Probes;
        for (var i = 0; i < probes.length; i++) { // Iterating through probes
            var currProbe = probes[i],
                AS_Number = currProbe.AS_Number,
                state = currProbe.state;

            if (! state){ // No data for the probe
                continue;
            }

            if(ASN_Data[AS_Number][state]){
                ASN_Data[AS_Number][state].total += 1; // Increment the number of probes for the current ASN in the current state
            }
            else{
                // Creating initial entry for the current ASN in the current state
                ASN_Data[AS_Number][state] = {
                    total: 1,
                    up: 0
                };
            }

            var icon;
            if (currProbe.Status == "UP") {
                ASN_Data[AS_Number][state].up += 1; // Increment the number of up probes for the current ASN in the current state
                icon = new L.Icon({
                    iconUrl: "Images/green-marker.png",
                    shadowUrl: "Images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
            }
            else{
                icon = new L.Icon({
                    iconUrl: "Images/red-marker.png",
                    shadowUrl: "Images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
            }

            // Creating marker
            var marker = L.marker([currProbe.Lat, currProbe.Long], {icon: icon}).addTo(Network_Groups[currProbe.network_name][AS_Number]);
            marker.bindPopup("<b>Percentage of packets received: </b>" + Math.round(currProbe.Packets_received) + "%");
        }

        // Creating button/dropdown for the network
        var networkBtns = L.DomUtil.get("network-btns");
        Object.keys(Network_Groups).forEach(function(networkName) {
            var splitBtn = L.DomUtil.create("div", "btn-group", networkBtns);

            var networkBtn = L.DomUtil.create("button", "network-btn btn", splitBtn);
            networkBtn.innerHTML = getInnerHTML(networkName.replace(/\W/g, "").toUpperCase());
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

            var dropdownMenu = L.DomUtil.create("ul", "networkdropdown dropdown-menu pull-right", splitBtn);
            dropdownMenu.ondblclick = L.DomEvent.stopPropagation;

            var title = document.createElement("li");
            title.style.textAlign = "center";
            title.style.cursor = "default";
            var label = document.createTextNode("ASNs");
            title.appendChild(label);
            dropdownMenu.appendChild(title);

            var divider = document.createElement("li");
            divider.className += "divider";
            dropdownMenu.appendChild(divider);

            var networkLayer = [];

            var ASNs = Network_Groups[networkName];
            Object.keys(ASNs).forEach(function(ASN) {
                var markers = ASNs[ASN];
                networkLayer.push(
                    {
                        markers: markers,
                        AS_Number: ASN
                    }
                );

                var ASN_Btn = document.createElement("input");
                ASN_Btn.type = "checkbox";
                ASN_Btn.className += "checkbox";
                ASN_Btn.id = "btn-" + ASN;
                ASN_Btn.ondblclick = L.DomEvent.stopPropagation;
                ASN_Btn.onclick = (function (l) {
                    return function () {
                        // Remove the ASN and all of its probes from the map
                        if (map.hasLayer(l)) {
                            removeASN(ASN);
                            activeLayers.splice(1, activeLayers.indexOf(l));
                            map.removeLayer(l);
                        }
                        // Add the ASN and all of its probes to the map
                        else {
                            addASN(ASN);
                            activeLayers.push(l);
                            l.addTo(map);
                        }
                    }
                }(markers));
                var ASN_List = document.createElement("li"),
                    label = document.createTextNode(ASN);
                ASN_List.appendChild(label);
                ASN_List.appendChild(ASN_Btn);
                dropdownMenu.appendChild(ASN_List);
            });

            networkBtn.onclick = (function (l, b) {
                var disabled = false;

                return function () {
                    if (! disabled) {
                        b.className += " btn-clicked";
                        // Add all ASNs for that network to the map if they are not already on it
                        l.forEach(function (layer) {
                            var markers = layer.markers;
                            if (! map.hasLayer(markers)) {
                                var AS_Number = layer.AS_Number;
                                document.getElementById("btn-" + AS_Number).checked = true;
                                addASN(AS_Number);
                                activeLayers.push(markers);
                                markers.addTo(map);
                            }
                        });
                        disabled = true;
                    }
                    else {
                        b.blur();
                        b.className = "network-btn btn";
                        // Remove all ASNs for that network from the map if they are on it
                        l.forEach(function (layer) {
                            var markers = layer.markers;
                            if(map.hasLayer(markers)) {
                                var AS_Number = layer.AS_Number;
                                document.getElementById("btn-" + AS_Number).checked = false;
                                removeASN(AS_Number);
                                activeLayers.splice(1, activeLayers.indexOf(markers));
                                map.removeLayer(markers);
                            }
                        });
                        disabled = false;
                    }
                }
            }(networkLayer, networkBtn));

            networkBtn.click(); // All network buttons are clicked initially
        });
    }

    return {
        createMap: createMap,
        addDataToMap: addDataToMap,
    };
})();

/**
 * Creates the inner HTML for a particular network's logo
 *
 * @returns html
 */
function getInnerHTML(networkName) {
    var html;

    if (networkName.indexOf("COX") != -1) {
        html = "<img src= Images/Logos/Cox.png>";
    }
    else if (networkName.indexOf("COMCAST") != -1) {
        html = "<img src= Images/Logos/Comcast.png>";
    }
    else if (networkName.indexOf("VERIZON") != -1) {
        html = "<img src= Images/Logos/Verizon.png>";
    }
    else if(networkName.indexOf("CENTURYLINK") != -1) {
        html = "<img src= Images/Logos/CenturyLink.png>";
    }
    else if(networkName.indexOf("ATT") != -1) {
        html = "<img src= Images/Logos/ATT.png width = 20px>";
    }
    else if(networkName.indexOf("TIMEWARNER") != -1) {
        html = "<img src= Images/Logos/TimeWarner.png>";
    }
    else if(networkName.indexOf("LEVEL3") != -1) {
        html = "<img src= Images/Logos/Level3.png>";
    }
    else if(networkName.indexOf("NCTA") != -1) {
        html = "<img src= Images/Logos/NCTA.png>";
    }
    else if(networkName.indexOf("SUDDENLINK") != -1) {
        html = "<img src= Images/Logos/SuddenLink.png>";
    }

    return html;
}
