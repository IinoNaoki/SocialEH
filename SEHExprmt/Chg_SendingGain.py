'''
Created on 22 Apr, 2015

@author: yzhang28
'''
import pickle
from experiment import Experiment
from parameters import Parameters
import myopic
from util import Util
import numpy as np

import sys
sys.path.append("..")

##################################################################
s_nothing, s_charger, s_messenger = [0], [1,2,3,4,5,6], [7,8,9,10,11,12]

charging_price = [-0.00, -1.00, -4.0, -9.0, -16.0, -25.0]
sending_prob = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
sending_gain = None #15.0

csize = len(s_nothing) + len(s_charger) + len(s_messenger)
esize = 10
qsize = 10

inj_prob, charge_prob = 0.4, 0.9

discount = 0.9
################################################################## 


TEST_SET = ['MDP', 'CAS', 'GREEDY', 'RANDOM', 'THRESHOLDRANDOM']
TEST_RANGE = [1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0]

for j,t in enumerate(TEST_SET):        
    # to store results
    exp_value_lis, steady_value_lis, steady_chg_rate_lis, steady_snd_rate_lis = [], [], [], []
    
    vi = [None for _ in range(len(TEST_SET))]
    for _sending_gain in TEST_RANGE:
        para = Parameters(s_nothing, s_charger, s_messenger, \
                          charging_price, sending_prob, _sending_gain,\
                          csize, esize, qsize, \
                          inj_prob, charge_prob, discount)
        expt = Experiment(para)
        util = Util(para)
        
        R, P, vi[j] = expt.Build_Problem(t)
        vi[j].run()
        
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
    
    if j==0:
        f = open("./Chg_SendingGain_result.txt","w")
    else:
        f = open("./Chg_SendingGain_result.txt","a")
    f.write(" -- "+ t +" --\n")
    f.write(" > Expd_Val:  ")
    for item in exp_value_lis:
        f.write(str(item))
        f.write("   ")
    f.write("\n")
    f.write(" > Steady_Val:  ")
    for item in steady_value_lis:
        f.write(str(item))
        f.write("   ")
    f.write("\n")
    f.write(" > Chg_Rate:  ")
    for item in steady_chg_rate_lis:
        f.write(str(item))
        f.write("   ")
    f.write("\n")
    f.write(" > Send_Rate:  ")
    for item in steady_snd_rate_lis:
        f.write(str(item))
        f.write("   ")
    f.write("\n\n")
    f.close()
    
    print "Dumping...["+str(TEST_SET.index(t)+1)+"/"+str(len(TEST_SET))+"]"
    pickle.dump(exp_value_lis, open("../rawresults/SendingGain/exp_value_lis_"+'_'+t,"w"))
    pickle.dump(steady_value_lis, open("../rawresults/SendingGain/steady_value_lis"+'_'+t,"w"))
    pickle.dump(steady_chg_rate_lis, open("../rawresults/SendingGain/steady_chg_rate_lis_"+'_'+t,"w"))
    pickle.dump(steady_snd_rate_lis, open("../rawresults/SendingGain/steady_snd_rate_lis_"+'_'+t,"w"))
pickle.dump(TEST_SET, open("../rawresults/SendingGain/TEST_SET","w"))
pickle.dump(TEST_RANGE, open("../rawresults/SendingGain/TEST_RANGE","w"))
print "FINISHED!"