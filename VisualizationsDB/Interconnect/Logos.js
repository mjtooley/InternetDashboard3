/**
 * Creates a color function for the input ASN
 *
 * @param AS_Name
 * @param maxCount
 * @returns color
 */
function getLogoColorScale(AS_Name, maxCount){
    var color = d3.scale.linear().domain([1,maxCount])
        .interpolate(d3.interpolateHcl)
        .range([d3.rgb("#e6944f"), d3.rgb("#c96d20")]);

    if (AS_Name.indexOf("TIMEWARNER") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#7ad3f6"), d3.rgb("#1b91c0")]);
    }
    else if (AS_Name.indexOf("COX") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4ca6d2"), d3.rgb("#006799")]);
    }
    else if (AS_Name.indexOf("COMCAST") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#e7be52"), d3.rgb("#b48b1f")]);
    }
    else if (AS_Name.indexOf("CHARTER") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4c9dc6"), d3.rgb("#005079")]);
    }
    else if (AS_Name.indexOf("VERIZON") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#e2696a"), d3.rgb("#a60406")]);
    }
    else if(AS_Name.indexOf("CENTURYLINK") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#8dc643"), d3.rgb("#118745")]);
    }
    else if(AS_Name.indexOf("ATT") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#6fc0e7"), d3.rgb("#23739a")]);
    }
    else if(AS_Name.indexOf("MEDIACOM") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4c94ca"), d3.rgb("#005290")]);
    }
    else if(AS_Name.indexOf("CABLEVISION") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#4c8dba"), d3.rgb("#005290")]);
    }
    else if(AS_Name.indexOf("SUDDENLINK") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#72c66c"), d3.rgb("#378032")]);
    }
    else if(AS_Name.indexOf("NCTA") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#d6eef9"), d3.rgb("#93a5ae")]);
    }
    else if (AS_Name.indexOf("BRIGHTHOUSE") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#fecc79"), d3.rgb("#cb9946")]);
    }
    else if (AS_Name.indexOf("YELP") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#cf4132"), d3.rgb("#9c0e00")]);
    }
    else if (AS_Name.indexOf("CISCO") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#436d7d"), d3.rgb("#103a4a")]);
    }
    else if (AS_Name.indexOf("CLOUDFLARE") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#f7a14b"), d3.rgb("#c46e18")]);
    }
    else if (AS_Name.indexOf("COGENT") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#328ec9"), d3.rgb("#005b96")]);
    }
    else if (AS_Name.indexOf("FRONTIER") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#e05257"), d3.rgb("#ad1f24")]);
    }
    else if (AS_Name.indexOf("GOOGLEFIBER") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#909090"), d3.rgb("#5d5d5d")]);
    }
    else if (AS_Name.indexOf("HURRICANE") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#515987"), d3.rgb("#1e2654")]);
    }
    else if (AS_Name.indexOf("LEVEL3") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#ef4555"), d3.rgb("#bc1222")]);
    }
    else if (AS_Name.indexOf("NTT") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#f1d21a"), d3.rgb("#a89000")]);
    }
    else if (AS_Name.indexOf("OPENDNS") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#f58346"), d3.rgb("#c25013")]);
    }
    else if (AS_Name.indexOf("VIASAT") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#6a8fb7"), d3.rgb("#375c84")]);
    }
    else if (AS_Name.indexOf("AKAMAI") != -1) {
        color = d3.scale.linear().domain([1,maxCount])
            .interpolate(d3.interpolateHcl)
            .range([d3.rgb("#ffad5b"), d3.rgb("#cc7a28")]);
    }

    return color;
}

/**
 * Retrieves the input ASN's logo URL
 *
 * @param AS_Name
 * @returns logo URL
 */
function getLogoURL(AS_Name) {
    var url;

    if (AS_Name.indexOf("TIMEWARNER") != -1) {
        url = "Images/Logos/TimeWarner.png";
    }
    else if (AS_Name.indexOf("COX") != -1) {
        url = "Images/Logos/Cox.png";
    }
    else if (AS_Name.indexOf("COMCAST") != -1) {
        url = "Images/Logos/Comcast.png";
    }
    else if (AS_Name.indexOf("CHARTER") != -1) {
        url = "Images/Logos/Charter.png";
    }
    else if (AS_Name.indexOf("VERIZON") != -1) {
        url = "Images/Logos/Verizon.png";
    }
    else if (AS_Name.indexOf("CENTURYLINK") != -1) {
        url = "Images/Logos/CenturyLink.png";
    }
    else if (AS_Name.indexOf("ATT") != -1) {
        url = "Images/Logos/ATT.png";
    }
    else if (AS_Name.indexOf("CABLEVISION") != -1) {
        url = "Images/Logos/Cablevision.png";
    }
    else if (AS_Name.indexOf("MEDIACOM") != -1) {
        url = "Images/Logos/Mediacom.png";
    }
    else if (AS_Name.indexOf("CENTURYLINK") != -1) {
        url = "Images/Logos/CenturyLink.png";
    }
    else if (AS_Name.indexOf("NCTA") != -1) {
        url = "Images/Logos/NCTA.png";
    }
    else if (AS_Name.indexOf("GOOGLE") != -1) {
        url = "Images/Logos/Google.png";
    }
    else if (AS_Name.indexOf("AMAZON") != -1) {
        url = "Images/Logos/Amazon.png";
    }
    else if (AS_Name.indexOf("FACEBOOK") != -1) {
        url = "Images/Logos/Facebook.png";
    }
    else if (AS_Name.indexOf("NETFLIX") != -1) {
        url = "Images/Logos/Netflix.png";
    }
    else if (AS_Name.indexOf("SUDDENLINK") != -1) {
        url = "Images/Logos/SuddenLink.png";
    }
    else if (AS_Name.indexOf("BRIGHTHOUSE") != -1) {
        url = "Images/Logos/BrightHouse.png";
    }
    else if (AS_Name.indexOf("YELP") != -1) {
        url = "Images/Logos/Yelp.png";
    }
    else if (AS_Name.indexOf("CISCO") != -1) {
        url = "Images/Logos/Cisco.png";
    }
    else if (AS_Name.indexOf("CLOUDFLARE") != -1) {
        url = "Images/Logos/CloudFlare.png";
    }
    else if (AS_Name.indexOf("COGENT") != -1) {
        url = "Images/Logos/Cogent.png";
    }
    else if (AS_Name.indexOf("FRONTIER") != -1) {
        url = "Images/Logos/Frontier.png";
    }
    else if (AS_Name.indexOf("GOOGLEFIBER") != -1) {
        url = "Images/Logos/GoogleFiber.png";
    }
    else if (AS_Name.indexOf("HURRICANE") != -1) {
        url = "Images/Logos/Hurricane.png";
    }
    else if (AS_Name.indexOf("LEVEL3") != -1) {
        url = "Images/Logos/Level3.png";
    }
    else if (AS_Name.indexOf("NTT") != -1) {
        url = "Images/Logos/NTT.png";
    }
    else if (AS_Name.indexOf("OPENDNS") != -1) {
        url = "Images/Logos/OpenDNS.png";
    }
    else if (AS_Name.indexOf("VIASAT") != -1) {
        url = "Images/Logos/ViaSat.png";
    }
    else if (AS_Name.indexOf("AKAMAI") != -1) {
        url = "Images/Logos/Akamai.png";
    }

    return url;
}
