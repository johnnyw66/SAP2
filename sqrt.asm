.org 0x8000

movi r0,197
movi r1,1
movi r2,1

:loop
; Display the current estimate of sqr(197)
out r2
sub r0,r1
jpnv continue
hlt
:continue
addi r1,2
inc r2
jmp loop

.end
