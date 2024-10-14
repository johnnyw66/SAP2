.org 0x8000

movi r2,197
movwi r0,data
st r2,0
st r2,(r0)

hlt
:data
.ds 16

.end
