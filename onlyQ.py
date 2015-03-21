'''
Created on 21 Mar, 2015

@author: yzhang28
'''

'''
Created on Mar 15, 2015

@author: yang
'''


import mdptoolbox
import numpy as np
from scipy.sparse import csr_matrix as sparse


CON_CSIZE = 5
CON_ESIZE = 10
CON_QSIZE = 10

CON_DIM = CON_CSIZE * CON_ESIZE * CON_QSIZE

CON_inj_prob = 0.0

# define actions
A_IDLE = 0 # 0: idle
A_Q = 2 # 2: send Q
SET_A = [A_IDLE, A_Q]
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
    elif act == A_Q:
        return Q_plus_mat().dot(Q_minus_mat())


def Get_Overall_mat(act):
    _cmat = Get_C_mat(act)
    _emat = Get_E_mat(act)
    _qmat = Get_Q_mat(act)
    overall_kron = np.kron(np.kron(_cmat, _emat), _qmat)
    return overall_kron



def MessengerDeliveryProb(_c):
    delvprob = [0.9, 0.7, 0.5, 0.3, 0.1]
    _prob = delvprob[_c]
#     _prob = 0.7
    return _prob

def QDelayCost(_q):
#     return -100.0
    return -10.0*_q
#     return -0.0*_q


def Reward(_c, _e, _q, action):
    # forbidded actions:
#     if (_c not in SET_CHARGER) and action==A_GETE:
#         return -65536000000000000.0
#     if (_c not in SET_MESSENGER) and action==A_Q:
#         return -65536000000000000.0

    if action == A_IDLE:
        return QDelayCost(_q)
    elif action == A_Q:
        if _e>0 and _q>0:
            return 10.0*MessengerDeliveryProb(_c) + QDelayCost(_q)
        else:
            return  -6553600000.0 + QDelayCost(_q)
    else:
        print "error in Reward()"
        exit()


def Get_2Dlized_Result(_vi, _displist):
    sizelist = [CON_CSIZE, CON_ESIZE, CON_QSIZE]
    namelist = ['C', 'E', 'Q']
    easynamelist = ['Contact state C', 'Energy state E', 'Queue state Q']
    if not len(_displist)==2:
        print "Error in Get_2Dlized_Result()"
        exit()
    
    dim1, dim2 = _displist
    ind_dim1, ind_dim2 = namelist.index(dim1), namelist.index(dim2)
    
    for i in range(len(sizelist)):
        if i not in [ind_dim1, ind_dim2]:
            NON_DISP_STATE = sizelist[i]
            NON_DISP_INDEX = i
    
    f = open('./MAT-'+str(dim1)+'-'+str(dim2),'w')
    for nondispstate in range(NON_DISP_STATE):
        f.write( str(easynamelist[NON_DISP_INDEX])+' = '+str(nondispstate)+', fixed.\n')
        f.write( str(easynamelist[ind_dim1])+' as vertical var |\n')
        f.write( str(easynamelist[ind_dim2])+' as horizontal var ->\n')
        for disp1 in range(sizelist[ind_dim1]):
            for disp2 in range(sizelist[ind_dim2]):
                _tuple = np.array([0.,0.,0.])
                _tuple[NON_DISP_INDEX] = nondispstate
                _tuple[ind_dim1] = disp1
                _tuple[ind_dim2] = disp2
                _ind = Trans_tuple_to_index(_tuple)
                actlist = ['-','Q']
                f.write( str(actlist[_vi.policy[_ind]])+'   ')
            f.write('\n')
        f.write('\n')
    f.write('\n')


R = np.zeros((CON_DIM,len(SET_A)))
# cnt = 0
for ic in range(CON_CSIZE):
    for ie in range(CON_ESIZE):
        for iq in range(CON_QSIZE):
            ind = Trans_tuple_to_index([ic, ie, iq])
            for action in SET_A:
                R[ind][SET_A.index(action)] = Reward(ic,ie,iq, action)
#             cnt = cnt + 1

P = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_Q) ])

vi = mdptoolbox.mdp.ValueIteration(P, R, 0.95)
vi.run()
print "Done"
# print vi.policy
Get_2Dlized_Result(vi,['C','E'])
Get_2Dlized_Result(vi,['C','Q'])
Get_2Dlized_Result(vi,['E','Q'])

print vi.iter

_ind1 = [3,4,0]
_ind2 = [3,4,1]
 
print vi.V[Trans_tuple_to_index(_ind1)],
print " should be smaller"
print vi.V[Trans_tuple_to_index(_ind2)],
print " should be larger"
