'''
Created on 2 Mar, 2015

@author: yzhang28
'''


from head import *

# a dirty function
def Get_2Dlized_Result(_vi, _displist):
    sizelist = [CON_CSize, CON_ESize, CON_QSize]
    namelist = ['C', 'E', 'Q']
    easynamelist = ['Contact state C', 'Energy state E', 'Queue state Q']
    if not len(_displist)==2:
        print "Error in Get_2Dlized_Result()"
        exit()
    
    dim1, dim2 = _displist
    ind_dim1, ind_dim2 = namelist.index(dim1), namelist.index(dim2)
    
    for i in range(len(sizelist)):
        if i not in [ind_dim1, ind_dim2]:
            NON_FIXED_STATE = sizelist[i]
            FIXED_INDEX = i
    
    prod_left = np.array([0.,0.,0.])
    prod_right = np.transpose(np.array([CON_ESize*CON_QSize, \
                                       CON_QSize, \
                                       1.0]))
    
    f = open('./MAT-'+str(dim1)+'-'+str(dim2),'w')
    for nonfixedstate in range(NON_FIXED_STATE):
        f.write( str(easynamelist[FIXED_INDEX])+' = '+str(nonfixedstate)+'\n')
        f.write( str(easynamelist[ind_dim1])+' as vertical var |\n')
        f.write( str(easynamelist[ind_dim2])+' as horizontal var ->\n')
        for disp1 in range(sizelist[ind_dim1]):
            for disp2 in range(sizelist[ind_dim2]):
                prod_left[FIXED_INDEX] = nonfixedstate
                prod_left[ind_dim1] = disp1
                prod_left[ind_dim2] = disp2
                _ind = int(prod_left.dot(prod_right))
                actlist = ['-','c','Q']
                f.write( str(actlist[_vi.policy[_ind]])+'   ')
            f.write('\n')
        f.write('\n')
    f.write('\n')


R = np.zeros((CON_DIM,len(SET_A)))
cnt = 0
for ic in range(CON_CSize):
    for ie in range(CON_ESize):
        for iq in range(CON_QSize):
            for action in SET_A:
                R[cnt][action] = Reward(ic,ie,iq, action)
            cnt = cnt + 1

P = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_GETE), Get_Overall_mat(A_Q) ])


print P
print
print R
vi = mdptoolbox.mdp.ValueIteration(P, R, 0.95)
vi.run()
print "Done"
# print vi.policy
Get_2Dlized_Result(vi,['C','E'])
Get_2Dlized_Result(vi,['C','Q'])
Get_2Dlized_Result(vi,['E','Q'])

# print vi.iter
# print vi.V
