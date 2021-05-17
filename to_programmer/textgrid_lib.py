from os.path import basename
import tgt
from parselmouth.praat import call
from typing import Tuple

class PraatTextgrid(object):
    @staticmethod
    def get_tiernames_from_tgfile(read_file, print_encoding_info=False):
        for encoding_type in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                tg = tgt.read_textgrid(read_file, encoding=encoding_type)
                if type(tg) is tgt.core.TextGrid:
                    if print_encoding_info:
                        print(f'\t\'{basename(read_file)}\' encoding in {encoding_type}.')
                    break
            except:
                # print(f'WARNING: failed with reading as {encoding_type}')
                continue
        tier_names = [tier.name for tier in tg.tiers]
        return tg, tier_names
        
    @staticmethod
    def write_tgfile(outfile, tiers):
        tg = tgt.core.TextGrid()
        for tier in tiers:
            tg.add_tier(tier)
        tgt.io.write_to_file(tg, outfile, format = 'long', encoding='utf-8')

    @staticmethod
    def create_interval_tier(start_time, end_time, name, intervals):
        try:
            tier = tgt.core.IntervalTier(float(start_time), float(end_time), name)
        except ValueError as e:
            print(e)
            print(f'[s]{start_time} [e]{end_time} [n]{name} [len]{len(intervals)}')
            return
        for interval in intervals:
            # interval = [start_time, end_time, text]
            annotation = tgt.core.Interval(interval[0], interval[1], interval[2])
            tier.add_interval(annotation)
        return tier

    @staticmethod
    def create_point_tier(start_time, end_time, name, points):
        tier = tgt.core.IntervalTier(start_time, end_time, name)
        for interval in intervals:
            # interval = [time, text]
            annotation = tgt.core.Interval(interval[0], interval[1])
            tier.add_interval(annotation)
        return tier
        
    @staticmethod
    def create_silence_tg(wav_path, output_sil_tg_path):
        wav_praat_read = call('Read from file', wav_path)
        sil_tier = call(wav_praat_read, 'To TextGrid (silences)', 100, 0, -25, 0.1, 0.1, "SIL", "")
        output = call(sil_tier, 'Write to text file', output_sil_tg_path)
    
    @staticmethod
    def get_wave_duration(wav_file):
        import sox
        duration = sox.file_info.duration(wav_file)
        return duration

    @staticmethod
    def validate_intervals(interval_annot: list, start_time=-1.0, end_time=-1.0) -> Tuple[int, list]:
        # interval_annot: list of [start_time, end_time, text]
        max_time = 0
        if start_time != -1.0 and start_time != interval_annot[0][0]:
            return 0, interval_annot[0]
        for index, annot in enumerate(interval_annot):
            seg_start_time = float(annot[0])
            seg_end_time = float(annot[1])
            seg_text = annot[2]
            if seg_start_time < max_time:
                return index, annot
            if seg_end_time < seg_start_time:
                return index, annot
            max_time = max(max_time, seg_end_time)
        if end_time != -1.0 and end_time != max_time:
            return len(interval_annot)-1, interval_annot[-1]
        return None, None



