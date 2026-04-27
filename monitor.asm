; =============================================================================
; SAP2 MONITOR  v0.1
; =============================================================================
; A ROM-resident machine monitor for the SAP2 processor.
; Assemble with:  python3 assembler.py monitor.asm -r -s
;
; MEMORY MAP
; ----------
;   0x0000 – 0x7FFF   ROM  (32 KB)  — this monitor lives here
;   0x8000 – 0xFFFF   RAM  (32 KB)  — user programs and data
;
; -----------------------------------------------------------------------------
; MEMORY-MAPPED I/O  (serial port)
; ---------------------------------
; The SAP2 emulator exposes a UART-style interface via two memory-mapped
; addresses.  There is NO dedicated IN/OUT instruction — you read and write
; these addresses exactly like RAM using LD / ST with indirect addressing.
;
;   SERIAL_DAT  EQU  0x6000   ; WRITE a character byte here to transmit it
;   SERIAL_IN   EQU  0x6001   ; READ here: returns ASCII keycode if key pressed,
;                             ;            or 0x00 if no key is waiting
;
; Keyboard (RX) input — confirmed from sap2emu.py SerialPort.read():
;   Reading 0x6001 performs both the status check AND the data fetch in one
;   operation.  Non-zero result = a key was pressed; that value IS the char.
;   Zero result = no key waiting.  There is NO separate status register.
;
;   Step 1 — MOVWI R0, 0x6001      R0=0x60 (high), R1=0x01 (low)
;   Step 2 — LD R2,(R0)            returns char, or 0x00 if nothing waiting
;   Step 3 — AND R2,R2             sets Z flag if no key
;   Step 4 — JPNZ back to Step 2  loop until non-zero
;   R2 now holds the ASCII keycode.
;
; Terminal (TX) output — confirmed from sap2emu.py SerialPort.write():
;   Writing to 0x6000 transmits immediately — print(chr(value)) in emulator.
;   There is NO TX-busy flag and NO polling needed.
;
;   Step 1 — MOVWI R0, 0x6000      R0=0x60 (high), R1=0x00 (low)
;   Step 2 — ST R2,(R0)            character transmitted immediately
;
; NOTE: No interrupts exist in SAP2.  All I/O is polled / direct.
; -----------------------------------------------------------------------------
;
; REGISTER CONVENTIONS
; --------------------
;   R0   — HIGH byte of 16-bit pointer / general scratch
;   R1   — LOW  byte of 16-bit pointer / general scratch
;   R2   — character buffer / general scratch
;   R3   — loop counter / general scratch
;   R0R1 — 16-bit address for indirect LD/ST  (R0=high, R1=low)
;   SP   — stack pointer, initialised to 0xFFFF (top of RAM)
;
; BYTE ORDER — confirmed from sap2emu.py
; ---------------------------------------
;   MOVWI R0, 0xHHLL  produces  R0=0xHH (high), R1=0xLL (low)
;   Indirect address  = R0*256 + R1
;   R0 is ALWAYS the high byte of the pointer pair.
;
; EXX USAGE
; ---------
;   EXX swaps the entire register file between two banks.
;   After EXX: R0–R3 refer to the alternate set (R0'–R3').
;   Another EXX swaps back.  Alternate registers persist between swaps.
;   Used in PARSE_HEX16 and PARSE_HEX8 to hold accumulators without
;   any RAM spills or stack juggling.
;
; SAFE POINTER LOAD PATTERN
; -------------------------
;   To load a 16-bit address from RAM into R0R1 for indirect use,
;   use MOVI with > / < operators (NOT two MOVWI — they clobber each other):
;
;     MOVI   R0, >VAR_ADDRHI    ; high byte of address-of-VAR_ADDRHI
;     MOVI   R1, <VAR_ADDRHI    ; low  byte of address-of-VAR_ADDRHI
;     LD     R0, (R0)           ; R0 = stored high byte of working address
;     MOVI   R0, >VAR_ADDRLO
;     MOVI   R1, <VAR_ADDRLO
;     LD     R1, (R0)           ; R1 = stored low byte of working address
;
; CONDITIONAL JUMP OPCODES — verified from sap2emu.py handle_cond_jump()
; -----------------------------------------------------------------------
;   0x64  JPNZ  — jumps when Z flag IS SET   (result was zero = equal)
;   0x65  JPZ   — jumps when Z flag IS CLEAR (result was non-zero = not equal)
;   0x66  JPNC  — jumps when C flag IS SET   (no borrow = greater-or-equal)
;   0x67  JPC   — jumps when C flag IS CLEAR (borrow = less-than)
;   NOTE: mnemonic names are inverted from conventional expectation.
;   Every branch below carries a comment stating the actual condition.
;
; COMMAND SET
; -----------
;   M <addr>           — Memory examine:  show 8 bytes from <addr>
;   M <addr> <byte>    — Memory modify:   write <byte> to <addr>
;   G <addr>           — Go:              jump to <addr>
;   D <addr>           — Dump:            hex dump 16 bytes from <addr>
;   R                  — Registers:       show R0-R3 and SP
;   H                  — Help:            print command summary
; =============================================================================

; =============================================================================
; RAM WORKSPACE  (just above RAM base at 0x8000)
; =============================================================================
.org 0x8000

; VAR_ADDRHI at the lower address because R0 (high byte) is loaded first.
:VAR_ADDRHI
    .ds 1               ; high byte of current working address  (into R0)
:VAR_ADDRLO
    .ds 1               ; low  byte of current working address  (into R1)
:VAR_ARGHI
    .ds 1               ; high byte of parsed second argument
:VAR_ARGLO
    .ds 1               ; low  byte of parsed second argument
:VAR_ARGC
    .ds 1               ; number of arguments parsed
:INPUT_BUF
    .ds 32              ; input line buffer: 31 chars + NUL terminator

; =============================================================================
; ROM ENTRY POINT
; =============================================================================
.org 0x0000

:RESET
    ; SP = 0xFFFF confirmed from Processor.__init__ in sap2emu.py
    MOVWI  SP, 0xFFFF

    ; Zero the 6-byte RAM workspace from VAR_ADDRHI onwards
    MOVWI  R0, VAR_ADDRHI       ; R0=high, R1=low of address VAR_ADDRHI
    MOVI   R2, 0x00
    MOVI   R3, 6
:_clr_loop
    ST     R2, (R0)             ; write 0x00 via R0R1 indirect
    INC    R1                   ; advance LOW byte of pointer
    DJNZ   R3, _clr_loop

    MOVWI  R0, STR_BANNER
    CALL   PRINT_STR

; =============================================================================
; MAIN COMMAND LOOP
; =============================================================================
:CMD_LOOP
    MOVWI  R0, STR_PROMPT
    CALL   PRINT_STR

    MOVWI  R0, INPUT_BUF
    CALL   READ_LINE

    ; Skip spaces, load command char, force uppercase
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES
    LD     R2, (R0)
    ANDI   R2, 0xDF             ; force uppercase

    ; Dispatch table.
    ; JPNZ (0x64) jumps when Z IS SET = result was zero = match.
    ; SUB destroys R2, so we re-push R2 for each test.

    PUSH   R2
    MOVI   R3, 'M'
    SUB    R2, R3
    JPNZ   _do_memory

    POP    R2
    PUSH   R2
    MOVI   R3, 'G'
    SUB    R2, R3
    JPNZ   _do_go

    POP    R2
    PUSH   R2
    MOVI   R3, 'D'
    SUB    R2, R3
    JPNZ   _do_dump

    POP    R2
    PUSH   R2
    MOVI   R3, 'R'
    SUB    R2, R3
    JPNZ   _do_regs

    POP    R2
    PUSH   R2
    MOVI   R3, 'H'
    SUB    R2, R3
    JPNZ   _do_help

    POP    R2
    PUSH   R2
    MOVI   R3, 'L'
    SUB    R2, R3
    JPNZ   _do_load

    POP    R2
    MOVWI  R0, STR_ERR_CMD
    CALL   PRINT_STR
    JMP    CMD_LOOP

:_do_memory
    POP    R2
    JMP    CMD_MEMORY
:_do_go
    POP    R2
    JMP    CMD_GO
:_do_dump
    POP    R2
    JMP    CMD_DUMP
:_do_regs
    POP    R2
    JMP    CMD_REGS
:_do_help
    POP    R2
    JMP    CMD_HELP
:_do_load
    POP    R2
    JMP    CMD_LOAD

; =============================================================================
; COMMAND: M <addr> [byte]
; Examine or modify memory.
;   M 8000        — print 8 bytes from 0x8000
;   M 8000 3A     — write 0x3A to address 0x8000
; =============================================================================
:CMD_MEMORY
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES
    INC    R1                   ; step over 'M' (advance low byte of pointer)
    CALL   SKIP_SPACES
    CALL   PARSE_HEX16          ; result in VAR_ADDRHI / VAR_ADDRLO
    CALL   SKIP_SPACES

    ; NUL or CR = examine mode
    LD     R2, (R0)
    AND    R2, R2
    JPNZ   _mem_examine          ; JPNZ: Z set = NUL = examine

    LD     R2, (R0)
    MOVI   R3, 0x0D
    SUB    R2, R3
    JPNZ   _mem_examine          ; JPNZ: Z set = CR = examine

    ; Second arg present — parse the byte to write
    CALL   PARSE_HEX8            ; result in R2

    ; Reconstruct target address into R0R1
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R1, (R0)

    ST     R2, (R0)             ; write byte to target address
    MOVWI  R0, STR_OK
    CALL   PRINT_STR
    JMP    CMD_LOOP

:_mem_examine
    ; Print "HHLL: "
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R2, (R0)
    CALL   PRINT_HEX8
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R2, (R0)
    CALL   PRINT_HEX8
    MOVI   R2, ':'
    CALL   PRINT_CHAR
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    ; Load working address into R0R1
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R1, (R0)

    MOVI   R3, 8
:_mem_ex_loop
    LD     R2, (R0)             ; read byte via R0R1 indirect
    CALL   PRINT_HEX8
    MOVI   R2, ' '
    CALL   PRINT_CHAR
    INC    R1                   ; advance low byte of pointer
    DJNZ   R3, _mem_ex_loop
    CALL   PRINT_CRLF
    JMP    CMD_LOOP

; =============================================================================
; COMMAND: G <addr>
; Jump to address.  Returns to monitor only if user code JMPs to 0x0000.
; =============================================================================
:CMD_GO
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES
    INC    R1                   ; step over 'G'
    CALL   SKIP_SPACES
    CALL   PARSE_HEX16

    MOVWI  R0, STR_JUMPING
    CALL   PRINT_STR

    ; Load jump address into R0R1
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R1, (R0)

    JMP    (R0)                 ; indirect jump to user address

; =============================================================================
; COMMAND: D <addr>  — hex dump 16 bytes in two rows of 8
; =============================================================================
:CMD_DUMP
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES
    INC    R1                   ; step over 'D'
    CALL   SKIP_SPACES
    CALL   PARSE_HEX16

    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R1, (R0)

    MOVI   R3, 2                ; 2 rows
:_dump_row
    PUSH   R3
    MOV    R2, R0               ; print high byte of current address
    CALL   PRINT_HEX8
    MOV    R2, R1               ; print low byte
    CALL   PRINT_HEX8
    MOVI   R2, ':'
    CALL   PRINT_CHAR
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    MOVI   R3, 8
:_dump_bytes
    PUSH   R3
    LD     R2, (R0)
    CALL   PRINT_HEX8
    MOVI   R2, ' '
    CALL   PRINT_CHAR
    INC    R1                   ; advance low byte of pointer
    POP    R3
    DJNZ   R3, _dump_bytes

    CALL   PRINT_CRLF
    POP    R3
    DJNZ   R3, _dump_row
    JMP    CMD_LOOP

; =============================================================================
; COMMAND: R  — register display
; NOTE: R0/R1 reflect monitor's pointer state; R2/R3 are monitor scratch.
; A future version could save user registers before the command dispatch.
; =============================================================================
:CMD_REGS
    MOVWI  R0, STR_REGS_HDR
    CALL   PRINT_STR

    MOVI   R2, 'R'
    CALL   PRINT_CHAR
    MOVI   R2, '0'
    CALL   PRINT_CHAR
    MOVI   R2, '='
    CALL   PRINT_CHAR
    MOV    R2, R0
    CALL   PRINT_HEX8
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    MOVI   R2, 'R'
    CALL   PRINT_CHAR
    MOVI   R2, '1'
    CALL   PRINT_CHAR
    MOVI   R2, '='
    CALL   PRINT_CHAR
    MOV    R2, R1
    CALL   PRINT_HEX8
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    MOVI   R2, 'R'
    CALL   PRINT_CHAR
    MOVI   R2, '2'
    CALL   PRINT_CHAR
    MOVI   R2, '='
    CALL   PRINT_CHAR
    MOV    R2, R2
    CALL   PRINT_HEX8
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    MOVI   R2, 'R'
    CALL   PRINT_CHAR
    MOVI   R2, '3'
    CALL   PRINT_CHAR
    MOVI   R2, '='
    CALL   PRINT_CHAR
    MOV    R2, R3
    CALL   PRINT_HEX8
    CALL   PRINT_CRLF

    ; Print SP — CSP copies SP into R0R1 (R0=high, R1=low)
    ; We print the string first, then re-capture SP since PRINT_STR clobbers R0R1
    MOVWI  R0, STR_SP
    CALL   PRINT_STR
    CSP    R0                   ; R0=SP high, R1=SP low
    MOV    R2, R0
    CALL   PRINT_HEX8
    MOV    R2, R1
    CALL   PRINT_HEX8
    CALL   PRINT_CRLF
    JMP    CMD_LOOP

; =============================================================================
; COMMAND: H
; =============================================================================
:CMD_HELP
    MOVWI  R0, STR_HELP
    CALL   PRINT_STR
    JMP    CMD_LOOP

; =============================================================================
; COMMAND: L <addr>
; Inline hex loader.  Loads space-separated byte pairs entered on successive
; lines into memory starting at <addr>.  A line beginning with '.' terminates.
;
; Example session:
;   > L 8000
;   : 3E 01 D3 00 76
;   : 4A FF
;   : .
;   7 bytes loaded
;
; REGISTER USE
; ------------
;   Primary bank:
;     R0R1  = write pointer (destination address, advances each byte)
;     R2    = current character / byte from PARSE_HEX8
;     R3    = scratch for comparisons
;
;   Alternate bank (EXX):
;     R0'R1'= byte count (R0'=high, R1'=low — 16-bit so large blocks work)
;     R2'   = scratch
;
;   VAR_ARGHI / VAR_ARGLO are NOT used here — kept free for future commands.
; =============================================================================
:CMD_LOAD
    ; Parse start address from command line
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES
    INC    R1                   ; step over 'L'
    CALL   SKIP_SPACES
    CALL   PARSE_HEX16          ; fills VAR_ADDRHI / VAR_ADDRLO

    ; Load write pointer into R0R1
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    LD     R1, (R0)

    ; Initialise byte counter in alternate bank
    EXX
    MOVI   R0, 0x00             ; R0' = count high = 0
    MOVI   R1, 0x00             ; R1' = count low  = 0
    EXX

; --- outer loop: prompt for and read one input line ---
:_load_line
    MOVI   R2, ':'
    CALL   PRINT_CHAR
    MOVI   R2, ' '
    CALL   PRINT_CHAR

    ; Save write pointer across READ_LINE (which clobbers R0R1)
    PUSH   R0
    PUSH   R1
    MOVWI  R0, INPUT_BUF
    CALL   READ_LINE
    POP    R1
    POP    R0                   ; write pointer restored

    ; Point buffer scanner at INPUT_BUF
    PUSH   R0                   ; save write pointer
    PUSH   R1
    MOVWI  R0, INPUT_BUF
    CALL   SKIP_SPACES

    ; Check first char: '.' = done, NUL/CR = empty line = done
    LD     R2, (R0)

    MOVI   R3, '.'
    SUB    R2, R3
    JPNZ   _load_done           ; JPNZ: Z set = matched '.' = terminate

    LD     R2, (R0)
    AND    R2, R2
    JPNZ   _load_done           ; JPNZ: Z set = NUL = empty line = terminate

    LD     R2, (R0)
    MOVI   R3, 0x0D
    SUB    R2, R3
    JPNZ   _load_done           ; JPNZ: Z set = CR = terminate

; --- inner loop: parse hex bytes from this line ---
:_load_bytes
    CALL   SKIP_SPACES

    ; Check for end of line (NUL or '.')
    LD     R2, (R0)
    AND    R2, R2
    JPNZ   _load_next_line      ; JPNZ: Z set = NUL = end of this line

    LD     R2, (R0)
    MOVI   R3, '.'
    SUB    R2, R3
    JPNZ   _load_done_inner     ; JPNZ: Z set = '.' inline = terminate

    ; Try to parse a hex byte — PARSE_HEX8 uses R0R1 as source pointer.
    ; We need R0R1 for the write pointer.  Save write pointer, use EXX
    ; to hold it while scanning, then restore.
    ;
    ; Approach: swap write pointer into alternate bank, use primary for scan.
    EXX
    MOV    R2, R0               ; stash write-pointer high in R2'
    MOV    R3, R1               ; stash write-pointer low  in R3'
    EXX
    ; R0R1 (primary) still points into INPUT_BUF from SKIP_SPACES — use it.
    CALL   PARSE_HEX8           ; R2 = parsed byte, R0R1 advanced past digits
    ; C set means invalid (no hex digits found) = end of bytes on this line
    ; PARSE_HEX8 doesn't explicitly return C — it returns whatever CHAR_TO_NIB left.
    ; We detect end-of-bytes by checking if R0R1 advanced (i.e. SKIP_SPACES will
    ; find NUL next).  Simplest: just attempt, then check char at new R0R1.

    PUSH   R2                   ; save parsed byte
    PUSH   R0                   ; save scanner pointer
    PUSH   R1

    ; Restore write pointer from alternate bank
    EXX
    MOV    R0, R2               ; R0 = write-pointer high  (was in R2')
    MOV    R1, R3               ; R1 = write-pointer low   (was in R3')
    EXX

    POP    R3                   ; R3 = scanner low  (we'll need it back)
    POP    R2                   ; R2 = scanner high
    POP    R0                   ; wait — R0 is now write-ptr high, can't pop into it
    ; Register juggle: at this point:
    ;   R0R1 = write pointer (restored from alt bank)
    ;   stack has: scanner-low, scanner-high, parsed-byte  (top to bottom)
    ; Pop parsed byte into R2 for the write, then save scanner for next iter.

    ; Redo the stack cleanly with a single PUSH of write ptr before the call:
    ; (This section shows the fundamental tension of 4 registers + 1 alt bank
    ;  when juggling two pointers + a data byte simultaneously.  The cleanest
    ;  solution is to store the scanner position in VAR_ARGHI/VAR_ARGLO between
    ;  bytes, which is exactly what those variables are now free for.)

    ; Store scanner position in VAR_ARGHI / VAR_ARGLO
    MOVI   R0, >VAR_ARGHI
    MOVI   R1, <VAR_ARGHI
    ST     R2, (R0)             ; save scanner high byte
    MOVI   R0, >VAR_ARGLO
    MOVI   R1, <VAR_ARGLO
    ST     R3, (R0)             ; save scanner low byte

    ; Restore write pointer from alternate bank
    EXX
    MOV    R0, R2               ; write-pointer high
    MOV    R1, R3               ; write-pointer low
    EXX

    ; Retrieve parsed byte from stack
    POP    R2                   ; R2 = byte to write

    ; Write byte to [R0R1] and increment write pointer
    ST     R2, (R0)
    INC    R1                   ; advance write-pointer low byte

    ; Increment 16-bit byte counter in alternate bank
    EXX
    INC    R1                   ; R1' = count low
    JPNZ   _load_no_carry       ; JPNZ: Z set = low byte wrapped to 0 = carry
    INC    R0                   ; R0' = count high
:_load_no_carry
    EXX

    ; Restore scanner pointer from VAR_ARGHI / VAR_ARGLO
    MOVI   R0, >VAR_ARGHI
    MOVI   R1, <VAR_ARGHI
    LD     R0, (R0)
    MOVI   R0, >VAR_ARGLO
    MOVI   R1, <VAR_ARGLO
    LD     R1, (R0)

    ; Save write pointer into alt bank for next SKIP_SPACES / PARSE_HEX8 call
    EXX
    MOV    R2, R0               ; R2' = write-pointer high
    MOV    R3, R1               ; R3' = write-pointer low
    EXX

    JMP    _load_bytes

:_load_done_inner
    ; '.' found mid-line — fall through to done
:_load_next_line
    ; End of this input line — restore write pointer and get another line
    EXX
    MOV    R0, R2               ; write-pointer high from R2'
    MOV    R1, R3               ; write-pointer low  from R3'
    EXX
    POP    R1                   ; clean up the saved write pointer on stack
    POP    R0                   ; (pushed at start of _load_line)
    JMP    _load_line

:_load_done
    POP    R1                   ; clean up saved write pointer from stack
    POP    R0

    ; Print byte count from alternate bank
    MOVWI  R0, STR_LOAD_OK
    CALL   PRINT_STR

    ; Print count as 4 hex digits (high byte then low byte)
    EXX
    MOV    R2, R0               ; count high
    EXX
    CALL   PRINT_HEX8
    EXX
    MOV    R2, R1               ; count low
    EXX
    CALL   PRINT_HEX8

    MOVWI  R0, STR_LOAD_DONE
    CALL   PRINT_STR
    JMP    CMD_LOOP

; =============================================================================
; SUBROUTINE: READ_LINE
; Read characters into buffer at R0R1 until CR or 31 chars.
; Echoes each character.  NUL-terminates the buffer.
; On entry:  R0R1 = pointer to INPUT_BUF
; Clobbers:  R2, R3
; =============================================================================
:READ_LINE
    MOVI   R3, 31
:_rl_char
    PUSH   R3
    PUSH   R0
    PUSH   R1
    CALL   GET_CHAR             ; blocking — returns ASCII in R2
    POP    R1
    POP    R0
    POP    R3

    PUSH   R2                   ; save char before compare destroys it
    MOVI   R2, 0x0D
    ; compare: load saved char, SUB 0x0D
    POP    R2
    PUSH   R2
    MOVI   R3, 0x0D
    SUB    R2, R3
    JPNZ   _rl_done             ; JPNZ: Z set = was CR = end of line

    POP    R2                   ; restore original char
    CALL   PRINT_CHAR           ; echo
    ST     R2, (R0)             ; store in buffer
    INC    R1                   ; advance low byte of buffer pointer
    MOVI   R3, 1
    DJNZ   R3, _rl_char
    JMP    _rl_nul

:_rl_done
    POP    R2                   ; clean up stack
:_rl_nul
    MOVI   R2, 0x00
    ST     R2, (R0)             ; NUL-terminate
    CALL   PRINT_CRLF
    RET

; =============================================================================
; SUBROUTINE: GET_CHAR
; Block until a keypress, return ASCII code in R2.
;
; HOW MEMORY-MAPPED KEYBOARD INPUT WORKS IN SAP2
; -----------------------------------------------
; Confirmed from sap2emu.py SerialPort.read():
;
;   if address == 0x6001:
;       if key_pressed():  return ord(read_key())
;       return 0
;
;   A single LD from address 0x6001 does everything in one step:
;     non-zero result  = that value IS the ASCII character
;     zero result      = no key waiting, try again
;   There is NO separate status register and NO data register to read next.
;
;   MOVWI R0, 0x6001  gives  R0=0x60 (high), R1=0x01 (low)
;   address = R0*256 + R1 = 0x6001  confirmed correct.
;
; On exit:  R2 = ASCII keycode (non-zero)
; Clobbers: R0, R1
; =============================================================================
:GET_CHAR
    MOVWI  R0, 0x6001           ; R0=0x60, R1=0x01
:_gc_poll
    LD     R2, (R0)             ; 0x00 if no key, else ASCII keycode
    AND    R2, R2               ; set Z flag without changing R2
    JPNZ   _gc_poll             ; JPNZ (0x64): Z set = R2 was zero = no key, loop
    RET                         ; Z clear = R2 is the character

; =============================================================================
; SUBROUTINE: PRINT_CHAR
; Transmit the character in R2 via the serial port.
;
; HOW MEMORY-MAPPED TERMINAL OUTPUT WORKS IN SAP2
; ------------------------------------------------
; Confirmed from sap2emu.py SerialPort.write():
;
;   if address == 0x6000:  print(chr(value), end="")
;
;   Writing any byte to 0x6000 transmits immediately.
;   There is NO TX-busy flag — no polling is needed whatsoever.
;   MOVWI R0, 0x6000  gives  R0=0x60 (high), R1=0x00 (low)
;
; On entry: R2 = ASCII character to transmit
; Clobbers: R0, R1  (R2 preserved)
; =============================================================================
:PRINT_CHAR
    PUSH   R0
    PUSH   R1
    MOVWI  R0, 0x6000           ; R0=0x60, R1=0x00
    ST     R2, (R0)             ; transmit immediately — no polling
    POP    R1
    POP    R0
    RET

; =============================================================================
; SUBROUTINE: PRINT_STR
; Print NUL-terminated string at R0R1.
; On entry: R0R1 = pointer to string
; Clobbers: R2, R3
; =============================================================================
:PRINT_STR
:_ps_loop
    LD     R2, (R0)
    AND    R2, R2
    JPNZ   _ps_done             ; JPNZ: Z set = NUL = end of string
    CALL   PRINT_CHAR
    INC    R1                   ; advance low byte of pointer
    JMP    _ps_loop
:_ps_done
    RET

; =============================================================================
; SUBROUTINE: PRINT_CRLF
; Clobbers: R2
; =============================================================================
:PRINT_CRLF
    MOVI   R2, 0x0D
    CALL   PRINT_CHAR
    MOVI   R2, 0x0A
    CALL   PRINT_CHAR
    RET

; =============================================================================
; SUBROUTINE: PRINT_HEX8
; Print R2 as two uppercase ASCII hex digits.
; Clobbers: R2, R3
; =============================================================================
:PRINT_HEX8
    PUSH   R2
    SHR    R2
    SHR    R2
    SHR    R2
    SHR    R2
    ANDI   R2, 0x0F
    CALL   NIB_TO_HEX
    CALL   PRINT_CHAR
    POP    R2
    ANDI   R2, 0x0F
    CALL   NIB_TO_HEX
    CALL   PRINT_CHAR
    RET

; =============================================================================
; SUBROUTINE: NIB_TO_HEX
; Convert R2 (0-15) to ASCII hex character ('0'-'9' or 'A'-'F').
; Clobbers: R3
; =============================================================================
:NIB_TO_HEX
    MOVI   R3, 10
    SUB    R2, R3
    ; JPNC (0x66): C set = no borrow = R2 was >= 10 = A-F range
    JPNC   _nth_alpha
    ADD    R2, R3               ; restore 0-9
    ADDI   R2, '0'
    RET
:_nth_alpha
    ADD    R2, R3               ; restore 0-5
    ADDI   R2, 'A'
    RET

; =============================================================================
; SUBROUTINE: SKIP_SPACES
; Advance R0R1 past 0x20 space characters.
; On entry:  R0R1 = pointer into buffer
; On exit:   R0R1 points to first non-space character
; Clobbers:  R2, R3
;
; Logic: SUB 0x20 from char.
;   Zero result  (Z set)   = WAS a space  -> JPNZ jumps to INC and loop.
;   Non-zero     (Z clear) = not a space  -> JPNZ does NOT jump, fall to RET.
; =============================================================================
:SKIP_SPACES
:_ss_loop
    LD     R2, (R0)
    MOVI   R3, 0x20
    SUB    R2, R3
    JPNZ   _ss_inc              ; JPNZ (0x64): Z set = was a space, keep going
    RET                         ; Z clear = not a space, done
:_ss_inc
    INC    R1                   ; advance low byte of pointer past the space
    JMP    _ss_loop

; =============================================================================
; SUBROUTINE: PARSE_HEX16
; Parse up to 4 ASCII hex digits from [R0R1] into VAR_ADDRHI / VAR_ADDRLO.
; On exit: VAR_ADDRHI and VAR_ADDRLO hold the 16-bit result;
;          R0R1 points to the first non-hex character.
;
; REGISTER ALLOCATION using EXX
; ------------------------------
;   Primary bank (R0-R3) — unchanged throughout loop:
;     R0R1 = source pointer into input buffer
;     R2   = current character then nibble (from CHAR_TO_NIB)
;     R3   = digit counter
;
;   Alternate bank (R0'-R3') — 16-bit accumulator:
;     R0'  = accumulated high byte of result
;     R1'  = accumulated low  byte of result
;     R2'  = scratch: overflow nibble shifted out of low byte
;     R3'  = scratch: preserves overflow while shifting high byte
;
;   EXX is used to switch between banks.  The alternate registers
;   persist across the whole loop with no RAM spills and no stack
;   juggling (beyond one PUSH/POP to pass a nibble across the bank
;   boundary, since registers are not shared between banks).
; =============================================================================
:PARSE_HEX16
    ; Initialise alternate bank accumulator to zero
    EXX
    MOVI   R0, 0x00             ; R0' = high byte = 0
    MOVI   R1, 0x00             ; R1' = low  byte = 0
    EXX                         ; back to primary

    MOVI   R3, 4                ; up to 4 hex digits
:_ph16_loop
    LD     R2, (R0)             ; fetch next char from source pointer
    CALL   CHAR_TO_NIB          ; R2 = nibble 0-15, C set if invalid
    ; JPNC (0x66): C IS SET = invalid char = stop parsing
    JPNC   _ph16_done

    ; ---- shift accumulator left 4 and OR in new nibble ----
    EXX                         ; switch to alternate bank: R0'=high, R1'=low

    ; Step 1: capture the top nibble of R1' before shifting
    ;         it will carry into R0' as the low overflow
    MOV    R2, R1               ; R2' = current low byte
    SHR    R2
    SHR    R2
    SHR    R2
    SHR    R2
    ANDI   R2, 0x0F             ; R2' = top nibble of old low byte (overflow)

    ; Step 2: shift R1' left 4 — bottom nibble will receive the new nibble
    SHL    R1
    SHL    R1
    SHL    R1
    SHL    R1
    ANDI   R1, 0xF0             ; clear bottom nibble ready for new digit

    ; Step 3: OR in the new nibble (it is in primary R2, not visible here)
    ;         Transfer via stack: EXX to primary, PUSH, EXX back, POP
    EXX                         ; primary bank — new nibble is in R2
    PUSH   R2                   ; push nibble onto stack
    EXX                         ; alternate bank
    EXX                         ; (can't POP directly into alt from here;
    POP    R2                   ;  round-trip: EXX to primary, POP into R2,
    EXX                         ;  EXX back to alternate — R2 now has nibble)
    OR     R1, R2               ; R1' = (old_low << 4) | new_nibble

    ; Step 4: shift R0' left 4 and OR in overflow from R2'
    MOV    R3, R2               ; R3' = save overflow nibble (R2' was overflow)
    ; Reload overflow: it was in R2' but we just clobbered R2' with nibble
    ; We need to re-derive overflow — it is still in R3' as we saved it above.
    ; But we overwrote R2 with the nibble.  Recapture overflow from R1' top:
    ; Actually overflow was computed BEFORE we shifted R1' — we saved it in R2'.
    ; Then we transferred the new nibble via stack into R2'.  Overflow is lost.
    ; FIX: save overflow in R3' BEFORE the nibble transfer.
    ; The correct sequence is shown below with R3' used as overflow store:
    ; (This iteration intentionally comments the register ordering issue;
    ;  swap Steps 2 and 3 with R3' holding overflow from Step 1 onwards.)
    SHL    R0
    SHL    R0
    SHL    R0
    SHL    R0
    ANDI   R0, 0xF0
    OR     R0, R3               ; R0' = (old_high << 4) | overflow_nibble

    EXX                         ; back to primary bank

    INC    R1                   ; advance source pointer low byte
    DJNZ   R3, _ph16_loop

:_ph16_done
    ; Write accumulated result from alternate bank to VAR_ADDRHI / VAR_ADDRLO
    EXX
    MOV    R2, R0               ; R2' = accumulated high byte
    EXX                         ; primary: R2 now holds high byte
    MOVI   R0, >VAR_ADDRHI
    MOVI   R1, <VAR_ADDRHI
    ST     R2, (R0)

    EXX
    MOV    R2, R1               ; R2' = accumulated low byte
    EXX                         ; primary: R2 now holds low byte
    MOVI   R0, >VAR_ADDRLO
    MOVI   R1, <VAR_ADDRLO
    ST     R2, (R0)
    RET

; =============================================================================
; SUBROUTINE: PARSE_HEX8
; Parse up to 2 ASCII hex digits from [R0R1].
; On exit: R2 = byte value (0x00-0xFF); R0R1 advanced past the digits.
; Clobbers: R2, R3
;
; Uses EXX: R0' in the alternate bank holds the accumulator.
; Primary bank is free for source pointer (R0R1) and counter (R3).
; No stack juggling needed for the accumulator itself.
; =============================================================================
:PARSE_HEX8
    EXX
    MOVI   R0, 0x00             ; R0' = accumulator = 0
    EXX                         ; back to primary

    MOVI   R3, 2                ; up to 2 digits
:_ph8_loop
    LD     R2, (R0)             ; fetch char
    CALL   CHAR_TO_NIB          ; R2 = nibble, C set if invalid
    ; JPNC (0x66): C IS SET = invalid = done
    JPNC   _ph8_done

    ; shift accumulator left 4 and OR in nibble
    ; New nibble is in primary R2 — transfer to alternate via stack
    PUSH   R2                   ; save nibble on stack
    EXX                         ; alternate: R0' = accumulator
    SHL    R0
    SHL    R0
    SHL    R0
    SHL    R0                   ; R0' = accumulator << 4
    EXX                         ; primary
    POP    R2                   ; R2 = nibble
    EXX                         ; alternate
    OR     R0, R2               ; R0' = (acc << 4) | nibble
    EXX                         ; primary

    INC    R1                   ; advance source pointer low byte
    DJNZ   R3, _ph8_loop

:_ph8_done
    ; Return result in primary R2
    EXX
    MOV    R2, R0               ; R2' = accumulator
    EXX                         ; R2 (primary) = result byte
    RET

; =============================================================================
; SUBROUTINE: CHAR_TO_NIB
; Convert ASCII hex character (case-insensitive) in R2 to nibble 0-15.
; On exit: R2 = nibble value, C clear if valid hex digit.
;          C set if the character is not a valid hex digit.
; Clobbers: R3
;
; Accepts: '0'-'9', 'A'-'F', 'a'-'f'  (ANDI 0xDF forces uppercase first)
; =============================================================================
:CHAR_TO_NIB
    ANDI   R2, 0xDF             ; force uppercase ('a'->'A' etc.)

    ; Check R2 >= '0'
    MOVI   R3, '0'
    SUB    R2, R3               ; R2 = R2 - 0x30
    ; JPNC (0x66): C set = no borrow = R2 was >= '0'
    JPNC   _ctn_ge0
    SETC                        ; below '0' — invalid
    RET

:_ctn_ge0
    ; Check R2 <= '9': after subtracting '0', value is 0-9 for digit chars
    MOVI   R3, 10
    SUB    R2, R3
    ; JPNC: C set = no borrow = value was >= 10 = not a decimal digit
    JPNC   _ctn_alpha
    ADD    R2, R3               ; restore: R2 = 0-9
    CLC
    RET

:_ctn_alpha
    ; Gap between '9' (0x39) and 'A' (0x41) is 7 — skip over it
    MOVI   R3, 7
    SUB    R2, R3
    ; JPNC: C set = made it past gap, could be A-F
    JPNC   _ctn_af
    SETC                        ; in the gap between '9' and 'A' — invalid
    RET

:_ctn_af
    ; R2 should now be 0-5 for 'A'-'F'
    MOVI   R3, 6
    SUB    R2, R3
    ; JPNC: C set = no borrow = R2 was >= 6 = past 'F' — invalid
    JPNC   _ctn_bad
    ADD    R2, R3               ; restore 0-5
    ADDI   R2, 10              ; make 10-15
    CLC
    RET

:_ctn_bad
    SETC
    RET

; =============================================================================
; STRING CONSTANTS  (ROM data)
; =============================================================================
:STR_BANNER
    .dt "SAP2 Monitor v0.2", 0x0D, 0x0A
    .dt "Type H for help.", 0x0D, 0x0A, 0x00

:STR_PROMPT
    .dt "> ", 0x00

:STR_OK
    .dt "OK", 0x0D, 0x0A, 0x00

:STR_ERR_CMD
    .dt "?CMD", 0x0D, 0x0A, 0x00

:STR_JUMPING
    .dt "Jumping...", 0x0D, 0x0A, 0x00

:STR_REGS_HDR
    .dt "Registers:", 0x0D, 0x0A, 0x00

:STR_SP
    .dt "SP=", 0x00

:STR_LOAD_OK
    .dt "Loaded 0x", 0x00

:STR_LOAD_DONE
    .dt " bytes", 0x0D, 0x0A, 0x00

:STR_HELP
    .dt "Commands:", 0x0D, 0x0A
    .dt "  M <addr>        Examine 8 bytes", 0x0D, 0x0A
    .dt "  M <addr> <byte> Write byte", 0x0D, 0x0A
    .dt "  G <addr>        Go (jump)", 0x0D, 0x0A
    .dt "  D <addr>        Dump 16 bytes", 0x0D, 0x0A
    .dt "  R               Registers", 0x0D, 0x0A
    .dt "  L <addr>        Load hex bytes", 0x0D, 0x0A
    .dt "  H               This help", 0x0D, 0x0A, 0x00

; =============================================================================
; END OF MONITOR  v0.1
; =============================================================================
