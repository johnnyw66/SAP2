# Simple script to use the C preprocessor
# ./asmcpp.sh asm/testmacro.asm
cpp $@ a.asm
python3 assembler.py a.asm -3 -s
rm -f a.asm
