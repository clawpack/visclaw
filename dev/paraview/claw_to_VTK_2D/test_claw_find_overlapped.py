from clawpack.pyclaw import Solution
import numpy as np
import matplotlib.pyplot as plt
from claw_find_overlapped import *
import pdb

# In[3]:

frame = 0 #decide reading data at which time
sol = Solution(frame,path='../acoustics_2d_radial/_output/',file_format='ascii')
print "number of states in this Solution object:", len(sol.states)
print "number of patches in Domain object:", len(sol.domain.patches)


# In[4]:

levels = [state.patch.level-1 for state in sol.states]
print levels, len(levels)
print type(levels[0])
level_count = {}
for i in levels:
    if i in level_count.keys():
        level_count[i] = level_count[i] + 1
    else:
        level_count[i] = 1
print level_count.items()
sorted_list = [item[1] for item in sorted(level_count.items(), key = lambda a: a[0])]
print sorted_list


# In[5]:

print sol.states[0].q.shape


# In[6]:


set_overlapped_status(sol)


# In[7]:

print sol.states[0].q.shape


# In[ ]:



