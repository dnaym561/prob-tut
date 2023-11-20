import numpy as np
from scipy.integrate import ode

class class_SDE:
    # dx/dt = state_eqn(t, x)
    # y = output_eqn(x) + v

    def __init__(self, xdim, ydim, Q, R):

        ### �V�X�e���̃T�C�Y
        self.xdim = xdim #��Ԃ̎���
        self.ydim = ydim #�ϑ��̎���

        ### �G��
        self.Q    = np.array(Q)         #�V�X�e���G���̋����U
        self.wdim = self.Q.shape[0]     #�V�X�e���G���̎���
        self.w    = np.zeros(self.wdim) #�V�X�e���G���x�N�g��
        self.wav  = np.zeros(self.wdim) #�V�X�e���G���̕���
        self.R    = np.array(R)         #�ϑ��G���̋����U
        self.vdim = self.R.shape[0]     #�ϑ��G���̎���
        self.v    = np.zeros(self.vdim) #�ϑ��G���x�N�g��
        self.vav  = np.zeros(self.vdim) #�ϑ��G���̕���

    def setup(s, x0, dt, t0=0.0, solver_type='dopri5'):
        s.x0 = np.array(x0) #������ԃx�N�g��
        s.dx = np.zeros_like(s.x0) #��ԃx�N�g���̎��Ԕ���
        s.dt = dt           #�ϕ��X�e�b�v 
        s.t0 = t0           #��������
        ### �\���o�̐ݒ�
        s.solver = ode(s.StateEqn).set_integrator(solver_type)
        s.solver.set_initial_value( s.x0, s.t0 )
        ### �N���X�ϐ����\���o�Ɠ���
        s.t = s.solver.t #�N���X�ϐ�(t,x)��solver����(x,y)�ɑΉ�
        s.x = s.solver.y     #��ԃx�N�g���̏����l
        s.y = s.get_output() #�ϑ��x�N�g���̏����l

    def StateEqn(s, t, x): 
        # dx/dt = StateEqn(t, x)
        # �֐����ŃV�X�e���G�� s.w, �ꎞ�ێ��p�� s.dx ���g����D
        ### dummy ###
        s.dx = x
        return s.dx

    def OutputEqn(s, x): #dx/dt = StateEqn(t, x)
        # y = output_func(x) + v
        # �ϑ��G�� v ��get_output()�Ŏ����I�ɉ��Z����� 
        ### dummy ###
        y = x
        return y

    def get_output(s): 
        ### �G���̍X�V
        s.update_v()
        return s.OutputEqn(s.x) + s.v

    def update_w(s):
        if s.wdim == 1:
            s.w = np.sqrt(s.Q[0]) * np.random.randn() #���K����
        else:
            s.w = np.random.multivariate_normal(s.wav, s.Q)
        
    def update_v(s):
        if s.vdim == 1:
            s.v = np.sqrt(s.R[0]) * np.random.randn() #���K����
        else:
            s.v = np.random.multivariate_normal(s.vav, s.R)

    def propagator(s, x0, t0):    
        ### �G���̍X�V
        s.update_w()

        # �Z�@12.1�ɂ���D�̕␳�Ɠ������Ƃ��Cw�̕␳�ł��Ă���D
        # �����u�m���V�X�e�����_�vISBN:4-88552-028-2, 89�łȂ�
        inv_sqrt_dt = 1.0/np.sqrt(s.dt)
        s.w *= inv_sqrt_dt

        s.solver.set_initial_value( x0, t0 )
        s.solver.integrate(s.solver.t + s.dt)

        return (s.solver.y, s.solver.t) #�{�N���X��(t,x)��solver��(t,y)
        
    def solve(s):
        s.x, s.t = s.propagator(s.x, s.t)

    def set_input(s, u):
        s.u = u

    def get_sample_path(s, tn):
        tt = np.zeros(tn+1)   #�����̗�
        xx = np.zeros((tn+1, s.xdim)) #��ԃx�N�g���̎��n��
        yy = np.zeros((tn+1, s.ydim)) #�ϑ��x�N�g���̎��n��

        for i in range(tn+1):
            tt[i] = s.t
            xx[i,:] = s.x
            yy[i] = s.get_output()
            s.solve()

        return tt, xx, yy
