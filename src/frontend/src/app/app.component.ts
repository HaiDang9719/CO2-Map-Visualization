import { Component } from '@angular/core';
import { MapVisService } from "./service/map-vis.service";
import {take} from "rxjs/operators";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'geographic-information-system';

  constructor(public mapvisService: MapVisService)  {
    this.mapvisService.load_init();
    this.mapvisService.load_init_prediction();
    this.mapvisService.test_load();
    // this.mapvisService.load_average_temp().pipe(take(1)).subscribe((response: any) => {
    //   this.mapvisService.temperatureData.next(response);
    // });
  }
}
