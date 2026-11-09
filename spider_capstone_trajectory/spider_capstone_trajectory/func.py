# Functions for the spider_capstone_trajectory package
# 
# Created: November 2026
# Author: Gabriel Minton
# Credit: Neil Breslich

import math, numpy as np
from dataclasses import dataclass

# Constants
LINK1_LEN = 5
LINK2_LEN = 9
LINK3_LEN = 10.5
XOFFSET = 5.66023622 / 2
YOFFSET = 4.98385827 / 2

# Matrix resize helper
def matrix_setup(A: np.ndarray) -> np.ndarray:
    rows = np.size(A, 0)
    if rows < 4:
        part_scale = np.ones([rows, 4-rows])
        return np.hstack((A, part_scale))
    return A

# Give translation/rotation offsets without needing "magic"
# numbers within all functions
# Allows for 1 Rotation_1_0 function covering all legs
def get_leg_offsets(leg_code: int | str) -> tuple:
    match leg_code:
        case (1 | "FR"):
            x_offset = XOFFSET
            y_offset = - YOFFSET
            theta_offset = -1/4 * np.pi
            pass
        case (2 | "FL"):
            x_offset = XOFFSET
            y_offset = YOFFSET
            theta_offset = 1/4 * np.pi
            pass
        case (3 | "BL"):
            x_offset = - XOFFSET
            y_offset = YOFFSET
            theta_offset = 3/4 * np.pi
            pass
        case (4 | "BR"):
            x_offset = - XOFFSET
            y_offset = - YOFFSET
            theta_offset = -3/4 * np.pi
            pass
        case _:
            raise Exception(f'Leg ({leg_code}) not supported')

    return x_offset, y_offset, theta_offset

## ROTATION MATRICES ##
# y-axis rotation
def Ry(theta, length: float) -> np.ndarray:
   return np.array([
       [ np.cos(theta), 0, np.sin(theta), length],
       [ 0,             1, 0,             0],
       [-np.sin(theta), 0, np.cos(theta), 0],
       [ 0,             0, 0,             1]
   ])

# z-axis rotation
def Rz(theta, x_off, y_off: float) -> np.ndarray:
   return np.array([
       [np.cos(theta), -np.sin(theta), 0, x_off],
       [np.sin(theta),  np.cos(theta), 0, y_off],
       [0,              0,             1, 0],
       [0,              0,             0, 1]
   ])

# Rotation from frame 1 to frame 0
def Rotation_1_0(link: np.ndarray, theta: float, leg_code: int | str) \
    -> tuple[np.ndarray, np.ndarray]:

    x_off, y_off, theta_off = get_leg_offsets(leg_code)
    link = matrix_setup(link)

    theta += theta_off
    rz = Rz(theta, x_off, y_off)
    trans_link = (rz @ link.T).T

    return trans_link, rz

# Rotation from frame 2 to frame 0
# takes rz from Rotation_1_0
def Rotation_2_0(link, rz: np.ndarray, theta, length: float) -> np.ndarray:
    link = matrix_setup(link)

    ry = Ry(theta, length)
    rzry = Rz @ Ry

    trans_link = (rzry @ link.T).T

    return trans_link, rzry

# Rotation from frame 3 to frame 0
# takes rzry from Rotation_2_0
def Rotation_3_0(link, rzry: np.ndarray, theta, length: float):
    link = matrix_setup(link)

    ry = Ry(theta, length)

    trans_link = (rzry @ ry @ link.T).T

    return trans_link

# NOTE
# should it be 3_2 to 2_1 to 1_0
# 3_2 @ 2_1 @ 1_0
# NOTE

## Inverse Kinematics ##
@dataclass
class Point3D():
    x: float
    y: float
    z: float

# Revisit the geometry, something is not adding up
def inverse_kinematics(p: Point3D, leg_code: int | str):
    # Get point offsets
    x_off, y_off, theta_off = get_leg_offsets(leg_code)
    x = p.x - x_off
    y = p.x - y_off
    z = p.z

    # Calculate theta angles
    theta1 = np.arctan2(y, x) - theta_off
    r2 = np.abs((x) / (np.cos(np.arctan2(y, x)))) - LINK1_LEN
    r1 = math.sqrt(z ** 2 + r2 ** 2)
    phi2 = np.arctan2(z, r2)

    try:
        with np.errstate(invalid = 'raise'):
            phi1 = np.arccos(
                (LINK3_LEN ** 2 - LINK2_LEN ** 2 - r1 ** 2) / 
                (-2 * LINK2_LEN * r1)
            )
    except (FloatingPointError, RuntimeWarning) as e:
        print(f'Warning: {p} out of range. Using default value')
        phi1 = 0.0
    
    theta2 = -(phi1 + phi2)

    try:
        with np.errstate(invalid = 'raise'):
            phi3 = np.arccos(
                (r1 ** 2 - LINK2_LEN ** 2 - LINK3_LEN ** 2) / 
                (-2 * LINK3_LEN * LINK2_LEN)
            )
    except (FloatingPointError, RuntimeWarning) as e:
        print(f'Warning: {p} out of range. Using default value')
        phi3 = 0.0

    theta3 = np.pi - phi3
    
    return theta1, theta2, theta3

if __name__ == '__main__':
    p = Point3D(1.0, 2.0, 3.0)
    pl = [1.0, 2.0, 3.0]

    from Inverse_Kinematics import *
    print('Neil to Gabe Errors:')
    print('FR')
    Gabe = (inverse_kinematics(p, 1))
    Neil = (inverse_kinematic_FR(pl))
    print([G - N for G,N in zip(Gabe, Neil)])
    
    print('FL')
    Gabe = (inverse_kinematics(p, 2))
    Neil = (inverse_kinematic_FL(pl))
    print([G - N for G,N in zip(Gabe, Neil)])

    print('RL')
    Gabe = (inverse_kinematics(p, 3))
    Neil = (inverse_kinematic_RL(pl))
    print([G - N for G,N in zip(Gabe, Neil)])

    print('RR')
    Gabe = (inverse_kinematics(p, 4))
    Neil = (inverse_kinematic_RR(pl))
    print([G - N for G,N in zip(Gabe, Neil)])

