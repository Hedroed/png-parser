from typing import List


class CRC:
    CRC_TABLE: List[int] = []

    @staticmethod
    def create_crc_table() -> None:
        CRC.CRC_TABLE = []
        for c in range(256):
            for _ in range(8):
                if (c & 1) == 1:
                    c = 0xedb88320 ^ (c >> 1)
                else:
                    c = c >> 1
            CRC.CRC_TABLE.append(c)

    @staticmethod
    def update_crc(data) -> int:
        c = 0xffffffff
        for val in data:
            c = CRC.CRC_TABLE[(c ^ val) & 0xff] ^ (c >> 8)
        return c ^ 0xffffffff

    def __init__(self, crc, data=None) -> None:
        if isinstance(crc, bytes):
            crc = int.from_bytes(crc, byteorder='big')

        self.crc = crc
        self.valid = True
        self.good = 0  # Initialize variable
        if data:
            self.check_crc(data)

    def check_crc(self, data) -> None:
        if self.CRC_TABLE is None:
            self.create_crc_table()

        crc = self.update_crc(data)

        self.valid = crc == self.crc
        self.good = crc

    def __repr__(self) -> str:
        valid = 'OK' if self.valid else f'Incorrect must be {self.good:x}'
        return f'{self.crc:x} : {valid}'
