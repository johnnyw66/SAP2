.org 0
:start
    movi r0,1
    out r0
    movi r1,7
:shft

    shl r0
    out r0 ;2

    shl r0
    out r0 ;4

    shl r0
    out r0 ;8

    shl r0
    out r0 ;16

    shl r0
    out r0 ;32

    shl r0
    out r0 ; 64

    ;djnz r1,shft
    hlt

:strobe
  movi r1,255
:lightup
  call alulights
  djnz r1, lightup
  ret


:alulights
      add r0,r0
      sub r0,r0
      shl r0
      shr r0
      and r0,r0
      or  r0,r0
      xor r0,r0
      ret


.end
