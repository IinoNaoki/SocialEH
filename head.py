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
CON_ESize = 10
CON_QSize = 10
CON_DIM = CON_CSize * CON_ESize * CON_QSize

CON_inj_prob = 0.4

# define actions
A_IDLE = 0 # 0: idle
A_GETE = 1 # 1: get energy
A_Q = 2 # 2: send Q
SET_A = [A_IDLE, A_GETE, A_Q]
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
    elif act == A_Q:
        return E_minus_mat()



def Get_Q_mat(act, inj_prob=CON_inj_prob):
        #
    def Q_plus_mat(getQ=1):
        _q_plus = np.zeros((CON_QSize,CON_QSize))
        for i in range(CON_QSize-1):
            _q_plus[i][i+1] = 1.0
        _q_plus[CON_QSize-1][CON_QSize-1] = 1.0
        return _q_plus
        
    def Q_minus_mat(sendQ=1):
        _q_minus = np.zeros((CON_QSize,CON_QSize))
        for j in range(1,CON_QSize):
            _q_minus[j][j-1] = 1.0
        _q_minus[0][0] = 1.0
        return _q_minus

    if act == A_IDLE:
        return Q_plus_mat()
    elif act == A_GETE:
        return Q_plus_mat()
    elif act == A_Q:
        return Q_plus_mat().dot(Q_minus_mat())

def Get_Overall_mat(act):
    _cmat = Get_C_mat(act)
    _emat = Get_E_mat(act)
    _qmat = Get_Q_mat( act)
    overall_kron = np.kron(np.kron(_cmat, _emat), _qmat)
    return overall_kron


def ElecPriceCost(_c):
    if _c<0 or _c>=CON_CSize:
        print "error in EPrice()"
        exit()
    
    if _c in SET_CHARGER:
        return -np.power(_c, 0.5)*0.1
    else:
        return -65536.0

def MessengerDeliveryProb(_c):
    if _c in SET_MESSENGER:
        _prob = np.power( (CON_CSize-1.0-_c)/(len(SET_MESSENGER)-1.0) , 0.8)
        return _prob
    else:
        return 0.0

def QDelayCost(_q):
#     return 0.0
    return -1.0*_q


def Reward(_c, _e, _q, action):
    if action == A_IDLE:
        return QDelayCost(_q)
    elif action == A_GETE:
        return ElecPriceCost(_c) + QDelayCost(_q)
    elif action == A_Q:
        if _q>0 and _e>0 and (_c in SET_MESSENGER):
            return 2.0*MessengerDeliveryProb(_c) + QDelayCost(_q)
#                 return 2.0 + QDelayCost(_qh, _ql)
        else:
            return -65536.0
    else:
        print "error in Reward()"
        exit()