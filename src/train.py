from filter import Filter
from py_t2t import PyT2T
from tokenizer import Tokenizer
from prepare_data import PrepareData
from data_augmentation import DataAugmentation

def train():
	# prepare data for sentencepiece training
	PrepareData.extract_each_sentence('./../data/taiyaku.tsv', './../data/ja_sentences.tsv', 'ja')
	PrepareData.extract_each_sentence('./../data/taiyaku.tsv', './../data/en_sentences.tsv', 'en')

	# train sentencepiece model
	Tokenizer.train_sentencepiece(32000, 'ja')

	#data augment
	da = DataAugmentation()
	da.add_aux_corpus()

	# data filtering process
	fl = Filter('./../data/taiyaku.tsv')
	fl.one_multi_filter()
	print('1st done')
	fl.src_equal_trg_filter()
	print('second done')
	fl.non_alphabet_filter(0.5)
	print('')
	fl.correct_lang_filter()
	fl.update_df()

	# prepare data for feeding to a model to make
	PrepareData.prepare_tokenized_taiyaku('./../data/tokenized_taiyaku.tsv')

	t2t = PyT2T()
	# data generate
	t2t.data_gen()
	# train phase
	t2t.train()

if __name__=='__main__':
	train()