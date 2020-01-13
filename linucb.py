import numpy as np 
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import Normalizer, MinMaxScaler
from scipy.sparse import csgraph 
import scipy
import os 

class LINUCB():
	def __init__(self, dimension, iteration, item_num, item_feature_matrix, true_user_feature, true_payoffs, gaps, best_arm, best_payoff, alpha, delta, sigma):
		self.dimension=dimension
		self.iteration=iteration
		self.item_num=item_num
		self.item_feature_matrix=item_feature_matrix
		self.true_user_feature=true_user_feature
		self.true_payoffs=true_payoffs
		self.gaps=gaps
		self.best_arm=best_arm
		self.best_payoff=best_payoff
		self.user_feature=np.zeros(self.dimension)
		self.I=np.identity(self.dimension)
		self.alpha=alpha
		self.delta=delta
		self.sigma=sigma
		self.beta=0
		self.real_beta=0
		self.user_cov=self.alpha*np.identity(self.dimension)
		self.user_xx=0.01*np.identity(self.dimension)
		self.user_bias=np.zeros(self.dimension)
		self.beta_list=[]
		self.real_beta_list=[]
		self.item_index_selected=[]
		self.index_matrix=np.zeros((self.iteration, self.item_num))
		self.x_norm_matrix=np.zeros((self.iteration, self.item_num))
		self.mean_matrix=np.zeros((self.iteration, self.item_num))
		self.gaps_ucb=np.zeros((self.iteration, self.item_num))
		self.est_gaps_ucb=np.zeros((self.iteration, self.item_num))
		self.best_index=np.zeros((self.iteration, self.item_num))
		self.ucb_matrix=np.zeros((self.iteration, self.item_num))
		self.true_ucb_matrix=np.zeros((self.iteration, self.item_num))
		self.payoff_error_matrix=np.zeros((self.iteration, self.item_num))
		self.item_counter=np.zeros(self.item_num)
		self.ucb_list=np.zeros(self.iteration)
		self.true_ucb_list=np.zeros(self.iteration)

	def update_beta(self):
		a = np.linalg.det(self.user_cov)**(1/2)
		b = np.linalg.det(self.alpha*self.I)**(-1/2)
		self.beta=self.sigma*np.sqrt(2*np.log(a*b/self.delta))+np.sqrt(self.alpha)*np.linalg.norm(self.user_feature)
		self.beta_list.extend([self.beta])
		self.real_beta=np.sqrt(np.dot(np.dot(self.user_feature-self.true_user_feature, self.user_cov),self.user_feature-self.true_user_feature))
		self.real_beta_list.extend([self.real_beta])

	def select_item(self, time):
		item_fs=self.item_feature_matrix.copy()
		estimated_payoffs=np.zeros(self.item_num)
		mean_y=np.zeros(self.item_num)
		cov_inv=np.linalg.pinv(self.user_cov)
		self.update_beta()
		for j in range(self.item_num):
			x=item_fs[j]
			x_norm=np.sqrt(np.dot(np.dot(x, cov_inv),x))
			x_star_norm=np.sqrt(np.dot(np.dot(item_fs[self.best_arm], cov_inv),item_fs[self.best_arm]))
			est_y=np.dot(x, self.user_feature)+self.beta*x_norm
			mean_y[j]=np.dot(x, self.user_feature)
			estimated_payoffs[j]=est_y
			self.ucb_matrix[time, j]=self.beta*x_norm
			self.true_ucb_matrix[time, j]=self.real_beta*x_norm
			self.index_matrix[time, j]=np.dot(x, self.user_feature)+self.beta*x_norm
			self.x_norm_matrix[time, j]=x_norm
			self.mean_matrix[time, j]=np.dot(x, self.user_feature)
			self.payoff_error_matrix[time, j]=np.abs(self.mean_matrix[time, j]-self.true_payoffs[j])
			self.gaps_ucb[time, j]=self.gaps[j]-2*self.beta*(x_norm)
			self.best_index[time, j]=self.best_payoff-self.index_matrix[time, j]
		est_gaps=np.max(mean_y)-mean_y
		self.est_gaps_ucb[time]=self.gaps_ucb[time]-self.gaps+est_gaps

		max_index=np.argmax(estimated_payoffs)
		self.item_index_selected.extend([max_index])
		self.item_counter[max_index]+=1
		selected_item_feature=item_fs[max_index]
		x_t_norm=np.sqrt(np.dot(np.dot(selected_item_feature, cov_inv),selected_item_feature))
		self.ucb_list[time]=self.beta*x_t_norm
		self.true_ucb_list[time]=np.abs(np.dot(self.user_feature, selected_item_feature)-self.true_payoffs[max_index])
		true_payoff=self.true_payoffs[max_index]
		max_ideal_payoff=np.max(self.true_payoffs)
		regret=max_ideal_payoff-true_payoff
		return true_payoff, selected_item_feature, regret,

	def update_user_feature(self, y, x):
		self.user_cov+=np.outer(x, x)
		self.user_xx+=np.outer(x, x)
		self.user_bias+=y*x
		self.user_feature=np.dot(np.linalg.pinv(self.user_cov), self.user_bias)

	def run(self,iteration):
		cumulative_regret=[0]
		learning_error_list=[]
		for time in range(iteration):	
			print('time/iteration', time, iteration,'~~~LinUCB')
			true_payoff, selected_item_feature, regret=self.select_item(time)
			self.update_user_feature(true_payoff, selected_item_feature)
			error=np.linalg.norm(self.user_feature-self.true_user_feature)
			cumulative_regret.extend([cumulative_regret[-1]+regret])
			learning_error_list.extend([error])

		return cumulative_regret[1:], learning_error_list, self.beta_list, self.real_beta_list, self.item_index_selected, self.index_matrix, self.x_norm_matrix, self.mean_matrix, self.gaps_ucb, self.est_gaps_ucb, self.best_index, self.ucb_matrix, self.true_ucb_matrix, self.payoff_error_matrix, self.ucb_list, self.true_ucb_list