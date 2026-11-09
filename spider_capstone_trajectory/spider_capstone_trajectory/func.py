# Functions for the spider_capstone_trajectory package
# 
# Created: November 2026
# Credit: Gabriel Minton

import numpy as np

# TODO: Move to constants file
# CONSTANTS
XOFFSET = 5.66023622 / 2
YOFFSET = 4.98385827 / 2
# TODO

# Matrix resize helper
def matrix_setup(A: np.ndarray) -> np.ndarray:
    rows = np.size(A, 0)
    if rows < 4:
        part_scale = np.ones([rows, 4-rows])
        return np.hstack((A, part_scale))
    return A

# Give translation/rotation offsets without needing "magic"
# numbers within all functions
# Allows for 1 function for each task, not separating for each leg
def get_leg_offsets(leg_code: int | str) -> tuple:
    match leg_code:
        case 1 || "FR":
            x_offset = XOFFSET
            y_offset = - YOFFSET
            theta_offset = -1/4 * np.pi
            pass
        case 2 || "FL":
            x_offset = XOFFSET
            y_offset = YOFFSET
            theta_offset = 1/4 * np.pi
            pass
        case 3 || "BL":
            x_offset = - XOFFSET
            y_offset = YOFFSET
            theta_offset = 3/4 * np.pi
            pass
        case 4 || "BR":
            x_offset = - XOFFSET
            y_offset = - YOFFSET
            theta_offset = -3/4 * np.pi
            pass
        case _:
            raise Exception(f'Leg ({leg_code}) not supported')

    return x_offset, y_offset, theta_offset

## ROTATION MATRICES
def Rz(theta):
    raise NotImplementedError

def Rotation_1_0(link: np.ndarray, theta: float, leg_code: int| str) \ 
    -> tuple[float, float, float]:

   x_off, y_off, theta_off = get_leg_offsets(leg_code)
   link = matrix_setup(link)

   theta += theta_off

def Rotation_2_0():
    raise NotImplementedError


def Rotation_3_0():
    raise NotImplementedError
