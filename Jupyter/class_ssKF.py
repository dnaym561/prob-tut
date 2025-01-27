import numpy as np
from scipy.linalg import solve_discrete_are

class class_ssKF: # Steady-state Kalman filter
    
    def __init__(s, F, G, H, Q, R, x0, cov0=None):
        
        ### VXesń
        s.F = np.array(F) #óÔÚsń
        s.G = np.array(G) #ěŽsń
        s.H = np.array(H) #ĎŞsń
        # Gš
        s.Q = np.array(Q) #VXeGšĚ¤ŞUsń
        s.R = np.array(R) #ĎŞGšĚ¤ŞUsń
        
        s.xdim = F.shape[1] #óÔxNgĚłóÔÚsńĚń
        s.ydim = H.shape[0] #ĎŞsńĚs
        
        ### KBFĚŕóÔ
        s.xf   = np.array(x0) #ŕhgčl
        s.xp   = np.array(x0) #\Şčl
        s.cov0 = cov0         #¤ŞUsń
        s.K    = None         #J}QC

        ### číJ}tB^Ěąo
        RicA = s.F.T
        RicB = s.H.T
        RicQ = s.G.dot(s.Q).dot(s.G.T)
        RicR = s.R
        #Jb`űöŽĚđ
        s.cov = solve_discrete_are(RicA, RicB, RicQ, RicR) 
        #číJ}QC
        HSH_R = s.H.dot(s.cov).dot(s.H.T)+s.R
        if HSH_R.ndim > 1:
            pinv = np.linalg.pinv(HSH_R)
        else:
            pinv = 1.0/HSH_R
        s.K   = s.cov.dot(s.H.T).dot(pinv) 
        print('Steady-state Kalman gain =\n', s.K)

    def recursion(s, yt, xp):

        # Filtering: xf ... x_t/t
        xf = xp + s.K.dot( yt - s.H.dot(xp) )   

        # Prediction: xp ... x_t+1/t
        xp = s.F.dot(xf)

        return (xf, xp)
    
    ### tB^O
    def filtering(s, y):

        s.xf, s.xp = s.recursion(y, s.xp)

    ### ŔčťĘ
    def stability(s):

        stability_matrix = s.F - np.dot(s.K, s.H)
        val,vec = np.linalg.eig( stability_matrix )
        absval = np.abs(val)
        if absval.max() < 1:
            print( 'This filter is stable' )
        else:
            print( 'This filter is unstable' )
        print( '> Eigenvalues:' )
        for v in val:
            print( '> ' + str(v) )
        print( '> Their absolute values:' )
        for av in absval:
            print( '> ' + str(av) )
