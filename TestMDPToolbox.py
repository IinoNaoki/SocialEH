import mdptoolbox
import numpy as np

# S = (C,Q)

A = [[1,2],
     [3,4]]

B = A
C = A

AkB = np.kron(A,B)
print AkB

AkBkC = np.kron(AkB,C)
print AkBkC