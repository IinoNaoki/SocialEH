'''
Created on Mar 15, 2015

@author: yang
'''


import mdptoolbox
import numpy as np
from scipy.sparse import csr_matrix as sparse

SET_NOTHING = [0]
SET_CHARGER = [1,2,3,4,5]
SET_MESSENGER = [6,7,8,9,10]

CON_CSize = len(SET_NOTHING) + len(SET_CHARGER) + len(SET_MESSENGER)
# CON_MSize = 5
CON_ESize = 5
CON_QSize_H = 2
CON_QSize_L = 8

CON_DIM = CON_CSize * CON_ESize * CON_QSize_H * CON_QSize_L

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


def Get_E_mat(act):
    #
    def E_plus_mat(chg=1):
        _e_plus = np.zeros((CON_ESize,CON_ESize))
        for i in range(CON_ESize-1):
            _e_plus[i][i+1] = 1.0
        _e_plus[CON_ESize-1][CON_ESize-1] = 1.0
        return _e_plus
    
    def E_zero_mat():
        return np.identity(CON_ESize, float)
    
    def E_minus_mat(dischg=1):
        _e_minus = np.zeros((CON_ESize,CON_ESize))
        for j in range(1,CON_ESize):
            _e_minus[j][j-1] = 1.0
        _e_minus[0][0] = 1.0
        return _e_minus

    if act == A_IDLE:
        return E_zero_mat()
    elif act == A_GETE:
        return E_plus_mat()
    elif act == A_QH or act == A_QL:
        return E_minus_mat()


def Get_Q_mat(HorL, act):
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
    _emat = Get_E_mat(act)
    _qhmat = Get_Q_mat('H', act)
    _qlmat = Get_Q_mat('L', act)
    overall_kron = np.kron(np.kron(_cmat, _emat), np.kron(_qhmat,_qlmat))
#     print overkron.shape
    return overall_kron


def ElecPriceCost(_c):
    if _c<0 or _c>=CON_CSize:
        print "error in EPrice()"
        exit()
    
    if _c in SET_CHARGER:
        return -np.power(_c, 0.5)*1.0
    else:
        return -65536.0

def MessengerDeliveryProb(_c):
    if _c in SET_MESSENGER:
        # return np.power( (CON_CSize-1.0-_c)/(len(SET_MESSENGER)-1.0) , 0.5)
        return 0.5
    else:
        return 0.0

def QDelayCost(_qh, _ql):
    return -0.6*_qh -0.4*_ql


def Reward(_c, _e, _qh, _ql, action):
    if action == A_IDLE:
        return QDelayCost(_qh, _ql)
    elif action == A_GETE:
        return ElecPriceCost(_c) + QDelayCost(_qh, _ql)
    elif action == A_QH:
        if _qh>0 and _e>0 and (_c in SET_MESSENGER):
            return 2.0*MessengerDeliveryProb(_c) + QDelayCost(_qh, _ql)
#                 return 2.0 + QDelayCost(_qh, _ql)
        else:
            return -65535000.0
    elif action == A_QL:
        if _ql>0 and _e>0 and (_c in SET_MESSENGER):
            return 1.0*MessengerDeliveryProb(_c) + QDelayCost(_qh, _ql)
#                 return 0.7 + QDelayCost(_qh, _ql)
        else:
            return -65535000.0
    else:
        print "error in Reward()"
        exit()