import numpy as np
from scipy.integrate import ode
from scipy.linalg import solve_continuous_are

class class_ssKBF: # Steady-state Kalman-Bucy filter

    def __init__(s, A, D, C, Q, R, x0, cov0=None, CL=None, t0=0.0):
        
        ### �V�X�e���s��
        s.A = np.array(A) #��ԍs��
        s.D = np.array(D) #�쓮�s��
        s.C = np.array(C) #�ϑ��s��
        # �G��
        s.Q = np.array(Q) #�V�X�e���G���̋����U
        s.R = np.array(R) #�ϑ��G���̋����U
        
        ### �V�X�e���̃T�C�Y
        s.xdim   = A.shape[1]   #��Ԃ̎�����A�̗�
        s.ydim   = C.shape[0]   #�ϑ��̎�����C�̍s��
        s.covdim = s.xdim**2 #�{���͎O�p���������ł悢���蔲��

        ### LQG����p�̕��[�v�s��(�f�t�H���g��A)
        if CL is None:
            s.CL = s.A
        else:
            s.CL = CL.copy()
        
        ### KBF�̏����l
        s.t    = 0.0
        s.xf   = np.array(x0) #�h�g����l
        s.cov0 = cov0         #�����U�s��
        s.K    = None         #�J���}���Q�C��

        ### ���J���}���t�B���^�̓��o
        RicA = s.A.T
        RicB = s.C.T
        RicQ = s.D.dot(s.Q).dot(s.D.T)
        RicR = s.R
        #���J�b�`�������̉�
        s.cov = solve_continuous_are(RicA, RicB, RicQ, RicR) 
        X0    = s.xf
        #���J���}���Q�C��
        s.K   = s.cov.dot(s.C.T).dot(np.linalg.pinv(s.R)) 
        print('Steady-state Kalman gain =\n', s.K)

        ### ������������̃\���o�[
        s.solver = ode(s.KBF_ode).set_integrator('dopri5')
        s.solver.set_initial_value( X0, t0 )

    ### KBF���X�V��������������(���J���}���t�B���^�̏ꍇ)
    def KBF_ode(s, t, x, y):
        
        dx = s.CL.dot(x) + s.K.dot(y - s.C.dot(x))
        
        return dx

    ### �t�B���^�����O
    def filtering(s, y, dt):
        s.solver.set_f_params( y )
        s.solver.integrate(s.solver.t + dt)

        s.xf = s.solver.y #solver.y �� s.xf
        s.t = s.solver.t

    ### ���蔻��
    def stability(s):
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
