#cpp $1 tmp.asm
cpp $@ a.asm
./newass.py a.asm -3 -s
rm -f a.asm
