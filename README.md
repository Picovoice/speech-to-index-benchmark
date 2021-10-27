# Speech-to-Index Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This is a minimalist and extensible framework for benchmarking different speech-to-index engines. It has been developed
and tested on Ubuntu 20.04 (x86_64) using Python3.8.

## Table of Contents

- [Speech-to-Index Benchmark](#speech-to-index-benchmark)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Data](#data)
  - [Metrics](#metrics)
    - [Missed detection and false alarm rate](#missed-detection-and-false-alarm-rate)
  - [Speech-to-Text Engines](#speech-to-text-engines)
    - [Google Speech-to-Text](#google-speech-to-text)
    - [Mozilla DeepSpeech](#mozilla-deepspeech)
    - [Picovoice Octopus](#picovoice-octopus)
  - [Usage](#usage)
  - [Results](#results)
  - [License](#license)

## Background

This framework has been developed by [Picovoice](http://picovoice.ai/) as part of the
[Octopus](https://github.com/Picovoice/octopus) project. Octopus is Picovoice's Speech-to-Index engine. It directly
indexes speech without relying on a text representation.

## Data

[TED-LIUM Release 3](https://openslr.org/51/) dataset is used for benchmarking.

## Metrics

This benchmark mainly considers two metrics: missed detection and false alarm rate

### Missed detection and false alarm rate

We measure the accuracy of the speech-to-index engines using false alarm per hour and missed detection rates. The false
alarm per hour is measured as a number of false positives in an hour. Missed detection is measured as the percentage of search phrases inside an audio file that an engine misses incorrectly.

## Speech-to-Text Engines

Since Octopus has no exact off-the-shelf counterpart, we use two well-known speech-to-text engines for comparison.

### Google Speech-to-Text

A cloud-based speech recognition engine offered by Google Cloud Platform. Find more information
[here](https://cloud.google.com/speech-to-text/).

### Mozilla DeepSpeech

[Mozilla DeepSpeech](https://github.com/mozilla/DeepSpeech) is an open-source implementation of
[Baidu's DeepSpeech](https://arxiv.org/abs/1412.5567) by Mozilla.

### Picovoice Octopus

[Octopus](https://github.com/Picovoice/cheetah) is a speech-to-index engine developed using
[Picovoice's](http://picovoice.ai/) proprietary deep learning technology, which directly indexes speech without relying
on a text representation. It works offline and is supported on a growing number of platforms including Android, iOS,
and [web](https://picovoice.ai/demos/audio-search/).

## Usage

Below is information on how to use this framework to benchmark the speech-to-text engines.

1. Make sure that you have installed DeepSpeech on your machine by following the instructions on its official pages.
2. Run the `config.py` script in order to download and unpack DeepSpeech's models
   under [resources/engines/deepspeech](/resources/engines/deepspeech).
3. Download [TED-LIUM Release 3](https://openslr.org/51/) and unpack it on your computer.
4. For running Google Speech-to-Text, you need to sign up and setup permissions /
   credentials according to its documentation. You also need to enable the 'Cloud Speech-to-Text' and 'Cloud storage' APIs
   and create a bucket for this benchmark. Running these services may incur fees.
5. For running Octopus, you need to get an `AccessKey` from the [Picovoice Console](https://picovoice.ai/console/).


Missed detection and false alarm rate can be measured by running the following command from the root of the repository:

```bash
python3 benchmark.py --engines {ENGINES} --dataset_folder {DATASET_FOLDER} --access_key {ACCESS_KEY} --google_bucket_name {GOOGLE_BUCKET_NAME}
```

where `{DATASET_FOLDER}` is the path to the folder in which the `TEDLIUM`
dataset is extracted. The valid options for the `{ENGINES}`
parameter are: `MOZILLA_DEEP_SPEECH`, `GOOGLE_SPEECH_TO_TEXT`, and `PICOVOICE_OCTOPUS`. `{ACCESS_KEY}` or `{GOOGLE_BUCKET_NAME}` should be entered as the input only if the selected engine is Octopus or Google Speech-to-text respectively.

## Results

The figure below compares the average missed detection rate of speech-to-index engines. Octopus achieves the best performance by spotting search phrases almost two times better than its closest opponent.

![](resources/figs/missed_detection_comparison.png)

The figure below shows the false alarm per hour versus the missed detection rate for different confidence levels. `Mozilla DeepSpeech` does not provide the confidence level of the result in the same way that other engines deliver. Therefore, there is only one data point for it in the plot instead of a curve.

In addition, as shown by a red line, for around 1 false alarm per hour, Octopus achieves 22% for the missed detection rate while Google Speech-to-Text acquires 30%.

![](resources/figs/false_alarm_vs_missed_detection.png)

## License

The benchmarking framework is freely available and can be used under the Apache 2.0 license.

For commercial enquiries contact us via this [form](https://picovoice.ai/contact.html).
