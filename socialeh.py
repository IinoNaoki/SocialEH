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

SET_IDLE = [0]
SET_CHARGER = [1,2,3,4,5]
SET_MESSENGER = [6,7,8,9,10]

CON_CSize = len(SET_IDLE) + len(SET_CHARGER) + len(SET_MESSENGER)
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


def Reward(_c, _m, _e, _qh, _ql, action):
    if action == A_IDLE:
        return 0.0 - 0.6*_qh - 0.4*_ql
    elif action == A_GETE:
        if _c in SET_CHARGER:
            return -0.1 - 0.6*_qh - 0.4*_ql # change to price of charger
        else:
            return -65536.0 
        #
    elif action == A_QH:
        if (_qh>0 and _e>0 and (_c in SET_MESSENGER)):
            return 2.0 - 0.6*_qh - 0.4*_ql
        else:
            return -65535.0
    elif action == A_QL:
        if (_ql>0 and _e>0 and (_c in SET_MESSENGER)):
            return 0.7 - 0.6*_qh - 0.4*_ql
        else:
            return -65535.0
    else:
        return 0.0 - 0.6*_qh - 0.4*_ql

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

P = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_GETE), Get_Overall_mat(A_QH), Get_Overall_mat(A_QL) ])


def Get_2Dlized_Result(_vi, _displist):
    sizelist = [CON_CSize, CON_MSize, CON_ESize, CON_QSize_H, CON_QSize_L]
    namelist = ['C', 'M', 'E', 'Q_H', 'Q_L']
    if not len(_displist)==2:
        print "Error in Get_2Dlized_Result()"
        exit()
        
    dim1, dim2 = _displist
    ind_dim1, ind_dim2 = namelist.index(dim1), namelist.index(dim2)
    
    loopset = []
    loopindset = []
    for i in range(len(sizelist)):
        if i not in [ind_dim1, ind_dim2]:
            loopset.append(sizelist[i])
            loopindset.append(i)
            
    _LOOP1, _LOOP2, _LOOP3 = loopset
    _LOOPIND1, _LOOPIND2, _LOOPIND3 = loopindset
    
    prod_left = np.array([0.,0.,0.,0.,0.])
    prod_right = np.transpose(np.array([CON_MSize*CON_ESize*CON_QSize_H*CON_QSize_L, \
                                       CON_ESize*CON_QSize_H*CON_QSize_L, \
                                       CON_QSize_H*CON_QSize_L, \
                                       CON_QSize_L, \
                                       1.0]))
    
    for lp1 in range(_LOOP1):
        for lp2 in range(_LOOP2):
            for lp3 in range(_LOOP3):
                print namelist[_LOOPIND1],' =', lp1
                print namelist[_LOOPIND2],' =', lp2
                print namelist[_LOOPIND3],' =', lp3
                print namelist[ind_dim1], ' as column var'
                print namelist[ind_dim2], ' as row var'
                for disp1 in range(sizelist[ind_dim1]):
                    for disp2 in range(sizelist[ind_dim2]):
                        prod_left[_LOOPIND1] = lp1
                        prod_left[_LOOPIND2] = lp2
                        prod_left[_LOOPIND3] = lp3
                        prod_left[ind_dim1] = disp1
                        prod_left[ind_dim2] = disp2
                        _ind = int(prod_left.dot(prod_right))
                        print _vi.policy[_ind],
                        print '  ',
                    print
                print
            print
        print
    

vi = mdptoolbox.mdp.ValueIteration(P, R, 0.99)
vi.run()
print "Done"
# print vi.policy
Get_2Dlized_Result(vi,['C','Q_L'])
# print vi.iter
# print vi.V
