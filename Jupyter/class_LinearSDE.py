import numpy as np
from scipy.integrate import ode
from class_SDE import * #���s�t�H���_��SDE.py��u���ăC���|�[�g���܂��D

class class_LinearSDE(class_SDE): #SDE�̎q�N���X

    def __init__(self, A, D, C, Q, R, x0, dt, t0=0.0, B=None):

        ### �V�X�e���s��
        self.A = np.array(A) #��ԍs��
        self.D = np.array(D) #�쓮�s��
        self.C = np.array(C) #�ϑ��s��
        # �V�X�e���̃T�C�Y
        xdim = A.shape[1] #��Ԃ̎�����A�̗�
        ydim = C.shape[0] #�ϑ��̎�����C�̍s��
        wdim = D.shape[1] #�V�X�e���G���̎�����D�̗�

        super().__init__(xdim, ydim, Q, R)

        ### �������
        if B is not None:
            self.B = np.array(B)
            self.udim = self.B.shape[1] #������͂̎���
            self.u = np.zeros(self.udim)
        else:
            self.udim = 0
                     
        ### �����ݒ�
        self.setup(x0, dt, t0)

    ### �m������������(SDE: stochastic differential equation)
    def StateEqn(s, t, x):
        Dww = np.ravel(s.D.dot(s.w)) #ode�̃x�N�g����1�����z��

        dx0 = s.A.dot(x) + Dww
        
        if s.udim==0:
            dx = dx0
        else:
            Bu = np.ravel(s.B.dot(s.u)) #ode�̃x�N�g����1�����z��
            dx = dx0 + Bu

        return dx

    def OutputEqn(s, x):
        return s.C.dot(x)
