from flask import Flask, request, jsonify
from twin import DigitalTwin
app=Flask(__name__)
@app.route("/simulate")
def simulate():
    pct = float(request.args)
    twin = DigitalTwin()
    twin.heart.sv_baseline = 70.0 * pct / 100.0
    twin.heart.k_fs_lv = 0.60 - 0.35 * (1 - pct / 100.0)
    twin.heart.k_fs_rv = twin.heart.k_fs_lv

    result = twin.run()
    P_sa, P_sv, P_pa, P_pv, V_extra, PaO2 = result.y[:, -1]
    hr = twin.heart.heart_rate(P_sa)
    gfr = twin.kidney.gfr(P_sa)
    sao2 = twin.lung.SaO2(PaO2)
    return jsonify({
        "MAP": round(P_sa, 1), "CVP": round(P_sv, 2),
        "mPAP": round(P_pa, 1), "PCWP": round(P_pv, 2),
        "PaO2": round(PaO2, 1), "SaO2": round(sao2, 1),
        "HR": round(hr, 1), "GFR": round(gfr, 1),
        "Vextra": round(V_extra, 1)
         })
if __name__ == "__main__":
    app.run(debug=True, port=5000)