
Shift functionality for the ALU.

In a similar fashion to my Logic Unit - this circuit will handle bit 8-bit shift instructions with a carry bit.

The inputs are:-

8-bit value 'I' , Carry In bit (1-bit) 'CIN', required shift function value (2-bits) 'func'.

The outputs are:-

8-bit value 'OUT', Carry out bit 'COUT' (1-bit).



Consisting of 5 x 74LS253 multiplexer chips - 4 of which handles the shifting of the original
8-bit input. The final 74253 handles the carry-out logic.



The unit handles the following functions. (selected from the 2-bit 'func' value)


Unchanged - (Carry In and 8-bit input are sent directly to the carry out and eight output lines)

Shift Right - (Divide by 2) - The 9-bit input (eight bits of our main input along with the carry-in as the most significant bit) is shifted right and presented on the 8-bit output bus.
Bit 0 of our input value is sent to the carry-out output.


Shift Left - (Multiply by 2) - The 9-bit input (eight bits of our main input along with the carry-in as the least significant bit) is shifted left and presented on the 8-bit output bus.
Bit 7 of our input value is sent to the carry-out output.

Clear - The 8-bit output and carry-out are set to zero.


Johnny Wilson, Brighton - 2021
