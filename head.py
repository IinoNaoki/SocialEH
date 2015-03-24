'''
Created on Mar 15, 2015

@author: yang
'''


import mdptoolbox
import numpy as np
from scipy.sparse import csr_matrix as sparse

# SET_NOTHING = [0]
# SET_CHARGER = [1,2,3,4,5]
# SET_MESSENGER = [6,7,8,9,10]
# 
SET_NOTHING = []
SET_CHARGER = [0,1,2,3,4]
SET_MESSENGER = [5,6,7,8,9]

CON_CSIZE = len(SET_NOTHING) + len(SET_CHARGER) + len(SET_MESSENGER)
CON_ESIZE = 10
CON_QSIZE = 10

CON_DIM = CON_CSIZE * CON_ESIZE * CON_QSIZE


CON_inj_prob = 0.2
CON_DISCOUNT = 0.9

# define actions
A_IDLE = 0 # 0: idle
A_GETE = 1 # 1: get energy
A_Q = 2 # 2: send Q
SET_A = [A_IDLE, A_GETE, A_Q]
#

def Trans_tuple_to_index(lis):
    if len(lis)!=3:
        print "error in Trans_tuple_to_index(lis)"
        exit()
        
    prod_left = np.asarray(lis)
    prod_right = np.transpose(np.array([CON_ESIZE*CON_QSIZE, \
                                        CON_QSIZE, \
                                        1.0]))
    return int(prod_left.dot(prod_right)) 

def Get_C_mat(act):
    # matrix for contacts
    C_mat = np.zeros((CON_CSIZE,CON_CSIZE))
    C_mat[:] = 1.0/CON_CSIZE
    return C_mat


def Get_E_mat(act):
    #
    def E_plus_mat(chg=1):
        _e_plus = np.zeros((CON_ESIZE,CON_ESIZE))
        for i in range(CON_ESIZE-1):
            _e_plus[i][i+1] = 1.0
        _e_plus[CON_ESIZE-1][CON_ESIZE-1] = 1.0
        return _e_plus
    
    def E_zero_mat():
        return np.identity(CON_ESIZE, float)
    
    def E_minus_mat(dischg=1):
        _e_minus = np.zeros((CON_ESIZE,CON_ESIZE))
        for j in range(1,CON_ESIZE):
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
    def Q_plus_mat(getQ=1, inj=inj_prob):
        _q_plus = np.zeros((CON_QSIZE,CON_QSIZE))
        for i in range(CON_QSIZE-1):
            _q_plus[i][i+1] = inj
            _q_plus[i][i] = 1.0 - inj
        _q_plus[CON_QSIZE-1][CON_QSIZE-1] = 1.0
        return _q_plus
        
    def Q_minus_mat(sendQ=1):
        _q_minus = np.zeros((CON_QSIZE,CON_QSIZE))
        for j in range(1,CON_QSIZE):
            _q_minus[j][j-1] = 1.0
        _q_minus[0][0] = 1.0
        return _q_minus

    if act == A_IDLE:
        return Q_plus_mat()
    elif act == A_GETE:
        return Q_plus_mat()
    elif act == A_Q:
        ret = Q_minus_mat().dot(Q_plus_mat())
#         ret[0][0] = 1.0
#         ret[0][1] = 0.0
        return ret


def Get_Overall_mat(act):
    _cmat = Get_C_mat(act)
    _emat = Get_E_mat(act)
    _qmat = Get_Q_mat(act)
    overall_kron = np.kron(np.kron(_cmat, _emat), _qmat)
    return overall_kron


def ElecPriceCost(_c):
    if _c<0 or _c>=CON_CSIZE:
        print "error in EPrice()"
        exit()
    
    if _c in SET_CHARGER:
        return ([-0.00, -0.001, -2.0, -7.0, -40.0, -100.0])[_c]
#         return -np.power(_c, 0.5)*0.2
    else:
        return -6553600000000000000000000000000.0

def MessengerDeliveryProb(_c):
#     delvprob = [0.9, 0.7, 0.4, 0.2, 0.1]
    delvprob = [0.1, 0.3, 0.5, 0.7, 0.9]
    if _c in SET_MESSENGER:
#         _prob = np.power( (CON_CSIZE-1.0-_c)/(len(SET_MESSENGER)-1.0) , 0.8)
        _prob = delvprob[SET_MESSENGER.index(_c)]
#         _prob = 0.5
        return _prob
    else:
        return 0.0

def QDelayCost(_q):
    return -1.0*_q
#     return -0.0



def Reward(_c, _e, _q, action):    
    if action == A_IDLE:
        return QDelayCost(_q)
    elif action == A_GETE:
        return ElecPriceCost(_c) + QDelayCost(_q)
    elif action == A_Q:
        if _e>0 and _q>0 and (_c in SET_MESSENGER):
            return 10.0*MessengerDeliveryProb(_c) + QDelayCost(_q)
        else:
            return  -6553600000000000000000000000000.0 + QDelayCost(_q)
    else:
        print "error in Reward()"
        exit()
        