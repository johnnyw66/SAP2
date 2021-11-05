.org 0x8000

movi r0,197
movi r1,1
movi r2,1

:loop
; Display the current estimate of sqr(197)
out r2
sub r0,r1
jpnc continue
hlt
:continue
addi r1,2
addi r2,1
jmp loop

.end
