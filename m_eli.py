import numpy as np 

class M_ELI():
	def __init__(self, dimension, phase_num, item_num, user_feature, item_feature, true_payoffs, alpha, delta, sigma, gamma):
		self.dimension=dimension
		self.phase_num=phase_num
		self.iteration=2**phase_num
		self.item_num=item_num
		self.user_feature=user_feature
		self.item_feature=item_feature
		self.true_payoffs=true_payoffs
		self.alpha=alpha
		self.delta=delta
		self.sigma=sigma
		self.gamma=gamma
		self.beta=np.sqrt(2*np.log(1/self.delta))
		self.cov=self.alpha*np.identity(self.dimension)
		self.cov_2=self.alpha*np.identity(self.dimension)
		self.bias=np.zeros(self.dimension)
		self.user_f=np.zeros(self.dimension)
		self.item_set=list(range(self.item_num))
		self.x_norm_matrix=np.zeros((self.item_num, self.iteration))
		self.est_y_matrix=np.zeros((self.item_num, self.iteration))
		self.low_ucb_list=np.zeros(self.item_num)
		self.upper_ucb_list=np.zeros(self.item_num)
		self.item_index=np.zeros(self.iteration)
		self.hist_low_matrix=np.zeros((self.item_num, self.iteration))
		self.hist_upper_matrix=np.zeros((self.item_num, self.iteration))
		self.est_gaps=np.zeros((self.item_num, self.iteration))
		self.item_num_list=self.item_num*np.ones(self.iteration)

	def update_beta(self):
		self.beta=np.sqrt(2*np.log(1/self.delta))

	def select_arm(self, time):
		self.low_ucb_list=np.zeros(self.item_num)
		self.upper_ucb_list=np.zeros(self.item_num)
		x_norm_list=np.zeros(self.item_num)
		cov_inv_2=np.linalg.pinv(self.cov_2)
		cov_inv=np.linalg.pinv(self.cov)
		est_y_list=np.zeros(self.item_num)
		for i in self.item_set:
			x=self.item_feature[i]
			x_norm_2=np.sqrt(np.dot(np.dot(x, cov_inv_2),x))
			x_norm=np.sqrt(np.dot(np.dot(x, cov_inv),x))
			x_norm_list[i]=x_norm_2
			self.x_norm_matrix[i,time]=x_norm 
			est_y=np.dot(self.user_f, x)
			est_y_list[i]=est_y
			self.est_y_matrix[i,time]=est_y
			self.low_ucb_list[i]=est_y-self.beta*x_norm 
			self.upper_ucb_list[i]=est_y+self.beta*x_norm
			self.hist_low_matrix[i,time]=self.low_ucb_list[i]
			self.hist_upper_matrix[i,time]=self.upper_ucb_list[i]

		best_arm=np.argmax(est_y_list)
		self.est_gaps[:,time]=est_y_list[best_arm]-est_y_list
		max_index=np.argmax(x_norm_list)
		self.item_index[time]=max_index
		payoff=self.true_payoffs[max_index]+np.random.normal(scale=self.sigma)
		regret=np.max(self.true_payoffs)-self.true_payoffs[max_index]
		x=self.item_feature[max_index]
		return x, payoff, regret 

	def update_feature(self, x, y):
		self.cov+=np.outer(x,x)
		self.cov_2+=np.outer(x,x)
		self.bias+=x*y
		#self.user_f=np.dot(np.linalg.pinv(self.cov), self.bias)
		self.user_f+=self.gamma*(y-np.dot(self.user_f, x))*x

	def reset(self):
		self.cov_2=self.alpha*np.identity(self.dimension)
		#self.bias=np.zeros(self.dimension)
		#self.user_f=np.zeros(self.dimension)

	def eliminate_arm(self):
		a=self.item_set.copy()
		for i in a:
			if np.max(self.low_ucb_list)>self.upper_ucb_list[i]:
				self.item_set.remove(i)
			else:
				pass 

	def run(self, iteration):
		cum_regret=[0]
		error=np.zeros(self.iteration)
		error[0]=1
		self.update_beta()
		for l in range(self.phase_num):
			start_time=2**l 
			end_time=2**(l+1)
			for time in range(start_time, end_time):
				print('time/iteration=%s/%s, item_num=%s ~~~~ M-Eliminator'%(time, iteration, len(self.item_set)))
				self.item_num_list[time]=len(self.item_set)
				x,y, regret=self.select_arm(time)
				self.update_feature(x,y)
				cum_regret.extend([cum_regret[-1]+regret])
				error[time]=np.linalg.norm(self.user_f-self.user_feature)
			self.eliminate_arm()
			self.reset()

		return cum_regret, error, self.item_index, self.x_norm_matrix, self.est_y_matrix, self.hist_low_matrix, self.hist_upper_matrix, self.item_num_list




























