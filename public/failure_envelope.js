function drawEnvelope(data) {
    // data is array of [sx, sy] tuples

    d3.select("#envelope-plot").html("");

    const width = 400;
    const height = 400;
    const margin = 50;

    const svg = d3.select("#envelope-plot")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const g = svg.append("g")
        .attr("transform", `translate(${margin},${margin})`);

    const innerWidth = width - 2*margin;
    const innerHeight = height - 2*margin;

    // Find min/max
    const xExtent = d3.extent(data, d => d[0]);
    const yExtent = d3.extent(data, d => d[1]);

    const maxVal = Math.max(
        Math.abs(xExtent[0] || 0), Math.abs(xExtent[1] || 0),
        Math.abs(yExtent[0] || 0), Math.abs(yExtent[1] || 0)
    );

    // Add buffer
    const limit = maxVal * 1.2;
    const domain = [-limit, limit];

    const x = d3.scaleLinear()
        .domain(domain)
        .range([0, innerWidth]);

    const y = d3.scaleLinear()
        .domain(domain)
        .range([innerHeight, 0]);

    // X-Axis
    g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => (d/1e6).toFixed(0)));

    // Y-Axis
    g.append("g")
        .call(d3.axisLeft(y).ticks(5).tickFormat(d => (d/1e6).toFixed(0)));

    // Zero lines
    g.append("line")
        .attr("x1", x(0))
        .attr("x2", x(0))
        .attr("y1", 0)
        .attr("y2", innerHeight)
        .attr("stroke", "#ccc")
        .attr("stroke-dasharray", "3,3");

    g.append("line")
        .attr("x1", 0)
        .attr("x2", innerWidth)
        .attr("y1", y(0))
        .attr("y2", y(0))
        .attr("stroke", "#ccc")
        .attr("stroke-dasharray", "3,3");

    // Labels
    g.append("text")
        .attr("x", innerWidth/2)
        .attr("y", innerHeight + 35)
        .style("text-anchor", "middle")
        .text("Sigma X (MPa)");

    g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -35)
        .attr("x", -innerHeight/2)
        .style("text-anchor", "middle")
        .text("Sigma Y (MPa)");

    // Line
    const line = d3.line()
        .x(d => x(d[0]))
        .y(d => y(d[1]))
        .curve(d3.curveLinearClosed);

    g.append("path")
        .datum(data)
        .attr("d", line)
        .attr("fill", "rgba(231, 76, 60, 0.3)")
        .attr("stroke", "#e74c3c")
        .attr("stroke-width", 2);
}
