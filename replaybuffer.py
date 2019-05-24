from envs import mazewandererenv
class ReplayBuffer:
    def __init__(self, env: mazewandererenv.Env):
        self.env = env
    
    def next_batch(self, batch_size):
        pass
    
    def shuffle(self):
        pass
    
    
        