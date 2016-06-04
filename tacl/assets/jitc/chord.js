// From http://bost.ocks.org/mike/uberdata/

var width = 720,
    height = 720,
    outerRadius = Math.min(width, height) / 2 - 10,
    innerRadius = outerRadius - 24;

var formatPercent = d3.format(".1%");

var arc = d3.svg.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

var layout = d3.layout.chord()
        .padding(.04)
        .sortSubgroups(d3.descending)
        .sortChords(d3.ascending);

var path = d3.svg.chord()
        .radius(innerRadius);

var chord_svg = d3.select("#chord").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", "0 0 " + width + " " + height)
        .append("g")
        .attr("id", "circle")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

chord_svg.append("circle")
    .attr("r", outerRadius);

function handleChordData (chordData) {
    var texts = chordData.texts;
    // Compute the chord layout.
    layout.matrix(chordData.matrix);

    // Add a group per neighborhood.
    var group = chord_svg.selectAll(".group")
            .data(layout.groups)
            .enter().append("g")
            .attr("class", "group")
            .on("mouseover", mouseover);

    // Add a mouseover title.
    group.append("title").text(function(d, i) {
        return texts[i].name + ": sum of shared text percentages: " + formatPercent(d.value);
    });

    // Add the group arc.
    var groupPath = group.append("path")
            .attr("id", function(d, i) { return "group" + i; })
            .attr("d", arc)
            .style("fill", function(d, i) { return texts[i].colour; });

    // Add a text label.
    var groupText = group.append("text")
            .attr("x", 6)
            .attr("dy", 15);

    groupText.append("textPath")
        .attr("xlink:href", function(d, i) { return "#group" + i; })
        .text(function(d, i) { return texts[i].name; });

    // Remove the labels that don't fit. :(
    groupText.filter(function(d, i) {
        return groupPath[0][i].getTotalLength() / 2 - 16 < this.getComputedTextLength(); })
        .remove();

    // Add the chords.
    var chord = chord_svg.selectAll(".chord")
            .data(layout.chords)
            .enter().append("path")
            .attr("class", "chord")
            .style("fill", function(d) { return texts[d.source.index].colour; })
            .attr("d", path);

    // Add an elaborate mouseover title for each chord.
    chord.append("title").text(function(d) {
        return "Percentage of " + texts[d.source.index].name
            + " shared with " + texts[d.target.index].name
            + ": " + formatPercent(d.source.value)
            + "\nPercentage of " + texts[d.target.index].name
            + " shared with " + texts[d.source.index].name
            + ": " + formatPercent(d.target.value);
    });

    function mouseover(d, i) {
        chord.classed("fade", function(p) {
            return p.source.index != i
                && p.target.index != i;
        });
    }
};

handleChordData(chordData);
