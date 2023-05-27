import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from "@angular/forms";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatOptionModule } from "@angular/material/core";
import { MatMenuModule } from '@angular/material/menu';
import { MatSelectModule } from '@angular/material/select';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatSliderModule} from '@angular/material/slider';
import {MatTabsModule} from '@angular/material/tabs';
import { AppComponent } from './app.component';
import { AuxiliaryComponent } from './auxiliary/auxiliary.component'
import { GraphComponent } from './graph/graph.component';
import { MapComponent } from './map/map.component';
import { TimeFrameSelectionComponent } from './time-frame-selection/time-frame-selection.component';
import { GraphCo2Component } from './graph-co2/graph-co2.component';
import { GraphCo2TempComponent } from './graph-co2-temp/graph-co2-temp.component'
import {MatRadioModule} from '@angular/material/radio';
import { UserInteractionComponent } from './auxiliary/user-interaction/user-interaction.component';
import {MatDialogModule} from '@angular/material/dialog';
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import { GraphGdpTempComponent } from './graph-gdp-temp/graph-gdp-temp.component';
@NgModule({
  declarations: [
    AppComponent,
    MapComponent,
    AuxiliaryComponent,
    GraphComponent,
    TimeFrameSelectionComponent,
    GraphCo2Component,
    GraphCo2TempComponent,
    UserInteractionComponent,
    GraphGdpTempComponent,
  ],
  imports: [
    BrowserModule,
    MatMenuModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatCheckboxModule,
    FormsModule,
    MatButtonModule,
    HttpClientModule,
    MatOptionModule,
    MatSelectModule,
    MatSliderModule,
    MatTabsModule,
    MatRadioModule,
    MatDialogModule,
    MatInputModule,
    MatFormFieldModule

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
