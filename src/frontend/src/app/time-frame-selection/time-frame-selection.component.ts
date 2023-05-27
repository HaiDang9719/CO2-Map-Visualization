import {Component, Input, OnInit} from '@angular/core';
import {FeatureCollection} from "geojson";
import {MapVisService} from "../service/map-vis.service";
import {take} from "rxjs/operators";

@Component({
  selector: 'app-time-frame-selection',
  templateUrl: './time-frame-selection.component.html',
  styleUrls: ['./time-frame-selection.component.scss']
})
export class TimeFrameSelectionComponent implements OnInit {

  constructor(private mapvisService: MapVisService) {
  }
  // @Input() temp: FeatureCollection | undefined;
  tempe: FeatureCollection | undefined;
  autoTicks = false;
  disabled = false;
  invert = false;
  max = 2020;
  min = 1980;
  showTicks = false;
  step = 1;
  thumbLabel = false;
  value = 2020;
  vertical = false;
  tickInterval = 1;


  getSliderTickInterval(): number | 'auto' {
    if (this.showTicks) {
      return this.autoTicks ? 'auto' : this.tickInterval;
    }
    return 1;
  }

  onInputChange(event: any) {
    // this.mapvisService.load_average_temp().subscribe((response: any) => {
    //   response?.features.forEach((ele: any) => {
    //     ele.properties.averageTemperatures = ele.properties.averageTemperatures.filter((ele2: any) => parseInt(ele2.year) <= this.value);
    //     // ele.properties.averageTemperatures = [];
    //   })
    //   // console.log(test)
    //   this.mapvisService.temperatureData.next(response);
    // })

    this.mapvisService.load_heatmap(this.value.toString());

  }

  ngOnInit(): void {
  }
}
