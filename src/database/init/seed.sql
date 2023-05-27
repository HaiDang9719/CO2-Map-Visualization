DROP TABLE IF EXISTS co2_ppm;
DROP TABLE IF EXISTS countries_with_center;
DROP TABLE IF EXISTS gross_domestic_product_change_prediction;
DROP TABLE IF EXISTS land_temperature;
DROP TABLE IF EXISTS land_stations;
DROP TABLE IF EXISTS yearly_average_temperature_by_station;
DROP TABLE IF EXISTS land_temperature_average;
DROP TABLE IF EXISTS ocean_temperature;
DROP TABLE IF EXISTS ocean_temperature_average;
DROP TABLE If EXISTS oceans_with_center;
DROP TABLE IF EXISTS ocean_temperature_average_aggregated;
DROP TABLE IF EXISTS land_heatmap_grid;

CREATE TABLE land_heatmap_grid
(
    id          serial,
    latitude    float,
    longitude   float,
    slope       float,
    primary key (id)
);

COPY land_heatmap_grid (latitude, longitude, slope)
    FROM '/LAND_HEATMAP.csv'
    DELIMITER ','
    CSV HEADER;

CREATE TABLE co2_ppm
(
    id          serial,
    date        timestamp,
    monthly_avg float,
    trend       float,
    primary key (id)
);

COPY co2_ppm (date, monthly_avg, trend)
    FROM '/GATACD.csv'
    DELIMITER ','
    CSV HEADER;

CREATE TABLE countries_with_center AS (
    SELECT gid, iso_a3 as code, name_en, boundary, ST_ClosestPoint(boundary, ST_Centroid(boundary)) as center
    FROM countries
);

CREATE TABLE gross_domestic_product_change_prediction
(
    "Country Identifier"                      text,
    "Year"                                    timestamp,
    "Projected Gross Domestic Product Change" float
);

COPY gross_domestic_product_change_prediction ("Country Identifier", "Year", "Projected Gross Domestic Product Change")
    FROM '/GDP-RCP85-SSP5.csv'
    DELIMITER ','
    CSV HEADER;

CREATE TABLE land_stations
(
    station_id varchar,
    name       varchar,
    latitude  float,
    longitude   float,
    elevation  float,
    primary key (station_id)
);

COPY land_stations (station_id, name, latitude, longitude, elevation)
    FROM '/GHCN-D_stations.csv'
    DELIMITER ','
    CSV HEADER;

CREATE TABLE land_temperature
(
    id          serial,
    station_id  varchar,
    date        timestamp,
    temperature float,
    primary key (id),
    constraint fk_station
        foreign key (station_id)
            references land_stations (station_id)
);

COPY land_temperature (station_id, date, temperature)
    FROM '/GHCN-D.csv'
    DELIMITER ','
    CSV HEADER;

-- only pairs of (station_id, year) are accepted, where every month has a measurement
-- this avoids weirds flukes in the date, where e.g. only the winter month have been measured
CREATE TABLE yearly_average_temperature_by_station as (
    SELECT r.station_id               as "station_id",
           date_trunc('year', r.date) as "Year",
           avg(r.temperature)         as "Yearly avg Temperature"
    FROM land_temperature r
    WHERE (r.station_id, date_trunc('year', r.date)) in
          (SELECT lt.station_id as accepted_stations, date_trunc('year', lt.date) as year
           From land_temperature lt
           GROUP BY lt.station_id, date_trunc('year', lt.date)
           HAVING count(lt."date") = 12)
    GROUP BY date_trunc('year', r.date), r.station_id
    ORDER BY station_id
);

-- only select stations with 35 or more complete (JAN to DEC) years of measurements
CREATE TABLE land_temperature_average AS (
    SELECT gid as "CountryID", Year, round(avg("Average Temperature")::numeric, 1) as "Average Temperature"
    FROM (
             SELECT yearly_average_temperature_by_station."Year"        as Year,
                    st_setsrid(st_makepoint(longitude, latitude), 4326) as Location,
                    avg("Yearly avg Temperature")                       as "Average Temperature"
             FROM land_stations
                      JOIN yearly_average_temperature_by_station
                           on land_stations.station_id = yearly_average_temperature_by_station.station_id
             WHERE land_stations.station_id in (SELECT yatbs.station_id
                                                FROM yearly_average_temperature_by_station yatbs
                                                GROUP BY yatbs.station_id
                                                HAVING count(yatbs."Year") >= 35)
             GROUP BY Year, latitude, longitude
         ) AS average_temperatures
             JOIN countries ON st_contains(countries.boundary, Location)
    GROUP BY "CountryID", Year
);

CREATE TABLE ocean_temperature
(
    id          serial,
    date        timestamp,
    latitude    float,
    longitude   float,
    temperature float,
    primary key (id)
);

COPY ocean_temperature (date, latitude, longitude, temperature)
    FROM '/ICOADS.csv'
    DELIMITER ','
    CSV HEADER;

CREATE TABLE ocean_temperature_average AS (
    SELECT gid as "OceanID", Year, round(avg("Average Temperature")::numeric, 1) as "Average Temperature"
    FROM (
             SELECT date_trunc('year', date)                            as Year,
                    st_setsrid(st_makepoint(longitude, latitude), 4326) as Location,
                    avg(temperature)                                    as "Average Temperature"
             FROM ocean_temperature
             GROUP BY Year, longitude, latitude
         ) AS average_temperatures
             JOIN oceans ON st_contains(oceans.boundary, Location) AND
                            (oceans.featurecla = 'ocean' OR oceans.featurecla = 'sea' OR oceans.featurecla = 'gulf')
    GROUP BY "OceanID", Year
);

CREATE TABLE ocean_temperature_average_aggregated AS (
    SELECT Year, Location, round(avg("Average Temperature")::numeric, 1) as "Average Temperature"
    FROM (
             SELECT Year, st_snaptogrid(Location, 2.5) as Location, "Average Temperature"
             FROM (
                      SELECT date_trunc('year', date)                            as Year,
                             st_setsrid(st_makepoint(longitude, latitude), 4326) as Location,
                             avg(temperature)                                    as "Average Temperature"
                      FROM ocean_temperature
                      GROUP BY Year, longitude, latitude
                  ) as average_temperatures
         ) as aggregated_average_temperatures
    WHERE NOT exists(
            SELECT boundary
            FROM countries
            WHERE ST_Contains(boundary, Location)
        )
    GROUP BY Year, Location
);

CREATE TABLE oceans_with_center AS (
    SELECT gid, name_en, boundary, ST_ClosestPoint(boundary, ST_Centroid(boundary)) as center
    FROM oceans
);
