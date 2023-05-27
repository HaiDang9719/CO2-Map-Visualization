import numpy as np
import math
import collections
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def predict_station(station, predicted_co2):
    co2 = []
    for year in range(1980,2021):
        co2.append(predicted_co2[year]['measured'])

    if len(station) > 1:
        temp_predictor = create_tempFromCO2_predictor(station, co2)
        station['R^2'] = round(temp_predictor[1], 5)
        station['slope'] = round(temp_predictor[0].coef_[0], 5)
        return True
    return False

def predict_global_temperature(temperature, predicted_co2):
    co2 = []
    co2_predictions = []
    for year in range(1980,2021):
        co2.append(predicted_co2[year]['measured'])
        co2_predictions.append(predicted_co2[year]['measured'])
    for year in range(2021,2031):
        co2_predictions.append(predicted_co2[year]['predicted'])

    temp_predictor = create_tempFromCO2_predictor(temperature, co2)
    predicted_temp = predict_values(predictor=temp_predictor[0], input=co2_predictions, transformer=None)

    predicted_temp_per_year = {}
    for i in range(1980,2031):
        if (i in temperature):
            predicted_temp_per_year[i] = {'measured': round(temperature[i], 2),'predicted': round(predicted_temp[i - 1980], 2)}
        else:
            predicted_temp_per_year[i] = {'predicted': round(predicted_temp[i - 1980], 2)}

    predicted_temp_per_year['R^2'] = round(temp_predictor[1], 5)
    predicted_temp_per_year['slope'] = round(temp_predictor[0].coef_[0], 5)

    return predicted_temp_per_year

def predict_ocean_heatmap(ocean_temperatures, predicted_co2):
    # use measured co2 from 1980 to 2020 and predicted co from 2021 to 2030
    co2 = []
    for year in range(1980,2021):
        co2.append(predicted_co2[year]['measured'])
    
    slope_by_location = {}
    for location, average_temperatures_and_geometry in ocean_temperatures.items():
        average_temperatures = average_temperatures_and_geometry['average_temperatures']
        location = str(average_temperatures_and_geometry['location'])
        # can't train a regressor with less than 2 data points
        if (len(average_temperatures) < 2):
            slope_by_location[location] = {"not enough measurements"}
            continue

        temp_predictor = create_ocean_tempFromCO2_predictor(average_temperatures, co2)
        
        slope_by_location[location] = round(temp_predictor[0].coef_[0], 5)
        
    return slope_by_location

def find_co2_curve(aggregated_temperatures, predicted_co2, year_max, temp_max):
    # use measured co2 from 1980 to 2020 and predicted co from 2021 to 2030
    co2 = []
    for year in range(1980,2021):
        co2.append(predicted_co2[year]['measured'])
    
    predictions_by_area = {}
    for aggregated_area in list(aggregated_temperatures.items()):
        # can't train a regressor with less than 2 data points
        if (len(aggregated_area[1]) < 2):
            predictions_by_area[aggregated_area[0]] = {"not enough measurements"}
            continue

        temp_predictor = create_tempFromCO2_predictor(aggregated_area[1], co2)
        predicted_fixed = predict_values(predictor=temp_predictor[0], input=co2, transformer=None)
        slope = temp_predictor[0].coef_[0]
        temp_2020 = predicted_fixed[len(predicted_fixed) - 1]
        co2_2020 = co2[len(co2) - 1]
        
        print(f"year_max: {year_max}")
        print(f"temp_max: {temp_max}")

        # reverse regression: for wich co2 value will we predict temp_max?
        co2_max = co2_2020 + (temp_max - temp_2020) / slope
        # saturated growth until year_max with growth rate k
        k = -1 * math.log(co2_max/(500 * (co2_max - co2_2020))) / (year_max - 2020)

        co2_predicted = []
        for year in range(1980,2021):
            co2_predicted.append(predicted_co2[year]['predicted'])
        for year in range(2021,year_max + 1):
            co2_pred = co2_max - (co2_max - co2_2020) * math.e**(-k*(year - 2020))
            co2_predicted.append(co2_pred)
            if year in predicted_co2:
                predicted_co2[year]['predicted'] = co2_pred
            else:
                predicted_co2[year] = {
                    'predicted': co2_pred
                }

        predicted_temp = predict_values(predictor=temp_predictor[0], input=co2_predicted, transformer=None)
        for year in range(1980,year_max + 1):
            print(f"year: {year}, co2: {co2_predicted[year - 1980]}")

        predicted_temp_per_year = {}
        for i in range(1980,year_max + 1):
            if (i in aggregated_area[1]):
                predicted_temp_per_year[i] = {'measured': round(aggregated_area[1][i], 2),'predicted': round(predicted_temp[i - 1980], 2)}
            else:
                predicted_temp_per_year[i] = {'predicted': round(predicted_temp[i - 1980], 2)}

        predicted_temp_per_year['R^2'] = round(temp_predictor[1], 5)
        predicted_temp_per_year['slope'] = round(temp_predictor[0].coef_[0], 5)

        predictions_by_area[aggregated_area[0]] = predicted_temp_per_year
        
        
    return predictions_by_area

def predict_aggregated_temperature(aggregated_temperatures, predicted_co2):
    # use measured co2 from 1980 to 2020 and predicted co from 2021 to 2030
    co2 = []
    co2_predictions = []
    for year in range(1980,2021):
        co2.append(predicted_co2[year]['measured'])
        co2_predictions.append(predicted_co2[year]['measured'])
    for year in range(2021,2031):
        co2_predictions.append(predicted_co2[year]['predicted'])

    predictions_by_area = {}
    for aggregated_area in list(aggregated_temperatures.items()):
        # can't train a regressor with less than 2 data points
        if (len(aggregated_area[1]) < 2):
            predictions_by_area[aggregated_area[0]] = {"not enough measurements"}
            continue

        temp_predictor = create_tempFromCO2_predictor(aggregated_area[1], co2)
        predicted_temp = predict_values(predictor=temp_predictor[0], input=co2_predictions, transformer=None)

        predicted_temp_per_year = {}
        for i in range(1980,2031):
            if (i in aggregated_area[1]):
                predicted_temp_per_year[i] = {'measured': round(aggregated_area[1][i], 2),'predicted': round(predicted_temp[i - 1980], 2)}
            else:
                predicted_temp_per_year[i] = {'predicted': round(predicted_temp[i - 1980], 2)}

        predicted_temp_per_year['R^2'] = round(temp_predictor[1], 5)
        predicted_temp_per_year['slope'] = round(temp_predictor[0].coef_[0], 5)

        predictions_by_area[aggregated_area[0]] = predicted_temp_per_year
        
        
    return predictions_by_area

def predict_co2(co2_data):
    co2_predictor = create_CO2_predictor(co2_data)
    
    predicted_co2 = predict_values(predictor=co2_predictor[0], input=range(1980,2031), transformer=co2_predictor[2])
    predicted_co2_per_year = {}
    for i in range(1980,2021):
        predicted_co2_per_year[i] = {'measured': co2_data[i],'predicted': predicted_co2[i - 1980]}

    for i in range(2021,2031):
        predicted_co2_per_year[i] = {'predicted': predicted_co2[i - 1980]}

    predicted_co2_per_year['R^2'] = round(co2_predictor[1], 5)
    predicted_co2_per_year['slope x^1'] = round(co2_predictor[0].coef_[0], 5)
    predicted_co2_per_year['slope x^2'] = round(co2_predictor[0].coef_[1], 5)

    return predicted_co2_per_year

def create_ocean_tempFromCO2_predictor(temperatures, co2):
    years = []
    temps = []

    for temp_dict in temperatures:
        temps.append(temp_dict["averageTemperature"])
        years.append(temp_dict["year"].year)

    temps = np.array(temps)

    if len(co2) != len(temps):
        filtered_co2 = []
        for year in range(1980,2021):
            if year in years:
                filtered_co2.append(co2[year-1980])
        co2 = filtered_co2
        
    # we want to predict the temperature based on the co2
    co2 = np.array(co2).reshape((-1, 1))

    # fit_intercept: calculates interception with x-axis if true (assumes 0 else)
    # normalize: normalize input data to [0,1] if true
    # copy: overwrites input arrays, reduces RAM usage if true (creates a copy if false)
    # n_jobs: number of parallel threads used, -1 for automatically
    # positive: forces the coefficient (slope) to be positive if true
    predictor = LinearRegression(fit_intercept=True, normalize=True, copy_X=True, n_jobs=-1, positive=False)
    
    # trains the predictor with the data, predict temperatures based on co2
    predictor.fit(co2, temps)
    
    # error measure R^2 based on training data, we kight display this as some kind of confidence value
    r_2 = predictor.score(co2, temps)

    return [predictor, r_2]

def create_tempFromCO2_predictor(temperatures, co2):
    ordered_data = collections.OrderedDict(sorted(temperatures.items()))
    years = list(ordered_data.keys())
    temps_yearly_avgs = list(ordered_data.values())
    temps = np.array(temps_yearly_avgs)

    if len(co2) != len(temps):
        filtered_co2 = []
        for year in range(1980,2021):
            if year in years:
                filtered_co2.append(co2[year-1980])
        co2 = filtered_co2

        
    # we want to predict the temperature based on the co2
    co2 = np.array(co2).reshape((-1, 1))

    # fit_intercept: calculates interception with x-axis if true (assumes 0 else)
    # normalize: normalize input data to [0,1] if true
    # copy: overwrites input arrays, reduces RAM usage if true (creates a copy if false)
    # n_jobs: number of parallel threads used, -1 for automatically
    # positive: forces the coefficient (slope) to be positive if true
    predictor = LinearRegression(fit_intercept=True, normalize=True, copy_X=True, n_jobs=-1, positive=False)
    
    # trains the predictor with the data, predict temperatures based on co2
    predictor.fit(co2, temps)
    
    # error measure R^2 based on training data, we kight display this as some kind of confidence value
    r_2 = predictor.score(co2, temps)

    return [predictor, r_2]

def create_CO2_predictor(co2_data):
    # we want to predict the co2 in the future based on our data
    ordered_data = collections.OrderedDict(sorted(co2_data.items()))
    years = list(ordered_data.keys())
    co2_yearly_avgs = list(ordered_data.values())
    
    n_years = len(years)
    years = np.array(years).reshape((-1, 1))
    co2 = np.array(co2_yearly_avgs)
    
    transformer = PolynomialFeatures(degree=2, include_bias=False)
    transformer.fit(years)
    years_trans = transformer.transform(years)

    predictor = LinearRegression(fit_intercept=True, normalize=True, copy_X=True, n_jobs=-1, positive=False)
    # predict co2 based on year
    predictor.fit(years_trans, co2)
    r_2 = predictor.score(years_trans, co2)
    return [predictor, r_2, transformer]

def predict_values(predictor, input, transformer=None):
    x = np.array(input).reshape((-1, 1))
    if transformer is not None:
        x = transformer.transform(x)
    return predictor.predict(x)

def get_index_for_year(temps, year):
    index = 0
    for temp_dict in temps:
        if (temp_dict["year"].year == year):
            return index
        else:
            index += 1

    return None

