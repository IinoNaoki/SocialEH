'''
Created on 2 Mar, 2015

@author: yzhang28
'''


'''
S = (CS, Q_H, Q_L, MS)
CS: 10 + 1 + 10 contact states
ES: 10 energy states
Q_H: 10 queue slot of high priority
Q_L: 10 queue slot of low priority
MS: 10
'''

import mdptoolbox
import numpy as np

CON_CSize = 10 + 1 + 10

CON_ESize = 10

CON_QSize_H = 8
CON_injec_high = 0.5
CON_QSize_L = 8
CON_injec_low = 0.5

CON_MSize = 10

# define actions
A = np.array([0,1,2])
A_IDLE = 0 # 0: idle
A_GETE = 1 # 1: get energy
A_QH = 2 # 2: send Q_H
A_QL = 3 # 3: send Q_L
#

# matrix for contacts
C_mat = np.zeros((CON_CSize,CON_CSize))
C_mat[:] = 1.0/CON_CSize
#


#
# def E_plus_mat(elen):
# 
# def E_minus

# def get_E_mat(act):
#     if act == A_GETE:
        


# matrix for Q high and Q low
def Q_plus_mat(qlen, inj):
    _q_plus = np.array([[0.0 for _ in range(qlen)] for _ in range(qlen)])
    for i in range(qlen-1):
        _q_plus[i][i] = 1.0 - inj
        _q_plus[i][i+1] = inj
    _q_plus[qlen-1][qlen-1] = 1.0
    return _q_plus

def Q_zero_mat(qlen):
    return np.identity(qlen, float)
    
def Q_minus_mat(qlen):    
    _q_minus = np.array([[0.0 for _ in range(qlen)] for _ in range(qlen)])
    for j in range(1,qlen):
        _q_minus[j][j-1] = 1.0
    _q_minus[0][0] = 1.0    
    return _q_minus

def get_Q_mat(HorL, act):
    Q_H_mat_plus = Q_plus_mat(CON_QSize_H,CON_injec_high)
    Q_H_mat_zero = Q_zero_mat(CON_QSize_H)
    Q_H_mat_minus = Q_minus_mat(CON_QSize_H)
    
    Q_L_mat_plus = Q_plus_mat(CON_QSize_L,CON_injec_low)
    Q_L_mat_zero = Q_zero_mat(CON_QSize_L)
    Q_L_mat_minus = Q_minus_mat(CON_QSize_L)
    
    if HorL == 'H':
        if act == A_QH:
            return Q_H_mat_plus.dot(Q_H_mat_minus)
        else:
            return Q_H_mat_plus.dot(Q_H_mat_zero)
    elif HorL == 'L':
        if act == A_QL:
            return Q_L_mat_plus.dot(Q_L_mat_minus)
        else:
            return Q_L_mat_plus.dot(Q_L_mat_zero)
    else:
        exit('Error in get_Q_mat()') 


# matrix for messenger
M_mat = np.zeros((CON_MSize,CON_MSize))
M_mat[:] = 1.0/CON_MSize


P = [ np.kron(Q_H_AisH,Q_H_AisL), np.kron(Q_L_AisH,Q_L_AisL) ]

R_AH = np.array([0 for _ in range(CON_Q_high*CON_Q_low)])
R_AL = np.array([0 for _ in range(CON_Q_high*CON_Q_low)])
for qh in range(CON_Q_high):
    for ql in range(CON_Q_low):
        ind = int(qh*(CON_Q_low) + ql)
        R_AH[ind] =  4.0 - 0.1*qh - 0.05*ql
        R_AL[ind] =  2.0 - 0.1*qh - 0.05*ql
        if qh==0:
            R_AH[ind] = 0.0
        if ql==0:
            R_AL[ind] = 0.0
R_AH = R_AH.reshape(CON_Q_high*CON_Q_low,1)    
R_AL = R_AL.reshape(CON_Q_high*CON_Q_low,1)
R = np.concatenate((R_AH, R_AL),axis=1)
# print R


vi = mdptoolbox.mdp.ValueIteration(P, R, 0.99)
vi.run()
print np.asarray(vi.policy).reshape(CON_Q_high,CON_Q_low)
# print vi.iter
# print np.asarray(vi.V).reshape(CON_Q_high,CON_Q_low)