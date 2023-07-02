.org 0x8000

; This simple program counts down, displaying numbers 255 to 1
; on the display unit.

; Build this with the Python assembler.py utility
; ./assembler.py display.asm
; to produce the assembled program 'display.hex'
; Then load the file display.hex into ram by
; moving the mouse pointer over the 'RAM MODULE' (whilst running LogiSim)
; right clicking the mouse and selecting 'Load Image'.
; Finally search, select and 'open' the file 'display.hex'.

; To run the program the program, reset the microprocessor (CMD/CTRL 'R')
; and then select CMD/CTRL 'K' to start the microprocessor clock.
; You can change the clock speed of the microprocessor by
; selecting the 'Simulate' option and 'Auto Tick Frequency'.

:start
  movi r0,255
:display
  out r0
  djnz r0,display
  hlt
.end
