.org 0
jmp 0x8000
.dt 'ROM (C) John Wilson 2021.'

.org 0x100
  jmp beep
  jmp swap

:beep
  push r0
  push r2


  pop r2
  pop r0
  ret

:swap
    xor r0,r1
    xor r1,r0
    xor r0,r1
    ret


.org 0x7000
.dt 'SIN'
.dt 'COS'
.db 0x66
.db 0x60

.end
