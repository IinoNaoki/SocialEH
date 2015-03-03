'''
Created on 2 Mar, 2015

@author: yzhang28
'''

import mdptoolbox
import numpy as np

CONST_Q_high = 8
CONST_Q_low = 8
CONST_injec_high = 0.5
CONST_injec_low = 0.5

def constr_Q_plus(qlen, inj):
    _q_plus = np.array([[0.0 for _ in range(qlen)] for _ in range(qlen)])
    for i in range(qlen-1):
        _q_plus[i][i] = 1.0 - inj
        _q_plus[i][i+1] = inj
    _q_plus[qlen-1][qlen-1] = 1.0
    return _q_plus
    
def constr_Q_minus(qlen, inj):    
    _q_minus = np.array([[0.0 for _ in range(qlen)] for _ in range(qlen)])
    for j in range(1,qlen):
        _q_minus[j][j-1] = 1.0
    _q_minus[0][0] = 1.0    
    return _q_minus

Q_H_AisH = constr_Q_plus(CONST_Q_high,CONST_injec_high).dot(constr_Q_minus(CONST_Q_high,CONST_injec_high))
Q_H_AisL = constr_Q_minus(CONST_Q_high,CONST_injec_high)
Q_L_AisH = constr_Q_minus(CONST_Q_low,CONST_injec_low)
Q_L_AisL = constr_Q_plus(CONST_Q_low,CONST_injec_low).dot(constr_Q_minus(CONST_Q_low,CONST_injec_low))

P = [ np.kron(Q_H_AisH,Q_H_AisL), np.kron(Q_L_AisH,Q_L_AisL) ]

R_AH = np.array([0 for _ in range(CONST_Q_high*CONST_Q_low)])
R_AL = np.array([0 for _ in range(CONST_Q_high*CONST_Q_low)])
for qh in range(CONST_Q_high):
    for ql in range(CONST_Q_low):
        ind = int(qh*(CONST_Q_low) + ql)
        R_AH[ind] =  4.0 - 0.1*qh - 0.05*ql
        R_AL[ind] =  2.0 - 0.1*qh - 0.05*ql
        if qh==0:
            R_AH[ind] = 0.0
        if ql==0:
            R_AL[ind] = 0.0
R_AH = R_AH.reshape(CONST_Q_high*CONST_Q_low,1)    
R_AL = R_AL.reshape(CONST_Q_high*CONST_Q_low,1)
R = np.concatenate((R_AH, R_AL),axis=1)
# print R


vi = mdptoolbox.mdp.ValueIteration(P, R, 0.99)
vi.run()
print np.asarray(vi.policy).reshape(CONST_Q_high,CONST_Q_low)
# print vi.iter
# print np.asarray(vi.V).reshape(CONST_Q_high,CONST_Q_low)