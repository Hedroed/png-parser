from typing import List

class CRC():
    CRC_TABLE: List[int] = []

    @staticmethod
    def createCRCTable():
        CRC.CRC_TABLE = []
        for c in range(256):
            for _ in range(8):
                if (c & 1) == 1:
                    c = 0xedb88320 ^ (c >> 1)
                else:
                    c = c >> 1
            CRC.CRC_TABLE.append(c)

    @staticmethod
    def updateCRC(data):
        c = 0xffffffff
        for val in data:
            c = CRC.CRC_TABLE[(c ^ val) & 0xff] ^ (c >> 8)
        return c ^ 0xffffffff

    def __init__(self, crc, data=None):
        if isinstance(crc, bytes):
            crc = int.from_bytes(crc, byteorder='big')

        self.crc = crc
        self.valid = True
        if data:
            self.checkCRC(data)

    def checkCRC(self, data):
        if self.CRC_TABLE is None:
            self.createCRCTable()

        crc = self.updateCRC(data)

        self.valid = crc == self.crc
        self.good = crc

    def __repr__(self):
        return "%x : %s" % (self.crc, "OK" if self.valid else "Incorrect must be %x" % self.good)
