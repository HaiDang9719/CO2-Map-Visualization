import {HttpClient, HttpParams} from "@angular/common/http";
import { Injectable } from '@angular/core';
import {BehaviorSubject, forkJoin, Observable, Subject} from "rxjs";
import { environment } from '../../environments/environment';
import {FeatureCollection} from 'geojson';
@Injectable({
  providedIn: 'root'
})
export class MapVisService {

  countrySelection = new BehaviorSubject('');
  variableSelection = new BehaviorSubject('temp');
  visualizationSelection = new BehaviorSubject('');
  currentCountrySelection = this.countrySelection.asObservable();
  temperatureData = new Subject<FeatureCollection>();
  predictionData = new Subject<any>();
  heatmapData = new Subject<FeatureCollection>();

  constructor(private http: HttpClient) {
  }

  // load_countries(): Observable<Object> {
  //   return this.http.get('assets/world-countries.json');
  // }
  load_countries(): Observable<Object> {
    return this.http.get(environment.apiUrl + '/countries');
  }

  set_country(name: string): void {
    this.countrySelection.next(name);

  }
  set_variable(name: string): void {
    this.variableSelection.next(name);

  }
  set_visualization(name: string): void {
    this.visualizationSelection.next(name);

  }
  load_graphData(): Observable<Object> {
    return this.http.get('assets/CIMIS_Station_125.csv', {responseType: 'text'});
  }
  load_geoJsonData(): Observable<Object> {
    return this.http.get('assets/us-states.json');
  }
  load_average_temp(): Observable<Object> {
    return this.http.get<FeatureCollection>(environment.apiUrl + '/countries-with-average-temperatures');
  }
  load_init(): void{
    this.http.get<FeatureCollection>(environment.apiUrl + '/countries-and-oceans-with-average-temperatures').subscribe( response => {
      this.temperatureData.next(response);
    });
  }
  load_init_prediction(): void{
    let countryPrediction = this.http.get(environment.apiUrl + '/country_predictions');
    let oceanPrediction = this.http.get(environment.apiUrl + '/ocean_predictions');
    forkJoin([countryPrediction, oceanPrediction]).subscribe( response => {
      this.predictionData.next(response);
    });
    // this.http.get<any>(environment.apiUrl + '/country_predictions').subscribe( response => {
    //   this.predictionData.next(response);
    // });
  }
  load_heatmap(year: string): void{
    let params = new HttpParams();
    params = params.append('year', year);
    // this.http.get<FeatureCollection>(environment.apiUrl + '/ocean-average-temperatures-aggregated',
    //     { params: params })
    //     .subscribe( response => {
    //   this.heatmapData.next(response);
    // });
    this.http.get<FeatureCollection>(environment.apiUrl + '/heatmap')
        .subscribe( response => {
          this.heatmapData.next(response);
        });

  }
  interaction(year: string, temp: string, area: string, code: string):  Observable<Object>{
    let params = new HttpParams();
    params = params.append('type', code);
    params = params.append('area', area);
    params = params.append('year', year);
    params = params.append('temperature', temp);

    return this.http.get<any>(environment.apiUrl + '/temperature-limit',
        { params: params });
  }
  test_load(): void{
    this.http.get<any>(environment.apiUrl + '/heatmap').subscribe( response => {
      // /console.log(response)
      // this.predictionData.next(response);
    });
  }
  load_prediction(): Observable<Object>{
    return this.http.get<any>(environment.apiUrl + '/country_predictions');
  }
}
