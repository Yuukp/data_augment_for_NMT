import os
import sentencepiece as spm
from tiny_tokenizer import WordTokenizer

class Tokenizer:
	def __init__(self):
		spm_model_dir = './../data/spm_model/'
		if not os.path.exists(spm_model_dir):
			os.mkdir(spm_model_dir)
		self.ja_spm_path = spm_model_dir + '/ja_spm.model'
		self.en_spm_path = spm_model_dir + '/en_spm.model'

		if os.path.exists(ja_spm_path):
			ja_sp = spm.SentencePieceProcessor()
			ja_sp.Load(ja_spm_path)
			self.ja_sp = ja_sp

		if os.path.exists(en_spm_path):
			en_sp = spm.SentencePieceProcessor()
			en_sp.Load(en_spm_path)
			self.en_sp = en_sp

	def train_sentencepiece(vocab_size, mode="ja"):
		# vocab_size = 8000,16000,32000 (ordinarily)
		input_file = './../data/{}_sentences.tsv'.format(mode)
		if os.path.exists(input_file):
			model_prefix = './../data/spm_model/{}_spm'.format(mode)
			vocab_size = str(vocab_size)
			cmd = '--input={} --model_prefix={} --vocab_size={}'.format(input_file, model_prefix, vocab_size)
			spm.SentencePieceTrainer.Train(cmd)
		else:
			print('Train data does not exist\nThe path is: ' + input_file)

	def ja_spm_tokenize(self, s):
		if os.path.exists(self.ja_spm_path):
			sp = self.ja_sp
			return [word for word in sp.EncodeAsPieces(s)[1:]]
    
	def en_spm_tokenize(self, s):
		if os.path.exists(self.en_spm_path):
			sp = self.en_sp
			return [word for word in sp.EncodeAsPieces(s)[1:]]

	#keyがpiece、valueが出てきた回数の辞書を作成
    def ja_vocab_create(self, ja_file = './../data/ja_sentences.tsv'):
        ja_vocab = {}
        f = open(ja_file)
        ja_line = f.readline()
        while(ja_line):
            if os.path.exists(self.ja_spm_path):
                sp = self.ja_sp
				tokenizer = WordTokenizer('Sentencepiece', model_path=self.ja_spm_path)
                for word in tokenizer.tokenize(ja_line.strip())[1:]:
                    if word in ja_vocab.keys():
                        ja_vocab[word] += 1
                    else:
                        ja_vocab[word] = 1
        f.close()
        return ja_vocab

    def en_vocab_create(self, en_file = './../data/en_sentences.tsv'):
        en_vocab = {}
        f = open(en_file)
        en_line = f.readline()
            for word in en_line.strip():
                if word in en_vocab.keys():
                    en_vocab[word] += 1
                else:
                    en_vocab[word] = 1
        f.close()
        return en_vocab
