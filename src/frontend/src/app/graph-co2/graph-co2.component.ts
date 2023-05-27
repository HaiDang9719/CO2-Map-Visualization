import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {FeatureCollection} from "geojson";
import {MapVisService} from "../service/map-vis.service";
import {take} from "rxjs/operators";
import * as d3 from "d3";

@Component({
  selector: 'app-graph-co2',
  templateUrl: './graph-co2.component.html',
  styleUrls: ['./graph-co2.component.scss']
})
export class GraphCo2Component implements OnInit {
  countrySelection = '';
  @Input() pred: any;
  @ViewChild("graphCountry", {read: ElementRef}) graphElement: ElementRef | undefined;
  private htmlElement: HTMLElement;
  private svg: any;
  r2COvalue = ''
  constructor(public el: ElementRef, private mapvisService: MapVisService) {
    this.htmlElement = el.nativeElement;
  }

  ngOnInit(): void {
    this.init_svg();
    // this.mapvisService.currentCountrySelection.subscribe((name: string) => {
    //   this.svg.selectAll('*').remove();
    //   this.countrySelection = name;
    //   const data = this.pred;
    //   this.generate_graphCO2(data)
    //
    // })
    const data = this.pred[0].co2Predictions;
    this.r2COvalue = data['R^2'];
    this.generate_graphCO2(data)

    // this.mapvisService.load_prediction().pipe(take(2)).subscribe((response: any) => {
    //   console.log(response)
    // });
    // this.mapvisService.load_graphData().pipe(take(2)).subscribe((response: any) => {
    //   const objs = d3.csvParse(response);
    //   this.generate_graph(objs);
    // });
  }

  selectedVariable(name: any): void {
    // console.log(name)
    // this.countrySelection = name;
    this.mapvisService.set_variable(name.value);
  }

  init_svg() {
    this.svg = d3.select(this.htmlElement).select('#graphCO2')
        // .attr('width', '600px')
        // .attr('height', '400px')
        .attr("viewBox", "0 0 " + 600 + " " + 300)
        .attr('preserveAspectRatio', 'none');
  }

  generate_graphCO2(dataInit: any): void {
    const data = Object.values(dataInit).slice(1,41);
    const dataPred = Object.values(dataInit).slice(1,51);
    const yValue = Object.keys(dataInit).slice(1,51);
    const year = yValue.map(function (x) {
      return parseInt(x, 10);
    });

    const margin = {top: 20, right: 20, bottom: 45, left: 50},
        margin2 = {top: 230, right: 20, bottom: 30, left: 40},
        width = 600 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom,
        height2 = 300 - margin2.top - margin2.bottom;
    const x = d3.scaleLinear().range([0, width]),
        x2 = d3.scaleLinear().range([0, width]),
        y = d3.scaleLinear().range([height, 0]),
        yPred = d3.scaleLinear().range([height, 0]),
        y2 = d3.scaleLinear().range([height2, 0]);

    const xAxis = d3.axisBottom(x).tickFormat(d3.format("d")),
        xAxis2 = d3.axisBottom(x2).tickFormat(d3.format("d")),
        yAxis = d3.axisLeft(y);
    let zoombrush = 0;
    const brushed = (event: any) => {
      if (zoombrush) return; // ignore brush-by-zoom
      zoombrush = 1;
      const s = event.selection || x2.range();
      x.domain(s.map(x2.invert, x2));
      Line_chart.select(".line").attr("d", line);
      focus.select(".axis--x").call(xAxis);
      // this.svg.select(".zoom").call(zoom.transform, d3.zoomIdentity
      //     .scale(width / (s[1] - s[0]))
      //     .translate(-s[0], 0));
      zoombrush = 0
    }

    // const zoomed = (event: any) => {
    //   if (zoombrush) return;
    //   zoombrush = 1;
    //   const t = event.transform;
    //   x.domain(t.rescaleX(x2).domain());
    //   Line_chart.select(".line").attr("d", line);
    //   focus.select(".axis--x").call(xAxis);
    //   // context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
    //   zoombrush = 0;
    // }

    const brush = d3.brushX()
        .extent([[0, 0], [width, height2]])
        .on("brush end", brushed);

    // const zoom = d3.zoom()
    //     .scaleExtent([1, Infinity])
    //     .translateExtent([[0, 0], [width, height]])
    //     .extent([[0, 0], [width, height]])
    //     .on("zoom", zoomed);

    const line = d3.line()
        .x(function (d: any, i) {
          return x(year[i]);
        })
        .y(function (d: any) {
          return y(d.measured);
        });

    const line2 = d3.line()
        .x(function (d: any, i) {
          return x2(year[i]);
        })
        .y(function (d: any) {
          return y2(d.measured);
        });

    const clip = this.svg.append("defs").append("svg:clipPath")
        .attr("id", "clip")
        .append("svg:rect")
        .attr("width", width)
        .attr("height", height)
        .attr("x", 0)
        .attr("y", 0);


    const Line_chart = this.svg.append("g")
        .attr("class", "focus")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        // .attr("clip-path", "url(#clip)");


    const focus = this.svg.append("g")
        .attr("class", "focus")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // const context = this.svg.append("g")
    //     .attr("class", "context")
    //     .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");
    // @ts-ignore
    x.domain(d3.extent(year));
    // @ts-ignore
    y.domain([d3.min(dataPred, function (d: any) {
      return (d.measured < d.predicted) ? d.measured : d.predicted;

    }), d3.max(dataPred, function (d: any) {
      return (d.measured > d.predicted) ? d.measured : d.predicted;
    })]);

    // yPred.domain([d3.min(dataPred, function (d: any) {
    //   return d.predicted;
    // }), d3.max(dataPred, function (d: any) {
    //   return (d.measured < d.predicted) ? d.measured : d.predicted;
    // })]);
    x2.domain(x.domain());
    y2.domain(y.domain());
    focus.append("circle")
        .attr("cx",100).attr("cy",0).attr("r", 6).style("fill", "blue");
    focus.append("circle")
        .attr("cx",300).attr("cy",0).attr("r", 6).style("fill", "red");
    focus.append("text")
        .attr("x", 120).attr("y", 0).text("CO₂ - measured")
        .style("font-size", "15px").attr("alignment-baseline","middle");
    focus.append("text")
        .attr("x", 320).attr("y", 0).text("CO₂ - predicted")
        .style("font-size", "15px").attr("alignment-baseline","middle");
    focus.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    focus.append("g")
        .attr("class", "axis axis--y")
        .call(yAxis);

    focus.append("text")
        .attr("transform",
            "translate(" + (width / 2) + " ," +
            (height + 35) + ")")
        .style("text-anchor", "middle")
        .style("font-size", "15px")
        .text("year");

    focus.append("text")
        .attr("transform",
            "translate(" + -35 + " ," +
            (height / 2) + ") rotate(-90)")
        .style("text-anchor", "middle")
        .style("font-size", "15px")
        .text("CO₂ concentration (ppm)");

    Line_chart.append("path")
        .datum(data)
        .attr("class", "line")
        .attr('stroke-width', '5')
        .attr("d", line);

    Line_chart.selectAll(".dot")
        .data(dataPred)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("cx", (d: any, i:number) => {
          return x(year[i]);
    })
        .attr("cy", (d: any) => {
          return y(d.predicted);
        })
        .attr("r", 1.5)
        .style("fill", "red");

    // context.append("path")
    //     .datum(data)
    //     .attr("class", "line")
    //     .attr("d", line2);
    //
    // context.append("g")
    //     .attr("class", "axis axis--x")
    //     .attr("transform", "translate(0," + height2 + ")")
    //     .call(xAxis2);
    //
    // context.append("g")
    //     .attr("class", "brush")
    //     .call(brush)
    //     .call(brush.move, x.range());

    this.svg.append("rect")
        .attr("class", "zoom")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        // .call(zoom);


  }
}
