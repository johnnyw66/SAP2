
  .org 0x8000
;  push r0
;  csp r0
;  push r2
;  csp r2

  movwi r0,somelabel
  ; above is equiv to ...
  movi r0,>somelabel
  movi r1,<somelabel
  .db 0x4e            ;
  addi r0,1
  addi r1,0
  .db 0x4f

;  movwi r0,0x1234
;  movwi r2,0xabcd
;  swp r0,r2
;  swp r1,r3

  hlt

  .ds 200
:somelabel
  .dw 0x1234


  .end
