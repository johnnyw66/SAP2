#!/bin/bash
# Script to compare assembler.py output from previous known 'good' version

f='assemblertest'
asmfile=$f.'asm'
hexfile=$f.'hex'
comparefile='compareassemblertest.hex'
# Make sure comparefile and asmfile exists

./assembler.py $asmfile -q -1 
a=$(md5 $hexfile | grep -E  -o "\s([0-9a-f]+$)")
b=$(md5 $comparefile | grep -E -o "\s([0-9a-f]+$)")
if [ $a = $b ];
then
  echo "Integrity Checks on assembler tool are OK"
else
  echo "***WE HAVE A PROBLEM **** The Assembler utility 'assembler.py'is producing different output than expected.****"
fi
