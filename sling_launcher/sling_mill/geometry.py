"""Exact hub-tangent geometry; SI coordinates, positive CCW driving torque."""
import numpy as np

def geometry(radius, hub_radius):
    if not 0 < hub_radius < radius:
        raise ValueError('Require 0 < hub radius < belt radius')
    O = np.zeros(2)
    P = np.array([radius, 0.])
    Q = np.array([hub_radius, 0.])
    H = np.array([hub_radius**2/radius,
                  hub_radius*np.sqrt(1-(hub_radius/radius)**2)])
    return O, P, Q, H

def rotate(points, angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.asarray(points) @ np.array([[c, s], [-s, c]])
