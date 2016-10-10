from datetime import datetime
import argparse
import itertools
import nltk
import numpy as np
import sys

from first_sentence_generator import FirstSentenceGenerator
from rnn_theano import RNNTheano
from rnn_theano_gru import GRUTheano
from tonal_checker import TonalChecker


class PoemGenerator():
    UNKNOWN_TOKEN = '<unknown>'
    POEM_START_TOKEN = '<start_poem>'
    POEM_END_TOKEN = '<end_poem>'
    SENTENCE_START_TOKEN = '<start>'

    def __init__(self, first_sentence_generator, tonal_checker):
        self.first_sentence_generator = first_sentence_generator
        self.tonal_checker = tonal_checker

    def load_poem_data(self, data_src):
        p = []
        with open(data_src, 'r') as f:
            while True:
                h = f.readline()
                if not h:
                    break
                h = int(h)
                s = [PoemGenerator.POEM_START_TOKEN]
                for i in range(h):
                    s.append(PoemGenerator.SENTENCE_START_TOKEN)
                    s.extend(f.readline()[:-1].split())

                s.append(PoemGenerator.POEM_END_TOKEN)
                p.append(s)
            word_freq = nltk.FreqDist(itertools.chain(*p))
            vocab = word_freq.most_common(6000)
            index_to_word = [x[0] for x in vocab]
            index_to_word.append(PoemGenerator.UNKNOWN_TOKEN)
            word_to_index = dict([(w, i) for i, w in enumerate(index_to_word)])

            for i, sent in enumerate(p):
                p[i] = [w
                        if w in word_to_index else PoemGenerator.UNKNOWN_TOKEN
                        for w in sent]

            self.X_train = np.asarray(
                [[word_to_index[w] for w in sent[:-1]] for sent in p],
            )
            self.y_train = np.asarray(
                [[word_to_index[w] for w in sent[1:]] for sent in p],
            )
            self.index_to_word = index_to_word
            self.word_to_index = word_to_index
            #self.model = RNNTheano(len(index_to_word))
            self.model = GRUTheano(len(index_to_word), bptt_truncate=20)
            print(len(index_to_word))

    def train_with_sgd(self, learning_rate=0.005, nepoch=1,
                       evaluate_loss_after=5):
        model = self.model
        X_train = self.X_train
        y_train = self.y_train
        # We keep track of the losses so we can plot them later
        losses = []
        num_examples_seen = 0
        for epoch in range(nepoch):
            # TODO: Find a faster way to calc loss
            # Optionally evaluate the loss
            '''
            if (epoch % evaluate_loss_after == 0):
                loss = model.calculate_loss(X_train, y_train)
                losses.append((num_examples_seen, loss))
                time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                print("%s: Loss after num_examples_seen=%d epoch=%d: %f" %
                      (time, num_examples_seen, epoch, loss))
                # Adjust the learning rate if loss increases
                if (len(losses) > 1 and losses[-1][1] > losses[-2][1]):
                    learning_rate = learning_rate * 0.5
                    print("Setting learning rate to %f" % learning_rate)
                    sys.stdout.flush()
                    # ADDED! Saving model oarameters
            '''
            # For each training example...
            # TODO: Fix the memory problem when using more data
            #for i in range(len(y_train)):
            for i in range(5000):
                # One SGD step
                model.sgd_step(X_train[i], y_train[i], learning_rate)
                num_examples_seen += 1
                if i % 1000 == 0:
                    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    print('%s: Done %d' % (time, i))
                    sys.stdout.flush()

    def load_modal(self, model_src):
        npzfile = np.load(model_src)
        U, V, W = npzfile["U"], npzfile["V"], npzfile["W"]
        self.model.hidden_dim = U.shape[0]
        self.model.word_dim = U.shape[1]
        self.model.U.set_value(U)
        self.model.V.set_value(V)
        self.model.W.set_value(W)

        msg = 'Loaded model parameters from %s. hidden_dim=%d word_dim=%d'
        print(msg % (model_src, U.shape[0], U.shape[1]))

    def save_model(self, outfile):
        model = self.model
        U, V, W = model.U.get_value(), model.V.get_value(), model.W.get_value()
        np.savez(outfile, U=U, V=V, W=W)
        print("Saved model parameters to %s." % outfile)

    def generate(self, keywords, length=5):
        if length not in [5, 7]:
            raise AttributeError()

        word_to_index = self.word_to_index
        unknown_token_index = word_to_index[PoemGenerator.UNKNOWN_TOKEN]

        for sentence in self.first_sentence_generator.generate(keywords,
                                                               length):
            s = sentence.s.split(' ')
            prev_sent = [word_to_index.get(w, unknown_token_index)
                         for w in s]
            prev_sent = ([word_to_index[PoemGenerator.POEM_START_TOKEN],
                          word_to_index[PoemGenerator.SENTENCE_START_TOKEN]] +
                         prev_sent)
            print(prev_sent)

            for tonal_index in sentence.tonal_index_list:
                target_rhyme = None

                print(''.join(s))
                for i in range(1, 4):
                    result = self._generate_sentence(i, prev_sent,
                                                     target_rhyme, tonal_index)
                    sent, prev_sent, target_rhyme = result
                    print(''.join(sent))
                print(target_rhyme)

    def _generate_sentence(self, tar_line, prev_sent, target_rhyme,
                           target_tonal_index):
        model = self.model
        tonal_checker = self.tonal_checker
        word_to_index = self.word_to_index
        index_to_word = self.index_to_word
        forbidden_tokens = [PoemGenerator.UNKNOWN_TOKEN,
                            PoemGenerator.SENTENCE_START_TOKEN,
                            PoemGenerator.POEM_START_TOKEN,
                            PoemGenerator.POEM_END_TOKEN]

        # We start the sentence with the start token
        new_sentence = [word_to_index[PoemGenerator.SENTENCE_START_TOKEN]]
        total_sent = prev_sent[:] + new_sentence
        for i in range(5):
            next_word_probs = model.forward_propagation(total_sent)[-1]
            for x in forbidden_tokens:
                next_word_probs[word_to_index[x]] = 0

            for idx in range(len(next_word_probs)):
                tar_word = index_to_word[idx]
                can_use_word = tonal_checker.check_word
                if not can_use_word(tar_word, tar_line, i,
                                    target_model=target_tonal_index):
                    next_word_probs[idx] = 0
                if ((tar_line == 3 and
                     i == 4 and
                     not tonal_checker.is_rhyme_equal(target_rhyme,
                                                      tar_word))):
                    next_word_probs[idx] = 0
            ss = sum(next_word_probs)
            next_word_probs = [p/ss for p in next_word_probs]

            samples = np.random.multinomial(1, next_word_probs)
            sampled_word = np.argmax(samples)
            new_sentence.append(sampled_word)
            total_sent.append(sampled_word)
            if tar_line == 1 and i == 4:
                target_rhyme = index_to_word[sampled_word]

        sentence_str = [index_to_word[x] for x in new_sentence[1:]]
        return sentence_str, total_sent, target_rhyme


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate Chinese Poem.',
    )

    # Poem config
    parser.add_argument('-k', '--keywords', nargs='+', required=True)
    # TODO: implement 7 word poem
    parser.add_argument('-l', '--length', type=int, default=5, choices=[5])

    # Data
    # TODO: store poem info in the trained model
    # NOTE: we need it for word_to_index right now
    parser.add_argument('-p', '--poem', help='Poem data.', required=True)
    # TODO: Just set it in tonal checker?
    parser.add_argument('-n', '--tonal', help='Tonal data.', required=True)
    parser.add_argument('-m', '--model',
                        help='Location of trained model',
                        required=True)

    # Generator config
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--train',
                        action='store_true',
                        help='Train a new model.')

    args = parser.parse_args()

    if args.verbose:
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        print('%s: start' % time)

    first_sentence_generator = FirstSentenceGenerator()
    tonal_checker = TonalChecker(args.tonal)

    poem_generator = PoemGenerator(first_sentence_generator,
                                   tonal_checker)
    poem_generator.load_poem_data(args.poem)

    if args.verbose:
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        print('%s: loaded poem data' % time)

    if args.train:
        poem_generator.train_with_sgd()
        poem_generator.save_model(args.model)

        if args.verbose:
            time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            print('%s: trained' % time)
    else:
        poem_generator.load_modal(args.model)

    poem_generator.generate(args.keywords, args.length)

    if args.verbose:
        time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        print('%s: end' % time)
