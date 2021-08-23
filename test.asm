.org 0
  call testmov1
  hlt

:testmov
  call testmov0
  call testmov1
  call testmov2
  call testmov3
  ret

:teststack
  inc sp
  inc sp
  dec sp
  dec sp
  ret

:testmov0
  call inittestmov
  mov r0,r0
  mov r0,r1
  mov r0,r2
  mov r0,r3
  ret

:testmov1
  call inittestmov
  mov r1,r0
  mov r1,r1
  mov r1,r2
  mov r1,r3
  ret

:testmov2
  call inittestmov
  mov r2,r0
  mov r2,r1
  mov r2,r2
  mov r2,r3
  ret

:testmov3
  call inittestmov
  mov r3,r0
  mov r3,r1
  mov r3,r2
  mov r3,r3
  ret

:inittestmov
  movi r0,0xaa
  movi r1,0xbb
  movi r2,0xcc
  movi r3,0xdd
  ret


:testdjnz
  movi r0,10
  movi r1,12
  movi r2,13
  movi r3,14
:tdjnz0
  djnz r0,tdjnz0
:tdjnz1
  djnz r1,tdjnz1
:tdjnz2
  djnz r2,tdjnz2
:tdjnz3
  djnz r3,tdjnz3
  ret

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
