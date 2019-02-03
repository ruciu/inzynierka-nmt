import sys
import os
import io
import getopt
import tensorflow as tf
import collections
import random
import string
from embed import createEmbeddings

UNK = "<unk>"
SOS = "<s>"
EOS = "</s>"

def get_arguments(argv):
    data_path = ""
    output_dir = ""
    vocabulary_size = ""
    dev_size = ""
    test_size = ""

    try:
        opts, args = getopt.getopt(argv, "hp:o:v:d:t:", [
            "data_path", "out_dir_path", "vocabulary_size", "dev_size", "test_size"])
        print(args)
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                "python prepare_data.py \n \
                    -p <corpora path> \n \
                    -o <out directory> \n \
                    -v <vocabulary size> \n \
                    -d <dev set size> \n \
                    -t <test set size> "
            )

            sys.exit()
        elif opt in ("-p", "--data_path"):
            data_path = arg
        elif opt in ("-o", "--out_dir_path"):
            output_dir = arg
        elif opt in ("-v", "--vocabulary_size"):
            vocabulary_size = int(arg)
        elif opt in ("-d", "--dev_size"):
            dev_size = float(arg)
        elif opt in ("-t", "--test_size"):
            test_size = float(arg)
    print('data_path = ', data_path)
    print('output_dir = ', output_dir)
    print('vocabulary_size = ', vocabulary_size)
    print('dev_size = ', dev_size)
    print('test_size = ', test_size)

    return data_path, output_dir, vocabulary_size, dev_size, test_size

def split_data_to_train_and_validation(data_path, language, dev_size, test_size, output_dir):
    test_dir = os.path.join(output_dir, "test_{}.txt".format(language))
    dev_dir = os.path.join(output_dir, "dev_{}.txt".format(language))
    train_dir = os.path.join(output_dir, "train_{}.txt".format(language))

    test_sentences = ""
    dev_sentences = ""
    train_sentences = ""

    sentences_path = os.path.join(data_path, "sentences_{}.txt".format(language))
    file = tf.read_file(sentences_path)
    with tf.Session() as sess:
        sentences = sess.run(file).decode("utf-8").splitlines()
        for sentence in sentences:
            rand = random.random()
            if rand < dev_size:
                dev_sentences += sentence + "\n"
            elif rand < dev_size + test_size:
                test_sentences += sentence + "\n"
            else:
                train_sentences += sentence + "\n"
        with io.open(test_dir, 'w', encoding='utf8') as f:
            f.write(test_sentences)
        with io.open(dev_dir, 'w', encoding='utf8') as f:
            f.write(dev_sentences)
        with io.open(train_dir, 'w', encoding='utf8') as f:
            f.write(train_sentences)
        sess.close()

def create_vocabulary(data_path, language, vocabulary_size, output_dir):
    sentences_path = os.path.join(data_path, "sentences_{}.txt".format(language))
    file = tf.read_file(sentences_path)
    with tf.Session() as sess:
        sentences = sess.run(file).decode("utf-8").replace('\n', ' ').replace('\r', '').split()
        sess.close()
        count = [[UNK, -1], [SOS, -1], [EOS, -1]]
        count.extend(collections.Counter(sentences).most_common(vocabulary_size))
        dictionary = dict()
        for word, _ in count:
            dictionary[word] = len(dictionary)
        data = list()
        unk_count = 0
        for word in sentences:
            index = dictionary.get(word, 0)
            if index == 0:  # dictionary['UNK']
                unk_count += 1
            data.append(index)
        count[0][1] = unk_count
        vocab_path = os.path.join(output_dir, "vocab_{}.txt".format(language))
        vocab = ''
        for word in list(dictionary.keys()):
            vocab += word + "\n"
        with io.open(vocab_path, 'w', encoding='utf8') as f:
            f.write(vocab)
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    return data, count, dictionary, reversed_dictionary


def split_languages(data_path, filename):
    path = os.path.join(data_path, filename)
    (language_1, language_2) = filename[6:-4].split('-')
    language_1_sentences_path = os.path.join(data_path, "sentences_{}.txt".format(language_1))
    language_2_sentences_path = os.path.join(data_path, "sentences_{}.txt".format(language_2))
    file = tf.read_file(path)
    with tf.Session() as sess:
        sentences = sess.run(file)
        lines = sentences.splitlines()
        file1 = ""
        file2 = ""
        for line in lines:
            try:
                (language_1_sentence, language_2_sentence) = line.decode("utf-8").split("\t")
                file1 += language_1_sentence + "\n"
                file2 += language_2_sentence + "\n"
            except:
                print("Unexpected error:", sys.exc_info()[0])
        with io.open(language_1_sentences_path, 'w', encoding='utf8') as f:
            f.write(file1)
        with io.open(language_2_sentences_path, 'w', encoding='utf8') as f:
            f.write(file2)
        sess.close()
    return language_1_sentences_path, language_2_sentences_path


def clean_text(data_path, filename):
    path = os.path.join(data_path, filename)
    file = tf.read_file(path)
    with tf.Session() as sess:
        lowercase = sess.run(file).decode("utf-8").lower()
        table = str.maketrans('', '', string.punctuation)
        no_punctuation = lowercase.translate(table)
        clean_path = os.path.join(data_path, "clean_en-pl.txt")
        with io.open(clean_path, 'w', encoding='utf8') as f:
            f.write(no_punctuation)
        sess.close()

if __name__ == "__main__":
    (data_path, output_dir, vocabulary_size, dev_size, test_size) = get_arguments(sys.argv[1:])
    log_dir = os.path.join(output_dir, 'log')

    #clean_text(data_path, 'en-pl.txt')

    split_languages(data_path, 'clean_en-pl.txt')

    data, count, dictionary, reverse_dictionary = create_vocabulary(data_path, 'en', vocabulary_size, output_dir=output_dir)
    create_vocabulary(data_path, 'pl', vocabulary_size, output_dir=output_dir)

    split_data_to_train_and_validation(data_path=data_path, language='en', dev_size=dev_size, test_size=test_size, output_dir=output_dir)
    split_data_to_train_and_validation(data_path=data_path, language='pl', dev_size=dev_size, test_size=test_size, output_dir=output_dir)

    createEmbeddings(data, dictionary, reverse_dictionary, log_dir)




