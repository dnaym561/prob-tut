import numpy as np
from scipy.integrate import ode

class class_EnKF: #�A���T���u���J���}���t�B���^(Ensemble Kalman filter)

    def __init__(self, xdim, ydim, Q, R, pn):

        ### �V�X�e���̃T�C�Y
        self.xdim = xdim #��Ԃ̎���
        self.ydim = ydim #�ϑ��̎���
        self.pn   = pn   #�A���T���u���̗��q��

        ### �G��
        self.Q    = np.array(Q)         #�V�X�e���G���̋����U
        self.wdim = self.Q.shape[0]     #�V�X�e���G���̎���
        self.w    = np.zeros(self.wdim) #�V�X�e���G���x�N�g��
        self.wav  = np.zeros(self.wdim) #�V�X�e���G���̕��� = 0

        self.R    = np.array(R)         #�ϑ��G���̋����U
        self.vdim = self.R.shape[0]     #�ϑ��G���̎���
        self.v    = np.zeros(self.vdim) #�ϑ��G���x�N�g��
        self.vav  = np.zeros(self.vdim) #�ϑ��G���̕��� = 0
        
        ### �A���T���u���s��
        self.Xp = np.zeros((self.xdim, self.pn))  #�\������A���T���u��
        self.Xf = np.zeros_like(self.Xp)          #�h�g�A���T���u��
        self.Yp = np.zeros((self.ydim, self.pn))  #�\���o�̓A���T���u��
        self.ones = np.ones((self.pn,1))
        
        self.bias = self.pn - 1
        self.yones = np.ones((self.ydim, self.pn))
    
    ### ���N���X�p�̏������֐�
    def system_definition(s, F_func, H_func, x0, P0, t0=0):

        s.F_func = F_func
        s.H_func = H_func
        
        s.init_ensemble(x0, P0) #�A���T���u���̏�����
        s.xf = np.mean(s.Xp, axis=1) #�h�g����l�̎b�菉���l

    def state_eqn(s, x): #��ԕ������̉E��
        s.update_w()
        return s.F_func(x, s.t) #s.t �� filtering(yt,t) �ōX�V���ꂽ�l
        
    def output_eqn(s, x): #�ϑ��������̉E��
        s.update_v()
        return s.H_func(x) + s.v
        
    def update_w(s): #�V�X�e���G���̍X�V
        if s.wdim == 1:
            s.w = np.sqrt(s.Q[0]) * np.random.randn() #���K����
        else:
            s.w = np.random.multivariate_normal(s.wav, s.Q)

    def update_v(s): #�ϑ��G��
        if s.vdim == 1:
            s.v = np.sqrt(s.R[0])*(np.random.randn()) #���K����
        else:
            s.v = np.random.multivariate_normal(s.vav, s.R)
        
    ### �A���T���u���̏������ƍX�V
    def init_ensemble(s, x0, P0):
        s.Xp = np.random.multivariate_normal(x0, P0, s.pn).T #(xdim)x(pn)�K�E�X�s��  
        
    def update_Yp(s): #�\���o�̓A���T���u���̍X�V
        s.Yp = np.apply_along_axis(s.output_eqn, 0, s.Xp)
        
    def update_Xp(s): #�\������A���T���u���̍X�V
        s.Xp = np.apply_along_axis(s.state_eqn, 0, s.Xp)
        
    ### �h�g����
    def filtering(s, yt, t, skip_prediction = False):
        
        ### �t�B���^���̎����̍X�V
        s.t = t
        
        ### �\���o�̓A���T���u���̌v�Z
        s.update_Yp()

        ### �J���}���Q�C���̌v�Z
        s.meanXp = np.mean(s.Xp, axis=1).reshape(-1,1)
        s.meanYp = np.mean(s.Yp, axis=1).reshape(-1,1)
        s.covXY = s.bias*( np.dot(s.Xp, s.Yp.T)/s.pn - np.dot(s.meanXp, s.meanYp.T) )
        s.covYY = s.bias*( np.dot(s.Yp, s.Yp.T)/s.pn - np.dot(s.meanYp, s.meanYp.T) )
        s.K = np.dot(s.covXY, np.linalg.pinv(s.covYY))

        ### �h�g�A���T���u�����h�g����l�̌v�Z
        yt_matrix = np.dot(np.diag(yt), s.yones)
        s.Xf = s.Xp + np.dot(s.K, (yt_matrix - s.Yp)) #�h�g�A���T���u��
        s.xf = np.mean(s.Xf, axis=1) #�h�g����l
    
        if skip_prediction is not True:
            s.prediction() #�\������

    ### �\������
    def prediction(s):
        s.Xp = s.Xf #�h�g����l��\���̏����l��
        s.update_Xp()
