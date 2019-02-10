class CRC():
    CRC_TABLE = None

    @staticmethod
    def createCRCTable():
        CRC.CRC_TABLE = []
        for c in range(256):
            for k in range(8):
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

    def __init__(self, CRC, data=None):
        if type(CRC) == bytes:
            CRC = int.from_bytes(CRC, byteorder='big')

        self.crc = CRC
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
