# coding: utf-8

import time


# Leibniz formula for pi
def leibniz_pi_precision(precision=10):
    rv = 1
    for i in range(precision):
        time.sleep(0.001)
        if i % 2 == 0:
            rv -= 1/(2*(i+1)+1)
        else:
            rv += 1/(2*(i+1)+1)
    return rv * 4.0


# Bailey–Borwein–Plouffe formula
# spigot algorithm for computing the nth binary digit of the mathematical
# constant pi using base-16 representation
def bailey_pi_precision(precision=10):
    p16 = 1
    pi = 0
    for k in range(precision):
        time.sleep(0.01)
        pi += 1.0/p16 * (4.0/(8*k + 1) - 2.0/(8*k + 4) - 1.0/(8*k + 5) - 1.0/(8*k+6));
        p16 *= 16;
    return pi
