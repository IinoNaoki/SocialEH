from onlyQ import *

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
    
print Get_Q_mat(2)