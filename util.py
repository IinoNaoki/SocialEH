'''
Created on 16 Apr, 2015

@author: yzhang28
'''

import numpy as np

class Util(object):
    '''
    classdocs
    '''


    def __init__(self, paras):
        '''
        Constructor
        '''
        self.CON_CSIZE = paras.CON_CSIZE
        self.CON_ESIZE = paras.CON_ESIZE
        self.CON_QSIZE = paras.CON_QSIZE

    def Trans_tuple_to_index(self, lis):        
        if len(lis)!=3:
            print "error in Trans_tuple_to_index(lis)"
            exit()
            
        prod_left = np.asarray(lis)
        prod_right = np.transpose(np.array([self.CON_ESIZE * self.CON_QSIZE, \
                                            self.CON_QSIZE, \
                                            1.0]))
        return int(prod_left.dot(prod_right)) 
        
    def Action_2Dlized_Result(self, _vi, _displist, _name):
        sizelist = [self.CON_CSIZE, self.CON_ESIZE, self.CON_QSIZE]
        namelist = ['C', 'E', 'Q']
        easynamelist = ['Contact state C', 'Energy state E', 'Queue state Q']
        if not len(_displist)==2:
            print "Error in Action_2Dlized_Result()"
            exit()
        
        dim1, dim2 = _displist
        ind_dim1, ind_dim2 = namelist.index(dim1), namelist.index(dim2)
        
        for i in range(len(sizelist)):
            if i not in [ind_dim1, ind_dim2]:
                NON_DISP_STATE = sizelist[i]
                NON_DISP_INDEX = i
        
        f = open('./'+_name+'/MAT-'+str(dim1)+'-'+str(dim2),'w')
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
                    _ind = self.Trans_tuple_to_index(_tuple)
                    actlist = ['-','c','Q']
                    f.write( str(actlist[_vi.policy[_ind]])+'   ')
                f.write('\n')
            f.write('\n')
        f.write('\n')   