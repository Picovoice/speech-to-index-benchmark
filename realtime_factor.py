import argparse
import logging
import os.path
from time import time

from benchmark import save
from dataset import *
from engine import *

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)


def run_realtime_factor(dataset_folder, access_key):
    test_file = os.path.join(
        os.path.abspath(dataset_folder),
        'legacy',
        'test',
        'sph',
        'BillGates_2010.wav')
    test_file_duration_sec = 1772.03

    commands = {
        Engines.MOZILLA_DEEP_SPEECH: {
            "build": "",
            "test": f"cd resources/engines/deep_speech/ && "
                    f"./deepspeech --model deepspeech-0.9.3-models.pbmm "
                    f"--scorer deepspeech-0.9.3-models.scorer "
                    f"--audio '{test_file}'",
        },
        Engines.PICOVOICE_OCTOPUS: {
            "build": f"cd resources/engines/octopus/ && "
                     f"cmake -S demo/c/ -B demo/c/build && cmake --build demo/c/build ",
            "test": f"cd resources/engines/octopus/ && "
                    f"./demo/c/build/octopus_index_demo lib/linux/x86_64/libpv_octopus.so "
                    f"lib/common/octopus_params.pv '{access_key}' "
                    f"'{test_file}' ../../data/index.oif && "
                    f"./demo/c/build/octopus_search_demo lib/linux/x86_64/libpv_octopus.so "
                    f"lib/common/octopus_params.pv '{access_key}' index.oif 'picovoice'",
        }
    }

    results = {}
    for engine in commands.keys():
        logging.info(f"{engine.value} is processing '{test_file}'...")
        os.system(commands[engine]["build"])
        start_sec = time()
        os.system(commands[engine]["test"])
        end_sec = time()
        results[engine.value] = (end_sec - start_sec) / test_file_duration_sec

    save('REAL_TIME_FACTOR', results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_folder', type=str, required=True)
    parser.add_argument('--access_key', type=str, required=True)

    args = parser.parse_args()

    dataset = Dataset.create('tedlium', args.dataset_folder)
    logging.info(f'loaded {str(dataset)} with {dataset.size_hours():.2f} hours of data')

    run_realtime_factor(args.dataset_folder, args.access_key)


if __name__ == '__main__':
    main()
