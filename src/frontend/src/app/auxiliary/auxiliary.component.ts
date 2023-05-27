import { Component, OnInit } from '@angular/core';
import { take } from "rxjs/operators";
import { MapVisService } from "../service/map-vis.service";
import {UserInteractionComponent} from "./user-interaction/user-interaction.component";
import {MatDialog} from "@angular/material/dialog";

@Component({
  selector: 'app-auxiliary',
  templateUrl: './auxiliary.component.html',
  styleUrls: ['./auxiliary.component.scss']
})
export class AuxiliaryComponent implements OnInit {
  countrySelection = '';
  showAirTemperature = false;
  showOceanTemperature = false;
  showMeasurementStations = false;
  countries: string[];
  heatMap = { name: 'heatmap', checked: false };
  glyphMap = { name: 'glyphmap', checked: false };

  constructor(private mapvisService: MapVisService, private dialog: MatDialog,) {
    this.countries = [''];}

  ngOnInit(): void {
    // this.mapvisService.load_countries().pipe(take(1)).subscribe((response: any) => {
    //   response.features.forEach((ele: { properties: { name: string; }; }) => {
    //     this.countries.push(ele.properties.name)
    //   })
    // });
    this.mapvisService.load_countries().pipe(take(1)).subscribe((response: any) => {
      this.countries = response;
    });
  }
  updateChecked(name: string){
    this.mapvisService.set_visualization(name)
    // if (this.heatMap.checked) {
    //   this.glyphMap.checked = false;
    //   this.mapvisService.set_visualization(this.heatMap.name)
    // }
    // else if (this.glyphMap.checked){
    //   this.heatMap.checked = true;
    //   this.mapvisService.set_visualization(this.glyphMap.name)
    // }

  }
  userInteraction(): void{
    const dialogRef = this.dialog.open(UserInteractionComponent);
    // subscribe to the upload progress to reload the tree after the upload has finished
    dialogRef.afterClosed().subscribe(result => {
      console.log(result);
    });

  }
  selectedCountry(name: string): void {
    this.countrySelection = name;
    this.mapvisService.set_country(name);
  }
}
