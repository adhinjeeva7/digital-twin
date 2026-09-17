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


if __name__ == "__main__":
    h = Heart()
    print(h.hr_baseline, h.sv_baseline, h.map_set)
    print(h.heart_rate(93.0), h.heart_rate(70.0), h.heart_rate(120.0))
    # outputs() needs sv_lv/sv_rv/outputs written first (section 4 of the design doc) -
    # uncomment once those are in place
    # print(h.outputs(P_pv=8.0, P_sv=6.0, P_sa=93.0, P_pa=15.0))
