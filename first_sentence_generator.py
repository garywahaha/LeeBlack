from itertools import permutations
from subprocess import Popen, PIPE
import argparse

from tonal_checker import TonalChecker


# TODO: so ugly... refactor this class
class KeywordsLoader():
    @staticmethod
    def _load_key_group(f, result):
        key_group = f.readline()[:-1]
        num_key = int(f.readline())

        if key_group not in result:
            result[key_group] = set()

        for i in range(num_key):
            keyword = f.readline()[:-1]
            result[key_group].add(keyword)

        # TODO: fix this bug in keywords.txt
        if not num_key:
            f.readline()

    @staticmethod
    def _load_key_class(f, result):
        f.readline()  # TODO: handle key_class
        num_group = int(f.readline())
        for i in range(num_group):
            KeywordsLoader._load_key_group(f, result)

    @staticmethod
    def load_data(src):
        result = {}

        with open(src, 'r') as f:
            num_class = int(f.readline())
            for i in range(num_class):
                KeywordsLoader._load_key_class(f, result)

        return result


class FirstSentence():
    def __init__(self, s):
        self.s = s
        self.score = 0
        self.tonal_index_list = []

    def __lt__(self, other):
        return self.score < other.score

    def set_score(self, score):
        self.score = score

    def add_tonal(self, tonal):
        self.tonal_index_list.append(tonal)


class FirstSentenceGenerator():
    def __init__(self, keywords_src='keywords.txt'):
        self.keywords_data = KeywordsLoader.load_data(keywords_src)
        self.tonal_checker = TonalChecker('tonal.txt')

    def permute(self, keywords, length):
        combined_set = set()
        for x in keywords:
            combined_set |= self.keywords_data[x]

        # TODO: gen by smarter way
        for x in range(1, 3):
            for gen_line in permutations(combined_set, x):
                target = ''.join(gen_line)
                if len(target) == length:
                    yield ' '.join(target)

    def generate(self, keywords, length):
        tonal_checker = self.tonal_checker

        result = []
        with open('.first.tmp', 'w') as f:
            for s in self.permute(keywords, length):
                first_sentence = FirstSentence(s)
                for i in range(4):
                    if tonal_checker.check(s.split(' '), length, 0, i):
                        first_sentence.add_tonal(i)

                if len(first_sentence.tonal_index_list) > 0:
                    print(s, file=f)
                    result.append(first_sentence)

        p = Popen(['./rnnlm',
                   '-rnnlm', 'first_1_1458.model',
                   '-test', '.first.tmp',
                   '-debug', '0',
                   '-nbest'],
                  stdout=PIPE)
        output, err = p.communicate()
        p.wait()

        pos = 0
        for score in output.decode().split('\n')[:-1]:
            result[pos].set_score(float(score))
            pos += 1

        result.sort(reverse=True)
        for x in result[:10]:
            yield x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Permute first sentence by keywords',
    )

    parser.add_argument('input')
    parser.add_argument('-k', '--keywords', nargs='+')
    parser.add_argument('-l', '--length', type=int, default=5, choices=[5, 7])

    args = parser.parse_args()

    g = FirstSentenceGenerator(args.input)
    g.generate(args.keywords, args.length)
    exit()

    data = KeywordsLoader.load_data(args.input)
    combined_set = set()
    for x in args.keywords:
        combined_set |= data[x]

    # TODO: gen by smarter way
    result = []
    with open('.first.tmp', 'w') as f:
        for x in range(1, 3):
            for gen_line in permutations(combined_set, x):
                target = ''.join(gen_line)
                if len(target) == args.length:
                    s = ' '.join(target)
                    result.append(FirstSentence(s))
                    print(s, file=f)

    p = Popen(['./rnnlm',
               '-rnnlm', 'first.model',
               '-test', '.first.tmp',
               '-debug', '0',
               '-nbest'],
              stdout=PIPE)
    output, err = p.communicate()
    exit_code = p.wait()

    pos = 0
    for score in output.decode().split('\n')[:-1]:
        result[pos].set_score(float(score))
        pos += 1

    result.sort(reverse=True)
    for x in result[:10]:
        print(x.s, x.score)
