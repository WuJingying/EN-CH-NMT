import json
import sys

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

if __name__ == "__main__":
    files = ['train', 'dev', 'test']
    ch_path = './data/corpus.ch'
    en_path = './data/corpus.en'
    ch_lines = []
    en_lines = []

    for file in files:
        corpus = json.load(open('./data/json/' + file + '.json', 'r'))
        for item in corpus:
            ch_lines.append(item[1] + '\n')
            en_lines.append(item[0] + '\n')

    with open(ch_path, "w",encoding='utf-8') as fch:
        fch.writelines(ch_lines)

    with open(en_path, "w",encoding='utf-8') as fen:
        fen.writelines(en_lines)

    # lines of Chinese: 252777
    print("lines of Chinese: ", len(ch_lines))
    # lines of English: 252777
    print("lines of English: ", len(en_lines))
    print("-------- Get Corpus ! --------")
