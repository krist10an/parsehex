
import sys

def raw_hex(val):
    return hex(val)[2:].upper()

class IntelHexDecoder(object):
    def __init__(self):
        self.records = [ 'Data record',
            'End Of File record',
            'Extended Segment Address Record',
            'Start Segment Address Record',
            'Extended Linear Address Record',
            'Start Linear Address Record' ]
        self.extended_segment_base_address = 0
        self.extended_linear_address = 0

    def record_name(self, id):
        return self.records[id]

    def tokenize(self, line):
        start, bytecount, address, recordtype, data = line[0:1], line[1:3], line[3:7], line[7:9], line[9:]
        if start != ":":
            return None

        try:
            bytecount = int(bytecount, 16)
            bc = bytecount * 2
            checksum = data[bc:]
            data = data[0:bc]
        except ValueError:
            return None

        try:
            checksum = int(checksum, 16)
            recordtype = int(recordtype, 16)
            address = int(address, 16)
        except ValueError:
            return None

        return start, bytecount, address, recordtype, data, checksum

    def decode_line(self, line):
        tokens = self.tokenize(line)
        if tokens is None:
            return None

        start, bytecount, address, recordtype, data, checksum = tokens

        if recordtype == 2:
            self.extended_segment_base_address = int(data, 16) << 4
            self.extended_linear_address = 0
            print "esba: ", self.extended_segment_base_address, address
        if recordtype == 4:
            self.extended_linear_address = int(data, 16) << 16
            self.extended_segment_base_address = 0
            print "ela: ", self.extended_linear_address, address

        comment = "# " + self.record_name(recordtype) + " @ " + str(address)

        return "%s%2s %4s %2s %s %2s %s" % (start, raw_hex(bytecount), raw_hex(address), raw_hex(recordtype), data.ljust(32), raw_hex(checksum), comment)


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        print "Loading ", filename
    except IndexError:
        from os.path import split
        print "Usage: ", split(sys.argv[0])[1], "<filename>"
        sys.exit()

    f = open(filename)

    print "startcode bytecount address recordtype data  checksum"
    print "example:"
    print ":         10        0000    00         12345 FF"
    print ""

    decoder = IntelHexDecoder()

    for line in f.readlines():
        print decoder.decode_line(line.strip())
