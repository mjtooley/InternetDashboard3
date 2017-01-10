/**
 * Makes an AJAX call that retrieves data from the input date.
 * This data is then visualized using the createGraph function.
 *
 * @param date
 */
function visualize(date) {
    $.ajax({
        dataType: "json",
        url: "Data.php",
        data: {date: date} // Pass in date for database querying
    }).done(function(data){
        createGraph(data);
    });
}

var svg = d3.select("body")
    .attr("align", "center")
    .append("svg")
    .attr("id", "graphContainer");

/**
 * Creates a graph from the input JSON
 *
 * @param json
 */
function createGraph(json){
    if (svg.select("#graph")) { // If the SVG already contains a graph
        svg.select("#graph").remove();
    }

    // Create new graph container
    var g = svg.append("g")
        .attr("id", "graph");

    var width = svg[0][0].clientWidth,
        height = svg[0][0].clientHeight;

    var graphNodes = json.Nodes,
        graphLinks = json.Links;

    // Search list for use in autocomplete
    var searchList = graphNodes
        .filter(function(d) { return d.value != 0 })
        .map(function(d) {
            var label = d.AS_Name + " " + d.AS_Number; // Search by AS name and AS number
            return {
                label: label,
                value: d
            };
        });
    $("#search-box").val(""); // Reset text in search box
    // Initializing jQuery autocomplete
    $("#search-box").autocomplete({
        source: searchList,
        select: function(event, ui) {
            // Set text to label of selected item
            event.preventDefault();
            $("#search-box").val(ui.item.label);

            findAllNeighbors(ui.item.value); // Find all neighbors of selected item
        },
        focus: function(event, ui) {
            // Set text to label of focused item
            event.preventDefault();
            $("#search-box").val(ui.item.label);
        }
    });

    // D3 force layout
    var force = d3.layout.force()
        .size([width, height])
        .gravity(.5)
        .linkDistance(width/20)
        .nodes(graphNodes)
        .charge(function(d) { return -width/graphNodes.length*50*d.value; })
        .links(graphLinks)
        .on("tick", tick)
        .start();

    // Modifying drag function so that a click event is not fired after dragging
    var drag = force.drag()
        .on("dragstart", function () {
            d3.event.sourceEvent.stopPropagation();
        });

    /**
     * Updates the infoLegend so that it displays the AS name and number for the input node
     *
     * @param node
     */
    function updateLegend(node) {
        var message;
        if (node) {
            message = "<b> AS Name: </b>" + node.AS_Name + "<br/><b> AS Number: </b>" + node.AS_Number + "<br/>";
        }
        else {
            message = "Click on a node";
        }
        document.getElementById("infoLegend").innerHTML = "<h4>Interconnection</h4>" + message;
    }
    updateLegend();

    // Creating links
    var links = g.selectAll(".link")
        .data(graphLinks)
        .enter()
        .append("g")
        .attr("class", "link")
        .attr("id", function (d) {
            return "link-" + d.Source_AS_Number+ "-" + d.Target_AS_Number;
        })
        .append("line")
        .attr("stroke", "#cecece");

    // Attributes initial x, y, and r values to nodes
    var nodeData = d3.layout.pack()
        .sort(null)
        .size([width / 2.4, height / 2.4])
        .nodes({children: graphNodes})
        .filter(function (d) {
            return ! d.children && d.value != 0; // Don't include nodes with a value of 0 in the data
        });

    // Creating nodes
    var nodes = g.selectAll(".node")
        .data(nodeData)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("id", function (d) {
            return "node-" + d.AS_Number;
        })
        .call(drag)
        .on("click", function (d) {
            if (! d3.event.defaultPrevented) { // Don't execute while dragging
                findAllNeighbors(d);
            }
        });

    // Tick function for D3 force layout
    function tick() {
        nodes.attr("transform", function (d) {
            // Prevents nodes from moving outside the window
            d.x = Math.max(d.r, Math.min(width - d.r, d.x));
            d.y = Math.max(d.r, Math.min(height - d.r, d.y));

            return "translate(" + d.x + "," + d.y + ")";
        });
        links.attr("x1", function (d) { return d.source.x; })
            .attr("y1", function (d) { return d.source.y; })
            .attr("x2", function (d) { return d.target.x; })
            .attr("y2", function (d) { return d.target.y; });
    }

    var Backbone_List = json.Backbone_AS_List,
        Source_List = json.Source_List;

    // Maps each source/backbone to the value of its most frequent neighbor
    var maxValue = {};
    graphNodes.forEach(function (d) {
        var source = d.Source_AS_Name;
        if(! maxValue[source]){
            maxValue[source] = 0;
        }
        else if(! d.Source && ! d.Shared) {
            maxValue[source] = Math.max(maxValue[source], d.value);
        }
    });

    // Using the maximum value map, creates color functions for each source/backbone
    var colors = {};
    Source_List.forEach(function (d) {
        var AS_Name = d.AS_Name;
        colors[AS_Name] = getLogoColorScale(AS_Name.replace(/\W/g, "").toUpperCase(), maxValue[AS_Name]);
    });
    Backbone_List.forEach(function (d) {
        var AS_Name = d.AS_Name;
        colors[AS_Name] = getLogoColorScale(AS_Name.replace(/\W/g, "").toUpperCase(), maxValue[AS_Name]);
    });

    var filter = [],
        sharedNodes = [],
        sharedLinks = [],
        highlightedNodes = {};

    /**
     * Called when a node is selected via a click or selection from the autocomplete menu. If the node is already
     * in the filter, it removes that node from the filter and removes the highlight. Otherwise, it adds the node
     * to the filter and adds the highlight. Nodes are highlighted if they are shared by all nodes in the filter.
     * Links are highlighted if their source and target are highlighted.
     *
     * @param node
     */
    function findAllNeighbors(node) {
        // Remove highlight from all nodes
        for (var i = 0; i < sharedNodes.length; i++) {
            sharedNodes[i].classed("sharedNode", false);
        }
        sharedNodes = [];
        highlightedNodes = {};

        // Remove highlight from all links
        for (var i = 0; i < sharedLinks.length; i++) {
            sharedLinks[i].classed("sharedLink", false);
        }
        sharedLinks = [];

        var AS_Number = node.AS_Number,
            clickedNode = d3.select("g.node#node-" + AS_Number);

        var index = filter.indexOf(AS_Number);
        if (index != -1) { // Node is already in filter
            updateLegend();
            clickedNode.classed("clickedNode", false);
            filter.splice(index, 1);
        }
        else {
            updateLegend(node);
            clickedNode.classed("clickedNode", true);
            filter.push(AS_Number);
        }

        if (filter.length != 0) {
            nodeData.forEach(function (d) {
                var sharedNode = true,
                    sharedBy = d.Shared_By;

                // Node must be shared by all nodes in filter
                for (var i = 0; i < filter.length; i++) {
                    if (sharedBy.indexOf(filter[i]) == -1) {
                        sharedNode = false;
                        break;
                    }
                }
                if (sharedNode) { // If node is shared by all nodes in filter
                    var currNode = d3.select("g.node#node-" + d.AS_Number);
                    currNode.classed("sharedNode", true);
                    sharedNodes.push(currNode);
                    highlightedNodes[d.AS_Number] = true;
                }
            });
            graphLinks.forEach(function (d) {
                var source = d.Source_AS_Number,
                    target = d.Target_AS_Number;

                /*
                 * At least one node connected to the link must be in the filter (the other can be highlighted or
                 * also in the filter)
                 */
                if (filter.indexOf(source) != -1 && highlightedNodes[target] || filter.indexOf(target) != -1 &&
                        highlightedNodes[source] || filter.indexOf(source) != -1 && filter.indexOf(target) != -1) {
                    var link = d3.select("g.link#link-" + source.replace(/\W/g, "") + "-" + target.replace(/\W/g, ""));
                    link.classed("sharedLink", true);
                    sharedLinks.push(link);
                }
            })
        }
    }

    // Creating circles for non-source nodes
    nodeData.forEach(function (d) {
        var node = d3.select("g.node#node-" + d.AS_Number);

        if (! d.Source) {
            node.append("circle")
                .attr("r", function (d) {
                    return d.r;
                })
                .attr("fill", function (d) {
                    if (d.Shared) { // Shared node
                        return "#66B266";
                    }
                    return colors[d.Source_AS_Name](d.value);
                });

            var logo = getLogoURL(d.AS_Name.replace(/\W/g, "").toUpperCase());
            if(logo) { // If a logo exists for the AS
                node.append("image")
                    .attr("xlink:href", logo)
                    .attr("width", function (d) { return 1.4*d.r; })
                    .attr("height", function (d) { return 1.4*d.r; })
                    .attr("x", function (d) { return -.7 * d.r; })
                    .attr("x", function (d) { return -.7 * d.r; })
                    .attr("y", function (d) { return -.7 * d.r; });
            }
        }
    });

    // For each backbone node, creates a circle and adds a logo image to it
    Backbone_List.forEach(function(d) {
        var node = d3.select("g.node#node-" + d.AS_Number);

        if(node.node()) {
            node.append("circle")
                .attr("r", function (d) { return d.r })
                .attr("class", "source-backbone");

            node.append("image")
                .attr("xlink:href", getLogoURL(d.AS_Name.replace(/\W/g, "").toUpperCase()))
                .attr("width", function (d) { return 1.8 * d.r; })
                .attr("height", function (d) { return 1.8 * d.r; })
                .attr("x", function (d) { return -.9 * d.r; })
                .attr("y", function (d) { return -.9 * d.r; });
        }
    });

    // For each source node, creates a cloud and adds a logo image to it
    Source_List.forEach(function(d){
        var node = d3.select("g.node#node-" + d.AS_Number);

        if(node.node()) {
            d3.xml("Images/white-cloud.svg", function(error, svg) {
                node.node().appendChild(svg.getElementsByTagName("svg")[0]);
                node.select("svg#cloud-group")
                    .attr("width", function (d) { return 2.4*d.r; })
                    .attr("height", function (d) { return 2.4*d.r; })
                    .attr("x", function (d) { return -1.2*d.r; })
                    .attr("y", function (d) { return -1.2*d.r; })
                    .attr("class", "source-backbone");

                node.append("image")
                    .attr("xlink:href", getLogoURL(d.AS_Name.replace(/\W/g, "").toUpperCase()))
                    .attr("width", function (d) { return 1.4 * d.r; })
                    .attr("height", function (d) { return 1.4 * d.r; })
                    .attr("x", function (d) { return -.65 * d.r; })
                    .attr("y", function (d) { return -.6 * d.r; });
            })
        }
    });
}
