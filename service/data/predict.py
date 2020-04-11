from datetime import timedelta

import numpy as np
import scipy.optimize


def get_data(datapoints, condition, get_value):
    """
    Returns a list of values since the moment the condition holds.

    :args datapoints: iterable
    :arg condition: lambda with one arg that returns a bool.
    :arg get_value: the value returned for this the condition holds, also a lambda with one arg.
    """
    time, values = [],  []
    for i, value in enumerate(datapoints):
        if condition(value):
            time.append(value.moment)
            values.append(get_value(i))

    time_number_days = [abs(t - time[0]).days for t in time]
    return time[0], time_number_days, values


def logistic(x, a, c, d):
    """Fit a logistic function."""
    return a / (1. + np.exp(-c * (x - d)))


def fit_predict(datapoints, condition, get_value, prediction_days):
    first_day, time_number_days, cases_ref = get_data(
        datapoints=datapoints,
        condition=condition,
        get_value=get_value,
    )
    popt, pcov = scipy.optimize.curve_fit(logistic, time_number_days, cases_ref, maxfev=100000)
    time_sim = [first_day + timedelta(days=i) for i in range(prediction_days)]
    return time_sim, cases_ref, list(logistic(range(prediction_days), *popt))
