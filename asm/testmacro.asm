
; Preprocess this source with the standard C preprocessor 'cpp'
; Eg. 'cpp -DADDRESS=0x1234 -P testmacro.asm testmacro_cpped.asm'
; and then assemble the processed cpp version - 'python3 assember.py testmacro_cpped.asm'


## We have more to this

#ifndef ADDRESS
#define ADDRESS 0x8000
#endif

#define multbit(_skipadd)  clc \
                          shr r1 \
                          shr r0 \
                          jpnc _skipadd \
                          push r2 \
                          exx \
                          pop r2 \
                          clc \
                          add r0,r2 \
                          add r1,r3 \
                          exx \
                    :_skipadd \
                          clc \
                          shl r2 \
                          shl r3

;                         RAM Source
                          .org ADDRESS

:start
                          movi r0, 0xab
                          movi r1, 0x00   ; mov r0r1, 0x00ab

                          movi r2, 0x78
                          movi r3, 0x01    ; mov r2r3, 0x0178
                          ; Answer should be 0xfb28

                          call mult16bit
                          hlt

:mult16bit
                          ; r0r1 = r0r1 x r2r3
                          exx
                          push r0     ; preserve main bank regs
                          push r2
                          movi r0,0
                          movi r1,0
                          exx

                          multbit(bit0)
                          multbit(bit1)
                          multbit(bit2)
                          multbit(bit3)

                          multbit(bit4)
                          multbit(bit5)
                          multbit(bit6)
                          multbit(bit7)

                          multbit(bit8)
                          multbit(bit9)
                          multbit(bit10)
                          multbit(bit11)

                          multbit(bit12)
                          multbit(bit13)
                          multbit(bit14)
                          multbit(bit15)


                          ; place answer in the bank we started with
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

                          .end
