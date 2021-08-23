.org 0
  jmp testincdec
  hlt

:testincdec1reg
    inc r0
    inc r1
    inc r2
    inc r3
    hlt


:testincdec
  inc r0
  inc r1
  inc r2
  inc r3
  exx
  dec r0
  dec r1
  dec r2
  dec r3
  exx
  hlt




:test1
  call init
  call display
  exx
  call display
  exx
  ret

:test2
  call init
  call flip
  call display
  ret

:test3
  movi r0,255
:loopdisp
  out r0
  djnz r0, loopdisp
  ret


:startpoint
  .db 10

:test4
  ld r0,startpoint
:loopdisp4
  out r0
  djnz r0, loopdisp4
  ret


:writepoint
    .db 0xaa
:test5
  movi r0,0
:ltest5
  inc r0
  out r0
  st r0,writepoint
  jmp ltest5


:flip
  push r0
  push r2
  pop r0
  pop r2
  ret



:display
  out r0
  out r1
  out r2
  out r3
  ret

:init
  movi r0,0xa1
  movi r1,0xb2
  movi r2,0xc3
  movi r3,0xd4
  exx
  movi r0,0x4f
  movi r1,0x3e
  movi r2,0x2d
  movi r3,0x1c
  exx
  ret

.end
