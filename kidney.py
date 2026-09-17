class Kidney:
    def __init__(self):
        self.gfr_baseline = 125.0
        self.p_sa_set = 93.0
        self.k_reabs = 0.988
        self.fluid_intake = 1.5

    def gfr(self, P_sa):
        if P_sa >= 80:
            return self.gfr_baseline * min(
                1.15,
                P_sa / self.p_sa_set
            )

        return self.gfr_baseline * (P_sa / 80) ** 2

    def urine_output(self, P_sa):
        return (
            self.gfr(P_sa)
            * (1 - self.k_reabs)
            * (P_sa / self.p_sa_set) ** 2
        )

    def dV_dt(self, P_sa):
        return (self.fluid_intake - self.urine_output(P_sa)) / 60


if __name__ == "__main__":
    kidney = Kidney()
   
    for pressure in [93.0, 70.0, 50.0]:
        print("MAP:", pressure)
        print("GFR:", kidney.gfr(pressure))
        print("Urine output:", kidney.urine_output(pressure))
        print("dV/dt:", kidney.dV_dt(pressure))
        print()