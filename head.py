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

SET_NOTHING = [] # no idle
SET_CHARGER = [] # no charger
SET_MESSENGER = [0,1,2,3,4]

CON_CSIZE = len(SET_NOTHING) + len(SET_CHARGER) + len(SET_MESSENGER)
CON_ESIZE = 10
CON_QSIZE = 10

CON_DIM = CON_CSIZE * CON_ESIZE * CON_QSIZE

# SET_NOTHING = [0]
# SET_CHARGER = [1]
# SET_MESSENGER = [2]
# 
# CON_CSIZE = len(SET_NOTHING) + len(SET_CHARGER) + len(SET_MESSENGER)
# CON_ESIZE = 2
# CON_QSIZE = 2
# CON_DIM = CON_CSIZE * CON_ESIZE * CON_QSIZE

CON_inj_prob = 0.4

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

def Build_C_prob(c1,e1,q1, c2,e2,q2, act):
    return 1.0/CON_CSIZE


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
    
def Build_E_prob(c1,e1,q1, c2,e2,q2, act):
    if act==A_IDLE:
        return np.identity(CON_ESIZE, float)[e1][e2]
    if act==A_GETE:
        if c1 in SET_CHARGER:
            if e2==e1 + 1 or (e1==CON_ESIZE-1 and e2==CON_ESIZE-1):
                return 1.0
            else:
                return 0.0
        else:
            return np.identity(CON_ESIZE, float)[e1][e2]
    if act==A_Q:
        if e2==e1-1 or (e2==0 and e1==0):
            return 1.0
        else:
            return 0.0
    else:
        print "error in Build_E_prob(c1,e1,q1, c2,e2,q2, act)!"
        exit()



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
        return Q_plus_mat().dot(Q_minus_mat())

def Build_Q_prob(c1,e1,q1, c2,e2,q2, act):
    if act==A_IDLE or act==A_GETE:
        if q2==CON_QSIZE-1 and q1==CON_QSIZE-1:
            return 1.0
        elif q2==q1+1:
            return CON_inj_prob
        elif q2==q1:
            return 1.0 - CON_inj_prob
        else:
            return 0.0
    if act==A_Q:
        if e1>0 and q1>0 and (c1 in SET_MESSENGER):
            if q2==q1-1:
                return 1.0
            else:
                return 0.0
        else:
            return np.identity(CON_QSIZE, float)[q1][q2]

def Get_Overall_mat(act):
    _cmat = Get_C_mat(act)
    _emat = Get_E_mat(act)
    _qmat = Get_Q_mat(act)
    overall_kron = np.kron(np.kron(_cmat, _emat), _qmat)
    return overall_kron


def Build_P_mat(act):
    p = np.zeros((CON_DIM,CON_DIM))
    for c1 in range(CON_CSIZE):
        for e1 in range(CON_ESIZE):
            for q1 in range(CON_ESIZE):
                for c2 in range(CON_CSIZE):
                    for e2 in range(CON_ESIZE):
                        for q2 in range(CON_ESIZE):
                            s1 = Trans_tuple_to_index([c1,e1,q1])
                            s2 = Trans_tuple_to_index([c2,e2,q2])
                            p[s1][s2] = Build_C_prob(c1, e1, q1, c2, e2, q2, act) \
                                        * Build_E_prob(c1, e1, q1, c2, e2, q2, act) \
                                        * Build_Q_prob(c1, e1, q1, c2, e2, q2, act)
    return p

def ElecPriceCost(_c):
    if _c<0 or _c>=CON_CSIZE:
        print "error in EPrice()"
        exit()
    
    if _c in SET_CHARGER:
        return ([-0.00, -0.001, -2.0, -7.0, -40.0, -100.0])[_c]
#         return -np.power(_c, 0.5)*0.2
    else:
        return 0.0

def MessengerDeliveryProb(_c):
    delvprob = [0.9, 0.7, 0.4, 0.2, 0.1]
    if _c in SET_MESSENGER:
#         _prob = np.power( (CON_CSIZE-1.0-_c)/(len(SET_MESSENGER)-1.0) , 0.8)
        _prob = delvprob[SET_MESSENGER.index(_c)]
#         _prob = 0.5
        return _prob
    else:
        return 0.0

def QDelayCost(_q):
#     return -100.0
#     return -10.0*_q
    return -0.0*_q
#     return 0.0


def Reward(_c, _e, _q, action):
    # forbidded actions:
    if (_c not in SET_CHARGER) and action==A_GETE:
        return -65536000000000000.0
    if (_c not in SET_MESSENGER) and action==A_Q:
        return -65536000000000000.0
    
    if action == A_IDLE:
        return QDelayCost(_q)
    elif action == A_GETE:
        return ElecPriceCost(_c) + QDelayCost(_q)
    elif action == A_Q:
        if _e>0 and _q>0:
            return 10.0*MessengerDeliveryProb(_c) + QDelayCost(_q)
        else:
            return  QDelayCost(_q)
    else:
        print "error in Reward()"
        exit()
        