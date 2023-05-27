import numpy as np
import math

R = 6371             # mean earth radius in kilometers
HEC = (math.pi*R)    # half earth circumference, used for normalization

# creates a 2.5° by 2.5° grid of slope values by collecting the slope
# from nearby stations and weighting them by distance, R^2 and the number of available measurements
def interpolate_grid_from_stations(stations, locations):
    # normalize the R^2 value
    max_r2 = max(station['R^2'] for station in stations.values())
    min_r2 = min(station['R^2'] for station in stations.values())
    # scale delta for desired output range [0.3333,1]
    delta = (3/2) * (max_r2 - min_r2)
    
    weighted_stations = []
    for station in list(stations.items()):
        r2 = station[1]['R^2']
        # inverse normalize to range [0.3333,1], s.t. the station with the best score (lowest R^2)
        # will have triple the weight of the station with the worst score
        # maps min_r2->1 and max_r2->1/3
        r2_norm = 1 - ((r2 - min_r2) / delta)
        # the number of complete years of measurements is the length - 2
        # because R^2 and slope are also in the list
        # in addition to that all stations, that are passed into this function
        # must have at least 2 complete years of measurements (avoids div by zero and zero weight)
        count_years = len(station[1]) - 2
        # 41 years of measurement give 41-1=40 delta
        years_norm = (count_years - 1) / (40)

        loc = locations[station[0]]
        weighted_stations.append({"weight": r2_norm * years_norm, "slope": station[1]['slope'], "lat": loc["latitude"], "lon": loc["longitude"]}) 

    grid = {}
    # create the grid    
    for y in range(-180, 180, 5):
        for x in range(-360, 360, 5):
            # desired: -90 to 90 lat in 2.5° steps
            lat = y/2
            # desired: -180 to 180 lon in 2.5° steps
            lon = x/2
            sum_slope = 0.0
            sum_weight = 0.0
            # collect and (weighted) average the data from nearby stations
            for station in weighted_stations:
                # distance in meters
                dist = haversine_distance(lat, lon, station['lat'], station['lon'])
                # inverse squared distance normalization with maximum distance (half earth circumference)
                # min dist is 0 (omitted)
                norm_dist = normalize_weight_dist(dist)
                # total weight = distance_weight * measurement_count_weight * R^2_weight
                weight = norm_dist * station['weight']
                sum_slope += station['slope'] * weight
                sum_weight += weight
            # avoid div by zero and filter out very low weight (=very low confidence) points
            if sum_weight > 20:
                grid[f"(latitude: {lat}, longitude: {lon})"] = sum_slope / sum_weight
            
    return grid

def normalize_weight_dist(dist):
    # first normalize to [0,1]
    ndist = dist / HEC
    # then normalize with an e function, that maps
    # 0.00 -> 1 (no distance, maximum weight)
    # 0.01 ~> 0.852 (1/100 of maximum dist ~60km)
    # 0.10 ~> 0.202 (1/10 of maximum dist ~600km)
    # 0.20 ~> 0.041 (2/10 of maximum dist ~1200km)
    # 0.50 ~> 0 (5/10 of maximum dist ~3000km)
    # 1.00 ~> 0 (maximum distance ~6000km, minimum weight)
    # this ensures, that very close stations have a much higher weight
    # than distant one (because there are far more distant one, than close ones)
    # on the other side, if there are no stations in the close area
    # the small weights for the more distant stations become more relevant
    # and allow a prediction/interpolation
    return math.e**(-16*ndist)

def haversine_distance(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    lambda1 = math.radians(lon1)
    lambda2 = math.radians(lon2)
    delta_phi: float = phi2 - phi1
    delta_lambda: float = lambda2 - lambda1

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def spherical_law_of_cosines(lat1, lon1, lat2, lon2):
    phi1 = lat1 * math.pi/180
    phi2 = lat2 * math.pi/180
    delta_phi = (lat2 - lat1) * math.pi/180
    delta_lambda = (lon2 - lon1) * math.pi/180
    return math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(delta_lambda)) * R