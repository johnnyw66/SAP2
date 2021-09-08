:start
  movi  r0,>label1
  movi  r1,<label1
;  movi  r0 ,@LOW(label1)
;  movi  r1 ,@HIGH(label1)
  movwi r2,label1
  movwi sp,0xfffe
  movwi r0,0x1234
  movwi r2,0xabcd
  movwi r0,start
  movwi r2,start

  nop
  clc
  setc
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
  nop

  out r0
  out r1
  out r2
  out r3


  ld r0,0x1234
  ld r1,0x5678
  ld r2,0x9abc
  ld r3,0xdef0

  st r0,0xabcd
  st r1,0x1234
  st r2,0x5678
  st r3,0x9abc

  movwi sp,0x0000
  inc sp
  dec sp
  push r0
  push r2
  pushall
  pop r0
  pop r2
  popall
  exx

  movi r0,0x01
  movi r1,0xf0
  movi r2,0x0f
  movi r3,0xee

  xori r0,0xef
  xori r1,0xef
  xori r2,0xef
  xori r3,0xef


  addi r0,0xef
  addi r1,0xef
  addi r2,0xef
  addi r3,0xef

  subi r0,0xef
  subi r1,0xef
  subi r2,0xef
  subi r3,0xef

  andi r0,0xef
  andi r1,0xef
  andi r2,0xef
  andi r3,0xef

  ori r0,0xef
  ori r1,0xef
  ori r2,0xef
  ori r3,0xef

  djnz r0,0x0000
  djnz r1,0x0000
  djnz r2,0x0000
  djnz r3,0x0000

  jpz 0x0000
  jpnz 0x0000
  jpc 0x0000
  jpnc 0x0000
  jps 0x0000
  jpns 0x0000
  jpo 0x0000
  jpno 0x0000
  jmp 0x0000
  nop
  call 0x0000
  ret

  shr r0
  shr r1
  shr r2
  shr r3

  shl r0
  shl r1
  shl r2
  shl r3

  inc r0
  inc r1
  inc r2
  inc r3

  dec r0
  dec r1
  dec r2
  dec r3

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

  hlt


  :label2
  .db 0
  .ds 20
  :label1
  .db 0
  .ds 200
  .dt 'Hello World (c) 2021    '
  nop

.end
