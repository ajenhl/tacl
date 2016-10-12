/*
 * Encapsulating chart 'class'.
 */
function stackedBarChart() {
    var margin = {top: 20, right: 20, bottom: 100, left: 40},
        width = 960 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .rangeRound([height, 0]);

    var color = d3.scale.ordinal()
        .range(["#D8B365", "#5AB4AC", "#F5F5F5"]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickFormat(d3.format(".2s"));

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([10, 0])
        .html(function(d) {
            return "<strong>" + d.name + ":</strong> " + (d.y1 - d.y0).toFixed(3);
        });

    function chart(selection) {
        selection.each(function(data) {
            color.domain(d3.keys(data[0]).filter(function(key) {
                return key !== "related_work";
            }));

            data.forEach(function(d) {
                var y0 = 0;
                d.groups = color.domain().map(function(name) {
                    return {name: name, y0: y0, y1: y0 += +d[name]};
                });
            });

            x.domain(data.map(function(d) { return d.related_work; }));
            y.domain([0, 100]);

            var svg = d3.select(this).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            svg.call(tip);

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
                    return "translate(" + x(d.related_work) + ",0)";
                });

            related_work.selectAll("rect")
                .data(function(d) { return d.groups; })
                .enter().append("rect")
                .attr("width", x.rangeBand())
                .attr("y", function(d) { return y(d.y1); })
                .attr("height", function(d) { return y(d.y0) - y(d.y1); })
                .style("fill", function(d) { return color(d.name); })
                .on('mouseover', tip.show)
                .on('mouseout', tip.hide);

            var legend = svg.selectAll(".legend")
                    .data(color.domain().slice().reverse())
                    .enter().append("g")
                    .attr("class", "legend")
                    .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

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
