from ast import literal_eval
from typing import Optional, Literal

from fastapi import FastAPI
from sqlalchemy import extract
from sqlalchemy import func
from starlette.middleware.cors import CORSMiddleware

from database import get_database
from database_entities.CountryWithGDPProjection import CountryWithGDPProjection
from database_entities.average_co2_ppm import AvgCO2PPM
from database_entities.country import Country
from database_entities.country_with_average_temperature import CountryWithAverageTemperature
from database_entities.land_heatmap import LandHeatmap
from database_entities.land_stations import LandStations
from database_entities.ocean import Ocean
from database_entities.ocean_average_temperature_aggregated import OceanAverageTemperatureAggregated
from database_entities.ocean_with_average_temperature import OceanWithAverageTemperature
from database_entities.yearly_station_average import YearlyStationAverage
from interpolation import interpolate_grid_from_stations
from regression import predict_aggregated_temperature
from regression import predict_co2
from regression import predict_global_temperature
from regression import predict_ocean_heatmap
from regression import predict_station
from regression import find_co2_curve

app = FastAPI()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/country_predictions")
def get_country_predictions():
    with get_database() as database:
        filter_stations = database.query(YearlyStationAverage.station_id).group_by(
            YearlyStationAverage.station_id).having(func.count(YearlyStationAverage.year) >= 35).subquery()
        countries_with_average_temperatures = database.query(Country, CountryWithAverageTemperature).join(
            CountryWithAverageTemperature).values(Country.name, CountryWithAverageTemperature.year,
                                                  CountryWithAverageTemperature.average_temperature)
        average_co2_ppm = database.query(AvgCO2PPM)

        land_temperatures = database.query(YearlyStationAverage.year,
                                           func.avg(YearlyStationAverage.temperature).label('avg_temp')).filter(
            YearlyStationAverage.station_id.in_(filter_stations)).group_by(YearlyStationAverage.year)

    grouped_countries_with_average_temperatures = {}

    for country_with_average_temperature in countries_with_average_temperatures:
        average_temperature: float = country_with_average_temperature.average_temperature
        country: str = country_with_average_temperature.name
        year: int = country_with_average_temperature.year.year

        if country in grouped_countries_with_average_temperatures:
            grouped_countries_with_average_temperatures[country][year] = average_temperature
        else:
            grouped_countries_with_average_temperatures[country] = {
                year: average_temperature
            }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    global_land_temperature = {}
    counter = {}
    for monthly_land_temperature in land_temperatures:
        temperature: float = monthly_land_temperature.avg_temp
        year: int = monthly_land_temperature.year.year
        if year in global_land_temperature:
            global_land_temperature[year] = global_land_temperature[year] + temperature
            counter[year] += 1
        else:
            global_land_temperature[year] = temperature
            counter[year] = 1

    for year in range(1980, 2021):
        global_land_temperature[year] = global_land_temperature[year] / counter[year]

    predicted_co2 = predict_co2(yearly_co2_ppm)

    predicted_country_temperature = predict_aggregated_temperature(grouped_countries_with_average_temperatures,
                                                                   predicted_co2)

    predicted_global_temperature = predict_global_temperature(global_land_temperature, predicted_co2)

    predicted_country_temperature['global'] = predicted_global_temperature

    return {'co2Predictions': predicted_co2, 'temperaturePredictions': predicted_country_temperature}


@app.get("/countries")
def get_countries():
    with get_database() as database:
        countries = database.query(Country).join(CountryWithAverageTemperature).distinct().order_by(
            Country.name.asc()).values(Country.name)

    return [country[0] for country in countries]


@app.get("/countries-with-average-temperatures")
def get_countries_with_average_temperatures():
    with get_database() as database:
        countries_with_average_temperatures = database \
            .query(Country, CountryWithAverageTemperature) \
            .join(CountryWithAverageTemperature) \
            .values(Country.name,
                    Country.boundaries.ST_AsGeoJSON().label('boundary'),
                    Country.center.ST_AsGeoJSON().label('center'),
                    CountryWithAverageTemperature.year,
                    CountryWithAverageTemperature.average_temperature)

        countries_with_gdp_predictions = database \
            .query(Country, CountryWithGDPProjection) \
            .join(CountryWithGDPProjection) \
            .order_by(CountryWithGDPProjection.year.asc()) \
            .values(Country.name, CountryWithGDPProjection.year, CountryWithGDPProjection.gdp_projection)

    grouped_countries_with_average_temperatures = {}

    for country_with_average_temperature in countries_with_average_temperatures:
        average_temperature: float = country_with_average_temperature.average_temperature
        country: str = country_with_average_temperature.name
        year: int = country_with_average_temperature.year

        if country not in grouped_countries_with_average_temperatures:
            grouped_countries_with_average_temperatures[country] = {
                'average_temperatures': [],
                'gdp_projections': [],
                # Convert the dictionary-as-string to an actual dictionary.
                'boundary': literal_eval(country_with_average_temperature.boundary),
                'center': literal_eval(country_with_average_temperature.center)
            }

        if average_temperature is not None:
            grouped_countries_with_average_temperatures[country]['average_temperatures'].append({
                'averageTemperature': average_temperature,
                'year': year
            })

    for country_with_gdp_predictions in countries_with_gdp_predictions:
        gdp_projection: float = country_with_gdp_predictions.gdp_projection
        country: str = country_with_gdp_predictions.name
        year: int = country_with_gdp_predictions.year

        if country in grouped_countries_with_average_temperatures:
            grouped_countries_with_average_temperatures[country]['gdp_projections'].append({
                'gdpProjection': gdp_projection,
                'year': year
            })

    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for country, average_temperatures_and_geometry in grouped_countries_with_average_temperatures.items():
        average_temperatures = average_temperatures_and_geometry['average_temperatures']
        gdp_projections = average_temperatures_and_geometry['gdp_projections']
        boundary = average_temperatures_and_geometry['boundary']
        center = average_temperatures_and_geometry['center']

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'GeometryCollection',
                'geometries': [boundary, center]
            },
            'properties': {
                'country': country,
                'averageTemperatures': average_temperatures,
                'gdpProjections': gdp_projections
            }
        })

    return geo_json


# this method was used to collect the data for the land heatmap
# to speed up the application, the heatmap data was added to the DB
# so this method is here only for documentation purposes
# the data created from this method is ued in LAND_HEATMAP.csv
@app.get("/land_heatmap_data")
def calculate_land_heatmap_data():
    with get_database() as database:
        average_co2_ppm = database.query(AvgCO2PPM)
        land_station_measurements = database.query(YearlyStationAverage) \
            .join(LandStations, LandStations.station_id == YearlyStationAverage.station_id) \
            .values(YearlyStationAverage.temperature, YearlyStationAverage.year,
                    LandStations.latitude, LandStations.longitude, LandStations.station_id)

    grouped_station_temperatures = {}
    station_locations = {}

    for yearly_station_data in land_station_measurements:
        average_temperature: float = yearly_station_data.temperature
        latitude: float = yearly_station_data.latitude
        longitude: float = yearly_station_data.longitude
        year: int = yearly_station_data.year.year
        name: str = yearly_station_data.station_id

        if name in grouped_station_temperatures:
            grouped_station_temperatures[name][year] = average_temperature
        else:
            grouped_station_temperatures[name] = {
                year: average_temperature
            }
        if name not in station_locations:
            station_locations[name] = {
                "latitude": latitude,
                "longitude": longitude
            }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    predicted_co2 = predict_co2(yearly_co2_ppm)

    accepted_stations = {}
    for station in list(grouped_station_temperatures.items()):
        if predict_station(station[1], predicted_co2):
            accepted_stations[station[0]] = station[1]

    grid = interpolate_grid_from_stations(accepted_stations, station_locations)

    return grid


@app.get("/heatmap")
def get_heatmap_grid():
    with get_database() as database:
        average_co2_ppm = database.query(AvgCO2PPM)
        land_heatmap_grid = database \
            .query(LandHeatmap.latitude, LandHeatmap.longitude, LandHeatmap.slope) \
            .join(Country, func.ST_Contains(Country.boundaries, func.ST_SetSRID(func.ST_MakePoint(LandHeatmap.longitude, LandHeatmap.latitude), 4326)))
        ocean_average_temperatures_aggregated = database \
            .query(OceanAverageTemperatureAggregated.year,
                   OceanAverageTemperatureAggregated.location.ST_AsGeoJSON().label('location'),
                   OceanAverageTemperatureAggregated.average_temperature)

    land_heatmap_data = {}

    for grid_point in land_heatmap_grid:
        latitude: float = grid_point.latitude
        longitude: float = grid_point.longitude
        slope: float = grid_point.slope
        location: str = f"POINT ({longitude} {latitude})"

        land_heatmap_data[location] = {
            'slope': slope,
            'latitude': latitude,
            'longitude': longitude
        }

    grouped_ocean_average_temperatures = {}

    for ocean_average_temperature_aggregated in ocean_average_temperatures_aggregated:
        average_temperature: float = ocean_average_temperature_aggregated.average_temperature
        location: str = ocean_average_temperature_aggregated.location
        year: int = ocean_average_temperature_aggregated.year

        if location in grouped_ocean_average_temperatures:
            grouped_ocean_average_temperatures[location]['average_temperatures'].append({
                'averageTemperature': average_temperature,
                'year': year
            })
        else:
            grouped_ocean_average_temperatures[location] = {
                'average_temperatures': [{
                    'averageTemperature': average_temperature,
                    'year': year
                }],
                # Convert the dictionary-as-string to an actual dictionary.
                'location': literal_eval(ocean_average_temperature_aggregated.location),
            }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    predicted_co2 = predict_co2(yearly_co2_ppm)

    predicted_ocean_slope = predict_ocean_heatmap(grouped_ocean_average_temperatures,
                                                  predicted_co2)

    
    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for location, heatmap_point in land_heatmap_data.items():
        latitude = heatmap_point['latitude']
        longitude = heatmap_point['longitude']
        slope = heatmap_point['slope']

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': "Point",
                'coordinates': [longitude, latitude]
            },
            'properties': {
                'slope': max(-0.025, min(0.025, slope))
            }
        })

    for location, average_temperatures_and_geometry in grouped_ocean_average_temperatures.items():
        location = average_temperatures_and_geometry['location']
        slope_ = predicted_ocean_slope[str(location)]
        if type(slope_) is set:
            slope = slope_   
        else:
            slope = max(-0.025, min(0.025, slope_))

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': location,
            'properties': {
                'slope': slope
            }
        })

    return geo_json


@app.get("/land_relative_temperature_change")
def get_land_relative_temperature_change():
    with get_database() as database:
        land_heatmap_grid = database \
            .query(LandHeatmap.longitude, LandHeatmap.latitude, LandHeatmap.slope)

    heatmap_data = {}

    for grid_point in land_heatmap_grid:
        latitude: float = grid_point.latitude
        longitude: float = grid_point.longitude
        slope: float = grid_point.slope
        location: str = f"POINT ({longitude} {latitude})"

        heatmap_data[location] = {
            'slope': slope,
            'latitude': latitude,
            'longitude': longitude
        }

    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for location, heatmap_point in heatmap_data.items():
        latitude = heatmap_point['latitude']
        longitude = heatmap_point['longitude']
        slope = heatmap_point['slope']

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': "Point",
                'coordinates': [longitude, latitude]
            },
            'properties': {
                'slope': slope
            }
        })
    return geo_json


@app.get("/ocean_relative_temperature_change")
def get_ocean_relative_temperature_change():
    with get_database() as database:
        average_co2_ppm = database.query(AvgCO2PPM)
        ocean_average_temperatures_aggregated = database \
            .query(OceanAverageTemperatureAggregated.year,
                   OceanAverageTemperatureAggregated.location.ST_AsGeoJSON().label('location'),
                   OceanAverageTemperatureAggregated.average_temperature)

    grouped_ocean_average_temperatures = {}

    for ocean_average_temperature_aggregated in ocean_average_temperatures_aggregated:
        average_temperature: float = ocean_average_temperature_aggregated.average_temperature
        location: str = ocean_average_temperature_aggregated.location
        year: int = ocean_average_temperature_aggregated.year

        if location in grouped_ocean_average_temperatures:
            grouped_ocean_average_temperatures[location]['average_temperatures'].append({
                'averageTemperature': average_temperature,
                'year': year
            })
        else:
            grouped_ocean_average_temperatures[location] = {
                'average_temperatures': [{
                    'averageTemperature': average_temperature,
                    'year': year
                }],
                # Convert the dictionary-as-string to an actual dictionary.
                'location': literal_eval(ocean_average_temperature_aggregated.location),
            }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    predicted_co2 = predict_co2(yearly_co2_ppm)

    predicted_ocean_slope = predict_ocean_heatmap(grouped_ocean_average_temperatures,
                                                  predicted_co2)

    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for location, average_temperatures_and_geometry in grouped_ocean_average_temperatures.items():
        location = average_temperatures_and_geometry['location']
        slope = predicted_ocean_slope[str(location)]

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': location,
            'properties': {
                'slope': slope
            }
        })

    return geo_json


@app.get("/oceans")
def get_oceans():
    with get_database() as database:
        oceans = database \
            .query(Ocean) \
            .join(OceanWithAverageTemperature) \
            .distinct() \
            .order_by(Ocean.name.asc()) \
            .values(Ocean.name)

    return [ocean[0] for ocean in oceans]

@app.get("/ocean-average-temperatures-aggregated")
def get_ocean_average_temperatures_aggregated(year: Optional[int] = None):
    with get_database() as database:
        ocean_average_temperatures_aggregated = database \
            .query(OceanAverageTemperatureAggregated.year,
                   OceanAverageTemperatureAggregated.location.ST_AsGeoJSON().label('location'),
                   OceanAverageTemperatureAggregated.average_temperature)

        if year is not None:
            ocean_average_temperatures_aggregated = ocean_average_temperatures_aggregated.filter(
                extract('year', OceanAverageTemperatureAggregated.year) == year)

    grouped_ocean_average_temperatures = {}

    for ocean_average_temperature_aggregated in ocean_average_temperatures_aggregated:
        average_temperature: float = ocean_average_temperature_aggregated.average_temperature
        location: str = ocean_average_temperature_aggregated.location
        year: int = ocean_average_temperature_aggregated.year

        if location in grouped_ocean_average_temperatures:
            grouped_ocean_average_temperatures[location]['average_temperatures'].append({
                'averageTemperature': average_temperature,
                'year': year
            })
        else:
            grouped_ocean_average_temperatures[location] = {
                'average_temperatures': [{
                    'averageTemperature': average_temperature,
                    'year': year
                }],
                # Convert the dictionary-as-string to an actual dictionary.
                'location': literal_eval(ocean_average_temperature_aggregated.location),
            }

    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for location, average_temperatures_and_geometry in grouped_ocean_average_temperatures.items():
        average_temperatures = average_temperatures_and_geometry['average_temperatures']
        location = average_temperatures_and_geometry['location']

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': location,
            'properties': {
                'averageTemperatures': average_temperatures
            }
        })

    return geo_json


@app.get("/ocean_predictions")
def get_ocean_predictions():
    with get_database() as database:
        oceans_with_average_temperatures = database \
            .query(Ocean, OceanWithAverageTemperature) \
            .join(OceanWithAverageTemperature) \
            .values(Ocean.name,
                    Ocean.boundaries.ST_AsGeoJSON().label('boundary'),
                    Ocean.center.ST_AsGeoJSON().label('center'),
                    OceanWithAverageTemperature.year,
                    OceanWithAverageTemperature.average_temperature)
        average_co2_ppm = database.query(AvgCO2PPM)

    grouped_oceans_with_average_temperatures = {}

    for ocean_with_average_temperature in oceans_with_average_temperatures:
        average_temperature: float = ocean_with_average_temperature.average_temperature
        ocean: str = ocean_with_average_temperature.name
        year: int = ocean_with_average_temperature.year.year

        if ocean in grouped_oceans_with_average_temperatures:
            grouped_oceans_with_average_temperatures[ocean][year] = average_temperature
        else:
            grouped_oceans_with_average_temperatures[ocean] = {
                year: average_temperature
            }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    predicted_co2 = predict_co2(yearly_co2_ppm)

    predicted_ocean_temperature = predict_aggregated_temperature(grouped_oceans_with_average_temperatures,
                                                                 predicted_co2)

    return {'co2Predictions': predicted_co2, 'temperaturePredictions': predicted_ocean_temperature}


@app.get("/oceans-with-average-temperatures")
def get_oceans_with_average_temperatures():
    with get_database() as database:
        oceans_with_average_temperatures = database \
            .query(Ocean, OceanWithAverageTemperature) \
            .join(OceanWithAverageTemperature) \
            .values(Ocean.name,
                    Ocean.boundaries.ST_AsGeoJSON().label('boundary'),
                    Ocean.center.ST_AsGeoJSON().label('center'),
                    OceanWithAverageTemperature.year,
                    OceanWithAverageTemperature.average_temperature)

    grouped_oceans_with_average_temperatures = {}

    for ocean_with_average_temperature in oceans_with_average_temperatures:
        average_temperature: float = ocean_with_average_temperature.average_temperature
        ocean: str = ocean_with_average_temperature.name
        year: int = ocean_with_average_temperature.year.year

        if ocean in grouped_oceans_with_average_temperatures:
            grouped_oceans_with_average_temperatures[ocean]['average_temperatures'].append({
                'averageTemperature': average_temperature,
                'year': year
            })
        else:
            grouped_oceans_with_average_temperatures[ocean] = {
                'average_temperatures': [{
                    'averageTemperature': average_temperature,
                    'year': year
                }],
                # Convert the dictionary-as-string to an actual dictionary.
                'boundary': literal_eval(ocean_with_average_temperature.boundary),
                'center': literal_eval(ocean_with_average_temperature.center)
            }

    geo_json = {
        'type': 'FeatureCollection',
        'features': []
    }

    for ocean, average_temperatures_and_geometry in grouped_oceans_with_average_temperatures.items():
        average_temperatures = average_temperatures_and_geometry['average_temperatures']
        boundary = average_temperatures_and_geometry['boundary']
        center = average_temperatures_and_geometry['center']

        geo_json['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'GeometryCollection',
                'geometries': [boundary, center]
            },
            'properties': {
                'ocean': ocean,
                'averageTemperatures': average_temperatures
            }
        })

    return geo_json


@app.get("/countries-and-oceans-with-average-temperatures")
def get_countries_oceans_with_average_temperatures():
    countries_with_average_temperatures = get_countries_with_average_temperatures()
    oceans_with_average_temperatures = get_oceans_with_average_temperatures()

    geo_json = {
        'type': 'FeatureCollection',
        'features': countries_with_average_temperatures['features'] + oceans_with_average_temperatures['features']
    }

    return geo_json


@app.get("/temperature-limit")
def get_predicted_co2_with_temperature_limit(type: Literal['country', 'ocean'], area: str, year: int,
                                             temperature: float):
    with get_database() as database:
        if type == 'country':
            filter_stations = database.query(YearlyStationAverage.station_id).group_by(
                YearlyStationAverage.station_id).having(func.count(YearlyStationAverage.year) >= 35).subquery()
            countries_with_average_temperatures = database \
                .query(Country, CountryWithAverageTemperature) \
                .filter(Country.name == area) \
                .join(CountryWithAverageTemperature) \
                .values(Country.name, CountryWithAverageTemperature.year,
                        CountryWithAverageTemperature.average_temperature)

            land_temperatures = database.query(YearlyStationAverage.year,
                                               func.avg(YearlyStationAverage.temperature).label('avg_temp')).filter(
                YearlyStationAverage.station_id.in_(filter_stations)).group_by(YearlyStationAverage.year)
        else:
            oceans_with_average_temperatures = database \
                .query(Ocean, OceanWithAverageTemperature) \
                .filter(Ocean.name == area) \
                .join(OceanWithAverageTemperature) \
                .values(Ocean.name,
                        OceanWithAverageTemperature.year,
                        OceanWithAverageTemperature.average_temperature)

        average_co2_ppm = database.query(AvgCO2PPM)

    if type == 'country':
        grouped_countries_with_average_temperatures = {}

        for country_with_average_temperature in countries_with_average_temperatures:
            average_temperature: float = country_with_average_temperature.average_temperature
            country: str = country_with_average_temperature.name
            year_: int = country_with_average_temperature.year.year

            if country in grouped_countries_with_average_temperatures:
                grouped_countries_with_average_temperatures[country][year_] = average_temperature
            else:
                grouped_countries_with_average_temperatures[country] = {
                    year_: average_temperature
                }

        global_land_temperature = {}
        counter = {}
        for monthly_land_temperature in land_temperatures:
            temperature_: float = monthly_land_temperature.avg_temp
            year_: int = monthly_land_temperature.year.year
            if year_ in global_land_temperature:
                global_land_temperature[year_] += temperature_
                counter[year_] += 1
            else:
                global_land_temperature[year_] = temperature_
                counter[year_] = 1

        for year_ in range(1980, 2021):
            global_land_temperature[year_] /= counter[year_]
    else:
        grouped_oceans_with_average_temperatures = {}

        for ocean_with_average_temperature in oceans_with_average_temperatures:
            average_temperature: float = ocean_with_average_temperature.average_temperature
            ocean: str = ocean_with_average_temperature.name
            year_: int = ocean_with_average_temperature.year.year

            if ocean in grouped_oceans_with_average_temperatures:
                grouped_oceans_with_average_temperatures[ocean][year_] = average_temperature
            else:
                grouped_oceans_with_average_temperatures[ocean] = {
                    year_: average_temperature
                }

    yearly_co2_ppm = get_co2_data_from_db_response(average_co2_ppm)

    predicted_co2 = predict_co2(yearly_co2_ppm)

    if type == 'country':
        predicted_country_temperature = find_co2_curve(grouped_countries_with_average_temperatures, predicted_co2, year, temperature)
        return {'co2Predictions': predicted_co2, 'temperaturePredictions': predicted_country_temperature}
    else:
        predicted_ocean_temperature = find_co2_curve(grouped_oceans_with_average_temperatures, predicted_co2, year, temperature)
        return {'co2Predictions': predicted_co2, 'temperaturePredictions': predicted_ocean_temperature}


def get_co2_data_from_db_response(average_co2_ppm):
    yearly_co2_ppm = {}
    counter = {}

    for monthly_co2_ppm in average_co2_ppm:
        monthly_co2: float = monthly_co2_ppm.monthly_avg
        year: int = monthly_co2_ppm.date.year
        if year in yearly_co2_ppm:
            yearly_co2_ppm[year] = yearly_co2_ppm[year] + monthly_co2
            counter[year] += 1
        else:
            yearly_co2_ppm[year] = monthly_co2
            counter[year] = 1

    for year in range(1980, 2021):
        yearly_co2_ppm[year] = yearly_co2_ppm[year] / counter[year]

    return yearly_co2_ppm