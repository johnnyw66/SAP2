.org 0
; Build this with the Python assembler.py utility
; ./assembler.py djnz.asm
; to produce djnz.hex
:start
  movi r0,255
  out r0
  djnz r0,start
  hlt

.end