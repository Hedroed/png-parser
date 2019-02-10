
class ChunkIterator(collections.Iterator):
    def __init__(self, file, autostop=True):
        self._stop = False
        self._file = file
        self._autostop = autostop
        self.count = 0

        self.header = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop and self._autostop:
            raise StopIteration

        start_position = self._file.tell()

        length = self._check_file_end(self._read_data_length())
        length = struct.unpack('>i', length)[0]
        _type = self._read_type()
        data = self._read_data(length)
        crc = self._read_crc()

        self.count += 1

        try:
            current_chunk = Chunk(_type, data, crc, start_position, self.count)
        except Exception as e:
            raise e
            return None
        else:
            if current_chunk.type is ChunkTypes.IEND:
                self._stop = True

            if current_chunk.type is ChunkTypes.IHDR:
                self.header = current_chunk

            return current_chunk

    def _check_file_end(self, value):
        if not value or len(value) == 0:
            raise StopIteration

        return value

    def _read_data_length(self):
        return self._file.read(ChunkField.DATA_LENGTH.length())

    def _read_type(self):
        return self._file.read(ChunkField.TYPE.length())

    def _read_data(self, chunk_length):
        return self._file.read(chunk_length)

    def _read_crc(self):
        return self._file.read(ChunkField.CRC.length())