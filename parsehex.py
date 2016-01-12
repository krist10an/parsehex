from __future__ import print_function
import sys

def raw_hex(val):
    return hex(val)[2:].zfill(2).upper()

def raw_hex_list(val):
    return "".join(raw_hex(x) for x in val)

def to_address(high, low):
    return (1 << 8) * high + low

class IntelHexRecord(object):
    records = [
        'Data',
        'End Of File',
        'Extended Segment Address',
        'Start Segment Address',
        'Extended Linear Address',
        'Start Linear Address'
    ]

    def __init__(self, start, bytecount, address, recordtype, data, checksum):
        self.start = start
        self.bytecount = bytecount
        self.address = address
        self.recordtype = recordtype
        self.data = data
        self.checksum = checksum

    @property
    def addr(self):
        return to_address(self.address[0], self.address[1])

    def record_name(self, id):
        return IntelHexRecord.records[self.recordtype] + " record"

    def is_checksum_ok(self):
        all_data = []
        all_data.append(self.bytecount)
        all_data.extend(self.address)
        all_data.append(self.recordtype)
        all_data.extend(self.data)
        all_data.append(self.checksum)

        checksum = 0
        for num in all_data:
            checksum = (checksum + num) % 256

        return checksum == 0

    def to_hexline(self):
        return ":{bc}{ad}{rt}{data}{cs}".format(
            bc=raw_hex(self.bytecount),
            ad=raw_hex_list(self.address),
            rt=raw_hex(self.recordtype),
            data=raw_hex_list(self.data),
            cs=raw_hex(self.checksum))

    def to_extended(self):
        return ":{bc} {ad} {rt} {data} {cs}".format(
            bc=raw_hex(self.bytecount),
            ad=raw_hex_list(self.address),
            rt=raw_hex(self.recordtype),
            data=raw_hex_list(self.data),
            cs=raw_hex(self.checksum))

    def to_extended_with_comment(self, offset=0):
        comment = "{} byte {} record @ {}".format(
            self.bytecount,
            IntelHexRecord.records[self.recordtype],
            self.addr + offset)

        if not self.is_checksum_ok():
            comment = comment + " Checksum error!"

        return ":{bc} {ad} {rt} {data} {cs} # {cmt}".format(
            bc=raw_hex(self.bytecount),
            ad=raw_hex_list(self.address),
            rt=raw_hex(self.recordtype),
            data=raw_hex_list(self.data),
            cs=raw_hex(self.checksum),
            cmt=comment)


class IntelHexDecoder(object):
    def __init__(self):
        self.extended_segment_base_address = 0
        self.extended_linear_address = 0

    def tokenize(self, line):
        start, bytecount, remaining = line[0:1], line[1:3], line[3:]
        if start != ":":
            return None

        try:
            bytecount = int(bytecount, 16)
        except ValueError:
            return None

        values = []
        for count in range(2 + 1 + bytecount + 1):
            try:
                num = int(remaining[0:2], 16)
                values.append(num)
            except ValueError:
                return None
            remaining = remaining[2:]

        address = values[0:2]
        recordtype = values[2]
        data = values[3:bytecount + 3]
        checksum = values[bytecount + 3]
        return IntelHexRecord(start, bytecount, address, recordtype, data, checksum)

    def decode_line(self, line):
        hex_record = self.tokenize(line)
        if hex_record is None:
            return None

        if hex_record.recordtype == 2:
            self.extended_segment_base_address = to_address(hex_record.data[0], hex_record.data[1]) << 4
            self.extended_linear_address = 0
        if hex_record.recordtype == 4:
            self.extended_linear_address = to_address(hex_record.data[0], hex_record.data[1]) << 16
            self.extended_segment_base_address = 0

        return hex_record.to_extended_with_comment(offset=self.extended_linear_address + self.extended_segment_base_address)

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        print("Loading ", filename)
    except IndexError:
        from os.path import split
        print("Usage: ", split(sys.argv[0])[1], "<filename>")
        sys.exit()

    f = open(filename)

    print("startcode bytecount address recordtype data  checksum")
    print("example:")
    print(":         10        0000    00         12345 FF")
    print("")

    decoder = IntelHexDecoder()

    for line in f.readlines():
        print(decoder.decode_line(line.strip()))
