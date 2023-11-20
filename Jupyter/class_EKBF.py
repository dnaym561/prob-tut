import numpy as np
from scipy.integrate import ode

class class_EKBF: #�g��Kalman-Bucy�t�B���^(Extended Kalman-Bucy filter)

    def __init__(s, xdim, ydim, D, Q, R, x0, cov0=None, t0=0.0):
        
        s.xdim = xdim #��ԃx�N�g���̎���
        s.ydim = ydim #�o�̓x�N�g���̎���

        ### �V�X�e���s��
        ### ��ԍs�� s.A �͐��莞�ɑ�������
        ### �ϑ��s�� s.C �͐��莞�ɑ�������
        s.D = np.array(D) #�쓮�s��
        # �G��
        s.Q = np.array(Q) #�V�X�e���G���̋����U
        s.R = np.array(R) #�ϑ��G���̋����U
        
        ### �����U�s��̃x�N�g�����̎���
        s.covdim = s.xdim**2 #�{���͎O�p���������ł悢���蔲��

        ### �t�B���^�̏����l
        s.t    = t0           #��������
        s.xf   = np.array(x0) #�h�g����l
        s.K    = None         #�J���}���Q�C��
        #�����U�s��Ƃ��̏����l
        if cov0 is not None:
            s.cov = np.array(cov0)
        else:
            s.cov = np.zeros((s.xdim,s.xdim))

        #���Ғl�Ƌ����U�s���1��ɕ��ׂ���ԃx�N�g��
        X0 = s.xcov2vec(s.xf, s.cov)

        ### ������������̃\���o�[
        s.solver = ode(s.ode_func).set_integrator('dopri5')
        s.solver.set_initial_value( X0, t0 )

    def vec2xcov(self, vec):
        x   = vec[:self.xdim]
        cov = vec[self.xdim:].reshape(self.xdim,self.xdim)
        return (x,cov)

    def xcov2vec(self, x, cov):
        vec   = np.zeros(self.xdim + self.covdim)
        vec[:self.xdim] = x
        vec[self.xdim:] = np.ravel(cov)
        return vec
    
    ### KBF���X�V��������������
    def ode_func(s, t, X, y):

        x,cov = s.vec2xcov(X) #���Ғl�Ƌ����U�s��̐؂蕪��

        C = s.C_jac(x,t)                               #�g��C_jac
        s.C = C
        
        # �J���}���Q�C��
        K = cov.dot(C.T).dot(np.linalg.pinv(s.R))
        s.K = K
        
        # ���Ғl�̏����������
        dx = s.A_func(x, t) + s.K.dot(y - s.C_func(x, t)) #�g��A_func, C_func

        # �����U�̏����������
        A = s.A_jac(x,t)                               #�g��A_jac
        s.A = A

        dcov = A.dot(cov) + cov.dot(A.T) \
              + s.D.dot(s.Q).dot(s.D.T) - s.K.dot(C).dot(cov)
        
        dX = s.xcov2vec(dx,dcov) #�x�N�g����
        
        return dX

    def filtering(s, y, dt, t=None ): 

        s.solver.set_f_params( y )

        if t is not None:
            s.solver.set_initial_value( s.solver.y, t )

        s.solver.integrate(s.solver.t + dt)

        s.xf, s.cov = s.vec2xcov(s.solver.y) 
        s.t = s.solver.t

    def stability(s): #�Q�l���x�����ꉞ�c���Ă���
        stability_matrix = s.A - np.dot(s.K, s.C)
        val,vec = np.linalg.eig( stability_matrix )
        realval = np.real(val)
        if realval.max() < 0:
            print( 'This filter is stable' )
        else:
            print( 'This filter is unstable' )
        print( '> Eigenvalues:' )
        for v in val:
            print( '> ' + str(v) )
