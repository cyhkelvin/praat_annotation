'''
## TextGrid 
[tgt git](https://github.com/hbuschme/TextGridTools)
[tgt doc](https://textgridtools.readthedocs.io/en/stable/api.html)

## Praat
[script doc](https://www.fon.hum.uva.nl/praat/manual/Scripting.html)
[小狐狸簡介](http://yhhuang1966.blogspot.com/2019/12/praat_9.html)
[parselmouth github](https://github.com/YannickJadoul/Parselmouth)
[parselmouth doc](https://parselmouth.readthedocs.io/en/stable/)

written 2022/03/25 by yihsuan
'''

import argparse
import re
from os import path, mkdir, system
import tgt
from tqdm import tqdm
from parselmouth import praat
from parselmouth import TextGrid

def write_segment(input_audio:str, sil_threshold:float):
    try:
        wav_praat_read = praat.call('Read from file', input_audio)
        sil_TextGrid = praat.call(wav_praat_read, 'To TextGrid (silences)', 100, 0, -25, 0.1, 0.1, "SIL", "")
        sil_tgt = TextGrid.to_tgt(sil_TextGrid)
        sil_tier = sil_tgt.get_tier_by_name('silences')
    except Exception as e:
        print(f'praat silence detection error: {e}')
        raise Exception

    times = list()
    print('number of intervals:', len(sil_tier.annotations))
    for interval in sil_tier.annotations:
        if interval.text == 'SIL':
            dur = interval.end_time - interval.start_time
            if dur > sil_threshold:
                time = interval.start_time + dur/2
                times.append(time)
                print(f'{input_audio}: {dur}, {interval.start_time}, {interval.end_time}')
    times.append(sil_tier.annotations[-1].end_time)

    input_name = path.splitext(path.basename(input_audio))[0]
    segment = dict() # 'segment_name' = [start_time, duration]
    start_time = 0
    for i, time in enumerate(times):
        segment[f'{input_name}-{start_time:07.2f}-{time:07.2f}'] = [start_time, time - start_time]
        start_time = time

    return segment


def convert_audio(input_audio: str, input_audio_format: str, output_audio: str):
    try:
        system(f'sox -t {input_audio_format} {input_audio} -r 16000 -b 16 -c 1 -t wav {output_audio}')
    except Exception as e:
        print(f'convert audio error: {input_audio}({input_audio_format}) -> {output_audio}')
        print(e)
        raise Exception


def trim_wav(input_audio, segment, out_dir):
    # segment[uttid] = [start_time, end_time]
    segname2wav = dict()
    for segname, interval in segment.items():
        out_wav = path.join(out_dir, f'{segname}.wav')
        system(f'sox {input_audio} {out_wav} trim {interval[0]} {interval[1]}')
        segname2wav[segname] = out_wav
    return segname2wav


def make_textgrids(utt2wav, utt2text, outdir):
    rule_ch_seq_space = re.compile(r'(?<=[\u4e00-\u9fa5])( +)(?=[\u4e00-\u9fa5])')
    for uttid, wav_path in tqdm(utt2wav.items()):
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


def main(wavscp, outdir, text, sil_thres):

    if not path.exists(outdir):
        mkdir(outdir)

    # read wavscp -> utt2wav
    utt2wav = dict()
    with open(wavscp, 'r') as rf:
        lines = rf.readlines()
    for line in lines:
        uttid = line.split(' ')[0]
        wav_path = line.split(' ')[1].strip()
        utt2wav[uttid] = wav_path
    print(f'done utt2wav({len(utt2wav.keys())})')

    # get utt2text
    utt2text = dict()
    if text is not None:
        with open(text, 'r') as rf:
            lines = rf.readlines()
        for line in lines:
            uttid = line.split(' ')[0]
            assert uttid not in utt2text.keys(), '[error]utterance name in text file should not be duplicated'
            utt2text[uttid] = ' '.join(line.split(' ')[1:]).strip()
    print(f'done utt2text({len(utt2text.keys())})')

    # make segment
    DONE_SEGMENT = False
    try:
        sil_threshold = float(sil_thres)
        data_name = path.basename(wavscp).replace('.scp', '')

        # segment or check for text
        if sil_threshold > 0:
            out_segment = path.join(outdir, f'{data_name}.segment')
            format_dir = path.join(outdir, 'format')
            if not path.exists(format_dir):
                mkdir(format_dir)
            trim_dir = path.join(outdir, 'trimed')
            if not path.exists(trim_dir):
                mkdir(trim_dir)
            trim_utt2wav = dict()
            trim_utt2text = dict()
            
            for wavid, wavpath in tqdm(utt2wav.items()):
                audio_type = path.splitext(wavpath)[1][1:]
                format_wav = path.join(format_dir, f'{path.splitext(path.basename(wavpath))[0]}.wav')
                convert_audio(wavpath, audio_type, format_wav)

                segment = write_segment(format_wav, sil_threshold)
                for sub_id, interval in segment.items():
                    with open(out_segment, 'a') as af:
                        af.write(f'{sub_id} {wavid} {interval[0]:.2f} {interval[1]:.2f}\n')
                sub_utt2wav = trim_wav(format_wav, segment, trim_dir)
                trim_utt2wav.update(sub_utt2wav)
                if wavid in utt2text.keys():
                    text = utt2text[wavid]
                    for sub_id in sub_utt2wav.keys():
                        trim_utt2text[sub_id] = text

            trim_scp = path.join(outdir, f'{data_name}trimed_wav.scp')
            with open(trim_scp, 'w') as wf:
                for sub_id, sub_wavpath in trim_utt2wav.items():
                    wf.write(f'{sub_id} {sub_wavpath}\n')
                
            DONE_SEGMENT = True
            print('done segmentation')
        else:
            print('pass segmentation')
            
    except Exception as e:
        print(f'error: set silence threshold {sil_thres} {e}')
        raise Exception

    # make textgrid
    if DONE_SEGMENT:
        make_textgrids(trim_utt2wav, trim_utt2text, trim_dir)
    else:
        make_textgrids(utt2wav, utt2text, outdir)

    #    tg_obj = TextGrid.from_tgt(tgt_obj)
    # saved in binary format: output = praat.call(tg_obj, 'Write to text file', output_tgt)
    # also saved in binary format: output = praat.call(tg_obj, 'Save as text file', output_tgt)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='e.g. python gen_textgrid_by_scp.py wav.scp output_folder -t text')
    parser.add_argument('wavscp', help='text file with <utterance name> <wav_path>')
    parser.add_argument('outdir', help='output directory of textgrid files.')
    parser.add_argument('-t', '--text', type=str, help='text file with <utterance name> <text>', default=None)
    parser.add_argument('-s', '--sil_threshold', help="silence interval threshold for making segment by " +
                        "praat-silence-detection, default pass this step", default=0.8)
    args = parser.parse_args()
    wavscp = args.wavscp
    outdir = args.outdir
    text = args.text
    sil_threshold = args.sil_threshold

    main(wavscp, outdir, text, sil_threshold)
