.org 0x8000
:start
  ; eat_comment
  movwi sp,0xffff ;xxx
  inc sp
  dec sp
  movi r0,255
  and r2,r3
  andi r3,255
  ld r0,counter
  st r0,here
  mov r0,r1
  mov r2,r3
  movi r3,255
:LOOP
  add r2,r0
  call outputchar
  djnz r3, LOOP
  movi r3,100
  out r3
  hlt

:outputchar
  exx
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  nop
  out r2
  exx
  ret

:counter
  .db 255
:here
.db 0
.ds 20
:otherlabel
.db 11
.dw 257

.end
