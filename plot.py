import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scenarios import run_healthy, run_hypoxia, run_fluid_overload, run_heart_failure


def derive(twin, result):
    t = result.t
    P_sa, P_sv, P_pa, P_pv, V_extra, PaO2 = result.y
    n = len(t)
    out = {
        'P_sa': P_sa,
        'P_sv': P_sv,
        'P_pa': P_pa,
        'P_pv': P_pv,
        'V_extra': V_extra,
        'PaO2': PaO2,
        'HR': np.zeros(n),
        'CO_lv': np.zeros(n),
        'GFR': np.zeros(n),
        'SaO2': np.zeros(n),
    }
    for i in range(n):
        P_sv_eff = P_sv[i] + V_extra[i] / twin.c_sv
        co_lv, co_rv, hr = twin.heart.outputs(P_pv[i], P_sv_eff, P_sa[i], P_pa[i])
        out['HR'][i] = hr
        out['CO_lv'][i] = co_lv * 60.0 / 1000.0   # mL/s -> L/min
        out['GFR'][i] = twin.kidney.gfr(P_sa[i])
        out['SaO2'][i] = twin.lung.SaO2(PaO2[i])

    return t, out


def plot_calibration(t, res, save_path='calibration_figure.png'):
    panels = [
        ('P_sa', 'MAP', 'mmHg', 70, 100), ('P_sv', 'CVP', 'mmHg', 2, 10),
        ('P_pa', 'mPAP', 'mmHg', 10, 20), ('P_pv', 'PCWP', 'mmHg', 5, 12),
        ('PaO2', 'PaO2', 'mmHg', 85, 100), ('HR', 'Heart Rate', 'bpm', 60, 80),
        ('CO_lv', 'Cardiac Output', 'L/min', 4.5, 5.5),
        ('GFR', 'GFR', 'mL/min', 90, 130), ('SaO2', 'SaO2', '%', 95, 100),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle('Calibration: Healthy Baseline', fontsize=16, fontweight='bold')
    for idx, (key, title, unit, lo, hi) in enumerate(panels):
        ax = axes[idx // 3, idx % 3]
        ax.plot(t / 60.0, res[key], 'b-', linewidth=1.5)
        ax.axhspan(lo, hi, alpha=0.15, color='green', label='Ref range')
        ax.set_xlabel('Time (min)')
        ax.set_ylabel(f'{title} ({unit})')
        ax.set_title(title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.show()

def plot_scenario(t_h, res_h, t_s, res_s, name, onset_min=5.0, save_path=None):
    panels = [
        ('P_sa', 'MAP', 'mmHg', 70, 100), ('P_pv', 'PCWP', 'mmHg', 5, 12),
        ('P_pa', 'mPAP', 'mmHg', 10, 20), ('CO_lv', 'Cardiac Output', 'L/min', 4.5, 5.5),
        ('HR', 'Heart Rate', 'bpm', 60, 80), ('PaO2', 'PaO2', 'mmHg', 85, 100),
        ('SaO2', 'SaO2', '%', 95, 100), ('GFR', 'GFR', 'mL/min', 90, 130),
        ('V_extra', 'Extra Volume', 'mL', None, None),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle(f'Healthy vs {name}', fontsize=16, fontweight='bold')
    for idx, (key, title, unit, lo, hi) in enumerate(panels):
        ax = axes[idx // 3, idx % 3]
        ax.plot(t_h / 60.0, res_h[key], 'b-', label='Healthy', alpha=0.7)
        ax.plot(t_s / 60.0, res_s[key], 'r-', label=name)
        if lo is not None:
            ax.axhspan(lo, hi, alpha=0.1, color='green')
        ax.axvline(x=onset_min, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Time (min)')
        ax.set_ylabel(f'{title} ({unit})')
        ax.set_title(title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path is None:
        save_path = f'scenario_{name.lower().replace(" ", "_")}.png'
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.show()


def save_summary_csv(all_res, save_path='scenario_summary.csv'):
    variables = [
        ('MAP (mmHg)', 'P_sa'), ('CVP (mmHg)', 'P_sv'), ('mPAP (mmHg)', 'P_pa'),
        ('PCWP (mmHg)', 'P_pv'), ('V_extra (mL)', 'V_extra'), ('PaO2 (mmHg)', 'PaO2'),
        ('HR (bpm)', 'HR'), ('CO (L/min)', 'CO_lv'), ('GFR (mL/min)', 'GFR'),
        ('SaO2 (%)', 'SaO2'),
    ]
    rows = []
    for label, key in variables:
        row = {'Variable': label}
        for name in ['healthy', 'hypoxia', 'fluid_overload', 'heart_failure']:
            row[name] = round(all_res[name][1][key][-1], 2)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(save_path, index=False)
    print(df.to_string(index=False))
    return df


if __name__ == "__main__":
    scenarios = {
        'healthy': run_healthy, 'hypoxia': run_hypoxia,
        'fluid_overload': run_fluid_overload, 'heart_failure': run_heart_failure,
    }
    all_res = {}
    for name, runner in scenarios.items():
        twin, result = runner()
        all_res[name] = derive(twin, result)
        print(f"{name} done")

    t_h, res_h = all_res['healthy']
    plot_calibration(t_h, res_h)
    for name in ['hypoxia', 'fluid_overload', 'heart_failure']:
        t_s, res_s = all_res[name]
        plot_scenario(t_h, res_h, t_s, res_s, name.replace('_', ' ').title())

    save_summary_csv(all_res)
