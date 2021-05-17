'''
written 2021/05/07 by yihsuan
'''
import argparse
from os import mkdir, path
import glob
import re
import tgt
from textgrid_lib import PraatTextgrid as ptg
from utils import TxtOperator as txtop

def parse_argument():
    parser = argparse.ArgumentParser(description='e.g. python audacity_txt_to_textgrid.py input\n' +
                        'output file <input_filename>.TextGrid.')
    parser.add_argument('input', help='input folder with textgrid files or single audacity txt file.')
    parser.add_argument('-o', '--output', type=str, help='write result to output directory/file.\n', default=None)
    arguments = parser.parse_args()
    return arguments

def convert_enitre_folder(input_folder: str, output_folder='./'):
    try:
        if not path.exists(output_folder):
            mkdir(output_folder)
    except:
        print('Error: failed building {output_folder}.')
    input_root = path.realpath(path.expanduser(path.normpath(input_folder)))
    txt_file_list = glob.glob(path.join(input_root, '**/*.txt'), recursive=True)
    for txt_file in txt_file_list:
        tg_file = path.join(output_folder, path.splitext(path.basename(txt_file))[0]+'.TextGrid')
        convert_audacity_txt_to_textgrid(txt_file, tg_file)

def convert_audacity_txt_to_textgrid(txt_file: str, tg_file=None):
    tg_file = tg_file if tg_file else path.splitext(path.basename(txt_file))[0]+'.TextGrid'
    lines, encoding_type = txtop.unknown_encoding_file_readlines(txt_file)
    tg_inter_annot = list()  # interval type of annotation in textgrid
    tg_tiers = list()
    for line in lines:
        annot = line.split('\t', 2)
        tg_inter_annot.append([float(annot[0]), float(annot[1]), annot[2].strip()])
    fixed_annot = fix_error_annot_within_halfsec(tg_inter_annot)
    error_index, error_annot = ptg.validate_intervals(fixed_annot)
    if error_annot is not None:
        print(f'[ERROR]{txt_file} has wrong annotation:\n\t{error_annot}')
        return
    else:
        print(f'{txt_file} convert into textgrid successfully with {len(fixed_annot)} segments')
        tier = ptg.create_interval_tier(0, fixed_annot[-1][1], 'audacity_annot', fixed_annot)
        tg_tiers.append(tier)
    ptg.write_tgfile(tg_file, tg_tiers)

def fix_error_annot_within_halfsec(inter_annot_list: list) -> list:
    fixed_list = list()
    max_time = 0.0
    for index, annot in enumerate(inter_annot_list):
        seg_start_time = annot[0]
        seg_end_time = annot[1]
        seg_text = annot[2]
        if seg_start_time < max_time and max_time-seg_start_time<0.5:
            seg_start_time = max_time
        max_time = max(max_time, seg_end_time)
        fixed_list.append([seg_start_time, seg_end_time, seg_text])
    return fixed_list
   

if __name__=='__main__':
    args = parse_argument()
    if path.isdir(args.input):
        input_folder = args.input
        if args.output is None:
            convert_enitre_folder(input_folder)
        else:
            output_folder = args.output
            if path.splitext(output_folder)[1]:  # has file extension
                print('[ERROR] output {args.output} should be a dircetory.')
            else:
                convert_enitre_folder(input_folder, output_folder=output_folder)
    elif path.isfile(args.input):
        convert_audacity_txt_to_textgrid(args.input, args.output)
    else:
        print('[ERROR] input {args.input} should be directory or file.')
