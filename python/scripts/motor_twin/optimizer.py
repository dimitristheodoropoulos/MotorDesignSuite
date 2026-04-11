import numpy as np

def pareto(model, speeds, torques):
    results = []

    for s in speeds:
        for t in torques:
            r = model.compute(s, t)
            score = r["efficiency"] - 0.01*r["loss"]
            results.append((s, t, r["efficiency"], r["loss"], score))

    return results