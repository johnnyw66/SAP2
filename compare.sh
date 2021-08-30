#!/bin/bash
# Script to compare assembler.py output from previous known 'good' version

f='allopcodes'

asmfile=$f.'asm'
hexfile=$f.'hex'
comparefile='compareallops.hex'

rm -f $comparefile
./newassembler.py $asmfile -q -1
cp $hexfile $comparefile
rm -f $hexfile
./assembler.py $asmfile -q -1

a=$(md5 $hexfile | grep -E  -o "\s([0-9a-f]+$)")
b=$(md5 $comparefile | grep -E -o "\s([0-9a-f]+$)")
if [ $a = $b ];
then
  echo "Integrity Checks on assembler tool are OK"
else
  echo "***WE HAVE A PROBLEM **** The Assembler utility versions'assembler.py'and 'newassembler.py' are producing different output than expected.****"
fi
rm -f $comparefile
rm -f $hexfile
