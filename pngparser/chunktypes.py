from enum import Enum, auto
from typing import Union, List

CHUNK_LENGTH_SIZE = 4
CHUNK_TYPE_SIZE = 4
CHUNK_CRC_SIZE = 4


TYPE_IHDR = b'IHDR'
TYPE_PLTE = b'PLTE'
TYPE_IDAT = b'IDAT'
TYPE_IEND = b'IEND'
TYPE_bKGD = b'bKGD'
TYPE_cHRM = b'cHRM'
TYPE_dSIG = b'dSIG'
TYPE_eXIf = b'eXIf'
TYPE_gAMA = b'gAMA'
TYPE_hIST = b'hIST'
TYPE_iCCP = b'iCCP'
TYPE_iTXt = b'iTXt'
TYPE_pHYs = b'pHYs'
TYPE_sBIT = b'sBIT'
TYPE_sPLT = b'sPLT'
TYPE_sRGB = b'sRGB'
TYPE_sTER = b'sTER'
TYPE_tEXt = b'tEXt'
TYPE_tIME = b'tIME'
TYPE_tRNS = b'tRNS'
TYPE_zTXt = b'zTXt'


def get_all() -> List[bytes]:
    return [v for k, v in locals().items() if k.startswith('TYPE_')]

def contains(chunk_type: bytes) -> bool:
    return chunk_type in get_all()

def is_text_chunk(chunk_type: bytes) -> bool:
    return chunk_type in (TYPE_iTXt, TYPE_tEXt, TYPE_zTXt)

