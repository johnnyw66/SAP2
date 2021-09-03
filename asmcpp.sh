#cpp $1 tmp.asm
cpp $@ a.asm
./newass.py a.asm -3 -r
rm -f a.asm
