function drawPolar(data) {
    // data is array of {angle, Ex, Ey, Gxy}

    d3.select("#polar-plot").html("");

    const width = 400;
    const height = 400;
    const margin = 40;
    const radius = Math.min(width, height) / 2 - margin;

    const svg = d3.select("#polar-plot")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2},${height/2})`);

    const r = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.Ex)])
        .range([0, radius]);

    const gr = svg.append("g")
        .attr("class", "r axis")
        .selectAll("g")
        .data(r.ticks(5).slice(1))
        .enter().append("g");

    gr.append("circle")
        .attr("r", r)
        .style("fill", "none")
        .style("stroke", "#ccc")
        .style("stroke-dasharray", "3,3");

    gr.append("text")
        .attr("y", d => -r(d) - 4)
        .attr("transform", "rotate(15)")
        .style("text-anchor", "middle")
        .text(d => (d/1e9).toFixed(1) + " GPa");

    const ga = svg.append("g")
        .attr("class", "a axis")
        .selectAll("g")
        .data(d3.range(0, 360, 45))
        .enter().append("g")
        .attr("transform", d => `rotate(${d-90})`);

    ga.append("line")
        .attr("x2", radius)
        .style("stroke", "#ddd");

    ga.append("text")
        .attr("x", radius + 6)
        .attr("dy", ".35em")
        .style("text-anchor", d => d < 270 && d > 90 ? "end" : null)
        .attr("transform", d => d < 270 && d > 90 ? `rotate(180 ${radius+6},0)` : null)
        .text(d => d + "°");

    const line = d3.lineRadial()
        .angle(d => d.angle * Math.PI / 180)
        .radius(d => r(d.Ex))
        .curve(d3.curveLinearClosed);

    svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line)
        .style("fill", "rgba(52, 152, 219, 0.3)")
        .style("stroke", "#3498db")
        .style("stroke-width", 2);
}
