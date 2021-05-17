'''
written 2021/05/07 by yihsuan
'''
import argparse
from os import path
import glob
import re
import tgt
from textgrid_lib import PraatTextgrid as ptg
from utils import Capturing

def parse_argument():
    parser = argparse.ArgumentParser(description='e.g. python textgrid_count.py input_folder -t mod\n' +
                        'std output for counting information')
    parser.add_argument('input_folder', help='input folder with textgrid files.')
    parser.add_argument('-t', '--annot_type', type=str, help='specify type of input files, \'new\' for new annotation, \'mod\' for modified data. dufault=\'new\'', default='new')
    parser.add_argument('--ori_folder', type=str, help='text folder contained original files of \'mod\' type of input.', default=None)
    parser.add_argument('-f', '--per_file_info', action='store_true', help='if -f will show information by file.')
    parser.add_argument('-o', '--output_info_file', type=str, help='write result to output file.\n', default=None)
    arguments = parser.parse_args()
    return arguments

def read_origin_tg_folder(unmodified_file_folder:str):
    ori_tg_dict = dict()
    return ori_tg_dict

def count_chars(input_str):
    rule_punctuation = re.compile(r'([,\t\r\n，。；：、？?~!！（）,～「」;:——．/|※↑↓←→&%`~!@#$%^&*()_=€§\(\)《 》【】\[\]…<>⁺\+\-\.])')
    return len(rule_punctuation.sub('', input_str))

def per_file_info_str(info_dict, info_index=-1, mod_annot=False):
    result_str = ''
    result_str += f'\tnum_segs:   {info_dict["num_segs"][info_index]}\n'
    result_str += f'\tnum_chars:  {info_dict["num_chars"][-1]}\n'
    result_str += f'\tnum_speaker:{info_dict["num_speaker"][-1]}\n'
    result_str += f'\tduration:   {info_dict["duration"][-1]:.2f} sec\n'
    result_str += f'\tempty_dur:  {info_dict["empty_duration_percentage"][-1]*100:.2f}%\n'
    if mod_annot:
        result_str += f'\tnum_mod_chars:   {info_dict["num_mod_chars"][-1]}\n'
        result_str += f'\torigin_cer:      {info_dict["cer"][-1]}\n'
    return result_str

def total_info_str(info_dict, mod_annot=False):
    result_str = ''
    if not mod_annot:
        del info_dict['num_mod_chars']
        del info_dict['cer']
    for k, v in info_dict.items():
        if type(v) is list:
            if k == 'duration':
                result_str += f'{k}: {sum(v)/60:.2f} mins\n'
            elif k == 'empty_duration_percentage':
                result_str += f'{k}: {sum(v)*100:.2f}%\n'
            else:
                result_str += f'{k}: {sum(v)}\n'
        else:
            if type(v) is float:
                result_str += f'{k}: {v:.2f}\n'
            else:
                result_str += f'{k}: {v}\n'
    return result_str

def count_info(input_folder:str, output_file, per_file_info=False, annot_type='new', unmodified_tg_folder=None):
    input_root = path.realpath(path.expanduser(path.normpath(input_folder)))
    tg_file_list = glob.glob(path.join(input_root, '**/*.TextGrid'), recursive=True)
    info_dict = {
        'num_segs':list(),
        'num_chars':list(),
        'num_speaker':list(),
        'duration':list(),
        'empty_duration_percentage': list(),  # (new:<30%; modified:~60%) segments(empty/silence/htr/<2chars) duration / (tier duration*num of tier)
        'num_mod_chars':list(),  # for modified files, original file is needed
        'cer':list(),  # for modified files, cer information filel is needed
        'num_file': 0,
        'min_avg_segs':0,  # average segments per file
        'min_avg_chars':0,  # average characters per minute
        'seg_avg_chars':0,  # average characters of segment
        'seg_avg_len':0  # average length of segment
    }

    for tgfile in tg_file_list:
        if per_file_info:
            print(f'{tgfile}')
            with Capturing() as stdout:
                tg, tier_names = ptg.get_tiernames_from_tgfile(tgfile, print_encoding_info=True)
            print(f'yes: {stdout}')
        else:
            tg, tier_names = ptg.get_tiernames_from_tgfile(tgfile)
        empty_dur, duration, num_speaker = 0, None, 0
        for index, name in enumerate(tier_names):
            tier = tg.get_tier_by_name(name)
            try:
                if duration is not None:
                    if duration != tier.end_time:
                        print(f'ERROR: duration mismatch between {tier_name[index-1]}({duration}) and {name}({tier.end_time})')
                else:
                    duration = tier.end_time
                annot_text_list = [i.text for i in tier.annotations]
                info_dict['num_segs'].append(len(annot_text_list))
                info_dict['num_chars'].append(sum([count_chars(i) for i in annot_text_list]))
                for annot in tier.annotations:
                    if len(annot.text) <= 2:
                        empty_dur += (annot.end_time - annot.start_time)
                num_speaker += 1
            except:
                print(f'ERROR: num_segs, num_chars goes wrong in {name} tier of {tgfile}!')
        info_dict['num_speaker'].append(num_speaker)
        info_dict['duration'].append(duration)
        info_dict['empty_duration_percentage'].append(empty_dur/(len(tier_names)*duration))
        if per_file_info:
            file_info = per_file_info_str(info_dict, mod_annot=(annot_type=='mod'))
            print(file_info)
        # TODO: annot_type = 'mod': get num_mod_chars and cer information
        # if annot_type == 'mod':
        #     ori_tg_dict = read_origin_tg_folder(unmodified_tg_folder)
        # TODO: write output_file if is not None
    info_dict['num_file'] = len(tg_file_list)
    info_dict['min_avg_segs'] = sum(info_dict['num_segs'])*60/sum(info_dict['duration'])
    info_dict['min_avg_chars'] = sum(info_dict['num_chars'])*60/sum(info_dict['duration'])
    info_dict['seg_avg_chars'] = sum(info_dict['num_chars'])/sum(info_dict['num_segs'])
    info_dict['seg_avg_len'] = sum(info_dict['duration'])/sum(info_dict['num_segs'])
    total_info = total_info_str(info_dict)
    print(total_info)


if __name__=='__main__':
    args = parse_argument()
    input_folder = args.input_folder
    per_file_info = args.per_file_info
    output_file = args.output_info_file
    annot_type = args.annot_type
    unmodified_tg_folder = args.ori_folder

    count_info(input_folder, output_file, per_file_info, annot_type, unmodified_tg_folder)

