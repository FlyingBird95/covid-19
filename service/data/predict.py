from service.data.epidemic import calculate_epidemic

import scipy.optimize
from scipy import interpolate


def get_data(location):
    """
    Many thanks to https://github.com/RemiTheWarrior/epidemic-simulator for his mathematical model.
    """
    time, cases, deaths = [], [], []
    for i, confirmed in enumerate(location.confirmations):
        if confirmed.amount > 50:
            time.append(confirmed.moment)
            cases.append(location.get_people_sick(i))
            deaths.append(location.deaths[i].amount)
    time_number_days = []
    for t in time:
        time_number_days.append(abs(t - time[0]).days)
    return time, time_number_days, cases, deaths


def fit_country(location):
    """
    Many thanks to https://github.com/RemiTheWarrior/epidemic-simulator for his mathematical model.
    Don't ask me how it works.
    """

    def cost_function(x):
        (a, b, c, d, e, f) = x
        v = a * 10 ** (-b)
        K_r_0 = c * 10 ** (-d)
        K_d_0 = e * 10 ** (-f)
        time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = calculate_epidemic(
            C=0,
            v=v,
            x_n=x_n,
            y_n=y_n,
            t_final=max(time_number_days),
            K_r_0=K_r_0, K_r_minus=0,
            K_d_0=K_d_0,
            K_d_plus=0,
        )
        interp_cases = interpolate.interp1d(time_sim, cases_sim, fill_value='extrapolate')
        interp_deaths = interpolate.interp1d(time_sim, deaths_sim, fill_value='extrapolate')
        fitness = 0
        N = 0

        for i in range(len(time_number_days)):
            fitness += (abs(deaths_ref[i] - interp_deaths(time_number_days[i])) / (max(deaths_ref) + 1))
            fitness += (abs(cases_ref[i] - interp_cases(time_number_days[i])) / (max(cases_ref) + 1))
            N += 2

        fitness /= N
        return fitness

    x_n = 1e5  # initial healthy population arbitrary

    time, time_number_days, cases_ref, deaths_ref = get_data(location)
    y_n = cases_ref[0]
    x0 = (2.78, 6.08, 25, 1.9, 1, 2)
    res = scipy.optimize.minimize(cost_function, x0, method="Nelder-Mead")
    x_opt = res.x
    (a, b, c, d, e, f) = x_opt
    v = a * 10 ** (-b)
    K_r_0 = c * 10 ** (-d)
    K_d_0 = e * 10 ** (-f)
    time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = calculate_epidemic(
        C=0,
        v=v,
        x_n=x_n,
        y_n=y_n,
        t_final=90,
        K_r_0=K_r_0,
        K_r_minus=0,
        K_d_0=K_d_0,
        K_d_plus=0,
    )
    return time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim
