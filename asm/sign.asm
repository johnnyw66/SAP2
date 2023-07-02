.org 0x8000

 movi r0,1
 movi r1,20
:loop
 sub r1,r0
 out r1
 jpv stop
 jmp loop
:stop
 hlt

.end
