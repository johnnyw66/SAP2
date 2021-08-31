  .org 0x8000

:start
      call multtest2
      hlt

:multtest1
      movi r0, 0x37
      movi r1, 0x00   ; mov r0r1, 0x0037

      movi r2, 0x40
      movi r3, 0x00    ; mov r2r3, 0x0040
      ; Answer should be 0xdc0
      call mult16
      ret

:multtest2

      exx
      movi r0,0xdd
      movi r1,0xcc
      movi r2,0xbb
      movi r3,0xaa
      exx

      movi r0, 0xab
      movi r1, 0x00   ; mov r0r1, 0x00ab

      movi r2, 0x78
      movi r3, 0x01    ; mov r2r3, 0x0178
      ; Answer should be 0xfb28
      call mult16
      ret


  :mult16
      ; r0r1 = r0r1 x r2r3
      exx
      push r0     ; preserve main bank regs
      push r2

      movi r0,0
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
