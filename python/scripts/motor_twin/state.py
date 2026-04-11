# motor_twin/state.py
from dataclasses import dataclass

@dataclass
class MotorState:
    speed: float = 0.0
    torque: float = 0.0
    temp: float = 25.0
    efficiency: float = 0.0
    loss: float = 0.0