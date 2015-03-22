'''
Created on 22 Mar, 2015

@author: yzhang28
'''

from head import *

def Build_C_prob(c1,e1,q1, c2,e2,q2, act):
    return 1.0/CON_CSIZE


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