.org 0x8000
; Build this with the Python assembler.py utility
; ./assembler.py djnz.asm
; to produce djnz.hex

:start
  movi r0,255
:display
  out r0
  djnz r0,display
  hlt

.end
