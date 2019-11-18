import os
from tokenizer import Tokenizer


class PyT2T:
  def __init__(self):
    self.file_to_decode = 'data_dir/decode_this.txt'
    self.mid_file = 'data_dir/tokenized.txt'
    self.decoded_file = 'data_dir/decoded.txt'
    self.gen_cmd = 't2t-datagen --data_dir=data_dir --tmp_dir=tmp_dir --problem=my_problem --t2t_usr_dir=my_problem'
    self.train_cmd = 't2t-trainer --data_dir=data_dir --problem=my_problem --model=transformer --hparams_set=transformer_base_single_gpu --output_dir=train_dir --t2t_usr_dir=my_problem'   
    self.decode_cmd = 't2t-decoder --data_dir=data_dir --problem=my_problem --model=transformer --hparams_set=transformer_base_single_gpu --output_dir=train_dir --decode_hparams="beam_size=4,alpha=0.6"  --decode_interactive=false --t2t_usr_dir=my_problem'
    self.decode_from_file_cmd = 't2t-decoder --data_dir=data_dir --problem=my_problem --model=transformer --hparams_set=transformer_base_single_gpu --output_dir=train_dir --decode_hparams="beam_size=4,alpha=0.6" --decode_from_file=data_dir/tokenized.txt  --decode_to_file=data_dir/decoded.txt --t2t_usr_dir=my_problem'

  def data_gen(self):
    os.system(self.gen_cmd)

  def train(self):
    os.system(self.train_cmd)

  def decode(self):
    os.system(self.decode_cmd)

  # English to Japanese
  def decode_from_file(self):
    f = open(self.file_to_decode,'r')
    lines = f.readlines()
    f.close()
    preprocessed_lines = list(map(lambda x: (x.lower()).replace('"',''),lines))
    f = open(self.mid_file,'w')
    f.writelines(preprocessed_lines)
    f.close()
    os.system(self.decode_from_file_cmd)
    f = open(self.decoded_file,'r')
    lines = f.readlines()
    lines = list(map(lambda x: x[1:] if len(x)>0 and x[0]=='､' else x, lines))
    print(lines)
    f.close()
    f = open(self.decoded_file,'w','ignore')
    f.writelines(lines)
    f.close()

  # Japanese to English
  def tokenize_and_decode_from_file(self):
    f = open(self.file_to_decode)
    lines = f.readlines()
    f.close()
    preprocessed_lines = list(map(lambda x: Tokenizer().ja_spm_tokenize(x.lower()),lines))
    f = open(self.mid_file)
    f.writelines(preprocessed_lines)
    f.close()
    os.system(self.ja_decode_from_file_cmd)