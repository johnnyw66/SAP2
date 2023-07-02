.org 0x8000
; Build this with the Python assembler.py utility
; ./assembler.py djnz.asm
; to produce djnz.hex
  movi r0,255
:loop
  out r0
  djnz r0,loop
  hlt

.end
