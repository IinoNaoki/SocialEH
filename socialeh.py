'''
Created on 2 Mar, 2015

@author: yzhang28
'''


from head import *


R_mdp = np.zeros((CON_DIM,len(SET_A)))
# cnt = 0
for ic in range(CON_CSIZE):
    for ie in range(CON_ESIZE):
        for iq in range(CON_QSIZE):
            ind = Trans_tuple_to_index([ic, ie, iq])
            for action in SET_A:
                R_mdp[ind][action] = Reward(ic,ie,iq, action)
#             cnt = cnt + 1

P_mdp = np.array([ Get_Overall_mat(A_IDLE), Get_Overall_mat(A_GETE), Get_Overall_mat(A_Q) ])
# P = np.array([ Build_P_mat(A_IDLE), Build_P_mat(A_GETE), Build_P_mat(A_Q) ])

vi_mdp = mdptoolbox.mdp.ValueIteration(P_mdp, R_mdp, CON_DISCOUNT)
vi_mdp.run()
print "Done"
# print vi_mdp.policy
Get_2Dlized_Result(vi_mdp,['C','E'])
Get_2Dlized_Result(vi_mdp,['C','Q'])
Get_2Dlized_Result(vi_mdp,['E','Q'])

print vi_mdp.iter
# print vi_mdp.policy

# # c e q
# def supermod(L,R):
#     return np.round(L)>=np.round(R)
#   
# print "start..."
# for c in range(CON_CSIZE):
#     for e in range(1,CON_ESIZE):
#         for q in range(1,CON_QSIZE-2):
#             dv1 = vi_mdp.V[Trans_tuple_to_index([c,e-1,q+1])] - vi_mdp.V[Trans_tuple_to_index([c,e-1,q])]
#             dv2 = vi_mdp.V[Trans_tuple_to_index([c,e-1,q])] - vi_mdp.V[Trans_tuple_to_index([c,e-1,q-1])]
#             dv3 = vi_mdp.V[Trans_tuple_to_index([c,e,q+2])] - vi_mdp.V[Trans_tuple_to_index([c,e,q+1])]
#             dv4 = vi_mdp.V[Trans_tuple_to_index([c,e,q+1])] - vi_mdp.V[Trans_tuple_to_index([c,e,q])]
#             L = CON_DISCOUNT*CON_inj_prob*dv1 + CON_DISCOUNT*(1-CON_inj_prob)*dv2 + (Reward(c,e,q+1,A_Q) - Reward(c,e,q,A_Q))
#             R = CON_DISCOUNT*CON_inj_prob*dv3 + CON_DISCOUNT*(1-CON_inj_prob)*dv4 + (Reward(c,e,q+1,A_IDLE) - Reward(c,e,q,A_IDLE))
# 
#             if not supermod(L,R):
#                 print "c="+str(c)
#                 print "e="+str(e)
#                 print "q="+str(q)
#                 print "L=",str(L)
#                 print "R=",str(R)
#                 print "False"
#                 print
# print "end..."
# 
# 
# 
# for c in range(CON_CSIZE):
#     for e in range(CON_ESIZE):
#         for q in range(1,CON_QSIZE):
#             L = vi_mdp.V[Trans_tuple_to_index([c,e,q])] - vi_mdp.V[Trans_tuple_to_index([c,e,q-1])]
#             if L<0:
#                 print L
            