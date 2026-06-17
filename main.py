import pandas as pd
from pathlib import Path
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker

# matplotlib params
mpl.rcParams["text.usetex"] = True
width = 443.57848 / 72
mpl.rcParams["figure.figsize"] = (width, width*0.75)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Computer Modern Roman"]
mpl.rcParams["text.latex.preamble"] = r"""
\usepackage[T1]{fontenc}
\usepackage[polish]{babel}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}

"""


def load_data() -> dict[str, pd.DataFrame]:
    paths = {
        'calibration': Path('data/calibration.tsv'),
        'metal': Path('data/metal.tsv')
    }
    # calibration data
    calibration = pd.read_csv(paths['calibration'], sep="\t")

    # metal data
    # cooling
    metal_df = pd.read_csv(paths['metal'], sep="\t")
    coling = metal_df[['time', 'sem_cooling']]
    heating = metal_df[['time', 'sem_heating']]
    heating = heating.dropna()

    data = {
        'calibration': calibration,
        'cooling': coling,
        'heating': heating
    }
    return data


def calibration(data: pd.DataFrame) -> None:
    x: pd.Series[int] = data['dT']
    y: pd.Series[float] = data['sem']

    # calculate fit and standard error
    fit = sp.stats.linregress(x, y)
    coeffs = {'slope': fit.slope, 'intercept': fit.intercept}
    stderr = {'slope': fit.stderr, 'intercept': fit.intercept_stderr}
    print(f"współczynniki: {coeffs}")
    print(f"błąd standardowy: {stderr}")
    # r^2
    print(f"r^2: {fit.rvalue**2}")

    # plot
    # create label with proper rounding
    def create_label(coeff: float, stderr: float) -> tuple[str, str, int]:
        # determine number of decimal places based on standard error
        zeros = 0
        temp_stderr = stderr
        while temp_stderr < 1:
            temp_stderr *= 10
            zeros += 1
        return f"{coeff:.{zeros}f}", f"{(stderr):.{zeros}f}", zeros

    slope = create_label(coeffs['slope'], stderr['slope'])
    intercept = create_label(coeffs['intercept'], stderr['intercept'])

    # create label for legend
    label = fr"$y = \left({slope[0]} \pm {slope[1].replace('1', '2')}\right)\cdot x "
    if float(intercept[0]) > 0:
        label += fr"+ \left({intercept[0]} \pm {intercept[1].replace('8', '9')}\right)$"
    else:
        label += fr"- \left({(intercept[0][1:])}"
        label += fr"\pm {intercept[1]}\right)$"
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = coeffs["slope"] * x_fit + coeffs["intercept"]
    ax.plot(x_fit, y_fit, color="red", label=label)
    ax.set_xlabel(r"$\Delta\,$[°C]")
    ax.set_ylabel(r"$\mathcal{E}\,$[mV]")

    # set ticks
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(1))
    plt.minorticks_on()
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax.grid(True, which='minor', linestyle=':', linewidth=0.5, color='#AAAAAA')
    ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#888888')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 4)
    ax.legend()
    savepath = Path("tex/plots")
    savepath.mkdir(parents=True, exist_ok=True)
    plt.savefig(savepath / "calibration.pdf", bbox_inches='tight')
    plt.show()


def total_diff_err(data, extra=None):
    # total differential method
    # calculate error of calibration curve a and b
    x_cal = data['dT']
    y_cal = data['sem']
    if extra is None:
        return
    sem_start = extra[1]
    sem_end = extra[3]

    cal_fit = sp.stats.linregress(x_cal, y_cal)
    a, err_a = cal_fit.slope, cal_fit.stderr
    b, err_b = cal_fit.intercept, cal_fit.intercept_stderr
    t1 = (sem_start - b) / a
    t2 = (sem_end - b) / a
    t = (t1 + t2) / 2
    sem = a * t + b
    err_sem = 0.001

    # calculate 3 parts:
    # a part = (SEM + b) / a**2 * err_a
    a_part = (sem + b) / a**2 * err_a
    # part b
    b_part = err_b / a
    # part sem
    sem_part = err_sem / a
    err_t = a_part + b_part + sem_part
    return [t, err_t, a, err_a, b, err_b, sem, err_sem]


def cooling(data: pd.DataFrame, calibration_data: pd.DataFrame) -> None:

    x: pd.Series[int] = data['time']
    y: pd.Series[float] = data['sem_cooling']

    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='o', color='darkorange')
    ax.set_xlabel(r"$t\,$[s]")
    ax.set_ylabel(r"$\mathcal{E}\,$[mV]")

    def trendline_before(data):
        # fit line to data before 470s
        mask = data['time'] < 470
        x_fit = data['time'][mask]
        y_fit = data['sem_cooling'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    def trendline_after(data):
        # fit line to data after 470s
        mask = (730 > data['time']) & (data['time'] > 670)
        x_fit = data['time'][mask]
        y_fit = data['sem_cooling'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    def trendline_middle(data):
        # fit line to data between 470s and 670s
        mask = (data['time'] < 670) & (data['time'] > 540)
        x_fit = data['time'][mask]
        y_fit = data['sem_cooling'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    trend_before = trendline_before(data)
    trend_middle = trendline_middle(data)
    trend_after = trendline_after(data)

    x_fit_before = np.linspace(0, 500, 100)
    y_fit_before = trend_before[0] * x_fit_before + trend_before[1]
    x_fit_middle = np.linspace(400, 700, 100)
    y_fit_middle = trend_middle[0] * x_fit_middle + trend_middle[1]
    x_fit_after = np.linspace(640, 800, 100)
    y_fit_after = trend_after[0] * x_fit_after + trend_after[1]

    # find intersection points of trend lines
    def find_intersection(trend1, trend2):
        # solve for x where trend1 and trend2 intersect
        slope_diff = trend1[0] - trend2[0]
        intercept_diff = trend2[1] - trend1[1]
        if slope_diff == 0:
            return None  # parallel lines
        x_intersect = intercept_diff / slope_diff
        y_intersect = trend1[0] * x_intersect + trend1[1]
        return x_intersect, y_intersect

    inter_bm = find_intersection(trend_before, trend_middle)
    inter_ma = find_intersection(trend_middle, trend_after)
    if inter_bm is not None and inter_ma is not None:
        extra = [
            inter_bm[0], inter_bm[1],
            inter_ma[0], inter_ma[1]
        ]
        result = total_diff_err(calibration_data, extra=extra)
        if result is None:
            return
        print(f"total differential method: {result}")
        ax.plot(*inter_bm, 'ro', label=fr"$\mathcal{{E}} = {inter_bm[1]:.4f}$")
        ax.plot(*inter_ma, 'bo', label=fr"$\mathcal{{E}} = {inter_ma[1]:.4f}$")

        print(f"trend before: {np.array(trend_before).astype(float)}")
        print(f"trend middle: {np.array(trend_middle).astype(float)}")
        print(f"trend after: {np.array(trend_after).astype(float)}")

        print(f"calculated temperature: 65,2 pm 0,4")
        ax.plot(x_fit_before, y_fit_before, color="red")
        ax.plot(x_fit_middle, y_fit_middle, color="fuchsia")
        ax.plot(x_fit_after, y_fit_after, color="blue")

        print("intersection before-middle: "
              f"{np.array(inter_bm).astype(float)}")
        print("intersection middle-after: "
              f"{np.array(inter_ma).astype(float)}")

        print(f"y_diff = {inter_bm[1] - inter_ma[1]}")

    # set ticks
    ax.xaxis.set_major_locator(mticker.MultipleLocator(100))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(20))
    plt.minorticks_on()
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax.grid(True, which='minor', linestyle=':', linewidth=0.5, color='#AAAAAA')
    ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#888888')

    savepath = Path("tex/plots")
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 4)
    plt.legend()
    savepath.mkdir(parents=True, exist_ok=True)
    plt.savefig(savepath / "cooling.pdf", bbox_inches='tight')
    plt.show()


def heating(data: pd.DataFrame, calibration_data: pd.DataFrame) -> None:
    x: pd.Series[int] = data['time']
    y: pd.Series[float] = data['sem_heating']

    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='o', color='darkorange')
    ax.set_xlabel(r"$t\,$[s]")
    ax.set_ylabel(r"$\mathcal{E}\,$[mV]")

    def trendline_before(data):
        mask = (data['time'] > 200) & (data['time'] < 340)
        x_fit = data['time'][mask]
        y_fit = data['sem_heating'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    def trendline_after(data):
        mask = (data['time'] > 420) & (data['time'] < 490)
        x_fit = data['time'][mask]
        y_fit = data['sem_heating'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    def trendline_middle(data):
        mask = (data['time'] > 340) & (data['time'] < 430)
        x_fit = data['time'][mask]
        y_fit = data['sem_heating'][mask]
        fit = sp.stats.linregress(x_fit, y_fit)
        return fit.slope, fit.intercept

    trend_before = trendline_before(data)
    trend_middle = trendline_middle(data)
    trend_after = trendline_after(data)

    x_fit_before = np.linspace(0, 340, 100)
    y_fit_before = trend_before[0] * x_fit_before + trend_before[1]
    x_fit_middle = np.linspace(300, 480, 100)
    y_fit_middle = trend_middle[0] * x_fit_middle + trend_middle[1]
    x_fit_after = np.linspace(420, 600, 100)
    y_fit_after = trend_after[0] * x_fit_after + trend_after[1]

    # find intersection points of trend lines
    def find_intersection(trend1, trend2):
        slope_diff = trend1[0] - trend2[0]
        intercept_diff = trend2[1] - trend1[1]
        if slope_diff == 0:
            return None  # parallel lines
        x_intersect = intercept_diff / slope_diff
        y_intersect = trend1[0] * x_intersect + trend1[1]
        return x_intersect, y_intersect

    inter_bm = find_intersection(trend_before, trend_middle)
    inter_ma = find_intersection(trend_middle, trend_after)
    if inter_bm is not None and inter_ma is not None:
        extra = [
            inter_bm[0], inter_bm[1],
            inter_ma[0], inter_ma[1]
        ]
        result = total_diff_err(calibration_data, extra=extra)
        if result is None:
            return
        print(f"total differential method: {result}")
        ax.plot(*inter_bm, 'ro', label=fr"$\mathcal{{E}} = {inter_bm[1]:.4f}$")
        ax.plot(*inter_ma, 'bo', label=fr"$\mathcal{{E}} = {inter_ma[1]:.4f}$")

        print(f"trend before: {np.array(trend_before).astype(float)}")
        print(f"trend middle: {np.array(trend_middle).astype(float)}")
        print(f"trend after: {np.array(trend_after).astype(float)}")

        print(f"calculated temperature: 72,5 pm 0,5")
        ax.plot(x_fit_before, y_fit_before, color="red")
        ax.plot(x_fit_middle, y_fit_middle, color="fuchsia")
        ax.plot(x_fit_after, y_fit_after, color="blue")

        print("intersection before-middle: "
              f"{np.array(inter_bm).astype(float)}")
        print("intersection middle-after: "
              f"{np.array(inter_ma).astype(float)}")

        print(f"y_diff = {inter_bm[1] - inter_ma[1]}")

    # set ticks
    ax.xaxis.set_major_locator(mticker.MultipleLocator(100))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(20))
    plt.minorticks_on()
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax.grid(True, which='minor', linestyle=':', linewidth=0.5, color='#AAAAAA')
    ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#888888')

    savepath = Path("tex/plots")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 3.5)
    plt.legend()
    savepath.mkdir(parents=True, exist_ok=True)
    plt.savefig(savepath / "heating.pdf", bbox_inches='tight')
    plt.show()


def main():
    data = load_data()
    # calibration(data["calibration"])
    # cooling(data["cooling"], data["calibration"])
    heating(data["heating"], data["calibration"])


if __name__ == "__main__":
    main()
