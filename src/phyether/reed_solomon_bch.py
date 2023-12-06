from typing import Type
from galois import GF, Poly, FieldArray

class BCH_RS:
    def __init__(self, n: int, k: int, gf: Type[FieldArray], generator: Poly):
        self.parity: list[FieldArray] = []
        self.i = 0
        self.n = n
        self.k = k
        self.gf = gf
        self.generator = generator

        self.clear_parity()

    def clear_parity(self):
        self.parity = [self.gf(0) for _ in range(self.n - self.k)]
        self.i = 0

    def encode_next_symbol(self, symbol: str | None):
        if symbol is None:
            parity = self.parity[-1]
            self.parity = [0] + self.parity[:-1]
            return parity
        m_i = self.gf(symbol)
        gen_coeffs = list(reversed(self.generator.coeffs))
        g_t = (m_i + self.parity[-1]) * gen_coeffs[-1]
        p_0 = g_t * gen_coeffs[0]
        self.parity = [p_0] + [self.parity[i-1] + g_t * gen_coeffs[i] for i in range(1, len(gen_coeffs))]

        if self.i < self.k:
            self.i += 1
            return m_i
        else:
            self.i += 1
            return self.parity[-1]