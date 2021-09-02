  .org 0x8000
:start
;  ld r0,0x000

;  .dt 'ABC'
;  movi r0,100

  movi r2,0xaa
  movi r3,0x81

  movi r2,@LOW(0x81aa)
  movi r3,@HIGH(0x81aa)

  movi r2,@LOW(here)
  movi r3,@HIGH(here)

;  hlt

  .org 0x81aa
:here
  .ds 0x200
