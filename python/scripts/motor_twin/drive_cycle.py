import numpy as np

def cycle(n=300):
    t = np.linspace(0, 1, n)

    speed = 3000 + 8000*(np.sin(2*np.pi*t)**2)
    torque = 40 + 220*(np.sin(4*np.pi*t)**2)

    return speed, torque