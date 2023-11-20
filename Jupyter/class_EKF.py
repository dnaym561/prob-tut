import numpy as np
from scipy.linalg import solve_discrete_are

class class_EKF: #�g���J���}���t�B���^(Extended Kalman filter)
    
    def __init__(s, xdim, ydim, G, Q, R, x0, cov0=None):
        
        s.xdim = xdim #��ԃx�N�g���̎���
        s.ydim = ydim #�o�̓x�N�g���̎���
        
        ### �V�X�e���s��
        ### ��Ԑ��ڍs�� s.F �͐��莞�ɑ�������
        ### �ϑ��s�� s.H �͐��莞�ɑ�������
        s.G = np.array(G) #�쓮�s��
        # �G��
        s.Q = np.array(Q) #�V�X�e���G���̋����U�s��
        s.R = np.array(R) #�ϑ��G���̋����U�s��
        
        ### �t�B���^�̏����l
        s.xf = np.array(x0) #�h�g����l
        s.xp = np.array(x0) #�\������l
        s.K  = None         #�J���}���Q�C��
        #�����U�s��Ƃ��̏����l
        if cov0 is not None:
            s.cov    = np.array(cov0)
        else:
            s.cov    = np.zeros((s.xdim,s.xdim))
            
    def recursion(s, yt, xp, cov, t): #yt:�ϑ���, xp=x_t/t-1, cov=S_t/t-1
        
        H = s.H_jac(xp,t)                      #�g�� H_jac
        s.H = H
        
        HSH_R = H.dot(cov).dot(H.T)+s.R
        if HSH_R.ndim > 1:
            pinv = np.linalg.pinv(HSH_R)
        else:
            pinv = 1.0/HSH_R

        # �J���}���Q�C��
        K = cov.dot(H.T).dot(pinv)
        s.K = K

        # �h�g����: xf ... x_t/t
        xf = xp + K.dot( yt - s.H_func(xp,t) ) #�g�� H_func 

        # Prediction: xp ... x_t+1/t
        xp = s.F_func(xf,t)                    #�g�� F_func
        
        # Prediction: Sp ... S_t+1/t
        F = s.F_jac(xf,t)                      #�g�� F_jac
        s.F = F
        
        cov = F.dot(cov).dot(F.T) + s.G.dot(s.Q).dot(s.G.T) \
                - F.dot(K).dot(H).dot(cov).dot(s.F.T)
        
        return (xf, xp, cov)
    
    def filtering(s, y, t=0):
        
        s.xf, s.xp, s.cov = s.recursion(y, s.xp, s.cov, t)

    def stability(s):

        stability_matrix = s.F - s.F.dot(s.K).dot(s.H)
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
