import argparse
import os.path

import matplotlib.pyplot as plt

from engine import *
from benchmark import CONFIDENCE_LEVELS

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

    ave_missed_rate = list()
    colors_list = [M_COLOR, G_COLOR, PV_COLOR]
    markers_list = ['o', 's', 'D']
    engine_labels = ['Mozilla DeepSpeech', 'Google Speech-to-Text', 'Picovoice Octopus']
    for index, engine in enumerate(Engines):
        path = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'results',
            '%s-%s.dat' % (args.dataset, engine.value)
        )

        with open(path) as f:
            results = json.load(f)

        false_rate = list()
        missed_rate = list()

        for confidence_level in CONFIDENCE_LEVELS:
            false_rate.append(results[str(confidence_level)][0])
            missed_rate.append(results[str(confidence_level)][1])
        line_plot.plot(false_rate, missed_rate, label=engine.value, marker=markers_list[index], color=colors_list[index])
        ave_missed_rate.append(sum(missed_rate) / len(false_rate))

    line_plot.set_yticks(np.arange(10, 70, 10))
    line_plot.set_yticklabels(["%s%%" % str(x) for x in np.arange(10, 70, 10)])
    line_plot.set_ylabel('Missed detection ratio')
    line_plot.set_xlabel('False alarm per hour')
    line_plot.set_title('False Alarm vs Missed Detection Rate\n')
    line_plot.legend(labels=engine_labels, frameon=False)
    line_plot.axvline(1.05, linewidth=0.5, color='r', ls='-.')
    line_fig.savefig(os.path.join(os.path.dirname(__file__), 'resources', 'figs', 'false_alarm_vs_missed_detection.png'))

    color = [GREY, GREY, PV_COLOR]
    bar_plot.set_title('Average Missed Detection Rate\n')
    bar_plot.set_yticks([])
    bar_plot.bar(engine_labels, ave_missed_rate, color=color)
    for i in range(len(ave_missed_rate)):
        bar_plot.text(i - 0.1, ave_missed_rate[i] + 2, '%.1f%%' % ave_missed_rate[i], color=color[i])
    bar_fig.savefig(os.path.join(os.path.dirname(__file__), 'resources', 'figs', 'missed_detection_comparison.png'))
    plt.show()


if __name__ == '__main__':
    main()
