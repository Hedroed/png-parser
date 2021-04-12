from enum import Enum


class ChunkField(Enum):
    DATA_LENGTH = 4
    TYPE = 4
    CRC = 4

    def length(self):
        return self.value


class ChunkUnknown:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Unknown [ %s ]' % self.name

    def to_bytes(self):
        return self.name.encode()

    def __eq__(self, other):
        if type(other) == str:
            return 'Unknown' == other


# todo migrate to python 3.6 for using automatic values - auto()
class ChunkTypes(Enum):
    IHDR = 1
    PLTE = 2
    IDAT = 3
    IEND = 4
    bKGD = 5
    cHRM = 6
    dSIG = 7
    eXIf = 8
    gAMA = 9
    hIST = 10
    iCCP = 11
    iTXt = 12
    pHYs = 13
    sBIT = 14
    sPLT = 15
    sRGB = 16
    sTER = 17
    tEXt = 18
    tIME = 19
    tRNS = 20
    zTXt = 21
    nONe = 22

    def __str__(self):
        return self.name

    def to_bytes(self):
        return self.name.encode()

    def __bytes__(self):
        return self.to_bytes()

    @staticmethod
    def getAll():
        all_chunk_types = [name for name, _ in ChunkTypes.__members__.items()]
        return all_chunk_types

    @staticmethod
    def contains(chunk_type_str):
        all_chunk_types = [name for name, _ in ChunkTypes.__members__.items()]
        return chunk_type_str in all_chunk_types

    @staticmethod
    def from_binary(data):
        if len(data) != ChunkField.TYPE.length():
            raise Exception(f'Incorrect a chunk type size {len(data)}!')

        try:
            chunk_type = data.decode('ascii')
        except UnicodeDecodeError:
            return ChunkUnknown(data)
        else:
            found_enums = [enum for name, enum in ChunkTypes.__members__.items()
                           if name == chunk_type]

            if len(found_enums) == 0:
                # raise Exception('Unknown "{}" chunk type!'.format(chunk_type))
                return ChunkUnknown(chunk_type)
            else:
                return found_enums[0]

    @staticmethod
    def is_text_chunk(chunk_type):
        return chunk_type in [ChunkTypes.iTXt, ChunkTypes.tEXt, ChunkTypes.zTXt]

    def __eq__(self, other):
        if type(other) is str:
            return self.name == other
        if type(other) is ChunkTypes:
            return self.name == other.name
