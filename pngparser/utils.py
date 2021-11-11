import collections.abc


# Debug decorator
def monitor_results(func):
    def wrapper(*func_args, **func_kwargs):
        print(f'function call {func.__name__}()')
        retval = func(*func_args, **func_kwargs)
        print('function {func.__name__}() returns {retval!r}')
        return retval
    wrapper.__name__ = func.__name__
    return wrapper


def pixel_type_to_length(color_type: int) -> int:
    if color_type == 0:  # Greyscale
        return 1
    elif color_type == 2:  # RGB
        return 3
    elif color_type == 3:  # Palette
        return 1
    elif color_type == 4:  # Greyscale + alpha
        return 2
    elif color_type == 6:  # RGB + Alpha
        return 4
    else:  # Other
        raise ValueError(f'Invalid color type {color_type}')


class BitArray(collections.abc.Iterator):
    def __init__(self, bytes_, depth=8):
        # print(f'Create BitArray with {bytes}, {depth}')
        self.bytes = bytes_
        self.pos = 0
        self.depth = depth

        self.accumulator = 0
        self.bcount = 0

        if depth == 16:
            self._readbits = self._read16bits
        elif depth == 8:
            self._readbits = self._read8bits
        elif depth in (4, 2, 1):
            self._readbits = self._readotherbits
        else:
            raise ValueError(f'Depth must be 16, 8, 4, 2, 1 not {depth}')

    def _readbit(self, n: int = 1) -> int:
        if self.pos >= len(self.bytes):
            return 0

        if n > 1:
            ret = self.bytes[self.pos: self.pos+n]
            self.pos += n
            return int.from_bytes(ret, byteorder='big')

        ret = self.bytes[self.pos]
        self.pos += 1
        return ret

    def _read16bits(self) -> int:
        return self._readbit(2)

    def _read8bits(self) -> int:
        return self._readbit(1)

    def _readotherbits(self) -> int:
        if self.bcount <= 0:
            a = self._readbit(1)
            self.accumulator = a
            self.bcount = 8
        self.bcount -= self.depth
        ret = self.accumulator >> self.bcount & (2 ** self.depth - 1)
        return ret

    def read(self) -> int:
        return self._readbits()

    def __len__(self) -> int:
        return (len(self.bytes) * 8) // self.depth

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.bytes):
            raise StopIteration
        return self.read()
