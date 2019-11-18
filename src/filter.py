import os
import langid
import pandas as pd
import MeCab

def alphabet_rate(sentence):
	num_alphabet = len([s for s in sentence if str(s).isalpha()])
	return num_alphabet/len(sentence)

def is_correct_lang(sentence,lang):
	which_lang,_ = langid.classify(sentence)
	return True if which_lang==lang else False

ja_tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
def is_contain_repeat(sentence):
	token_info_list = ja_tagger.parse(sentence)
	token_info_list = token_info_list.split('\n')
	duplicate_list = [x for x in set(token_info_list) if token_info_list.count(x) > 1]
	return True if len(duplicate_list)>0 else False

# 対象ファイルの構成
# 英文 + '\t' + 日文 + '\n'
class Filter:
	def __init__(self, file):
		self.file = file
		self.df = pd.read_csv(file, delimiter='\t',names=['question','answer','tmp'])

	def update_df(self):
		f = open(self.file,'w')
		df = self.df
		f.write('question'+'\t'+'answer'+'\n')
		for index,row in df.iterrows():
			f.write(str(row.question).lower()+'\t'+str(row.answer).lower()+'\n')
		f.close()

	# unique parallel sentence filterとmultiple filterを兼ねる
	def one_multi_filter(self):
		df = self.df
		df = df.drop_duplicates(subset='question')
		df = df.drop_duplicates(subset='answer')
		self.df = df

	def src_equal_trg_filter(self):
		df = self.df
		df = df[df.question!=df.answer]
		self.df = df

	def non_alphabet_filter(self, threshold):
		df = self.df
		for index,row in df.iterrows():
			if alphabet_rate(row.question)<threshold:
				df.drop(index, inplace=True)
		self.df = df

	def correct_lang_filter(self):
		df = self.df
		for index,row in df.iterrows():
			if not is_correct_lang(row.question,'en') or not is_correct_lang(row.answer,'ja'):
				df.drop(index, inplace=True)
		self.df = df

	# 日本語の繰り返しを含むものだけ削除する仕様、削れ過ぎな気がする(論文にあったから実装した)
	# 英語は必要そうなら追加実装
	def repeating_token_filter(self):
		df = self.df
		for index,row in df.iterrows():
			if is_contain_repeat(row.answer):
				df.drop(index, inplace=True)
		self.df = df