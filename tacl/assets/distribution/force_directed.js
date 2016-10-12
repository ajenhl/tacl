function forceDirectedChart() {

    var width = 900,
        height = 700;

    var force = d3.layout.force().size([width, height]).charge(-300);

    function chart(selection) {
        selection.each(function(data) {
            force.nodes(data.nodes)
                .links(data.links)
                .linkDistance(function(link, index) {
                    return 170 + link.weight * 400;
                })
                .linkStrength(function(link, index) {
                    return link.strength;
                })
                .on("tick", tick)
                .start();

            var svg = d3.select(this).append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g");

            var node = svg.selectAll(".node")
                .data(force.nodes())
                .enter().append("g")
                .attr("class", "node")
                .call(force.drag);

            node.append("circle")
                .attr("r", function(d) {
                    return d3.max([5, Math.log(d.count) * 2]);
                }).attr("title", function(d) { return d.name + ": " + d.count; });

            function tick() {
                node.attr("transform", function(d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });
            }
        });

    }

    return chart;
}
