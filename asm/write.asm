.org 0x8000


:start
:test1b
  movi r0,0xff
  st r0,0x7ffe
  movi r0,0x00
  st r0,0x7ffe
  jmp test1b




:test1a
    mov r0,r0
    addi r0,22
    jmp test1a

:test1
  ; PASS
  nop
  jmp test1


:test2
    ;PASS
    movi r3,0xff
    jmp test2

:test3
    ; FAILED CONTENTION
    addi r3,0xaa
    jmp test3

:test4
    ; PASS
    movi r3,0xaa
    jmp test4

:test5
      movi r3,0xff
      st r3,0xfffe
      jmp test5


:test6
      movi r0,0
:test6a
      movi r3,0xff
      st r3,0xfffe
      jpnz test6a
      jmp test6


  .end
