# Countries and Oceans

The data for [countries](http://www.naturalearthdata.com/downloads/50m-cultural-vectors/) and [oceans](https://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-physical-labels/) is generated with [`shp2pgsql`](https://postgis.net/docs/using_postgis_dbmanagement.html#shp2pgsql_usage) using

```bash
shp2pgsql -s 4326 -g boundary -I -W ISO-8859-15 assets/data\ sets/raw/countries/countries.dbf > src/database/init/countries.sql
shp2pgsql -s 4326 -g boundary -I -W ISO-8859-15 assets/data\ sets/raw/oceans/oceans.dbf > src/database/init/oceans.sql
```
where `-s 4326` specifies the WGS84 coordinate systems, `-g boundary` the column to contain the boundaries, `-I` to create an index of `boundary`, and `-W ISO-8859-15` the encoding of the stored data. The command is assumed to run from the root directory of the project.
