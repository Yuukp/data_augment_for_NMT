import os
import re
import sys
import pandas as pd
import xml.etree.ElementTree as ET
from langdetect import detect

from tokenizer import Tokenizer


en_claims_index_pattern = r'\[[0-9]{4}\]'
ja_claims_index_pattern = r'【[０-９]{4}】'
en_description_index_pattern = r'[0-9]+\.'
ja_description_index_pattern = r'[0-9]+\.'

class PrepareData:
	def first_process(file_to_write):
		f = open(file_to_write,'a')
		f.write('question'+'\t'+'answer'+'\n')
		f.close()

	def prepare_ib_data(file_to_write):
		f = open(file_to_write,'a')
		num = 0
		# IBからのデータの処理
		IB_data_path = './../data/IB/'
		for folder in os.listdir(IB_data_path):
			if 'IB' in folder:
				folder_path = IB_data_path + folder
				for sub_folder in os.listdir(folder_path):
					if not 'DS_Store' in sub_folder:
						sub_folder_path = folder_path + '/' + sub_folder
						for file in os.listdir(sub_folder_path):
							file_path = sub_folder_path + '/' + file
							if 'US' in file:
								df = pd.read_csv(file_path)
								for index, row in df.iterrows():
									print(num)
									en_raw_text = row[0]
									ja_raw_text = row[1]
									if isinstance(en_raw_text,str) and isinstance(ja_raw_text,str) and not '\\' in en_raw_text:
										# matchは先頭マッチでsearchが途中マッチ
										if re.match(en_claims_index_pattern,en_raw_text) and re.match(ja_claims_index_pattern,ja_raw_text):
											es_text = (re.sub(en_claims_index_pattern,'',en_raw_text)).strip()
											ja_text = (re.sub(ja_claims_index_pattern,'',ja_raw_text)).strip()
											if es_text.count('. ')-es_text.count('FIG. ')-es_text.count('FIGS. ')==ja_text.count('。'):
												ja_list = ja_text.split('。')
												pre_es_list = es_text.split('. ')
												es_list = []
												tmp = ''
												for es in pre_es_list:
													if es.endswith('FIG') or es.endswith('FIGS'):
														tmp += es + '.'
													else:
														tmp += es
														es_list.append(tmp)
														tmp = ''
												if len(es_list)==len(ja_list):
													for es,js in zip(es_list,ja_list):
														taiyaku = es + '\t' + js + '\n'
														f.write(taiyaku)
														num+=1
										elif re.match(en_description_index_pattern,en_raw_text) and re.match(ja_description_index_pattern,ja_raw_text):
											es_text = (re.sub(en_description_index_pattern,'',en_raw_text)).strip()
											ja_text = (re.sub(ja_description_index_pattern,'',ja_raw_text)).strip()
											taiyaku = es_text + '\t' + ja_text + '\n'
											f.write(taiyaku)
											num+=1
		f.close()

	def prepare_kyoto_wiki(file_to_write):
		num = 0
		f = open(file_to_write,'a')
		corpus_folder_path = './../data/open_taiyaku/wiki_corpus/'
		folder_list = os.listdir(corpus_folder_path)
		for folder in folder_list:
			folder_path = corpus_folder_path + folder
			if os.path.isdir(folder_path):
				for file in os.listdir(folder_path):
					file_path = folder_path+'/'+file
					try:
						tree = ET.parse(file_path)
						root = tree.getroot()
						for child in root:
							ja_sentence = ''
							en_sentence = ''
							for off in child:								
								if off.tag=='j':
									ja_sentence = str(off.text).strip()
								if off.tag=='e' and off.attrib['type']=='check':
									en_sentence = str(off.text).strip()
							if ja_sentence!='' and en_sentence!='':
								taiyaku = en_sentence + '\t' + ja_sentence + '\n'
								f.write(taiyaku)
								num += 1
					except:
						pass
		f.close()

	# 英辞郎はshift_jis
	def prepare_eijiro_data(file_to_write):
		# f = open(file_to_write,'a')
		corpus_file_path = './../data/open_taiyaku/EIJIRO-1446.TXT'
		# f_read = open(corpus_file_path,'r',encoding='shift_jis')
		f_read = open(corpus_file_path,'r',encoding='cp932')

		line = f_read.readline()
		while (line):
			try:
				print(line)
			except:
				pass
			line = f_read.readline()
		
		# s = s.encode('utf-8')
		# f.write(s)

	def gather_processed_data(file_to_write):
		f = open(file_to_write,'a')
		processed_folder = './../data/processed/'
		for folder in os.listdir(processed_folder)[:2]:
			folder_contains_files = processed_folder + '/' + folder
			if os.path.isdir(folder_contains_files):
				for file in os.listdir(folder_contains_files):
					file_path = folder_contains_files + '/' + file
					print(file_path)
					f_read = open(file_path,'r')
					line = f_read.readline()
					l = line.split('\t')
					s1 = l[0].strip()
					s2 = l[1].strip()
					if detect(s1)=='en' or detect(s2)=='ja':
						is_en_first = True
					else:
						is_en_first = False
					while(line):
						l = line.split('\t')
						s1 = l[0].strip()
						s2 = l[1].strip()
						if is_en_first:
							taiyaku = s1 + '\t' + s2 + '\n'
						else:
							taiayku = s2 + '\t' + s1 + '\n'
						if not taiyaku=='question\tanswer\n':
							taiyaku = taiyaku.replace('\n\n','\n')
							f.write(taiyaku)
						line = f_read.readline()
		f.close()

	def prepare_patent_data(file_to_write):
		f = open(file_to_write,'a')
		patent_folder = './../data/patent/'
		for folder in os.listdir(patent_folder):
			folder_path = patent_folder + folder
			if not 'DS_Store' in folder_path:
				for sub_folder in os.listdir(folder_path):
					sub_folder_path = folder_path + '/' + sub_folder
					if not 'DS_Store' in sub_folder_path:
						print(sub_folder_path)
						taiyaku_path = sub_folder_path + '/taiyaku.txt'
						if os.path.exists(taiyaku_path):
							print(taiyaku_path)
							f_read = open(taiyaku_path,'r')
							taiyaku = f_read.read()
							f.write(taiyaku)
							f_read.close()
		f.close()

	# taiyakuを分割
	def extract_each_sentence(file_to_read, file_to_write, mode='ja'):
		f = open(file_to_write,'a')
		file_to_read = open(file_to_read)
		line = file_to_read.readline()
		if mode=='ja':
			mode_num=1
		else:
			mode_num=0
		while(line):
			sentence_list = line.split('\t')
			if len(sentence_list)>1:
				sentence = (sentence_list)[mode_num]
				sentence = sentence.strip() + '\n'
				f.write(sentence)
			line = file_to_read.readline()
		f.close()
		file_to_read.close()

	def prepare_tokenized_taiyaku(file_to_write):
		sp = Tokenizer()
		f = open(file_to_write,'w')
		ja_file = './../data/ja_sentences.tsv'
		en_file = './../data/en_sentences.tsv'
		ja_f = open(ja_file)
		en_f = open(en_file)
		ja_line = ja_f.readline()
		en_line = en_f.readline()
		taiyaku = en_line.strip() + '\t' + ja_line.strip() + '\n'
		f.write(taiyaku)
		ja_line = ja_f.readline()
		en_line = en_f.readline()
		# この２行は間違えて入ってるカラム名を無視するため、今後消す
		ja_line = ja_f.readline()
		en_line = en_f.readline()		
		while(ja_line):
			taiyaku = en_line.strip() + '\t' + sp.ja_spm_tokenize(ja_line.strip()) + '\n'
			f.write(taiyaku)
			ja_line = ja_f.readline()
			en_line = en_f.readline()
		f.close()
		ja_f.close()
		en_f.close()