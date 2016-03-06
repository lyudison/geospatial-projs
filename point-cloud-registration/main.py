from pylab import *
from scipy import spatial
from sys import stdout

def calRotationMat(qr):
    q0 = qr[0]
    q1 = qr[1]
    q2 = qr[2]
    q3 = qr[3]
    return asarray([
        [q0**2+q1**2-q2**2-q3**2, 2*(q1*q2-q0*q3), 2*(q1*q3+q0*q2)],
        [2*(q1*q2+q0*q3), q0**2+q2**2-q1**2-q3**2, 2*(q2*q3-q0*q1)],
        [2*(q1*q3-q0*q2), 2*(q2*q3+q0*q1), q0**2+q3**2-q1**2-q2**2]
        ])

def calRegistration(P0, Yk):
    # here uy (miu y) correspond to ux in the paper
    up = divide(sum(P0, 0), len(P0))
    uy = divide(sum(Yk, 0), len(Yk))
    # below matrix and vector are column-vector form
    Epy = divide(P0.T.dot(Yk) - up.T.dot(uy), len(P0))
    tr = trace(Epy)
    A = subtract(Epy, Epy.T)
    B = subtract(add(Epy, Epy.T), multiply(identity(3), tr))
    QEpy = asarray([
        [tr,        A[1][2],       A[2][0],      A[0][1]], 
        [A[1][2],   B[0][0],             0,            0],
        [A[2][0],         0,       B[1][1],            0],
        [A[0][1],         0,             0,      B[2][2]]])
    # above matrix and vector are column-vector form
    w, v = eig(QEpy)
    qr = v[:, argmin(w)]
    qt = subtract(uy.T, calRotationMat(qr).dot(up.T)).T # change to row-vector form
    return (qr, qt)

def applyRegistration(qk, P0):
    qr = qk[0]
    qt = qk[1]
    return add(P0.dot(calRotationMat(qr).T), qt)

def calMeanSquareError(Yk, Pk):
    # Pk is actually Pk+1
    return divide(sum(square(subtract(Yk, Pk))), len(Pk))

def ICP(P0, X):
    k = 10 # max iteration
    threshold = 5*10**-2 # converge threshold
    Pk = P0
    dk = 10 # init change of error
    qk = None # quaternion vector (can be converted into transformation matrix)
    kdTree = spatial.KDTree(X) # use k-d tree to find closest point
    for i in xrange(k):
        print '---- iteration %dth ----' % (i+1)
        Yk = []
        for i in xrange(len(Pk)):
            Yk.append(X[kdTree.query(Pk[i])[1]])
            if i % int(len(Pk)/100) == 0:
                stdout.write('\rcalculating closest point set... %d%%' % (i / int(len(Pk)/100)))
                stdout.flush()
        stdout.write('\n')
        Yk = asarray(Yk)
        # calculate the transformation (registration)
        print 'calculating registration (transformation)...'
        qk = calRegistration(P0, Yk)
        # calculate the next point set
        print 'applying registration...'
        Pk = applyRegistration(qk, P0)
        print 'calculating mean square error...'
        dkNext = calMeanSquareError(Yk, Pk)
        print 'change of error: d = %f' % abs(dkNext - dk)
        if abs(dkNext - dk) < threshold:
            break
        dk = dkNext
    # use qk to get transformation matrices R and T
    # notice that R and T are now in column-vector form
    return asarray(calRotationMat(qk[0])), asarray(qk[1]).reshape((3,1))

# ---- MAIN ---- 
# read the point set
print 'loading measured point cloud set...'
fin = open('pointcloud1.fuse')
lines = fin.readlines()
P = asarray([map(float, line.split(' ')[:-1]) for line in lines])
fin.close()

# read the model shape
print 'loading model shape point cloud set...'
fin = open('pointcloud2.fuse')
lines = fin.readlines()
X = asarray([map(float, line.split(' ')[:-1]) for line in lines])
fin.close()

# use ICP (Iterative Closest Points) algorithm to find the transformation matrices R (rotation) and vector T (translation)
print 'calculating transformation using ICP...'
R, T = ICP(P, X)

# now you can use R*P+T to transform the point set
print 'Rotation Matrix `R` = '
print R
print 'Translation Vector `T` = '
print T
