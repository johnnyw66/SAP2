  mov r0,r0
  mov r0,r1
  mov r0,r2
  mov r0,r3
  mov r1,r0
  mov r1,r1
  mov r1,r2
  mov r1,r3
  mov r2,r0
  mov r2,r1
  mov r2,r2
  mov r2,r3
  mov r3,r0
  mov r3,r1
  mov r3,r2
  mov r3,r3

  add r0,r0
  add r0,r1
  add r0,r2
  add r0,r3
  add r1,r0
  add r1,r1
  add r1,r2
  add r1,r3
  add r2,r0
  add r2,r1
  add r2,r2
  add r2,r3
  add r3,r0
  add r3,r1
  add r3,r2
  add r3,r3

  sub r0,r0
  sub r0,r1
  sub r0,r2
  sub r0,r3
  sub r1,r0
  sub r1,r1
  sub r1,r2
  sub r1,r3
  sub r2,r0
  sub r2,r1
  sub r2,r2
  sub r2,r3
  sub r3,r0
  sub r3,r1
  sub r3,r2
  sub r3,r3

  and r0,r0
  and r0,r1
  and r0,r2
  and r0,r3
  and r1,r0
  and r1,r1
  and r1,r2
  and r1,r3
  and r2,r0
  and r2,r1
  and r2,r2
  and r2,r3
  and r3,r0
  and r3,r1
  and r3,r2
  and r3,r3

  or r0,r0
  or r0,r1
  or r0,r2
  or r0,r3
  or r1,r0
  or r1,r1
  or r1,r2
  or r1,r3
  or r2,r0
  or r2,r1
  or r2,r2
  or r2,r3
  or r3,r0
  or r3,r1
  or r3,r2
  or r3,r3

  xor r0,r0
  xor r0,r1
  xor r0,r2
  xor r0,r3
  xor r1,r0
  xor r1,r1
  xor r1,r2
  xor r1,r3
  xor r2,r0
  xor r2,r1
  xor r2,r2
  xor r2,r3
  xor r3,r0
  xor r3,r1
  xor r3,r2
  xor r3,r3

  movi r0,0x01
  movi r1,0xf0
  movi r2,0x0f
  movi r3,0xee

  add r0,0xef
  add r1,0xef
  add r2,0xef
  add r3,0xef

  sub r0,0xef
  sub r1,0xef
  sub r2,0xef
  sub r3,0xef

  and r0,0xef
  and r1,0xef
  and r2,0xef
  and r3,0xef

  or r0,0xef
  or r1,0xef
  or r2,0xef
  or r3,0xef

  xor r0,0xef
  xor r1,0xef
  xor r2,0xef
  xor r3,0xef

  out r0
  out r1
  out r2
  out r3

  inc r0
  inc r1
  inc r2
  inc r3

  dec r0
  dec r1
  dec r2
  dec r3

  ld r0,0xff00
  ld r1,0xff01
  ld r2,0xff02
  ld r3,0xff03

  st r0,0xff00
  st r1,0xff01
  st r2,0xff02
  st r3,0xff03




.end
