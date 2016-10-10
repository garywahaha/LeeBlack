from constants import TONAL5, TONAL7


class TonalChecker():
    def __init__(self, src):
        self.tonal = {}
        self.rhyme = {}
        with open(src, 'r') as f:
            for line in f:
                x, tonal, rhyme = line.split()
                if x not in self.tonal:
                    self.tonal[x] = set()
                if '平' in tonal:
                    self.tonal[x].add('平')
                else:
                    self.tonal[x].add('仄')
                if x not in self.rhyme:
                    self.rhyme[x] = set()
                self.rhyme[x].add(rhyme)

    def check(self, s, target_length, target_line, tonal_index=0):
        if target_length == 5:
            target_tonal = TONAL5[tonal_index]
        else:
            target_tonal = TONAL7[tonal_index]

        for i, x in enumerate(s):
            if x not in self.tonal:
                return False
            if target_tonal[target_line][i] not in self.tonal[x]:
                return False
        return True

    def check_word(self, word, target_line, target_pos,
                   target_length=5, target_model=0):
        if target_length == 5:
            target_tonal = TONAL5[target_model]
        else:
            target_tonal = TONAL7[target_model]

        if word not in self.tonal:
            return False

        if target_tonal[target_line][target_pos] not in self.tonal[word]:
            return False
        return True

    def is_rhyme_equal(self, x, y):
        if x not in self.rhyme or y not in self.rhyme:
            return False
        return len(self.rhyme[x] & self.rhyme[y]) > 0


# data = load_data('tonal.txt')
# print(check(data, '國破山河在', [1, 1, 0, 0, 1]))
