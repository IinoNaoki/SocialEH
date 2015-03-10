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
from scipy.sparse import csr_matrix as sparse

CON_CSize = 10 + 1 + 10
CON_MSize = 10
CON_ESize = 10
CON_QSize_H = 8
CON_QSize_L = 8

CON_CSize = 5 + 1 + 5
CON_MSize = 5
CON_ESize = 5
CON_QSize_H = 2
CON_QSize_L = 8

CON_DIM = CON_CSize * CON_MSize * CON_ESize * CON_QSize_H * CON_QSize_L

CON_injec_low = 0.8
CON_injec_high = 0.1

# define actions
A_IDLE = 0 # 0: idle
A_GETE = 1 # 1: get energy
A_QH = 2 # 2: send Q_H
A_QL = 3 # 3: send Q_L
SET_A = [A_IDLE, A_GETE, A_QH, A_QL]
#

def Get_C_mat(act):
    # matrix for contacts
    C_mat = np.zeros((CON_CSize,CON_CSize))
    C_mat[:] = 1.0/CON_CSize
    return C_mat
#

def Get_M_mat(act):
    # matrix for messenger
    M_mat = np.zeros((CON_MSize,CON_MSize))
    M_mat[:] = 1.0/CON_MSize
    return M_mat

#
def E_plus_mat(elen, chg=1):
    _e_plus = np.array([[0.0 for _ in range(elen)] for _ in range(elen)])
    for i in range(elen-1):
        _e_plus[i][i+1] = 1.0
    _e_plus[elen-1][elen-1] = 1.0
    return _e_plus

def E_zero_mat(elen):
    return np.identity(elen, float)

def E_minus_mat(elen,dischg=1):
    _e_minus = np.array([[0.0 for _ in range(elen)] for _ in range(elen)])
    for j in range(1,elen):
        _e_minus[j][j-1] = 1.0
    _e_minus[0][0] = 1.0
    return _e_minus

def Get_E_mat(act):
    if act == A_IDLE:
        return E_zero_mat(CON_ESize)
    elif act == A_GETE:
        return E_plus_mat(CON_ESize)
    elif act == A_QH or act == A_QL:
        return E_minus_mat(CON_ESize)


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

def Get_Q_mat(HorL, act):
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



def Get_Overall_mat(act):
    _cmat = Get_C_mat(act)
    _mmat = Get_M_mat(act)
    _emat = Get_E_mat(act)
    _qhmat = Get_Q_mat('H', act)
    _qlmat = Get_Q_mat('L', act)
    overkron = np.kron(np.kron(np.kron(_cmat, _mmat), _emat), np.kron(_qhmat,_qlmat))
#     print overkron.shape
    return overkron


def Reward(_c,_m,_e,_qh,_ql, action):
    if action == A_IDLE:
        return 0.0
    elif action == A_GETE and _c in [0,1,2,3,4]:
        return -0.5
    elif action == A_QH and _qh>0 and _c in [6,7,8,9,10]:
        return 2.0
    elif action == A_QL and _ql>0 and _c in [6,7,8,9,10]:
        return 0.7
    else:
        return 0.0

R = np.zeros((CON_DIM,len(SET_A)))
cnt = 0
for ic in range(CON_CSize):
    for im in range(CON_MSize):
        for ie in range(CON_ESize):
            for iqh in range(CON_QSize_H):
                for iql in range(CON_QSize_L):
                    for action in SET_A:
                        R[cnt][action] = Reward(ic,im,ie,iqh,iql, action)
                    cnt = cnt + 1
                    
# R = np.random.randint(0,5,(CON_DIM,len(SET_A)))
print R
print R.shape

P = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_GETE), Get_Overall_mat(A_QH), Get_Overall_mat(A_QL) ])
# 
# print P.shape
# print P
# print R.shape
# print R

vi = mdptoolbox.mdp.ValueIteration(P, R, 0.99)
vi.run()
print "Done"
# print vi.policy
print vi.iter
# print vi.V