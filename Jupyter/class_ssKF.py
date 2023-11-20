import numpy as np
from scipy.linalg import solve_discrete_are

class class_ssKF: # Steady-state Kalman filter
    
    def __init__(s, F, G, H, Q, R, x0, cov0=None):
        
        ### �V�X�e���s��
        s.F = np.array(F) #��Ԑ��ڍs��
        s.G = np.array(G) #�쓮�s��
        s.H = np.array(H) #�ϑ��s��
        # �G��
        s.Q = np.array(Q) #�V�X�e���G���̋����U�s��
        s.R = np.array(R) #�ϑ��G���̋����U�s��
        
        s.xdim = F.shape[1] #��ԃx�N�g���̎�������Ԑ��ڍs��̗�
        s.ydim = H.shape[0] #�ϑ��s��̍s��
        
        ### KBF�̓������
        s.xf   = np.array(x0) #�h�g����l
        s.xp   = np.array(x0) #�\������l
        s.cov0 = cov0         #�����U�s��
        s.K    = None         #�J���}���Q�C��

        ### ���J���}���t�B���^�̓��o
        RicA = s.F.T
        RicB = s.H.T
        RicQ = s.G.dot(s.Q).dot(s.G.T)
        RicR = s.R
        #���J�b�`�������̉�
        s.cov = solve_discrete_are(RicA, RicB, RicQ, RicR) 
        #���J���}���Q�C��
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
    
    ### �t�B���^�����O
    def filtering(s, y):

        s.xf, s.xp = s.recursion(y, s.xp)

    ### ���蔻��
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
