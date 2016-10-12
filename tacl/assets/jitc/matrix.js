// Code adapted from http://bost.ocks.org/mike/miserables/

var margin = {top: 120, right: 0, bottom: 10, left: 180},
    width = 720,
    height = 720;

var x = d3.scale.ordinal().rangeBands([0, width]),
    z = d3.scale.linear().domain([0, 20]).range([0, 1]).clamp(true),
    c = d3.scale.category10().domain(d3.range(10));

var table_svg = d3.select("#matrix").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .style("margin-left", -margin.left + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

function handleTableData (works) {
    var matrix = [],
        nodes = works.nodes,
        n = nodes.length;

    // Compute index per node.
    nodes.forEach(function(node, i) {
        node.index = i;
        node.count = 0;
        matrix[i] = d3.range(n).map(function(j) { return {x: j, y: i, z: 0}; });
    });

    // Convert links to matrix; sum percentages for each work (to get a
    // measure of how much it overlaps with all the other works).
    works.links.forEach(function(link) {
        matrix[link.source][link.target].z += link.value;
        matrix[link.target][link.source].z += link.value;
        matrix[link.source][link.source].z = 0;
        matrix[link.target][link.target].z = 0;
        nodes[link.source].count += link.value;
        nodes[link.target].count += link.value;
    });

    // Precompute the orders.
    var orders = {
        work: d3.range(n).sort(function(a, b) {
            return d3.ascending(nodes[a].work, nodes[b].work); }),
        count: d3.range(n).sort(function(a, b) {
            return nodes[b].count - nodes[a].count; })
    };

    // The default sort order.
    x.domain(orders.work);

    table_svg.append("rect")
        .attr("class", "background")
        .attr("width", width)
        .attr("height", height);

    var row = table_svg.selectAll(".row")
            .data(matrix)
            .enter().append("g")
            .attr("class", "row")
            .attr("transform", function(d, i) {
                return "translate(0," + x(i) + ")"; })
            .each(row);

    row.append("line")
        .attr("x2", width);

    row.append("text")
        .attr("x", -6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "end")
        .text(function(d, i) { return nodes[i].work; });

    var column = table_svg.selectAll(".column")
            .data(matrix)
            .enter().append("g")
            .attr("class", "column")
            .attr("transform", function(d, i) {
                return "translate(" + x(i) + ")rotate(-90)"; });

    column.append("line")
        .attr("x1", -width);

    column.append("text")
        .attr("x", 6)
        .attr("y", x.rangeBand() / 2)
        .attr("dy", ".32em")
        .attr("text-anchor", "start")
        .text(function(d, i) { return nodes[i].work; });

    function row(row) {
        var cell = d3.select(this).selectAll(".cell")
                .data(row.filter(function(d) { return d.z; }))
                .enter().append("rect")
                .attr("class", "cell")
                .attr("x", function(d) { return x(d.x); })
                .attr("width", x.rangeBand())
                .attr("height", x.rangeBand())
                .style("fill-opacity", function(d) { return z(d.z); })
                .style("fill", function(d) { return nodes[d.x].group == nodes[d.y].group ? c(nodes[d.x].group) : null; })
                .on("mouseover", mouseover)
                .on("mouseout", mouseout)
                .append("svg:title").text(function(d) { return d.z; });
    }

    function mouseover(p) {
        d3.selectAll(".row text").classed("active", function(d, i) { return i == p.y; });
        d3.selectAll(".column text").classed("active", function(d, i) { return i == p.x; });
    }

    function mouseout() {
        d3.selectAll("text").classed("active", false);
    }

    d3.select("#order").on("change", function() {
        clearTimeout(timeout);
        order(this.value);
    });

    function order(value) {
        x.domain(orders[value]);

        var t = table_svg.transition().duration(2500);

        t.selectAll(".row")
            .delay(function(d, i) { return x(i) * 4; })
            .attr("transform", function(d, i) { return "translate(0," + x(i) + ")"; })
            .selectAll(".cell")
            .delay(function(d) { return x(d.x) * 4; })
            .attr("x", function(d) { return x(d.x); });

        t.selectAll(".column")
            .delay(function(d, i) { return x(i) * 4; })
            .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });
    }

    var timeout = setTimeout(function() {
        order("work");
        d3.select("#order").property("selectedIndex", 0).node().focus();
    }, 5000);
}

handleTableData(matrixData);
