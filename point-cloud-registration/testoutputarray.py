from pylab import *

arr = array([[1,2,3],
             [4,5,6],
             [7,8,9]])
fout = open('output.txt', 'w')
print arr
fout.write(arr)
fout.close()
