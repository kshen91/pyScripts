#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: cylisery@outlook.com
# date: 2019.1.10

from numpy import array, append, sin, cos, pi, cross, dot
from numpy.linalg import norm

def runRotation( point, rVector, angle ):
    '''
    point: [ x, y, z ]
    rVertor: rotation vector [ a, b, c ]
    angle : in degree

    return : point in [x',y',z'] after rotation
    '''

    # Create quaternion for input point and rotation
    p = append(array(point), 0)
    q = array(rVector) * sin(angle * pi / 360)
    q = append( q, cos(angle* pi / 360))

    # calculate the inverse quaternion for rotation
    q_inv = quaternionInv(q)

    # calculate the point quaternion after rotation
    p_rot = quaternionMult(q, quaternionMult(p, q_inv))

    return p_rot[:3].tolist()

def quaternionInv( q ):
    q_conjugation = array([ -q[0], -q[1], -q[2], q[3] ])
    q_inv = q_conjugation / norm(q)

    return q_inv

def quaternionMult( q1, q2 ):
    v1 = q1[:3]
    w1 = q1[3]
    v2 = q2[:3]
    w2 = q2[3]

    v = cross(v1, v2) + w1*v2 + w2*v1
    w = w1*w2 - dot(v1, v2)

    return append(v, w)
