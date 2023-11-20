import numpy as np
import matplotlib.pyplot as plt

### �f�t�H���g�l
default_values = ( #Q, R, C, D, x0, dt, tn, p_list
    np.diag([0.0001,0.0001]), #Q:  �V�X�e���G���̋����U
    np.array([[0.0001]]),     #R:  �ϑ��G���̋����U
    np.array([[1, 0]]),       #C:  �ψʂ̂�
    np.eye(2),                #D:  �쓮�s��
    np.array([0.0, 0.0]),     #x0: �����l
    0.02,                     #dt: ���ԃX�e�b�v
    2000,                     #tn: ���n��
    [1, 0.2, 1],              #p_list: k, c, a
)

### �O����U
def Forcing(t):
    return np.sin(1.5*t)

### �g��n�̓��o
def get_extended_system(x0, Q, D, C, A=None, Qval=1.2):
        
    ex0 = np.append(x0, [0.0])
    # �g��n
    if A is not None:
        eA = np.pad(A, (0,1), 'constant') #A��1�s1��g�債��0�Ŗ��߂�
        eA[-2,-1] = 1 #�K�v�ӏ���1��������
    else:
        eA = None
    # ����p�����[�^�ɂ��V�X�e���G��������i�����Ɛ���p�����[�^�������Ȃ��Ȃ�j
    eD = np.pad(D, (0,1), 'constant')
    eD[-1,-1] = 1
    # ����p�����[�^�͊ϑ��ł��Ȃ��Ƃ���
    eC = np.pad(C, (0,1), 'constant')
    eC = np.delete(eC, axis=0, obj=-1)
    # ����p�����[�^�p�̃V�X�e���G�����x��ǉ�
    eQ = np.pad(Q, (0,1), 'constant')
    eQ[-1,-1] = Qval    #���܂菬�����Ǝ������x�����C�傫�����Ă����ʂȂ��D

    print('Extended x0 =\n',ex0)
    print('Extended A =\n',eA)
    print('Extended D =\n',eD)
    print('Extended C =\n',eC)
    print('Extended Q =\n',eQ)
        
    if A is not None:
        return (ex0, eQ, eD, eC, eA)
    else:
        return (ex0, eQ, eD, eC)


### �T���v���f�[�^�̎擾
from class_SDE import * #���s�t�H���_��class_SDE.py��u���ăC���|�[�g���܂��D

class model_1dof_tv(class_SDE): #class_SDE�̎q�N���X, 1���R�x�U���n�C���σp�����[�^

    def __init__(s, p_idx, p1, p2, t1=None):
        
        Q, R, C, D, x0, dt, tn, p_list = default_values
        s.C = C
        s.D = D
        s.tn = tn
        s.p_list = p_list.copy()
        
        xdim = 2               #��Ԃ̎���
        ydim = s.C.shape[0] #�ϑ��̎�����C�̍s��
        t0 = 0.0
        
        super().__init__(xdim, ydim, Q, R)
        s.setup(x0, dt, t0)

        # ����t1�ŕω�����p�����[�^
        s.p_idx  = p_idx   
        s.p1 = p1
        s.p2 = p2
        if t1 is None:
            s.t1=(s.tn*s.dt)/2
        else:
            s.t1 = t1
        
    ### ��ԕ������̒�`(�K�{)
    def StateEqn(s, t, x):
        
        if t<s.t1:
            s.p_list[s.p_idx] = s.p1
        else:
            s.p_list[s.p_idx] = s.p2
               
        k, c, a = s.p_list
        Dw = np.ravel(s.D.dot(s.w))
        
        s.dx[0] = x[1] + Dw[0]
        s.dx[1] = - k*x[0] - c*x[1] + a*Forcing(t) + Dw[1]
        
        return s.dx
    
    ### �ϑ��������̒�`(�K�{)
    def OutputEqn(s, x):
        return s.C.dot(x)
    
    ### �T���v���f�[�^�̎擾
    def get_sample_path(s): 
        s.tt, s.xx, s.yy = super().get_sample_path(s.tn)
        s.param = np.zeros_like(s.tt)
        for i, t in enumerate(s.tt):
            if t<s.t1:
                s.param[i] = s.p1
            else:
                s.param[i] = s.p2

### �v���b�g
def plot(cls, param_label='Parameter'):

    fig, ax = plt.subplots(3, 1, figsize=(4,4))

    lb_exa = 'Exact'
    ls_exa = ':'
    lc_exa = 'black'
    lw_exa = 1.5
    lw_est = 1.5

    ax[0].plot(cls.tt, cls.xx[:,0],  ls_exa, label=lb_exa, color=lc_exa, linewidth=lw_exa )
    ax[0].plot(cls.tt, cls.xxf[:,0], '-', label='Estimated', color='black',   linewidth=lw_est )
    ax[0].set_ylabel('$x_1$', fontsize=12)
    ax[0].legend(bbox_to_anchor=(1.0, 0.85), loc='lower right', ncol=2)

    ax[1].plot(cls.tt, cls.xx[:,1], ls_exa, label=None, color=lc_exa,  linewidth=lw_exa )
    ax[1].plot(cls.tt, cls.xxf[:,1],   '-', label=None, color='black', linewidth=lw_est )
    ax[1].set_ylabel('$x_2$', fontsize=12)

    for i in range(2):
        plt.setp(ax[i].get_xticklabels(),visible=False)
        ax[i].grid(); 

    ax[2].plot(cls.tt, cls.param, ls_exa, label=lb_exa,  color=lc_exa,  linewidth=lw_exa )
    ax[2].plot(cls.tt, cls.xxf[:,2], '-', label='Estimated', color='black', linewidth=lw_est )
    ax[2].set_ylabel(param_label, fontsize=12)
    ax[2].set_xlabel('$t$', fontsize=12)
    ax[2].grid(); 
        
    plt.tight_layout()

def save(filename):
    plt.savefig(filename, bbox_inches="tight")
