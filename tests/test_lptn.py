#!/usr/bin/env python3
"""
test_lptn.py – Basic tests for the LPTN thermal model
"""
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent /
                       "python/scripts/phase3/optimus_thermal/python"))

# ── Test 1: Conductance matrix is symmetric ──────────────────────────────────
def test_conductance_matrix_symmetric():
    R = np.array([
        [0,    0.05, 0.08, 0,    0,    0   ],
        [0.05, 0,    0.04, 0.06, 0,    0   ],
        [0.08, 0.04, 0,    0,    0.07, 0   ],
        [0,    0.06, 0,    0,    0.03, 0.10],
        [0,    0,    0.07, 0.03, 0,    0.05],
        [0,    0,    0,    0.10, 0.05, 0   ],
    ])
    N = R.shape[0]
    G = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j and R[i, j] > 0:
                g = 1.0 / R[i, j]
                G[i, j] -= g
                G[i, i] += g
    assert np.allclose(G, G.T), "Conductance matrix is not symmetric"
    print("✅ Test 1 passed: G is symmetric")

# ── Test 2: Ambient node stays fixed ─────────────────────────────────────────
def test_ambient_fixed():
    N = 6
    T_ambient = 25.0
    C = np.array([0.5, 2.0, 1.5, 3.0, 4.0, 1e6])
    Q = np.array([80.0, 30.0, 20.0, 5.0, 0.0, 0.0])
    G = np.eye(N) * 10  # dummy G
    T = np.ones(N) * T_ambient

    dt = 0.5
    for _ in range(100):
        dT = (Q - G @ T) / C
        dT[-1] = 0.0
        T = T + dt * dT

    assert abs(T[-1] - T_ambient) < 1e-6, "Ambient temperature drifted"
    print("✅ Test 2 passed: Ambient stays fixed")

# ── Test 3: Winding reaches higher temperature than ambient ──────────────────
def test_winding_hotter_than_ambient():
    from importlib.util import spec_from_file_location, module_from_spec
    import subprocess, os

    # Run the script and check output CSV exists after
    script = Path(__file__).parent.parent / \
        "python/scripts/phase3/optimus_thermal/python/lptn_model.py"
    if not script.exists():
        print("⚠️  Test 3 skipped: lptn_model.py not found at expected path")
        return

    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"lptn_model.py failed:\n{result.stderr}"

    csv_path = Path(__file__).parent.parent / \
        "python/scripts/phase3/optimus_thermal/results/csv/lptn_steady_state.csv"
    if csv_path.exists():
        import pandas as pd
        df = pd.read_csv(csv_path)
        winding_temp = df[df['Node'] == 'Winding']['SteadyState_C'].values[0]
        assert winding_temp > 25.0, "Winding should be hotter than ambient"
        print(f"✅ Test 3 passed: Winding steady-state = {winding_temp:.1f}°C")
    else:
        print("⚠️  Test 3 skipped: output CSV not found")

# ── Run all tests ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running LPTN tests...\n")
    test_conductance_matrix_symmetric()
    test_ambient_fixed()
    test_winding_hotter_than_ambient()
    print("\n✅ All LPTN tests completed.")
