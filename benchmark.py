import argparse
import logging
import os.path

from dataset import *
from engine import *

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

CONFIDENCE_LEVELS = [0.7, 0.8, 0.9, 0.95, 0.99]

SEARCH_PHRASES = [
    'amazon',
    'america',
    'anthropology',
    'bacteria',
    'beethoven',
    'blizzard'
    'california',
    'canada',
    'chromosome',
    'colonoscopy',
    'computer',
    'david',
    'environment',
    'flickr',
    'google',
    'manhattan',
    'microsoft',
    'molecule',
    'nathaniel',
    'pharmaceutical',
    'phytoplankton',
    'satellite',
    'titanic',
    'twitter',
    'uranium',
    'virginia',
    'warcraft',
    'wikipedia',
]


class MatchedResult:
    def __init__(self, match, phrase):
        self._start_sec = match.start_sec
        self._end_sec = match.end_sec
        self._content = match.content
        self._num_occurrence = sum([phrase.lower() in word for word in match.content.strip('\n ').lower().split()])

    def matched(self):
        self._num_occurrence -= 1

    @property
    def start_sec(self):
        return self._start_sec

    @property
    def end_sec(self):
        return self._end_sec

    @property
    def num_occurrence(self):
        return self._num_occurrence


def save(file_name, results):
    path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'results',
        f'{file_name}.dat'
    )
    with open(path, 'w') as f:
        json.dump(results, f)


def run(engine_name, dataset, search_phrases, access_key='', bucket_name=''):
    engine_handle = Engine.create(Engines[engine_name], access_key=access_key, bucket_name=bucket_name)
    logging.info('created %s engine' % str(engine_handle))

    results = dict()

    for confidence_level in CONFIDENCE_LEVELS:

        num_false_alarm = 0
        num_missed_detection = 0
        num_total_ref_occurrence = 0

        for i in range(dataset.size()):
            path, ref_transcript = dataset.get(i)

            for search_phrase in search_phrases:
                ref_matches = list()
                for sentence in ref_transcript:
                    if any(search_phrase.lower() in word.lower() for word in sentence.content.split()):
                        ref_matches.append(MatchedResult(sentence, search_phrase))

                for ref_match in ref_matches:
                    num_total_ref_occurrence += ref_match.num_occurrence

                matches = engine_handle.search(
                    path=path,
                    search_phrase=search_phrase,
                    confidence_threshold=confidence_level
                )

                for match in matches:
                    matched = [occurrence for occurrence in ref_matches if
                               match.start_sec > (occurrence.start_sec - 1) and match.end_sec < (
                                       occurrence.end_sec + 1)]
                    if len(matched) > 0:
                        matched[0].matched()
                    else:
                        num_false_alarm += 1

                for ref_match in ref_matches:
                    num_missed_detection += ref_match.num_occurrence

        false_alarm_per_hour = float(num_false_alarm) / dataset.size_hours()
        if num_total_ref_occurrence == 0:
            missed_detection_rate = 0
        else:
            missed_detection_rate = 100 * float(num_missed_detection) / num_total_ref_occurrence
        results[confidence_level] = [false_alarm_per_hour, missed_detection_rate]
        logging.info(f'[{engine_name} - {confidence_level:.2f}] false alarm per hour : {false_alarm_per_hour:.2f}')
        logging.info(f'[{engine_name} - {confidence_level:.2f}] missed detection rate : {missed_detection_rate:.2f}\n')

    engine_handle.delete()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--engines',
        nargs='+',
        choices=[engine.value for engine in Engines],
        default=[engine.value for engine in Engines]
    )
    parser.add_argument('--dataset_folder', type=str, required=True)
    parser.add_argument('--access_key', type=str)
    parser.add_argument('--google_bucket_name', type=str)

    args = parser.parse_args()

    if Engines.PICOVOICE_OCTOPUS.value in args.engines and args.access_key is None:
        print('Picovoice Octopus engine requires an AccessKey to perform the tests')
        exit(1)

    if Engines.GOOGLE_SPEECH_TO_TEXT.value in args.engines and args.google_bucket_name is None:
        print('Google Speech-to-Text engine requires a Google Storage bucket name to perform the tests')
        exit(1)

    dataset = Dataset.create('tedlium', args.dataset_folder)
    logging.info(f'loaded {str(dataset)} with {dataset.size_hours():.2f} hours of data')

    for engine in args.engines:
        results = run(
            engine_name=engine,
            dataset=dataset,
            search_phrases=SEARCH_PHRASES,
            access_key=args.access_key,
            bucket_name=args.google_bucket_name
        )
        save(file_name=f'{str(dataset)}-{engine}', results=results)


if __name__ == '__main__':
    main()
