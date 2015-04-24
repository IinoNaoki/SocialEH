'''
Created on 23 Apr, 2015

@author: yzhang28
'''

'''
*********************
Change random precision (how many states to randomly choose to initial a threshold-randomization updating
*********************
'''

import pickle
from experiment import Experiment
from parameters import Parameters
import myopic
from util import Util
import numpy as np

import random
import time

import sys
sys.path.append("..")

##################################################################
s_nothing, s_charger, s_messenger = [0], [1,2,3,4,5,6], [7,8,9,10,11,12]

charging_price = [-0.00, -1.00, -4.0, -9.0, -16.0, -25.0]
sending_prob = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
sending_gain = 15.0

csize = len(s_nothing) + len(s_charger) + len(s_messenger)
esize = 10
qsize = 10

inj_prob, charge_prob = 0.4, 0.9

discount = 0.9
################################################################## 


TEST_SET = ['GREEDY', 'RANDOM', 'THRESHOLDRANDOM']
# TEST_SET = ['THRESHOLDRANDOM']
TEST_RANGE = [0,1,2,3,4,5,6]

def paralist_func(item):
    s = csize*esize*qsize
    upset = [1,2,3,4,5,6,7]
    wt = range(int(s*3.0/24.0))
    return [upset[item], wt] # slack state and choice set

for j,t in enumerate(TEST_SET):
    # to store results
    exp_value_lis, steady_value_lis, steady_chg_rate_lis, steady_snd_rate_lis = [], [], [], []
    
    time_consumed_lis = []
    
    vi = [None for _ in range(len(TEST_SET))]
    for item in TEST_RANGE:
        para = Parameters(s_nothing, s_charger, s_messenger, \
                          charging_price, sending_prob, sending_gain,\
                          csize, esize, qsize, \
                          inj_prob, charge_prob, discount, extra_para_lis=paralist_func(item))
        expt = Experiment(para)
        util = Util(para)
        
        R, P, vi[j] = expt.Build_Problem(t)
        t_start = time.time()
        vi[j].run()
        time_consumed_lis.append(time.time()-t_start)
        
        exp_value_lis.append( sum(vi[j].V)*1.0/(csize*esize*qsize) )
        
        steadys = util.SteadyStateMatrix(P, vi[j].policy, para)
        
        _steady_v = 0.0
        _steady_act_charge = 0.0
        _steady_act_send = 0.0
        for s in range(csize*esize*qsize):
            c1,e1,q1 = util.Trans_index_to_tuple(s)
            if c1 in s_charger:
                _steady_act_charge += vi[j].policy[s] * steadys[s]
            if c1 in s_messenger:
                _steady_act_send += vi[j].policy[s]/2.0 * steadys[s]        
            _steady_v += vi[j].V[s] * steadys[s]
        steady_value_lis.append(_steady_v)
        steady_chg_rate_lis.append(_steady_act_charge)
        steady_snd_rate_lis.append(_steady_act_send)
    
    
    print "Dumping...["+str(TEST_SET.index(t)+1)+"/"+str(len(TEST_SET))+"]"
    pickle.dump(exp_value_lis, open("../rawresults/UpdatePrecs/exp_value_lis_"+'_'+t,"w"))
    pickle.dump(steady_value_lis, open("../rawresults/UpdatePrecs/steady_value_lis"+'_'+t,"w"))
    pickle.dump(steady_chg_rate_lis, open("../rawresults/UpdatePrecs/steady_chg_rate_lis_"+'_'+t,"w"))
    pickle.dump(steady_snd_rate_lis, open("../rawresults/UpdatePrecs/steady_snd_rate_lis_"+'_'+t,"w"))
    pickle.dump(time_consumed_lis, open("../rawresults/UpdatePrecs/time_consumed_lis"+'_'+t,"w"))
pickle.dump(TEST_SET, open("../rawresults/UpdatePrecs/TEST_SET","w"))
pickle.dump(TEST_RANGE, open("../rawresults/UpdatePrecs/TEST_RANGE","w"))
print "FINISHED!"