'''
Created on 2 Mar, 2015

@author: yzhang28
'''


from experiment import Experiment
from parameters import Parameters
import myopic
from util import Util
import numpy as np


##################################################################
s_nothing = [0]
s_charger = [1,2,3,4,5,6]
s_messenger = [7,8,9,10,11,12]

csize = len(s_nothing) + len(s_charger) + len(s_messenger)
esize = 3
qsize = 10

injprob = 0.4
discount = 0.9
################################################################## 
testset = ['MDP', 'CAS', 'GREEDY', 'RANDOM']

for j,t in enumerate(testset):    
    print t+": Avg. value:"
    vi = [None for _ in range(len(testset))]
    for qsize in range(2,5):
        para = Parameters(s_nothing, s_charger, s_messenger, csize, esize, qsize, injprob, discount)
        expt = Experiment(para)
        util = Util(para)
        
        R, P, vi[j] = expt.Build_Problem(t)
        vi[j].run()
#         print str(sum(vi[j].V)*1.0/P[0].shape[0]),
#         print '  ',
#         print
        steadys = util.SteadyStateMatrix(P, vi[j].policy, para)
        steady_act_charge = 0.0
        steady_mat1 = []
        loc1 = []
        steady_act_send = 0.0
        steady_mat2 = []
        loc2 = []
        for s in range(csize*esize*qsize):
            c1,e1,q1 = util.Trans_index_to_tuple(s)
#             print c1, e1, q1
            if c1 in s_charger:
                steady_act_charge += vi[j].policy[s]*steadys[s]
                steady_mat1.append(steadys[s])
                loc1.append(s)
            if c1 in s_messenger:
                steady_act_send += vi[j].policy[s]/2.0 *steadys[s]
                steady_mat2.append(steadys[s])
                loc2.append(s)
#         print [steady_act_charge, steady_act_send],
        print "mat1"
        print loc1
        print "mat2"
        print loc2
        print len(steadys)

        util.Action_2Dlized_Result(vi[j], ['C','E'],t)
        util.Action_2Dlized_Result(vi[j], ['C','Q'],t)
        util.Action_2Dlized_Result(vi[j], ['E','Q'],t)
    print

 
# R, P, vi_cas = expt.Build_Problem('CAS')
# vi_cas.run("CAS")
# print "CAS. Done!"
# print "CAS: Avg. value:"+str(sum(vi_cas.V)*1.0/P[0].shape[0])
# util.Action_2Dlized_Result(vi_cas,['C','E'],"CAS")
# util.Action_2Dlized_Result(vi_cas,['C','Q'],"CAS")
# util.Action_2Dlized_Result(vi_cas,['E','Q'],"CAS")
#  
# R, P, vi_grd = expt.Build_Problem('GREEDY')
# vi_grd.run("GREEDY")
# print "Greedy. Done!"
# print "Greedy: Avg. value:"+str(sum(vi_grd.V)*1.0/P[0].shape[0])
# util.Action_2Dlized_Result(vi_grd,['C','E'],"GREEDY")
# util.Action_2Dlized_Result(vi_grd,['C','Q'],"GREEDY")
# util.Action_2Dlized_Result(vi_grd,['E','Q'],"GREEDY")
#  
# vi_rnd = myopic.BaseLineScheme(P, R, CON_DISCOUNT)
# vi_rnd.run("RANDOM")
# print "Random. Done!"
# print "Random: Avg. value:"+str(sum(vi_rnd.V)*1.0/P[0].shape[0])
# Action_2Dlized_Result(vi_rnd,['C','E'],"RANDOM")
# Action_2Dlized_Result(vi_rnd,['C','Q'],"RANDOM")
# Action_2Dlized_Result(vi_rnd,['E','Q'],"RANDOM")


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
            