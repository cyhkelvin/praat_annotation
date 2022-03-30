'''
## TextGrid 
[tgt git](https://github.com/hbuschme/TextGridTools)
[tgt doc](https://textgridtools.readthedocs.io/en/stable/api.html)

## Praat
[script doc](https://www.fon.hum.uva.nl/praat/manual/Scripting.html)
[小狐狸簡介](http://yhhuang1966.blogspot.com/2019/12/praat_9.html)
[parselmouth github](https://github.com/YannickJadoul/Parselmouth)
[parselmouth doc](https://parselmouth.readthedocs.io/en/stable/)

written 2021/07/11 by yihsuan
'''

import argparse
import re
from os import path, mkdir
import tgt
from tqdm import tqdm
from parselmouth import praat
from parselmouth import TextGrid


def main(wavscp, outdir, text):
    utt2text = dict()
    if not path.exists(outdir):
        mkdir(outdir)
    if text is not None:
        with open(text, 'r') as rf:
            lines = rf.readlines()
        for line in lines:
            uttid = line.split(' ')[0]
            assert uttid not in utt2text.keys(), '[error]utterance name in text file should not be duplicated'
            utt2text[uttid] = ' '.join(line.split(' ')[1:]).strip()

    with open(wavscp, 'r') as rf:
        lines = rf.readlines()
    rule_ch_seq_space = re.compile(r'(?<=[\u4e00-\u9fa5])( +)(?=[\u4e00-\u9fa5])')
    for line in tqdm(lines):
        uttid = line.split(' ')[0]
        wav_path = line.split(' ')[1].strip()
        wav_name = path.splitext(path.basename(wav_path))[0]
        output_tgt = path.join(outdir, f'{wav_name}.TextGrid')
        
        wav_read = praat.call('Read from file', wav_path)
        tg_obj = praat.call(wav_read, 'To TextGrid', 'spk1', '')
        tgt_obj = tg_obj.to_tgt()
        if uttid in utt2text.keys():
            text_content = rule_ch_seq_space.sub('', utt2text[uttid])
            annot_text = tgt.core.Interval(tgt_obj.start_time, tgt_obj.end_time, text_content)
            tgt_obj.get_tier_by_name('spk1').add_annotation(annot_text)
        tgt.io.write_to_file(tgt_obj, output_tgt, format='long', encoding='utf-8')    
        #    tg_obj = TextGrid.from_tgt(tgt_obj)
        # saved in binary format: output = praat.call(tg_obj, 'Write to text file', output_tgt)
        # also saved in binary format: output = praat.call(tg_obj, 'Save as text file', output_tgt)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='e.g. python gen_textgrid_by_scp.py wav.scp output_folder -t text')
    parser.add_argument('wavscp', help='text file with <utterance name> <wav_path>')
    parser.add_argument('outdir', help='output directory of textgrid files.')
    parser.add_argument('-t', '--text', type=str, help='text file with <utterance name> <text>', default=None)
    args = parser.parse_args()
    wavscp = args.wavscp
    outdir = args.outdir
    text = args.text

    main(wavscp, outdir, text)
