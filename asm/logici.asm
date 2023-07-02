.org 0x8000
:start
  movi r0,100
  movi r1,200

  call flipr0r1
  xori r1,100
  xori r0,200
  hlt



:flipr0r1

  xor r0,r1
  xor r1,r0
  xor r0,r1
  ret


.end
