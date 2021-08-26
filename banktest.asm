.org 0x8000
; Build this with the Python assembler.py utility
; ./assembler.py djnz.asm
; to produce djnz.hex

:start
  movi r0,0xaf
  movi r1,0xbe
  movi r2,0xcd
  movi r3,0xdc

  exx
  movi r0,0xf1
  movi r1,0xe2
  movi r2,0xd3
  movi r3,0xe4

:flip
  exx
  out r0
  nop
  out r1
  nop
  out r2
  nop
  out r3
  nop
  jmp flip

  hlt

.end
