import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
from sklearn.preprocessing import Normalizer, MinMaxScaler
import os 
#os.chdir('C:/DATA/Kaige_Research/Code/optimal_bandit/code/')
from linucb import LINUCB
from eliminator import ELI
from lse import LSE 
from lse_soft import LSE_soft
from lse_soft_v import LSE_soft_v
from linucb_soft import LinUCB_soft
from utils import *
path='../results/'
# np.random.seed(2018)

user_num=1
item_num=10
dimension=5
phase_num=13
iteration=2**phase_num
sigma=0.01# noise
delta=0.1# high probability
alpha=0.1 # regularizer
loop=10


lse_regret_matrix=np.zeros((loop, iteration))
for l in range(loop):
	item_features=Normalizer().fit_transform(np.random.normal(size=(item_num, dimension)))
	user_feature=np.random.normal(size=dimension)
	user_feature=user_feature/np.linalg.norm(user_feature)
	true_payoffs=np.dot(item_features, user_feature)
	best_arm=np.argmax(true_payoffs)
	worst_arm=np.argmin(true_payoffs)
	gaps=np.max(true_payoffs)-true_payoffs

	lse_model=LSE(dimension, iteration, item_num, user_feature, item_features, true_payoffs, alpha, delta, sigma)

	lse_regret, lse_error, lse_upper_matrix, lse_low_matrix, lse_payoff_error_matrix, lse_worst_payoff_error, lse_nosie_norm, lse_noise_norm_phase, lse_error_bound, lse_error_bound_phase, lse_threshold, lse_est_beta, lse_left_item_num, lse_est_beta2=lse_model.run()

	lse_regret_matrix[l]=lse_regret


lse_mean=np.mean(lse_regret_matrix, axis=0)
lse_std=lse_regret_matrix.std(0)

np.save(path+'lse_regret_mean_item_num_%s_phase_num_%s'%(item_num, phase_num),lse_mean)
np.save(path+'lse_regret_std_item_num_%s_phase_num_%s'%(item_num, phase_num),lse_std)

x=range(iteration)
color_list=matplotlib.cm.get_cmap(name='tab10', lut=None).colors

plt.figure(figsize=(5,5))
plt.plot(x, lse_mean, '-o', color='orange', markevery=0.1, linewidth=2, markersize=8, label='LSE')
plt.fill_between(x, lse_mean-lse_std*0.95,lse_mean+lse_std*0.95, color='orange', alpha=0.2)
plt.legend(loc=2, fontsize=12)
plt.xlabel('Time', fontsize=12)
plt.ylabel('Cumulative Regret', fontsize=12)
plt.tight_layout()
plt.savefig(path+'regret_shadow_lse'+'.png', dpi=300)
plt.show()



plt.figure(figsize=(5,5))
for i in range(item_num):
	if i==best_arm:
		plt.plot(x, lse_upper_matrix[i], '-', color='m', markevery=0.1, linewidth=2, markersize=5, label='Best Arm')
		plt.plot(x, lse_low_matrix[i], '-.', color='m', markevery=0.1, linewidth=2, markersize=5)
	else:
		plt.plot(x, lse_upper_matrix[i], '-', color=color_list[i], markevery=0.1, linewidth=2, markersize=5)
		# plt.plot(x, eli_low_matrix[i], '-.', color=color_list[i], markevery=0.1, linewidth=2, markersize=5)
plt.legend(loc=4, fontsize=10)
plt.ylim([-2,3])
plt.xlabel('Time', fontsize=12)
plt.ylabel('Estimated Reward Interval', fontsize=12)
plt.tight_layout()
plt.savefig(path+'lse_payoff_interval'+'.png', dpi=300)
plt.show()
