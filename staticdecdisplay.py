negseg = 0x80
emptyseg = 0x00
blanksegoffset = 10
negsegoffset = 11

segdigits = [0x7e, 0x12, 0xbc, 0xb6, 0xd2, 0xe6, 0xee, 0x32, 0xfe, 0xf6, emptyseg, negseg]


def writeSegData(file, signed):
	for n in range(0, 256):
		v = n if not signed else ((n ^ 255)) + 1 if (n & 128 != 0) else n
		negative = False if not signed else (n & 128 != 0)
		units = v % 10
		tens = (v // 10) % 10
		hundreds = v // 100
		segs = segdigits[negsegoffset if negative else blanksegoffset] << 24 | \
				segdigits[blanksegoffset if hundreds == 0 else hundreds] << 16 | \
				segdigits[blanksegoffset if v < 10 else tens] << 8 | \
				segdigits[units]
		file.write("{0:08x} ".format(segs))


file = open("staticdecdisplayrom", "w+")
file.write("v2.0 raw\n")
writeSegData(file, False)
writeSegData(file, True)

file.close();
