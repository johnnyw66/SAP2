.org 0x8000
movi r0,0xa1
movi r1,0xb2
movi r2,0x3c
movi r3,0x4d
; flip reg pairs
call flipndisplay
hlt


:flipndisplay
  call display
  call flipem

  exx
  movi r0,0xaa
  out r0
  movi r1,255
:here
  djnz r1, here ; just loop for a while
  exx

  call display
  ret

:display
  out r0
  out r1
  out r2
  out r3
  ret

:flipem
  push r0
  push r2
  pop r0
  pop r2
  ret
