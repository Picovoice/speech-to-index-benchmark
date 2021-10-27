import argparse
import os.path

import matplotlib.pyplot as plt

from engine import *
from benchmark import CONFIDENCE_LEVELS
import numpy as np

GREY = (100 / 255, 100 / 255, 100 / 255)
G_COLOR = (0, 153 / 255, 37 / 255)
M_COLOR = (255 / 255, 102 / 255, 17 / 255)
PV_COLOR = (55 / 255, 125 / 255, 255 / 255)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()

    line_fig, line_plot = plt.subplots()
    for spine in plt.gca().spines.values():
        if spine.spine_type != 'bottom' and spine.spine_type != 'left':
            spine.set_visible(False)

    bar_fig, bar_plot = plt.subplots()
    for spine in plt.gca().spines.values():
        if spine.spine_type != 'bottom':
            spine.set_visible(False)

    max_missed_rate = list()
    min_missed_rate = list()
    colors_list = [M_COLOR, G_COLOR, PV_COLOR]
    markers_list = ['o', 's', 'D']
    engines = ['MOZILLA_DEEP_SPEECH', 'GOOGLE_SPEECH_TO_TEXT', 'PICOVOICE_OCTOPUS']
    engine_labels = ['Mozilla DeepSpeech', 'Google Speech-to-Text', 'Picovoice Octopus']
    for index, engine in enumerate(engines):
        path = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'results',
            '%s-%s.dat' % (args.dataset, engine)
        )

        with open(path) as f:
            results = json.load(f)

        false_rate = list()
        missed_rate = list()
        for confidence_level in CONFIDENCE_LEVELS:
            false_rate.append(results[str(confidence_level)][0])
            missed_rate.append(results[str(confidence_level)][1])
        line_plot.plot(false_rate, missed_rate, label=engine, marker=markers_list[index], color=colors_list[index])
        print(missed_rate)
        max_missed_rate.append(max(missed_rate))
        min_missed_rate.append(min(missed_rate))

    line_plot.set_yticks(np.arange(10, 70, 10))
    line_plot.set_yticklabels(["%s%%" % str(x) for x in np.arange(10, 70, 10)])
    line_plot.set_ylabel('Missed detection ratio')
    line_plot.set_xlabel('False alarm per hour')
    line_plot.set_title('False Alarm vs Missed Detection Rate\n')
    line_plot.legend(labels=engine_labels, frameon=False)
    line_plot.axvline(1.05, linewidth=0.5, color='r', ls='-.')
    line_fig.savefig(os.path.join(os.path.dirname(__file__), 'resources', 'figs', 'false_alarm_vs_missed_detection.png'))

    bar_plot.set_title('Ranges for the missed detection rates\n')
    bar_plot.set_yticks([])
    bar_plot.set_xticks([0, 1, 2])
    bar_plot.set_xticklabels(engine_labels)
    bar_plot.set_ylim(0, 70)
    for index, engine in enumerate(engine_labels):
        mean = (max_missed_rate[index] + min_missed_rate[index]) / 2
        error = (max_missed_rate[index] - min_missed_rate[index] + 2) / 2
        bar_plot.errorbar(
            index,
            mean,
            yerr=error,
            fmt='o',
            color=colors_list[index],
            ecolor=colors_list[index],
            elinewidth=3,
            capsize=10
        )
        bar_plot.text(index - 0.1, max_missed_rate[index] + 2, '%.1f%%' % max_missed_rate[index], color=colors_list[index])
        bar_plot.text(index - 0.1, min_missed_rate[index] - 4, '%.1f%%' % min_missed_rate[index],
                      color=colors_list[index])

    bar_fig.savefig(os.path.join(os.path.dirname(__file__), 'resources', 'figs', 'missed_detection_comparison.png'))

    rtf_result_path = os.path.join(os.path.dirname(__file__), 'resources', 'results', 'REAL_TIME_FACTOR.dat')
    if os.path.isfile(rtf_result_path):
        color = [GREY, PV_COLOR]
        engine_labels = ['Mozilla DeepSpeech', 'Picovoice Octopus']
        bar_fig_rtf, bar_plot_rtf = plt.subplots()
        for spine in plt.gca().spines.values():
            if spine.spine_type != 'bottom':
                spine.set_visible(False)

        with open(rtf_result_path) as f:
            results = json.load(f)

        rtf_list = [element * 60 for element in results.values()]
        bar_plot_rtf.set_title('Process time for an hour of audio\n')
        bar_plot_rtf.set_yticks([])
        bar_plot_rtf.bar(engine_labels, rtf_list, color=color)
        for i in range(len(rtf_list)):
            bar_plot_rtf.text(i - 0.1, rtf_list[i] + 2, '%.1f min' % rtf_list[i], color=color[i])
        bar_fig_rtf.savefig(os.path.join(os.path.dirname(__file__), 'resources', 'figs', 'realtime_factor_comparison.png'))
    plt.show()


if __name__ == '__main__':
    main()
