from itertools import product
import pandas
import time

from pykep import lambert_problem, MU_SUN, DAY2SEC, AU
from pykep.orbit_plots import plot_planet, plot_lambert

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

mpl.rcParams['legend.fontsize'] = 10

def load_df(filename):
    df = pandas.read_csv(filename, header=0)
    df.columns = map(str.strip, df.columns)
    df.drop(['JDTDB', 'Unnamed: 8'], axis=1, inplace=True)
    return df


def build_column(max_time, trip_time, df_launch, df_arrive):

    col0 = pandas.Series(index=range(max_time))
    colf = pandas.Series(index=range(max_time))

    for t in range(max_time - trip_time):

        # data is in km & km/s, so we multiply by 1000 to make it m & m/s
        r0 = df_launch.loc[t, ['X', 'Y', 'Z']].astype(float) * 1000
        rf = df_arrive.loc[t + trip_time, ['X', 'Y', 'Z']].astype(float) * 1000
        v0 = df_launch.loc[t, ['VX', 'VY', 'VZ']].astype(float) * 1000
        vf = df_arrive.loc[t + trip_time, ['VX', 'VY', 'VZ']].astype(float) * 1000
        dt = float(trip_time * DAY2SEC)

        # solve the problem, l0 and lf are velocity solutions to Lambert problem
        # given in units of m/s
        sols = lambert_problem(r0, rf, dt, MU_SUN)
        l0 = sols.get_v1()[-1]
        lf = sols.get_v2()[-1]

        # remove orbital body velocities to attain net velocity differences
        d0 = l0 - v0
        df = lf - vf

        # drop square root of sum of squares into respective Series objects
        col0[t] = sum(v ** 2 for v in d0) ** 0.5 / 1000
        colf[t] = sum(v ** 2 for v in df) ** 0.5 / 1000

        """
        if t % 100 == 0:
            c = ['r', 'y', 'g', 'b']
            for n in range(sols.get_Nmax()):
                fig = plt.figure()
                axis = fig.gca(projection='3d')
                plot_lambert(sols, sol=n, color=c[n], legend=True, units=AU, ax=axis)
            plt.show()
        """

    return col0, colf

demand = ['earth', 'mars']
supply = ['ceres']
dat_file = {
    'earth': './posvel_earth.csv',
    'mars': './posvel_mars.csv',
    'ceres': './posvel_ceres.csv'
}

trip_times = range(120, 601, 30)

df = load_df(dat_file['earth'])
max_time = max(df.index) - max(trip_times)
max_time = 3000

df_DeltaV = pandas.DataFrame()
df_DeltaV['Calendar Date (TDB)'] = df['Calendar Date (TDB)']

edges = [i for i in product(demand, supply)]
edges += [i for i in product(supply, demand)]

for (launch, arrive) in edges:

    df_launch = load_df(dat_file[launch])
    df_arrive = load_df(dat_file[arrive])

    for trip_time in trip_times:
        print(launch, arrive, trip_time)
        base_name = launch[0].upper() + arrive[0].upper() + 'f' + str(trip_time)
        col0_name = base_name + '_0'
        colf_name = base_name + '_f'
        col0, colf = build_column(max_time, trip_time, df_launch, df_arrive)
        df_DeltaV[col0_name] = col0
        df_DeltaV[colf_name] = colf

df_DeltaV.to_csv('output.csv')
