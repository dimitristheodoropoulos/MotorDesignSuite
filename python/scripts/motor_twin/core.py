# motor_twin/core.py
import numpy as np

class MotorModel:
    def __init__(self, Rs=0.03, kfe=1.2, kmech=0.25):
        self.Rs = Rs
        self.kfe = kfe
        self.kmech = kmech
        self.base_speed = 6000

    def compute(self, speed, torque, Vdc=400):
        omega = speed * 2*np.pi/60

        # Flux weakening region
        if speed > self.base_speed:
            torque *= self.base_speed / speed

        P_out = torque * omega

        I = torque / 8.0

        P_cu = 3 * self.Rs * I**2
        P_fe = self.kfe * (speed/1000)**2 * 120
        P_mech = self.kmech * omega

        loss = P_cu + P_fe + P_mech
        P_in = P_out + loss

        eff = P_out / (P_in + 1e-9)

        return {
            "efficiency": eff * 100,
            "loss": loss,
            "P_out": P_out
        }