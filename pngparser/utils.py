import collections

# Debug decorator
def monitor_results(func):
    def wrapper(*func_args, **func_kwargs):
        print('function call ' + func.__name__ + '()')
        retval = func(*func_args, **func_kwargs)
        print('function ' + func.__name__ + '() returns ' + repr(retval))
        return retval
    wrapper.__name__ = func.__name__
    return wrapper

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def pixel_type_to_length(type_):
    if type_ == 0:  # Greyscale
        return 1
    elif type_ == 2:  # RGB
        return 3
    elif type_ == 4:  # Greyscale + alpha
        return 2
    elif type_ == 6:  # RGB + Alpha
        return 4
    else:  # Palette
        return 1

class BitArray(collections.Iterator):
    def __init__(self, bytes, deep=8):
        # print("Create BitArray with %s, %s" % (bytes, deep))
        self.bytes = bytes
        self.pos = 0
        self.deep = deep

        self.accumulator = 0
        self.bcount = 0

        if deep == 16:
            self._readbits = self._read16bits
        elif deep == 8:
            self._readbits = self._read8bits
        elif deep == 4 or deep == 2 or deep == 1:
            self._readbits = self._readotherbits
        else:
            raise ValueError("Deep must be 16, 8, 4, 2, 1 not %s" % deep)

    def _readbit(self, n=1):
        if self.pos >= len(self.bytes):
            return 0

        if n > 1:
            ret = self.bytes[self.pos: self.pos+n]
            self.pos += n
            return int.from_bytes(ret, byteorder='big')
        else:
            ret = self.bytes[self.pos]
            self.pos += 1
            return ret

    def _read16bits(self):
        return self._readbit(2)

    def _read8bits(self):
        return self._readbit(1)

    def _readotherbits(self):
        if self.bcount <= 0:
            a = self._readbit(1)
            self.accumulator = a
            self.bcount = 8
        self.bcount -= self.deep
        ret = self.accumulator >> self.bcount & (2 ** self.deep - 1)
        return ret

    def read(self):
        return self._readbits()

    def __len__(self):
        return (len(self.bytes) * 8) // self.deep

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.bytes):
            raise StopIteration
        else:
            return self.read()