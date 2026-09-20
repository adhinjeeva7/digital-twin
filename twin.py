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
    def heart_parameters_at(self, t):
        if self.scenario == "heart_failure" and t >= self.onset_s:
            return 38.5, 0.25, 0.25

        return 70.0, 0.60, 0.60
    def apply_scenario(self, t):
        if self.scenario == "hypoxia":
            self.fio2 = 0.10

        elif self.scenario == "fluid_overload":
            self.kidney.fluid_intake = 10.0

        elif self.scenario == "heart_failure":
            sv, k_lv, k_rv = self.heart_parameters_at(self.onset_s)
            self.heart.sv_baseline = sv
            self.heart.k_fs_lv = k_lv
            self.heart.k_fs_rv = k_rv

    def rhs(self, t, y):

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

        options = {
            "method": "RK45",
            "rtol": 1e-6,
            "atol": 1e-8,
            "max_step": 5.0,
        }

        if t_end <= self.onset_s:
            return solve_ivp(
                self.rhs,
                [0, t_end],
                self.y0,
                t_eval=times,
                **options,
            )

        pre_times = times[times <= self.onset_s]
        post_times = times[times >= self.onset_s]

        baseline = solve_ivp(
            self.rhs,
            [0, self.onset_s],
            self.y0,
            t_eval=pre_times,
            **options,
        )

        if not baseline.success:
            return baseline

        if self.scenario is not None:
            self.apply_scenario()

        scenario = solve_ivp(
            self.rhs,
            [self.onset_s, t_end],
            baseline.y[:, -1],
            t_eval=post_times,
            **options,
        )

        scenario.t = np.concatenate([
            baseline.t,
            scenario.t[1:],
        ])

        scenario.y = np.concatenate([
            baseline.y,
            scenario.y[:, 1:],
        ], axis=1)

        scenario.nfev += baseline.nfev
        scenario.success = baseline.success and scenario.success

        return scenario

    def show_results(self, result):
        names = [
            "MAP",
            "CVP",
            "Pulmonary pressure",
            "Pulmonary venous pressure",
            "Extra fluid",
            "PaO2"
        ]

        final_values = result.y[:, -1]

        print("Simulation success:", result.success)

        for name, value in zip(names, final_values):
            print(name, "=", round(value, 2))


if __name__ == "__main__":
    twin = DigitalTwin()
    result = twin.run()
    twin.show_results(result)