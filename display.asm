.org 0x8000
; Build this with the Python assembler.py utility
; ./assembler.py djnz.asm
; to produce djnz.hex

:start
  movi r0,255
:display
  out r0
  st r0,0
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP
  NOP

  ld r2,0x3fff

  djnz r0,display
  hlt
.end
