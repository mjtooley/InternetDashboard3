/**
 * Creates a color function for the input ASN
 *
 * @param networkName
 * @param maxCount
 * @returns color
 */
function getLogoColorScale(networkName, maxCount){
    var color;

    if (networkName.indexOf("COX") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4ca6d2"), d3.rgb("#006799")]);
    }
    else if (networkName.indexOf("COMCAST") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#e7be52"), d3.rgb("#b48b1f")]);
    }
    else if (networkName.indexOf("CHARTER") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4c9dc6"), d3.rgb("#005079")]);
    }
    else if (networkName.indexOf("VERIZON") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#e2696a"), d3.rgb("#a60406")]);
    }
    else if(networkName.indexOf("CENTURYLINK") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#8dc643"), d3.rgb("#118745")]);
    }
    else if(networkName.indexOf("ATT") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#6fc0e7"), d3.rgb("#23739a")]);
    }
    else if(networkName.indexOf("ALTICE") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#9867a7"), d3.rgb("#571e68")]);
    }
    else if(networkName.indexOf("MEDIACOM") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4c94ca"), d3.rgb("#005290")]);
    }

    return color;
}

/**
 * Creates the inner HTML for a particular network's logo
 *
 * @param networkName
 * @returns html
 */
function getInnerHTML(networkName) {
    var html;

    if (networkName.indexOf("COX") != -1) {
        html = "<img src= Images/Logos/Cox.png>"
    }
    else if (networkName.indexOf("COMCAST") != -1) {
        html = "<img src= Images/Logos/Comcast.png>"
    }
    else if (networkName.indexOf("CHARTER") != -1) {
        html = "<img src= Images/Logos/Charter.png>"
    }
    else if (networkName.indexOf("VERIZON") != -1) {
        html = "<img src= Images/Logos/Verizon.png>"
    }
    else if(networkName.indexOf("CENTURYLINK") != -1) {
        html = "<img src= Images/Logos/CenturyLink.png>"
    }
    else if(networkName.indexOf("ATT") != -1) {
        html = "<img src= Images/Logos/ATT.png width=20px>"
    }
    else if(networkName.indexOf("ALTICE") != -1) {
        html = "<img src= Images/Logos/Altice.png>"
    }
    else if(networkName.indexOf("MEDIACOM") != -1) {
        html = "<img src= Images/Logos/Mediacom.png>"
    }

    return html;
}
