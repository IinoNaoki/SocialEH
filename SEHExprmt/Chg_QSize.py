'''
Created on 21 Apr, 2015

@author: yzhang28
'''

from experiment import Experiment
from parameters import Parameters
import myopic
from util import Util
import numpy as np


##################################################################
s_nothing, s_charger, s_messenger = [0], [1,2,3,4,5,6], [7,8,9,10,11,12]

charging_price = [-0.00, -1.00, -4.0, -9.0, -16.0, -25.0]
sending_prob = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
sending_gain = 50.0

if (len(s_charger) != len(charging_price)) or (len(s_messenger)!=len(sending_prob)):
    print "Error, head of main.py"
    exit(0)

csize, esize, qsize = len(s_nothing) + len(s_charger) + len(s_messenger), 10, 10

inj_prob, charge_prob = 0.4, 0.9

discount = 0.9
################################################################## 
testset = ['MDP', 'CAS', 'GREEDY', 'RANDOM']

for j,t in enumerate(testset):    
    print t+": Avg. value:"
    vi = [None for _ in range(len(testset))]
    for qsize in range(2,8):
        para = Parameters(s_nothing, s_charger, s_messenger, \
                          charging_price, sending_prob, sending_gain,\
                          csize, esize, qsize, \
                          inj_prob, charge_prob, discount)
        expt = Experiment(para)
        util = Util(para)
        
        R, P, vi[j] = expt.Build_Problem(t)
        vi[j].run()
#         print str(sum(vi[j].V)*1.0/P[0].shape[0]),
#         print '  ',
#         print
        steadys = util.SteadyStateMatrix(P, vi[j].policy, para)
        steady_act_charge = 0.0
        steady_act_send = 0.0
        for s in range(csize*esize*qsize):
            c1,e1,q1 = util.Trans_index_to_tuple(s)
            
            if c1 in s_charger:
                steady_act_charge += vi[j].policy[s] * steadys[s]
                
            if c1 in s_messenger:
                steady_act_send += vi[j].policy[s]/2.0 * steadys[s]        

        print [steady_act_charge, steady_act_send],
        print '   ',
        util.Action_2Dlized_Result(vi[j], ['C','E'],t)
        util.Action_2Dlized_Result(vi[j], ['C','Q'],t)
        util.Action_2Dlized_Result(vi[j], ['E','Q'],t)
    print