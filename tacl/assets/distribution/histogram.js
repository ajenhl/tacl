function histogramChart() {

    var margin = {top: 30, right: 30, bottom: 50, left: 70},
        width = 1000 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var formatCount = d3.format(",.0f");

    var histogram = d3.layout.histogram();

    var title = undefined;

    var x = d3.scale.linear()
            .domain([0, 1])
            .range([0, width]);

    var y = d3.scale.linear(),
        xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(d3.format(".0%"))
            .tickSize(6, 0),
        yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .tickFormat(d3.format(".0d"));


    function chart(selection) {
        selection.each(function(data) {

            // Compute the histogram.
            data = histogram.bins(x.ticks(100))(data);

            // Update the y-scale.
            y   .domain([0, d3.max(data, function(d) { return d.y; })])
                .range([height, 0]);

            var svg = d3.select(this).append("svg")
                .attr("viewBox", "0 0 " + (width + margin.left + margin.right)
                      + " " + (height + margin.top + margin.bottom))
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Update the bars.
            var bar = svg.selectAll(".bar").data(data)
                .enter().append("g")
                .attr("class", "bar")
                .attr("transform", function(d) {
                    return "translate(" + x(d.x) + "," + y(d.y) + ")";
                });

            bar.append("rect")
                .attr("x", 1)
                .attr("width", x(data[0].dx) - 1)
                .attr("height", function(d) { return height - y(d.y); })
                .attr("title", function(d) { return "Occurences: " + d.y; });

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height + margin.bottom)
                .attr("text-anchor", "middle")
                .text("Place in text");

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .text("Number of occurrences");

            title = svg.append("text")
                .attr("x", (width / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle");
        });
    }

    chart.margin = function(_) {
        if (!arguments.length) return margin;
        margin = _;
        return chart;
    };

    chart.width = function(_) {
        if (!arguments.length) return width;
        width = _;
        return chart;
    };

    chart.height = function(_) {
        if (!arguments.length) return height;
        height = _;
        return chart;
    };

    chart.title = function(text) {
        if (!arguments.length) return title.text();
        title.text(text);
        return chart;
    };

    // Expose the histogram's value, range and bins method.
    d3.rebind(chart, histogram, "value", "range", "bins");

    // Expose the x-axis' tickFormat method.
    d3.rebind(chart, xAxis, "tickFormat");

    return chart;
}
