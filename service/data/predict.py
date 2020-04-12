from datetime import timedelta

import numpy as np
import scipy.optimize


def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) / 4 / stddev) ** 2)


def delta(iterable):
    return [iterable[i] - iterable[i - 1] for i in range(1, len(iterable))]


def avg(iterable, n=3):
    n_half = n // 2
    return [sum(iterable[i - n_half + j] for j in range(n)) / n
            for i in range(n_half, len(iterable) - n_half)]


class Predict(object):

    def __init__(self, location, prediction_days=90):
        self.location = location
        self.prediction_days = prediction_days
        self.time_sim = None
        self.original_y = None
        self.new_y = None
        self.predictions = None

    def datapoints(self):
        """Must return an iterable with values."""
        raise NotImplementedError('Implement yourself')

    def condition(self, value):
        """Must return a boolean."""
        raise NotImplementedError('Implement yourself')

    def get_value(self, i):
        """Must return a number."""
        raise NotImplementedError('Implement yourself')

    def get_data(self):
        """Returns a list of values since the moment the condition holds."""
        time, values = [], []
        for i, value in enumerate(self.datapoints()):
            if self.condition(value):
                time.append(value.moment)
                values.append(self.get_value(i))

        time_number_days = [abs(t - time[0]).days for t in time]
        return time[0], time_number_days, values

    def predict(self):
        first_day, time_number_days, cases_ref = self.get_data()

        new_x = time_number_days[1:-2]
        self.original_y = delta(cases_ref)
        self.new_y = avg(self.original_y)
        self.original_y = self.original_y[1:-1]

        (a, b, c), _ = scipy.optimize.curve_fit(
            f=gaussian,
            xdata=new_x,
            ydata=self.new_y,
        )
        self.time_sim = [first_day + timedelta(days=i) for i in range(self.prediction_days)]
        self.predictions = list(gaussian(range(self.prediction_days), a, b, c))

    def to_json(self):
        if self.time_sim is None:
            self.predict()
        return {
            'time': [t.isoformat() for t in self.time_sim],
            'values': [float(i) for i in self.original_y],
            'predictions': [float(i) for i in self.predictions],
        }


class PredictConfirmations(Predict):
    def datapoints(self):
        return self.location.confirmations

    def condition(self, value):
        return value.amount > 50

    def get_value(self, i):
        return self.location.confirmations[i].amount


class PredictDeaths(Predict):
    def datapoints(self):
        return self.location.deaths

    def condition(self, value):
        return value.amount > 20

    def get_value(self, i):
        return self.location.deaths[i].amount
