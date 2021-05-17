from io import StringIO 
from typing import Tuple
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class TxtOperator(object):
    @staticmethod
    def unknown_encoding_file_readlines(txt_path: str) -> Tuple[list, str]:
        support_types = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be']
        for encoding_type in support_types:
            try:
                with open(txt_path, 'r', encoding=encoding_type) as rf:
                    lines = rf.readlines()
                return lines, encoding_type
            except:
                continue
        return None, None