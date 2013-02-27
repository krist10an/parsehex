
import sys

try:
    filename = sys.argv[1]
    print "Loading ", filename
except IndexError:
    from os.path import split
    print "Usage: ", split(sys.argv[0])[1], "<filename>"
    sys.exit()

f = open(filename)

records = [ 'Data record',
            'End Of File record',
            'Extended Segment Address Record',
            'Start Segment Address Record',
            'Extended Linear Address Record',
            'Start Linear Address Record' ]

print "startcode bytecount address recordtype data  checksum"
print "example:"
print ":         10        0000    00         12345 FF"
print ""

extended_segment_base_address = 0
extended_linear_address = 0

for line in f.readlines():
    line = line.strip()

    checksum = 0
    start, bytecount, address, recordtype, data = \
           line[0:1], line[1:3], line[3:7], line[7:9], line[9:]

    # split out checksum
    try:
        bc = int(bytecount, 16) * 2
        checksum = data[bc:]
        data = data[0:bc]
    except ValueError:
        pass

    try:
        recordtype = int(recordtype)
        comment = " - " + records[recordtype]

    except ValueError:
        recordtype = -1
        comment = ""

    try:
        address = int(address, 16)
    except ValueError:
        print "convert error"
        address = "unknown"

    if recordtype == 2:
        extended_segment_base_address = int(data, 16) << 4
        extended_linear_address = 0
        print "esba: ", extended_segment_base_address, address
    if recordtype == 4:
        extended_linear_address = int(data, 16) << 16
        extended_segment_base_address = 0
        print "ela: ", extended_linear_address, address

    ad = 0
    if recordtype == 0:
        ad = extended_linear_address + extended_segment_base_address + address

    print start, bytecount, address, recordtype, data, checksum, comment, "@", hex(ad)
