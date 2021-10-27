import logging
import os
import shutil

import requests

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)


def download_file(url, name, folder):
    file_path = os.path.join(folder, name)
    if not os.path.isfile(file_path):
        print(f"Downloading '{file_path}'...")
        with requests.get(url, stream=True) as r:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)


def deep_speech_setup(engines_folder):
    deep_speech_folder = os.path.join(engines_folder, 'deep_speech')
    acoustic_model_name = 'deepspeech-0.9.3-models.pbmm'
    acoustic_model_url = f'https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/{acoustic_model_name}'
    download_file(acoustic_model_url, acoustic_model_name, deep_speech_folder)
    language_model_name = 'deepspeech-0.9.3-models.scorer'
    language_model_url = f'https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/{language_model_name}'
    download_file(language_model_url, language_model_name, deep_speech_folder)


def main():
    engines_folder = os.path.join(os.path.dirname(__file__), 'resources', 'engines')

    logging.info('Setting up DeepSpeech engine...')
    deep_speech_setup(engines_folder)
    logging.info('Done setting up DeepSpeech engine...')


if __name__ == '__main__':
    main()
