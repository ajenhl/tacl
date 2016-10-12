function groupedBarChart() {
    var margin = {top: 20, right: 20, bottom: 100, left: 40},
        width = 960 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    var x0 = d3.scale.ordinal().rangeRoundBands([0, width], .1);

    var x1 = d3.scale.ordinal();

    var y = d3.scale.linear().range([height, 0]);

    var color = d3.scale.ordinal().range(["#D8B365", "#5AB4AC"]);

    var xAxis = d3.svg.axis().scale(x0).orient("bottom");

    var yAxis = d3.svg.axis().scale(y).orient("left")
        .tickFormat(d3.format(".2s"));

    function chart(selection) {
        selection.each(function(data) {
            var groupNames = d3.keys(data[0]).filter(function(key) {
                return key !== "related_work";
            });

            data.forEach(function(d) {
                d.groups = groupNames.map(function(name) {
                    return {name: name, value: +d[name]};
                });
            });

            x0.domain(data.map(function(d) { return d.related_work; }));
            x1.domain(groupNames).rangeRoundBands([0, x0.rangeBand()]);
            y.domain([0, 100]);

            var svg = d3.select(this).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis)
                .selectAll("text")
                .attr("y", 0)
                .attr("x", 9)
                .attr("dy", ".35em")
                .attr("transform", "rotate(90)")
                .style("text-anchor", "start");

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Percentage of text");

            var related_work = svg.selectAll(".related_work")
                .data(data)
                .enter().append("g")
                .attr("class", "g")
                .attr("transform", function(d) {
                    return "translate(" + x0(d.related_work) + ",0)";
                });

            related_work.selectAll("rect")
                .data(function(d) { return d.groups; })
                .enter().append("rect")
                .attr("width", x1.rangeBand())
                .attr("x", function(d) { return x1(d.name); })
                .attr("y", function(d) { return y(d.value); })
                .attr("height", function(d) { return height - y(d.value); })
                .style("fill", function(d) { return color(d.name); });

            var legend = svg.selectAll(".legend")
                .data(groupNames.slice().reverse())
                .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function(d, i) {
                    return "translate(0," + i * 20 + ")";
                });

            legend.append("rect")
                .attr("x", width - 18)
                .attr("width", 18)
                .attr("height", 18)
                .style("fill", color);

            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9)
                .attr("dy", ".35em")
                .style("text-anchor", "end")
                .text(function(d) { return d; });
        });
    }

    return chart;
}
