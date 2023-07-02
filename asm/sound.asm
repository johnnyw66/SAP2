  .org 0x8000

  call sound1
  hlt

:sound1
  movi r0, 0xff
  movi r1, 0x00
  movi r2, 0x8f
  call playfreq
  movi r3,30
:delay
  out r3
  djnz r3,delay
  movi r2, 0x00
  call playfreq
  ret


:sound9
  movi r0, 0xff
  movi r1, 0x00
  movi r2, 0x8f

:loopsnd
  call playfreq
  djnz r0, loopsnd
  ret



:playfreq
  st r0,0x7ff0    ; low freq
  st r1,0x7ff1    ; high freq 6 bits
  st r2, 0x7ff2   ; vol and enable (top bit)
  ret


.end
