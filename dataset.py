import os
from collections import namedtuple

import librosa
import soundfile


class Dataset(object):
    Transcript = namedtuple('sentence', ['start_sec', 'end_sec', 'content'])

    def size(self):
        raise NotImplementedError()

    def size_hours(self):
        return sum(soundfile.read(self.get(i)[0])[0].size / (16000 * 3600) for i in range(self.size()))

    def get(self, index):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, dataset_type, root_folder):
        if dataset_type == 'tedlium':
            return TEDLIUMRelease3(root_folder)
        else:
            raise ValueError("cannot create %s of type '%s'" % (cls.__name__, dataset_type))


class TEDLIUMRelease3(Dataset):
    def __init__(self, root):
        self._data = list()

        for sub_data in ['dev', 'test']:
            talk_folder = os.path.join(root, 'legacy', sub_data, 'sph')
            transcript_folder = os.path.join(root, 'legacy', sub_data, 'stm')
            for talk in os.listdir(talk_folder):
                if talk.endswith('.sph'):
                    wav_file = talk.replace('.sph', '.wav')
                    wav_path = os.path.join(talk_folder, wav_file)
                    if not os.path.exists(wav_path):
                        pcm, sample_rate = librosa.load(os.path.join(talk_folder, talk), sr=16000)
                        soundfile.write(wav_path, pcm, sample_rate)

                    transcript_path = os.path.join(transcript_folder, talk.replace('.sph', '.stm'))
                    transcript = []
                    with open(transcript_path, 'r') as f:
                        for line in f.readlines():
                            transcript.append(
                                self.Transcript(
                                    start_sec=float(line.split()[3]),
                                    end_sec=float(line.split()[4]),
                                    content=' '.join(line.split()[6:])
                                )
                            )
                    self._data.append((wav_path, transcript))

    def size(self):
        return len(self._data)

    def get(self, index):
        return self._data[index]

    def __str__(self):
        return 'TEDLIUM'