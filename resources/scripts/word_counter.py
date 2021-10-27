import argparse
import os
from collections import Counter


def run(dataset_directory, filename_extension):
    c = Counter()
    trans_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dataset_directory) for f in filenames if
                   os.path.splitext(f)[1] == f'.{filename_extension}']

    for file in trans_files:
        with open(file) as f:
            c += Counter(f.read().split())

    for word, num in c.most_common():
        if len(word) > 5 and word.replace("'", '').isalpha():
            print(num, word)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', required=True)
    parser.add_argument('--extension', default='txt', required=True)

    args = parser.parse_args()

    run(args.directory, args.extension)


if __name__ == '__main__':
    main()
