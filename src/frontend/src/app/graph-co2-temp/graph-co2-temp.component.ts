import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import {MapVisService} from "../service/map-vis.service";
import * as d3 from "d3";

@Component({
  selector: 'app-graph-co2-temp',
  templateUrl: './graph-co2-temp.component.html',
  styleUrls: ['./graph-co2-temp.component.scss']
})
export class GraphCo2TempComponent implements OnInit {

  countrySelection = '';
  @Input() pred: any;
  @ViewChild("graphCountry", {read: ElementRef}) graphElement: ElementRef | undefined;
  private htmlElement: HTMLElement;
  private svg: any;
  r2value = ''
  r2COvalue = ''
  tempTrend = ''
  constructor(public el: ElementRef, private mapvisService: MapVisService) {
    this.htmlElement = el.nativeElement;
  }

  ngOnInit(): void {
    this.init_svg();
    this.mapvisService.currentCountrySelection.subscribe((name: string) => {
      this.svg.selectAll('*').remove();
      if (name !== ''){
        this.countrySelection = name;
        const data = this.pred;
        this.generate_graphCO2Temp(data, name)
      }

    })
    // const data = this.pred;
    // this.generate_graphCO2Temp(data)
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
    this.svg = d3.select(this.htmlElement).select('#graphCO2Temp')
        // .attr('width', '600px')
        // .attr('height', '400px')
        .attr("viewBox", "0 0 " + 600 + " " + 300)
        .attr('preserveAspectRatio', 'none');
  }

  generate_graphCO2Temp(dataV: any, name: string): void {
    // const dataInit = dataV.co2Predictions;
    // const dataInit2 = dataV.temperaturePredictions[name];
    let dataInit = dataV[0].co2Predictions;
    let dataInit2 = dataV[0].temperaturePredictions[name];
    // console.log(dataV)
    if(dataInit2 === undefined){
      dataInit = dataV[1].co2Predictions;
      dataInit2 = dataV[1].temperaturePredictions[name];
    }
    this.r2value = dataInit2['R^2'];
    this.r2COvalue = dataInit['R^2'];
    this.tempTrend = (Math.floor(((dataInit2['2020'].predicted - dataInit2['1980'].predicted)/41)*100)/100).toString()
    const data = Object.values(dataInit).slice(1,41);
    const dataPred = Object.values(dataInit).slice(1,51);
    const data2 = Object.values(dataInit2).slice(1,41);
    const dataPred2 = Object.values(dataInit2).slice(1,51);
    const yValue = Object.keys(dataInit).slice(1,51);
    const year = yValue.map(function (x) {
      return parseInt(x, 10);
    });

    const margin = {top: 40, right: 50, bottom: 45, left: 50},
        margin2 = {top: 230, right: 40, bottom: 30, left: 40},
        width = 600 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom,
        height2 = 300 - margin2.top - margin2.bottom;
    const x = d3.scaleLinear().range([0, width]),
        x2 = d3.scaleLinear().range([0, width]),
        y = d3.scaleLinear().range([height, 0]),
        yPred = d3.scaleLinear().range([height, 0]),
        y2 = d3.scaleLinear().range([height2, 0]),
        yTemp = d3.scaleLinear().range([height, 0]),
        yTemp2 = d3.scaleLinear().range([height, 0]);

    const xAxis = d3.axisBottom(x).tickFormat(d3.format("d")),
        xAxis2 = d3.axisBottom(x2),
        yAxis = d3.axisLeft(y),
        yAxis2 = d3.axisRight(yTemp);
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
    //
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
          if (d.measured === undefined){
            return 0;
          }
          else return y(d.measured);
        });
    const line2 = d3.line()
        .x(function (d: any, i) {
          return x(year[i]);
        })
        .y(function (d: any) {
          if (d.measured === undefined){
            return 0;
          }
          else return yTemp(d.measured);
        });


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
    yTemp2.domain([d3.min(data2, function (d: any) {
      return d.measured;
    }), d3.max(data2, function (d: any) {
      return d.measured;
    })]);
    yPred.domain([d3.min(dataPred, function (d: any) {
      return d.predicted;
    }), d3.max(dataPred, function (d: any) {
      return d.predicted;
    })]);
    yTemp.domain([d3.min(dataPred2, function (d: any) {
      return (d.measured < d.predicted) ? d.measured : d.predicted;
    }), d3.max(dataPred2, function (d: any) {
      return (d.measured > d.predicted) ? d.measured : d.predicted;
    })]);

    x2.domain(x.domain());
    y2.domain(y.domain());
    focus.append("circle")
        .attr("cx",-20).attr("cy",-25).attr("r", 3).style("fill", "blue");
    focus.append("line")
        .attr("x1",110).attr("y1",-20).attr("x2",130).attr("y2",-30).style("stroke", "blue");
    focus.append("circle")
        .attr("cx",260).attr("cy",-25).attr("r", 3).style("fill", "black");
    focus.append("line")
        .attr("x1",390).attr("y1",-20).attr("x2",410).attr("y2",-30).style("stroke", "black");
    focus.append("text")
        .attr("x", -10).attr("y", -20).text("CO₂ - predicted")
        .style("font-size", "15px").attr("alignment-baseline","middle");
    focus.append("text")
        .attr("x", 140).attr("y", -20).text("CO₂ - measured")
        .style("font-size", "15px").attr("alignment-baseline","middle");
    focus.append("text")
        .attr("x", 270).attr("y", -20).text("temp - predicted")
        .style("font-size", "15px").attr("alignment-baseline","middle");
    focus.append("text")
        .attr("x", 420).attr("y", -20).text("temp - measured")
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

    focus.append("text")
        .attr("transform",
            "translate(" + (width + 45)  + " ," +
            (height / 2) + ") rotate(-90)")
        .style("text-anchor", "middle")
        .style("font-size", "15px")
        .text("temperature value (°C)");

    focus.append("g")
        .attr("class", "axis axis--y2")
        .attr("transform", "translate("+width+",0)")
        .call(yAxis2);

    Line_chart.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line);

    Line_chart.append("path")
        .datum(data2)
        .attr("class", "line2")
        .attr("stroke", "black")
        .attr("fill", "none")
        .attr("d", line2);

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
        .style("fill", "blue");

    Line_chart.selectAll(".dot2")
        .data(dataPred2)
        .enter()
        .append("circle")
        .attr("class", "dot2")
        .attr("cx", (d: any, i:number) => {
          return x(year[i]);
        })
        .attr("cy", (d: any) => {
          return yTemp(d.predicted);
        })
        .attr("r", 1.5)
        .style("fill", "black");

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
