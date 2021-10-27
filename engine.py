import json
import os
from collections import namedtuple
from enum import Enum

import numpy as np
import pvoctopus
import soundfile
from deepspeech import Model
from deepspeech import client
from google.cloud import speech
from google.cloud import storage
from google.protobuf.json_format import MessageToDict


class Engines(Enum):
    MOZILLA_DEEP_SPEECH = 'MOZILLA_DEEP_SPEECH'
    GOOGLE_SPEECH_TO_TEXT = 'GOOGLE_SPEECH_TO_TEXT'
    PICOVOICE_OCTOPUS = 'PICOVOICE_OCTOPUS'


class Engine(object):
    Match = namedtuple('Match', ['start_sec', 'end_sec'])

    def search(self, path, search_phrase, confidence_threshold):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, engine_type, **kwargs):
        if engine_type is Engines.GOOGLE_SPEECH_TO_TEXT:
            return GoogleSpeechToText(kwargs['bucket_name'])
        elif engine_type is Engines.MOZILLA_DEEP_SPEECH:
            return MozillaDeepSpeech()
        elif engine_type is Engines.PICOVOICE_OCTOPUS:
            return PicovoiceOctopus(kwargs['access_key'])
        else:
            raise ValueError(f"cannot create {cls.__name__} of type 'engine_type'")


class PicovoiceOctopus(Engine):
    def __init__(self, access_key):
        self._octopus = pvoctopus.create(
            access_key=access_key,
            library_path=pvoctopus.LIBRARY_PATH,
            model_path=pvoctopus.MODEL_PATH)

    def search(self, path, search_phrase, confidence_threshold=0.8):
        cache_path = path.replace('.wav', '.oif')
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                metadata = pvoctopus.OctopusMetadata.from_bytes(f.read())
        else:
            metadata = self._octopus.index_audio_file(os.path.abspath(path))
            with open(cache_path, 'wb') as f:
                f.write(metadata.to_bytes())

        matches = self._octopus.search(metadata, [search_phrase])
        matches_list = list()
        if len(matches) != 0:
            results = matches[str(search_phrase)]
            for result in results:
                if result.probability >= confidence_threshold:
                    match = self.Match(
                        start_sec=result.start_sec,
                        end_sec=result.end_sec
                    )
                    matches_list.append(match)

        return matches_list

    def delete(self):
        self._octopus.delete()

    def __str__(self):
        return 'Picovoice Octopus'


class GoogleSpeechToText(Engine):
    def __init__(self, bucket_name):
        self._client = speech.SpeechClient()
        self._bucket_name = bucket_name

    def search(self, path, search_phrase, confidence_threshold=0.8):
        cache_path = path.replace('.wav', '.ggl')
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                response_dict = json.load(f)
                transcripts = response_dict['results']
        else:
            self.upload_audio_to_storage(self._bucket_name, path, os.path.basename(path))
            audio = speech.RecognitionAudio(uri=f'gs://{self._bucket_name}/{os.path.basename(path)}')
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US',
                enable_word_time_offsets=True,
            )

            operation = self._client.long_running_recognize(config=config, audio=audio)
            print("Waiting for operation to complete...")
            response = operation.result(timeout=600)
            response_dict = MessageToDict(response._pb)
            transcripts = response_dict['results']
            with open(cache_path, 'w') as f:
                json.dump(response_dict, f)

        matches = list()

        for transcript in transcripts:
            confidence = transcript['alternatives'][0]['confidence']
            if confidence >= confidence_threshold:
                for word in transcript['alternatives'][0]['words']:
                    if word['word'].lower() == search_phrase.lower():
                        match = self.Match(
                            start_sec=float(word['startTime'][:-1]),
                            end_sec=float(word['endTime'][:-1])
                        )
                        matches.append(match)

        return matches

    def delete(self):
        pass

    @staticmethod
    def upload_audio_to_storage(bucket_name, source_file_name, destination_name):

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_name)
        stats = storage.Blob(bucket=bucket, name=destination_name).exists(storage_client)
        if not stats:
            blob.upload_from_filename(source_file_name)
            print(f"File {source_file_name} uploaded to {destination_name}")

    def __str__(self):
        return 'Google Speech-to-Text'


class MozillaDeepSpeech(Engine):
    def __init__(self):
        deep_speech_folder = os.path.join(os.path.dirname(__file__), 'resources', 'engines', 'deep_speech')
        acoustic_model = os.path.join(deep_speech_folder, 'deepspeech-0.9.3-models.pbmm')
        language_model = os.path.join(deep_speech_folder, 'deepspeech-0.9.3-models.scorer')

        self._model = Model(acoustic_model)
        self._model.enableExternalScorer(language_model)

    def search(self, path, search_phrase, confidence_threshold):
        cache_path = path.replace('.wav', '.mdp')
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                response_dict = json.load(f)
                words = response_dict['transcripts'][0]['words']

        else:
            pcm, sample_rate = soundfile.read(path)
            pcm = (np.iinfo(np.int16).max * pcm).astype(np.int16)
            transcript_with_metadata = self._model.sttWithMetadata(pcm)
            response_dict = json.loads(client.metadata_json_output(transcript_with_metadata))
            words = response_dict['transcripts'][0]['words']
            with open(cache_path, 'w') as f:
                json.dump(response_dict, f)

        matches = list()
        for word in words:
            if word['word'].lower() == search_phrase.lower():
                match = self.Match(
                    start_sec=word['start_time'],
                    end_sec=word['start_time'] + word['duration']
                )
                matches.append(match)

        return matches

    def delete(self):
        pass

    def __str__(self):
        return 'Mozilla DeepSpeech'
