from read_data import read_weight, read_sleep_scores, get_songs
import matplotlib.pyplot as plt
import matplotlib
import numpy
from datetime import datetime

def smooth(values, distance):
    return smooth2(values, distance, distance)

def smooth2(values, before, after):
    return [
        sum(values[i-before : i+after+1]) / (before + after + 1)
        for i in range(before, len(values) - after)
    ]

def delta(values):
    return [values[i] - values[i - 1] for i in range(1, len(values))]

def split_on_threshold(values, threshold=0):
    return (
        numpy.ma.masked_less_equal(values, threshold - 0.05),
        numpy.ma.masked_greater_equal(values, threshold + 0.05)
    )

if __name__ == "__main__":
    # handle some weight data
    weight_times, weight = zip(*read_weight())

    weight_smoothing = 5
    smoothed_weights = smooth(weight, weight_smoothing)
    smoothed_weight_times = [datetime.fromtimestamp(x) for x in smooth(smooth(weight_times, weight_smoothing), 2)]

    weight_change = [smoothed_weights[i] - smoothed_weights[i - 1] for i in range(1, len(smoothed_weights))]

    smoothed_weight_change = smooth(weight_change, 2)

    # gain, loss = split_on_threshold(smoothed_weight_change, 0)

    # handle some sleep data
    sleep_data = read_sleep_scores()
    sleep_timestamps = [score['timestamp'] for score in sleep_data]
    sleep_scores = [int(score['overall_score']) for score in sleep_data]
    sleep_heart_rates = [int(score['resting_heart_rate']) for score in sleep_data]
    sleep_restlessnesses = [float(score['restlessness']) for score in sleep_data]

    sleep_smoothing = 3
    smoothed_sleep_timestamps = [datetime.fromtimestamp(x) for x in smooth(sleep_timestamps, sleep_smoothing)]
    smoothed_sleep_scores = smooth(sleep_scores, sleep_smoothing)
    smoothed_sleep_heart_rates = smooth(sleep_heart_rates, sleep_smoothing)
    smoothed_sleep_restlessnesses = smooth(sleep_restlessnesses, sleep_smoothing)

    # graph
    fig, axs = plt.subplots(4, figsize=(20, 10))

    # weight
    for ax in axs:
        ax.plot(smoothed_weight_times[1:], smoothed_weight_change, 'k', linewidth=0.9, linestyle=':', label='weight change')
        ax.fill_between(smoothed_weight_times[1:], smoothed_weight_change, 0, color='k', alpha=0.3)
        ax.set_ylabel('weight')
        ax.legend(loc='lower left')

    # sleep
    for i in range(len(axs)):
        twin_ax = axs[i].twinx()
        if (i == 0):
            twin_ax.plot([datetime.fromtimestamp(x) for x in smooth(weight_times, 2)], smooth(weight, 2), 'b', linewidth=2, label='total weight')
        if (i == 1):
            twin_ax.plot(smoothed_sleep_timestamps, smoothed_sleep_scores, 'b', linewidth=2, label='sleep score')
            twin_ax.set_ylabel('score')
        elif (i == 2):
            twin_ax.plot(smoothed_sleep_timestamps, smoothed_sleep_heart_rates, 'b', linewidth=2, label='sleep resting heart rate')
            twin_ax.set_ylabel('bpm')
        elif (i == 3):
            twin_ax.plot(smoothed_sleep_timestamps, smoothed_sleep_restlessnesses, 'b', linewidth=2, label='sleep restlessness')
            twin_ax.set_ylabel('restlessness')
        twin_ax.legend(loc='upper right')

    years = matplotlib.dates.YearLocator()
    months = matplotlib.dates.MonthLocator()
    year_fmt = matplotlib.dates.DateFormatter('%Y')
    month_fmt = matplotlib.dates.DateFormatter('%b')

    for ax in axs:
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(year_fmt)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(month_fmt)

    plt.xlabel('date')
    plt.show()
    plt.savefig('sleep-weight.png')
