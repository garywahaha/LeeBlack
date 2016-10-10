with open('tang_poems_1_1458.txt', 'r') as f, open('poem_1_1458.train', 'w') as o:
    while True:
        title = f.readline()
        if not title:
            break
        author = f.readline()
        h, w = [int(x) for x in f.readline().split()]
        #print(h, file=o)
        for i in range(h):
            s = f.readline()
            print(' '.join(s[:-1]), file=o)
        print('done %s' % title)
