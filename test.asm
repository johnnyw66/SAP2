.org 0
:start
  call testsubi
  hlt


  :testsubi
    clc
    ld r0,addstuff0
    subi r0,0x32 ;  0x04

    clc
    ld r1,addstuff1
    subi r1,0x12 ; 0x00

    clc
    ld r2,addstuff2
    subi r2,0x20  ; 0x12

    clc
    ld r3,addstuff3
    subi r3,0x24 ; 0x23
    ret

:testaddi
  clc
  ld r0,addstuff0
  addi r0,0x32 ; 0x68

  ld r1,addstuff1
  addi r1,0x44 ; 0x56

  ld r2,addstuff2
  addi r2,0x78  ; 0xaa

  setc
  ld r3,addstuff3
  addi r3,0x25 ; 0x6d (0x6c + carry)
  ret

:addstuff0
.db 0x36
:addstuff1
.db 0x12
:addstuff2
.db 0x32
:addstuff3
.db 0x47


:wrnld
    call writetest
    call loadldtest
    ret



    :data1
      .db 0xaa
    :data2
      .db 0xbb
    :data3
      .db 0xcc
    :data4
      .db 0xdd

:writetest
  movi r0,0x01
  movi r1,0x02
  movi r2,0x03
  movi r3,0x04
  st r0,data1
  st r1,data2
  st r2,data3
  st r3,data4
  ret


:loadldtest
    ld r0,data1
    ld r1,data2
    ld r2,data3
    ld r3,data4
    ret

:stldtest
ret




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
  movi r0,0xad
  movi r1,0xbe
  movi r2,0xcf
  movi r3,0xd0
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
