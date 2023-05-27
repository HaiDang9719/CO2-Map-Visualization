import {Component, ElementRef, Input, OnInit, ViewChild} from '@angular/core';
import * as d3 from 'd3';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js';
// import {queue} from 'd3-queue';
import {MapVisService} from "../service/map-vis.service";
import {take} from "rxjs/operators";
import {FeatureCollection} from "geojson";
import "leaflet.heat/dist/leaflet-heat.js";
// import * as turf from '@turf/turf';

// import { addressPoints } from '../assets/realworld.10000'

@Component({
    selector: 'app-map',
    templateUrl: './map.component.html',
    styleUrls: ['./map.component.scss']
})
export class MapComponent implements OnInit {

    @ViewChild('map')
    private htmlElement: HTMLElement;
    private svg: any;
    private map!: L.Map;
    private layerGeo: L.LayerGroup<any> = L.layerGroup();
    private layerGlyph: L.LayerGroup<any> = L.layerGroup();
    private extentColor: any;
    private predictionData: any;
    private heatmapData: any;

    @Input() temp: FeatureCollection | undefined;

    constructor(public el: ElementRef, private mapvisService: MapVisService) {
        this.htmlElement = el.nativeElement;
    }

    ngOnInit(): void {
        // map initialize
        let mapV = L.map('map', {
            center: [39.8282, -98.5795],
            zoom: 4,
            renderer: L.svg()
        });

        const tiles = L.tileLayer("https://api.mapbox.com/styles/v1/dnlfrst/ckkvhe2yz43b517p5i4axnj1u/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiZG5sZnJzdCIsImEiOiJja2t2aGRka3AxcnRhMnFwZmYyMzBxdjJnIn0.SpX_ucXVnqC_3uij8p_18Q",
            {
                maxZoom: 6,
                attribution:
                    '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            }
        );
        // const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        //     maxZoom: 17,
        //     attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        // });

        tiles.addTo(mapV);

        // load data
        let points: any[] = [];
        let optionVis = "";
        let GeoLayer = (L as any).heatLayer(points, {
            maxZoom: 10
        })
            .addTo(mapV);
        // @ts-ignore
        let layerGlyph = L.svg({clickable: true}).addTo(mapV);
        this.mapvisService.visualizationSelection.subscribe(res => {
            if (res === 'heatmap') {
                // console.log(res);
                optionVis = "heatmap";
                mapV.removeLayer(layerGlyph);
                d3.select("#map")
                    .select("svg")
                    .selectAll(".myRect").remove();
                d3.select("#map")
                    .select("svg")
                    .selectAll(".myCircles").remove();
                // L.svg().removeFrom(mapV);
                this.mapvisService.countrySelection.next('')
                this.mapvisService.load_heatmap('2020');
                this.mapvisService.heatmapData.subscribe(response => {
                    mapV.removeLayer(GeoLayer);
                    const quakePoints: any[][] = []

                    // var scale = d3.scaleLinear().domain([d3.min(response.features, function (d: any) {
                    //     return d.properties.averageTemperatures[0].averageTemperature;
                    // }), d3.max(response.features, function (d: any) {
                    //     return d.properties.averageTemperatures[0].averageTemperature;
                    // })]).range([0, 1]);
                    // response.features.forEach((ele: any) => {
                    //
                    //     quakePoints.push([ele.geometry.coordinates[1], ele.geometry.coordinates[0],
                    //         scale(ele.properties.averageTemperatures[0].averageTemperature)])
                    // })
                    console.log(response)
                    var scale = d3.scaleLinear().domain([d3.min(response.features, function (d: any) {
                        return d.properties.slope;
                    }), d3.max(response.features, function (d: any) {
                        return d.properties.slope;
                    })]).range([0, 1]);
                    response.features.forEach((ele: any) => {

                        quakePoints.push([ele.geometry.coordinates[1], ele.geometry.coordinates[0],
                            scale(ele.properties.slope)])
                    })
                    // console.log(quakePoints);
                    GeoLayer = (L as any).heatLayer(quakePoints, {
                        radius: 23,
                        blur: 29,
                        maxZoom: 2,
                    }).addTo(mapV);

                    // this.layerGeo = GeoLayer;
                    // console.log(heatData);
                    function getRadius(val: number) {
                        let rad = 0;
                        const currentZoom = val;
                        // console.log(currentZoom)
                        if (currentZoom === 1) {
                            rad = 8;
                        } else if (currentZoom === 2) {
                            rad = 10;
                        } else if (currentZoom === 3) {
                            rad = 17;
                        } else if (currentZoom === 4) {
                            rad = 23;
                        } else if (currentZoom === 5) {
                            rad = 43;
                        } else if (currentZoom === 6) {
                            rad = 83;
                        }
                        return rad;
                    }

                    function getBlurr(val: number) {
                        let rad = 0;
                        const currentZoom = val;
                        if (currentZoom === 1) {
                            rad = 18;
                        } else if (currentZoom === 2) {
                            rad = 20;
                        } else if (currentZoom === 3) {
                            rad = 26;
                        } else if (currentZoom === 4) {
                            rad = 29;
                        } else if (currentZoom === 5) {
                            rad = 35;
                        } else if (currentZoom === 6) {
                            rad = 50;
                        }
                        return rad;
                    }

                    mapV.on('zoomend', function (ev) {
                        if (optionVis === "heatmap") {
                            // console.log(GeoLayer);
                            GeoLayer.setOptions({
                                radius: getRadius(ev.sourceTarget._zoom),
                                // max: 1.0,
                                blur: getBlurr(ev.sourceTarget._zoom),
                                // gradient: {
                                //     0.0: 'green',
                                //     0.5: 'yellow',
                                //     1.0: 'red'
                                // },
                                // minOpacity: 0.7
                            });
                            // render the new options
                            GeoLayer.redraw();
                        }

                    })
                });
            } else if (res === 'glyphmap') {
                mapV.removeLayer(GeoLayer);
                optionVis = "glyphmap"
                // @ts-ignore
                layerGlyph = L.svg({clickable: true}).addTo(mapV);
                this.mapvisService.load_init();
                this.mapvisService.load_init_prediction();
                this.mapvisService.predictionData.subscribe(response => {
                    this.predictionData = response;
                });
                this.mapvisService.temperatureData.subscribe(response => {
                    const ser = this.mapvisService;
                    const pred0 = this.predictionData[0];
                    const pred1 = this.predictionData[1];
                    const globalTrend0 = pred0.temperaturePredictions.global.slope;
                    // console.log(pred1.temperaturePredictions["Arctic Ocean"].slope)
                    // console.log(pred0)
                    // const globalTrend1 = pred1.temperaturePredictions.global.slope;
                    const data1 = [];
                    for (const [key, val] of Object.entries(pred0.temperaturePredictions)) {
                        // if (key != "global"){
                        // @ts-ignore
                        if (val.slope == undefined) {
                            data1.push(globalTrend0);
                        } else {
                            // @ts-ignore
                            data1.push(val.slope)
                        }

                        // }
                    }
                    for (const [key, val] of Object.entries(pred1.temperaturePredictions)) {
                        // @ts-ignore
                        data1.push(val.slope)
                    }

                    const extentColor = d3.extent(data1);
                    // const scaleAnomaly = d3.scaleDiverging(t => d3.interpolateRdBu(1 - t))
                    //       .domain([extentColor[0], globalTrend, extentColor[1]])

                    const scaleAnomaly = d3.scaleLinear()
                        .domain([extentColor[0], extentColor[1]])
                        // @ts-ignore
                        .range(['blue', 'red']);
                    // add svg glyph to the map

                    const xScale = d3.scaleLinear().domain([1980, 2020]).range([0, 220]);
                    // @ts-ignore

                    let data: { x: number; y: number; }[] = []

                    const markers: { long: number; lat: number; data: { x: number; y: number; }[]; country: string }[] = [];

                    response?.features.forEach((ele: any, index: number) => {
                        // console.log(ele);
                        const lon = ele.geometry.geometries[1].coordinates[0];
                        const lat = ele.geometry.geometries[1].coordinates[1];
                        let data: { x: number; y: number; }[] = [];
                        // @ts-ignore
                        const yScale = d3.scaleLinear().domain(d3.extent(ele.properties.averageTemperatures,
                            (d: any) => d.averageTemperature)).range([0, 500]);
                        ele.properties.averageTemperatures.forEach((ele1: any, index: number) => {
                            data.push({x: index, y: yScale(ele1.averageTemperature)})
                        })
                        let name = ele.properties.country;
                        if (name === undefined) {
                            name = ele.properties.ocean;
                        }
                        markers.push({long: lon, lat: lat, data: data, country: name})
                    })
                    // define area glyph
                    d3.select("#map")
                        .select("svg")
                        .selectAll(".myRect")
                        .data(markers)
                        .enter()
                        .append("rect")
                        .attr("class", "myRect")
                        .attr("x", function (d) {
                            return mapV.latLngToLayerPoint([d.lat, d.long]).x;
                        })
                        .attr("y", function (d) {
                            return mapV.latLngToLayerPoint([d.lat, d.long]).y - 50;
                        })
                        .attr("width", 40)
                        .attr("height", 48)
                        .attr("fill", "white");

                    const circle = d3.select("#map")
                        .select("svg")
                        .selectAll(".myCircles")
                        .data(markers)
                        .enter()
                        .append("path")
                        .attr("class", "myCircles")
                        .attr("d", function (d) {
                            // console.log(d);
                            const realX = mapV.latLngToLayerPoint([d.lat, d.long]).x;
                            const realY = mapV.latLngToLayerPoint([d.lat, d.long]).y;
                            let dateValue: { x: number; y: number; }[] = [];
                            // const data = [{x: 0, y: 100},
                            //     {x: 150, y: 150}, {x: 300, y: 100}, {x: 450, y: 20}, {x: 600, y: 130}]
                            d.data.forEach(ele => {
                                dateValue.push({x: realX + ele.x, y: realY - ele.y / 10})

                            })
                            // console.log(realY);
                            const curveFunc = d3.area()
                                .x(function (d: any) {
                                    return d.x
                                })      // Position of both line breaks on the X axis
                                .y1(function (d: any) {
                                    return d.y
                                })     // Y position of top line breaks
                                .y0(realY);
                            // @ts-ignore
                            return curveFunc(dateValue);
                        })
                        .style("fill", function (d: any) {
                            if (pred0.temperaturePredictions[d.country] === undefined) {
                                return scaleAnomaly(pred1.temperaturePredictions[d.country].slope)
                            }
                            return scaleAnomaly(pred0.temperaturePredictions[d.country].slope);
                            // if (pred.temperaturePredictions[d.country].slope < globalTrend){
                            //     return 'blue';
                            // }else{
                            //     return 'red';
                            // }
                        })
                        .attr("stroke", function (d: any) {
                            if (pred0.temperaturePredictions[d.country] === undefined) {
                                return scaleAnomaly(pred1.temperaturePredictions[d.country].slope)
                            }
                            return scaleAnomaly(pred0.temperaturePredictions[d.country].slope);
                            // if (pred.temperaturePredictions[d.country].slope < globalTrend){
                            //     return 'blue';
                            // }else{
                            //     return 'red';
                            // }
                        })
                        .attr("stroke-width", 1)
                        .attr("fill-opacity", .4)


// Function that update circle position if something change
                    function update() {
                        d3.selectAll(".myCircles")
                            .attr("d", function (d: any) {
                                // console.log(d);
                                const realX = mapV.latLngToLayerPoint([d.lat, d.long]).x;
                                const realY = mapV.latLngToLayerPoint([d.lat, d.long]).y;
                                let dateValue: { x: number; y: number; }[] = [];
                                d.data.forEach((ele: { x: number; y: number; }) => {
                                    dateValue.push({x: realX + ele.x, y: realY - ele.y / 10})

                                })
                                const curveFunc = d3.area()
                                    .x(function (d: any) {
                                        return d.x
                                    })      // Position of both line breaks on the X axis
                                    .y1(function (d: any) {
                                        return d.y
                                    })     // Y position of top line breaks
                                    .y0(realY);
                                // @ts-ignore
                                return curveFunc(dateValue);
                            })
                        d3.selectAll(".myRect")
                            .attr("x", function (d: any) {
                                return mapV.latLngToLayerPoint([d.lat, d.long]).x;
                            })
                            .attr("y", function (d: any) {
                                return mapV.latLngToLayerPoint([d.lat, d.long]).y - 50;
                            })
                    }

                    // @ts-ignore
                    const test = this.temp?.features.map(ele => {
                        if ("geometries" in ele.geometry) {
                            ele.geometry.geometries = [ele.geometry.geometries[0]];
                        }
                        // console.log(ele.geometry.geometries[1]);
                        return ele;
                    })
                    // console.log(test)
                    // @ts-ignore
                    L.geoJSON(test, {
                        style: this.style, onEachFeature(feature: any, layer: any) {
                            layer.on('click', function (e: any) {
                                // e = event
                                // @ts-ignore
                                // console.log(Object.values(e.sourceTarget._eventParents)[0].feature);
                                // @ts-ignore
                                let con = Object.values(e.sourceTarget._eventParents)[0].feature.properties.country
                                if (con === undefined){
                                    // @ts-ignore
                                    con = Object.values(e.sourceTarget._eventParents)[0].feature.properties.ocean
                                }
                                // console.log(Object.values(e.sourceTarget._eventParents)[0].feature.properties);
                                // console.log(e.sourceTarget._eventParents[0]);
                                ser.set_country(con);
                            });
                        }
                    }).addTo(mapV);
// If the user change the map (zoom or drag), I update circle position:
                    mapV.on("moveend",(d)=>{
                        if (optionVis === "glyphmap") {
                        return update
                        }
                        return;
                    } )


                });
            }
        })
    }

    style(): any {
        return {
            fillColor: 'transparent',
            weight: 2,
            opacity: 1,
            color: 'blue',
            dashArray: '2',
            fillOpacity: 0.3
        };

    }
}
