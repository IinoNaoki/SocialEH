'''
Created on 2 Mar, 2015

@author: yzhang28
'''


from head import *

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
                actlist = ['-','c','Q']
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
                R[ind][action] = Reward(ic,ie,iq, action)
#             cnt = cnt + 1

P = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_GETE), Get_Overall_mat(A_Q) ])
# P = np.array([ Build_P_mat(A_IDLE), Build_P_mat(A_GETE), Build_P_mat(A_Q) ])

vi = mdptoolbox.mdp.ValueIteration(P, R, 0.95)
vi.run()
print "Done"
# print vi.policy
Get_2Dlized_Result(vi,['C','E'])
Get_2Dlized_Result(vi,['C','Q'])
Get_2Dlized_Result(vi,['E','Q'])

print vi.iter
print vi.policy

_ind1 = [3,4,0]
_ind2 = [3,4,1]

print vi.V[Trans_tuple_to_index(_ind1)],
print " should be smaller"
print vi.V[Trans_tuple_to_index(_ind2)],
print " should be larger"