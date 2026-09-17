import numpy as np


class Heart:
    def __init__(self):
        # baseline values (healthy adult at rest)
        self.hr_baseline = 70.0
        self.sv_baseline = 70.0

        # Frank-Starling gains — more filling = bigger stroke volume
        self.k_fs_lv = 0.60
        self.k_fs_rv = 0.60

        # baroreceptor reflex — pressure drops, HR goes up
        self.k_baro = 0.50
        self.map_set = 93.0
        self.hr_min = 45.0
        self.hr_max = 160.0

        # afterload sensitivity (RV is thinner, more sensitive)
        self.k_al_lv = 0.003
        self.k_al_rv = 0.020

    def heart_rate(self, P_sa):
        # baroreceptor reflex: pressure below setpoint -> heart beats faster
        hr = self.hr_baseline - self.k_baro * (P_sa - self.map_set)
        return np.clip(hr, self.hr_min, self.hr_max)

    def sv_lv(self, P_pv, P_sa):
        # left ventricle: Frank-Starling preload gain x afterload penalty
        preload = 1.0 + self.k_fs_lv * (P_pv - 8.0)
        afterload = 1.0 - self.k_al_lv * (P_sa - 93.0)
        return max(self.sv_baseline * preload * afterload, 5.0)

    def sv_rv(self, P_sv, P_pa):
        # right ventricle: same shape as sv_lv, its own preload/afterload refs
        preload = 1.0 + self.k_fs_rv * (P_sv - 6.0)
        afterload = 1.0 - self.k_al_rv * (P_pa - 15.0)
        return max(self.sv_baseline * preload * afterload, 5.0)

    def outputs(self, P_pv, P_sv, P_sa, P_pa):
        # cardiac output for each side: CO = SV x HR / 60
        hr = self.heart_rate(P_sa)
        co_lv = self.sv_lv(P_pv, P_sa) * hr / 60.0
        co_rv = self.sv_rv(P_sv, P_pa) * hr / 60.0
        return co_lv, co_rv, hr


if __name__ == "__main__":
    h = Heart()
    print(h.hr_baseline, h.sv_baseline, h.map_set)
    print(h.heart_rate(93.0), h.heart_rate(70.0), h.heart_rate(120.0))
    # outputs() needs sv_lv/sv_rv/outputs written first (section 4 of the design doc) -
    # uncomment once those are in place
    print(h.outputs(P_pv=8.0, P_sv=6.0, P_sa=93.0, P_pa=15.0))
