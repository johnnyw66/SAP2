.org 0x8000

  movi r0,0

:sound
  movi r2,10
:loop1
  st r0,0xffff0
  djnz r2,loop1
  xori r0,1
  movi r2,10
:loop2
  st r0,0xffff0
  djnz r2,loop2
  jmp sound
  hlt

  .end
