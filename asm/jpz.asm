  .org 0x8000
  movi r0,22
  movi r1,21
  sub r0,r1
  jpz zset
  movi r2,255
  out r2
  hlt
:zset
  movi r2,100
  out r2
  hlt
