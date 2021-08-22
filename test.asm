.org 100
:start
  mov r0,r1
  mov r2,r3
  movi r3,255
:LOOP
  add r2,r0
  out r2
  djnz r3, LOOP
  movi r3,100
  out r3
  
.end
