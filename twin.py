import numpy as np
from scipy.integrate import solve_ivp

from heart import Heart
from lung import Lung
from kidney import Kidney


class DigitalTwin:
    def __init__(self):
        self.heart = Heart()
        self.lung = Lung()
        self.kidney = Kidney()

        self.r_sys = 1.06
        self.c_sa = 1.60
        self.c_sv = 60.0

        self.fio2 = 0.21
        self.pao2_normal = 95.0
        self.tau_o2 = 30.0

        self.y0 = [93.0, 6.0, 15.0, 8.0, 0.0, 95.0]

        self.scenario = None
        self.onset_s = 300.0

    def apply_scenario(self, t):
        if t < self.onset_s:
            return

        if self.scenario == "hypoxia":
            self.fio2 = 0.10

        elif self.scenario == "fluid_overload":
            self.kidney.fluid_intake = 10.0

        elif self.scenario == "heart_failure":
            self.heart.sv_baseline = 38.5
            self.heart.k_fs_lv = 0.25
            self.heart.k_fs_rv = 0.25

    def rhs(self, t, y):
        self.apply_scenario(t)

        P_sa, P_sv, P_pa, P_pv, V_extra, PaO2 = y

        P_sv_effective = P_sv + V_extra / self.c_sv

        co_lv, co_rv, hr = self.heart.outputs(
            P_pv,
            P_sv_effective,
            P_sa,
            P_pa
        )

        q_sys = (P_sa - P_sv_effective) / self.r_sys

        dP_sa = (co_lv - q_sys) / self.c_sa
        dP_sv = (q_sys - co_rv) / self.c_sv

        q_pul = self.lung.flow(P_pa, P_pv, PaO2)

        dP_pa = (co_rv - q_pul) / self.lung.c_pa
        dP_pv = (q_pul - co_lv) / self.lung.c_pv

        dV = self.kidney.dV_dt(P_sa)

        edema = max(
            0.2,
            1.0 - 0.025 * max(0.0, P_pv - 12.0)
        )

        flow_factor = np.clip(
            q_pul / 83.33,
            0.05,
            1.0
        )

        oxygen_target = (
            self.pao2_normal
            * (self.fio2 / 0.21)
            * edema
            * flow_factor
        )

        dPaO2 = (oxygen_target - PaO2) / self.tau_o2

        return [
            dP_sa,
            dP_sv,
            dP_pa,
            dP_pv,
            dV,
            dPaO2
        ]

    def run(self, t_end=1800, dt=2.0):
        times = np.arange(0, t_end + dt, dt)

        return solve_ivp(
            self.rhs,
            [0, t_end],
            self.y0,
            t_eval=times,
            method="RK45",
            rtol=1e-6,
            atol=1e-8,
            max_step=5.0
        )


if __name__ == "__main__":
    twin = DigitalTwin()
    result = twin.run()

    print("Success:", result.success)
    print("Final state:", result.y[:, -1])