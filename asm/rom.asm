.org 0
jmp 0x8000
.dt 'ROM (C) John Wilson 2021.'

.org 0x100
  jmp beep
  jmp swap
  jmp mult16




.org 0x1000

:mult16
    ; r0r1 = r0r1 x r2r3
    exx
    push r0     ; preserve secondary bank regs
    push r2

    movi r0,0   ; set total to 0
    movi r1,0
    exx

    call mul16bit
    call mul16bit
    call mul16bit
    call mul16bit

    call mul16bit
    call mul16bit
    call mul16bit
    call mul16bit


    call mul16bit
    call mul16bit
    call mul16bit
    call mul16bit

    call mul16bit
    call mul16bit
    call mul16bit
    call mul16bit

    ; place answer in r0r1 pair - in the bank we started with
    exx
    push r0
    exx
    pop r0

    ; Restore secondary bank regs
    exx
    pop r2
    pop r0
    exx

    ret


:mul16bit
    clc
    shr r1
    shr r0
    jpnc skipadd
    ; addition total is kept by alternative r0/r1 pair
    push r2
    exx
    pop r2
    clc
    add r0,r2
    add r1,r3
    exx

:skipadd
    clc
    shl r2
    shl r3
    ret



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
