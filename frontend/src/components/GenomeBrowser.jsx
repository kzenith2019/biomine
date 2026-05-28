import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export function GenomeBrowser({ regionLength, genes = [] }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const W = 760, H = 100, mx = 20
    const xScale = d3.scaleLinear().domain([0, regionLength]).range([mx, W - mx])

    svg.append('line')
      .attr('x1', mx).attr('y1', H / 2)
      .attr('x2', W - mx).attr('y2', H / 2)
      .attr('stroke', '#334155').attr('stroke-width', 2)

    const ticks = d3.range(0, regionLength + 1, Math.ceil(regionLength / 5))
    ticks.forEach(t => {
      svg.append('line')
        .attr('x1', xScale(t)).attr('x2', xScale(t))
        .attr('y1', H / 2 - 5).attr('y2', H / 2 + 5)
        .attr('stroke', '#475569').attr('stroke-width', 1)
      svg.append('text')
        .attr('x', xScale(t)).attr('y', H / 2 + 18)
        .attr('text-anchor', 'middle')
        .attr('fill', '#64748b').attr('font-size', 9)
        .text(`${(t / 1000).toFixed(0)}kb`)
    })

    if (genes.length === 0) {
      svg.append('text')
        .attr('x', W / 2).attr('y', H / 2 - 12)
        .attr('text-anchor', 'middle')
        .attr('fill', '#475569').attr('font-size', 12)
        .text('No gene annotations available for submitted sequence')
      return
    }

    const arrowH = 28, tipW = 10
    genes.forEach(gene => {
      const x1 = xScale(gene.start)
      const x2 = xScale(gene.end)
      const cy = H / 2
      const color = gene.strand > 0 ? '#3b82f6' : '#f59e0b'
      const pts = gene.strand > 0
        ? [[x1, cy - arrowH / 2], [x2 - tipW, cy - arrowH / 2], [x2, cy], [x2 - tipW, cy + arrowH / 2], [x1, cy + arrowH / 2]]
        : [[x2, cy - arrowH / 2], [x1 + tipW, cy - arrowH / 2], [x1, cy], [x1 + tipW, cy + arrowH / 2], [x2, cy + arrowH / 2]]
      svg.append('polygon')
        .attr('points', pts.map(p => p.join(',')).join(' '))
        .attr('fill', color).attr('opacity', 0.8)
    })

    svg.append('circle').attr('cx', W - 130).attr('cy', 14).attr('r', 5).attr('fill', '#3b82f6')
    svg.append('text').attr('x', W - 120).attr('y', 18).attr('fill', '#94a3b8').attr('font-size', 10).text('Forward')
    svg.append('circle').attr('cx', W - 65).attr('cy', 14).attr('r', 5).attr('fill', '#f59e0b')
    svg.append('text').attr('x', W - 55).attr('y', 18).attr('fill', '#94a3b8').attr('font-size', 10).text('Reverse')
  }, [regionLength, genes])

  return (
    <div className="genome-browser">
      <h3>Gene Cluster Map</h3>
      <svg ref={svgRef} width={760} height={100} />
    </div>
  )
}
