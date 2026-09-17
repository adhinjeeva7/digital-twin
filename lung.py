import numpy as np

class Lung:
    def __init__(self):
        self.r_pul_base = 0.08
        self.c_pa = 4.50
        self.c_pv = 8.00
        self.k_hpv = 0.60
        self.pao2_normal = 95.0
        self.p50 = 26.6
        self.n = 2.7

    def pvr(self, PaO2):
        oxygen_drop = max(0, 1 - PaO2 / self.pao2_normal)
        return self.r_pul_base * (1 + self.k_hpv * oxygen_drop**2)

    def flow(self, P_pa, P_pv, PaO2):
        return max(0, (P_pa - P_pv) / self.pvr(PaO2))

    def SaO2(self, PaO2):
        top = PaO2**self.n
        bottom = self.p50**self.n + PaO2**self.n
        return top / bottom * 100


if __name__ == "__main__":
    lung = Lung()

    print(lung.pvr(95.0))
    print(lung.pvr(40.0))
    print(lung.pvr(20.0))

    print(lung.flow(15.0, 8.0, 95.0))

    print(lung.SaO2(95.0))
    print(lung.SaO2(60.0))
    print(lung.SaO2(40.0))