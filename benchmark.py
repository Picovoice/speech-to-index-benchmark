import argparse
import logging
import os.path

from dataset import *
from engine import *

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

CONFIDENCE_LEVELS = [0.7, 0.8, 0.9, 0.95, 0.99]

# for this test, it is assumed that search phrases have only one word without any space in between
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


class CaptionMetadata(object):
    def __init__(self, caption, phrase):
        self._start_sec = caption.start_sec
        self._end_sec = caption.end_sec
        self._content = caption.content
        self._num_occurrence = sum(
            [phrase.lower() in word for word in caption.content.strip('\n ').lower().split()])
        self._num_found = 0

    def found(self):
        self._num_found += 1

    @property
    def start_sec(self):
        return self._start_sec

    @property
    def end_sec(self):
        return self._end_sec

    @property
    def num_occurrence(self):
        return self._num_occurrence

    @property
    def num_missed(self):
        return self._num_occurrence - self._num_found


def save(file_name, results):
    path = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'results',
        f'{file_name}.dat'
    )
    with open(path, 'w') as f:
        json.dump(results, f)


def run(engine_name, dataset, search_phrases, access_key=None, bucket_name=None):
    engine_handle = Engine.create(
        Engines[engine_name], access_key=access_key, bucket_name=bucket_name)
    logging.info(f'created {str(engine_handle)} engine')

    results = dict()

    for confidence_level in CONFIDENCE_LEVELS:

        num_false_alarm = 0
        num_missed_detection = 0
        num_total_ref_occurrence = 0

        for i in range(dataset.size()):
            path, captions = dataset.get(i)

            for search_phrase in search_phrases:
                ref_matches = list()
                for caption in captions:
                    if any(search_phrase.lower() in word.lower() for word in caption.content.split()):
                        ref_matches.append(
                            CaptionMetadata(caption, search_phrase))

                for caption_metadata in ref_matches:
                    num_total_ref_occurrence += caption_metadata.num_occurrence

                engine_matches = engine_handle.search(
                    path=path,
                    search_phrase=search_phrase,
                    confidence_threshold=confidence_level
                )

                eps_sec = 1
                for match in engine_matches:
                    is_found = False
                    for caption_metadata in ref_matches:
                        if match.start_sec > (caption_metadata.start_sec - eps_sec) \
                                and match.end_sec < (caption_metadata.end_sec + eps_sec):
                            caption_metadata.found()
                            is_found = True
                            break
                    if is_found is False:
                        num_false_alarm += 1

                for caption_metadata in ref_matches:
                    num_missed_detection += caption_metadata.num_missed

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
    logging.info(
        f'loaded {str(dataset)} with {dataset.size_hours():.2f} hours of data')

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
