'''
Created on 2 Mar, 2015

@author: yzhang28
'''

'''
S = (CS, Q_H, Q_L, MS)
CS: 5 + 1 + 5 contact states
ES: 10 energy states
Q_H: 10 queue slot of high priority
Q_L: 10 queue slot of low priority
MS: 10
'''

from head import *

# a dirty function
def Get_2Dlized_Result(_vi, _displist):
    sizelist = [CON_CSize, CON_MSize, CON_ESize, CON_QSize_H, CON_QSize_L]
    namelist = ['C', 'M', 'E', 'Q_H', 'Q_L']
    easynamelist = ['Contact state C', 'Messenger state M', 'Energy state E', 'High queue Q_H', 'Low queue Q_L']
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
    
    f = open('./MAT-'+str(dim1)+'-'+str(dim2),'w')
    for lp1 in range(_LOOP1):
        for lp2 in range(_LOOP2):
            for lp3 in range(_LOOP3):
                f.write( str(easynamelist[_LOOPIND1])+' = '+str(lp1)+'\n')
                f.write( str(easynamelist[_LOOPIND2])+' = '+str(lp2)+'\n')
                f.write( str(easynamelist[_LOOPIND3])+' = '+str(lp3)+'\n')
                f.write( str(easynamelist[ind_dim1])+' as row var |\n')
                f.write( str(easynamelist[ind_dim2])+' as row var ->\n')
                for disp1 in range(sizelist[ind_dim1]):
                    for disp2 in range(sizelist[ind_dim2]):
                        prod_left[_LOOPIND1] = lp1
                        prod_left[_LOOPIND2] = lp2
                        prod_left[_LOOPIND3] = lp3
                        prod_left[ind_dim1] = disp1
                        prod_left[ind_dim2] = disp2
                        _ind = int(prod_left.dot(prod_right))
                        f.write( str(_vi.policy[_ind])+'   ')
                    f.write('\n')
                f.write('\n')
            f.write('\n')
        f.write('\n')
    f.close()


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

vi = mdptoolbox.mdp.ValueIteration(P, R, 0.99)
vi.run()
print "Done"
# print vi.policy
Get_2Dlized_Result(vi,['C','Q_L'])
Get_2Dlized_Result(vi,['C','Q_H'])
Get_2Dlized_Result(vi,['M','Q_L'])
Get_2Dlized_Result(vi,['Q_L','Q_H'])
# print vi.iter
# print vi.V
