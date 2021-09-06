#cpp $1 tmp.asm
cpp $@ a.asm
./assembler.py a.asm -3 -s
rm -f a.asm
