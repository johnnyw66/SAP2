  .org 0x8000
#define tableentry(_nm) jmp _nm \
                        nop

:start
  movwi r0,0x1234
  movwi r2,0xabcd

  movi r0,0
  call indexjmp

  movi r0,1
  call indexjmp

  movi r0,2
  call indexjmp

  movi r0,0x66
  out r0
  hlt

:indexjmp
    ; Call from a list of functions define at 'functable'
    ; indexed by the lower 6-bit number in R0 -

    ; Assuming our table has each entry defined by
    ; 4 bytes - (1 x jpm addr + 1 x nop instructions) -
    ; we simply multiply the 16 bit value R1R0 pair by 4
    ; and add the result to the address
    ; of the start of the table (functable).
    ; The resultant address is pushed onto the stack
    ; and called by executing a RET instruction

    andi r0,0x3f
    movi r1,0
    clc
    shl r0
    shl r1
    shl r0
    shl r1
    
    movi r2,@LOW(functable)
    movi r3,@HIGH(functable)

    add  r2,r0
    add r3,r1

    push r2
    ret





:fnc1
    movi r0,0x11
    out r0
    ret

:fnc2
    movi r0,0x22
    out r0
    ret

:fnc3
    movi r0,0x33
    out r0
    ret

.org 0x8100
:functable
    tableentry(fnc1)
    tableentry(fnc2)
    tableentry(fnc3)

    .end
