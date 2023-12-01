from bitarray import bitarray

class PAM:
    def __init__(self, type):
        assert(type in ["NRZ", "PAM4", "PAM16"])
        self.type = type

    @property
    def high_symbol(self):
        if self.type == "NRZ":
            return 1
        elif self.type == "PAM4":
            return 3
        else: 
            return 15
    
    @property
    def symbol_step(self):
        return 2

    def hex_to_signals(self, hex_data):
        if self.type == "NRZ":
            return self._nrz_hex_to_signals(hex_data)
        elif self.type == "PAM4":
            return self._pam4_hex_to_signals(hex_data)
        else:
            return self._pam16_hex_to_signals(hex_data)

    def _nrz_hex_to_signals(self, hex_data):
        bits = bitarray(bin(int(hex_data, 16))[2:])
        return " ".join(['1' if bit else '-1' for bit in bits])

    def _pam4_hex_to_signals(self, hex_data):
        bits = bitarray(bin(int(hex_data, 16))[2:])
        signals = ""
        for i in range(0, len(bits), 2):
            if bits[i:i+2] == bitarray("00"):
                signals += " -3"
            elif bits[i:i+2] == bitarray("01"):
                signals += " -1"
            elif bits[i:i+2] == bitarray("10"):
                signals += " 1"
            else:
                signals += " 3"
        return signals[1:]

    def _pam16_hex_to_signals(self, hex_data):
        bits = bitarray(bin(int(hex_data, 16))[2:])
        padding_length = (4 - (len(bits) % 4)) % 4
        bits += bitarray('0' * padding_length)
        signals = ""
        for i in range(0, len(bits), 4):
            if bits[i:i+4] == bitarray("0000"):
                signals += " -15"
            elif bits[i:i+4] == bitarray("0001"):
                signals += " -13"
            elif bits[i:i+4] == bitarray("0010"):
                signals += " -11"
            elif bits[i:i+4] == bitarray("0011"):
                signals += " -9"
            elif bits[i:i+4] == bitarray("0100"):
                signals += " -7"
            elif bits[i:i+4] == bitarray("0101"):
                signals += " -5"
            elif bits[i:i+4] == bitarray("0110"):
                signals += " -3"
            elif bits[i:i+4] == bitarray("0111"):
                signals += " -1"
            elif bits[i:i+4] == bitarray("1000"):
                signals += " 1"
            elif bits[i:i+4] == bitarray("1001"):
                signals += " 3"
            elif bits[i:i+4] == bitarray("1010"):
                signals += " 5"
            elif bits[i:i+4] == bitarray("1011"):
                signals += " 7"
            elif bits[i:i+4] == bitarray("1100"):
                signals += " 9"
            elif bits[i:i+4] == bitarray("1101"):
                signals += " 11"
            elif bits[i:i+4] == bitarray("1110"):
                signals += " 13"
            else:
                signals += " 15"
        return signals[1:]

