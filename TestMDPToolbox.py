import mdptoolbox
import numpy as np

a = [0,1,3,4]
b = np.transpose([0,1,3,4])

print a.dot(b)


# f = [q,w,e]
# 
# (0,0) (0,1) (0,2) (0,3) | (1,0) (1,1) (1,2) (1,3) | (2,0) (2,1) (2,2) (2,3) | (3,0) (3,1) (3,2) (3,3) | (4,0) (4,1) (4,2) (4,3)
#   0    1     2     3        4    5     6     7        8     9     10    11      12    13    14    15      16    17    18    19
# 
# 
# 
# A*(len(b)-1) + B
# 
# 
# F = [0,1,2] lenF=3
# A = [0,1] lenA 2
# B = [0,1] lenB 2
# 
# (0,0,0) (0,0,1) | (0,1,0) (0,1,1) || (1,0,0) (1,0,1) | (1,1,0) (1,1,1) || (2,0,0) (2,0,1) | (2,1,0) (2,1,1)
#    0      1          2       3          4       5         6       7          8       9         10      11 
#    
# 0*lenA*lenB + 0*lenB + 0
# 0 +   0 + 1
# 0 + 1*2 + 0
# 0 + 1*2 + 1
# 
# F*(len(a)-1)*(len(b)-1) + A*(len(b)-1) + B-1
# 
# 0,1,1
# 
# 2,1,0
# 
# 2*2*2 + 1*2 + 0