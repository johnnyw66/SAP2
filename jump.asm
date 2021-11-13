	.org 0x8000
	jmp				label
	jmp      label
	jmpv label
	jpz label
	jpnz label
	jpv label
	jpnv label

:label
	.db 0xff
