# motor_twin/thermal.py

class ThermalModel:
    def __init__(self, Rth=0.05, Cth=50):
        self.Rth = Rth
        self.Cth = Cth

    def step(self, temp, loss, dt=1.0):
        dT = (loss * self.Rth - (temp - 25)) / self.Cth
        return temp + dT * dt