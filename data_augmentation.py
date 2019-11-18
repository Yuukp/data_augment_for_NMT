#トレーニングデータに於けるレアな単語について、補助的なコーパスを用いてデータを水増し

from tokenizer import Tokenizer
from prepare_data import PrepareData 
import requests
from bs4 import BeautifulSoup

#freqが50未満の単語リストを作成
def rare_vocab_create(vocab_dic):
    rare_vocab = []
    for key, value in vocab_dic:
        if value < 50:
            rare_vocab.append(key)
    return rare_vocab

#weblioから例文を取得
def scraping(word, mode="en"):
    url = f'https://ejje.weblio.jp/sentence/content/{word}'
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    bs = BeautifulSoup(response.text, 'html.parser')
    qotC = bs.find_all(class_="qotC")
    taiyaku = []
    for q in qotC:
        if mode == "en":
            en = q.find(class_="qotCE").text.strip("例文帳に追加")
            ja = q.find(class_="qotCJ")
            ja.find("span").decompose()
            ja = ja.text
        elif mode == "ja":
            ja = q.find(class_="qotCJJ").text.strip("例文帳に追加")
            en = q.find(class_="qotCJE")
            en.find("span").decompose()
            en = en.text
        sentence = en + '\t' + ja  
        taiyaku.append(sentence)
    return taiyaku


class DataAugmentation:
    def __init__(self):
        self.src_vocab = Tokenizer.en_vocab_create()
        self.trg_vocab = Tokenizer.ja_vocab_create()


    def add_aux_corpus(self, file_to_read):
        src_rare_vocab = rare_vocab_create(self.src_vocab)
        trg_rare_vocab = rare_vocab_create(self.trg_vocab)
        
        #rare_vocabの単語を含む対訳を抽出
        aux_taiyaku = []
        for src in src_rare_vocab:
            aux_taiyaku.append(scraping(src, "en"))

        for trg in trg_rare_vocab:
            aux_taiyaku.append(scraping(trg, "ja"))

        aux_corpus = './../data/aux_taiyaku.tsv'
        f = open(aux_corpus, 'a')
        for s in aux_taiyaku:
            f.write(s+'\n')
        f.close()

        PrepareData.extract_each_sentence(aux_corpus, './../data/ja_aux_sentences.tsv', 'ja')
        PrepareData.extract_each_sentence(aux_corpus, './../data/en_aux_sentences.tsv', 'en')

        #aux_corpusについてもvocabを作成
        aux_src_vocab = Tokenizer.en_vocab_create('./../data/en_aux_sentences.tsv')
        aux_trg_vocab = Tokenizer.ja_vocab_create('./../data/ja_aux_sentences.tsv')

        #vocabにない、かつaux_vocabにおいてもfreq50未満の単語　が含まれている文をaux_corpusから削除
        no_use_src_vocab = rare_vocab_create(aux_src_vocab)
        no_use_trg_vocab = rare_vocab_create(aux_trg_vocab)

        for i in range(len(no_use_src_vocab)):
            if no_use_src_vocab[i] in self.src_vocab.keys():
                del no_use_src_vocab[i]

        for i in range(len(no_use_trg_vocab)):
            if no_use_trg_vocab[i] in self.trg_vocab.keys():
                del no_use_trg_vocab[i]

        f = open(aux_corpus, 'w')

        #トレーニングデータセットにaux_corpusを追加

