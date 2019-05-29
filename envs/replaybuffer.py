import numpy as np

# ToDo & Bugs:
# - Extra dimension appears when using next_batch at end of buffer
# - Buffer tuple should be (state, newState, action, reward)
# - 

class ReplayBuffer:
    def __init__(self, max_buffer_size = 500):
        self.action_buffer = None
        self.reward_buffer = None
        self.obs_buffer = None
        self.max_buffer_size = max_buffer_size
        self.current_buffer_size = 0
        self.first = True
        self.read_idx = 0
        self.write_idx = 0
        # ToDo: Allocate full size of buffer at start
    
    def append(self, observation, reward, action):
        if self.current_buffer_size < self.max_buffer_size:
            if self.first:
                self.obs_buffer = np.expand_dims(observation, axis=0)
                self.reward_buffer = reward
                self.action_buffer = action
                self.first = False
            else:
                observation = np.expand_dims(observation, axis=0)
                self.obs_buffer = np.concatenate((self.obs_buffer, observation), axis=0)
                self.reward_buffer = np.append(self.reward_buffer, reward)
                self.action_buffer = np.append(self.action_buffer, action)
            self.current_buffer_size += 1
        else:
            self.obs_buffer[self.write_idx] = observation
            self.reward_buffer[self.write_idx] = reward
            self.action_buffer[self.write_idx] = action
            self.write_idx = self.write_idx % (self.max_buffer_size + 1)

    def next_batch(self, batch_size):
        done = True # ToDo: true only if one round through buffer completed
        if self.read_idx + batch_size <= self.max_buffer_size:
            obs = self.obs_buffer[self.read_idx:self.read_idx+batch_size]
            action = self.action_buffer[self.read_idx:self.read_idx+batch_size]
            reward = self.reward_buffer[self.read_idx:self.read_idx+batch_size]
            self.read_idx += batch_size

            return obs, reward, action, done
        else:
            tail_indices = batch_size - (self.max_buffer_size - self.read_idx)
            top_indices = batch_size - tail_indices
            tail_data = self.obs_buffer[self.read_idx:]
            top_data = self.obs_buffer[:top_indices]
            action = np.concatenate((self.action_buffer[self.read_idx:],self.action_buffer[:top_indices]))
            reward = np.concatenate((self.reward_buffer[self.read_idx:],self.reward_buffer[:top_indices]))
            self.read_idx = top_indices

            return np.stack((tail_data, top_data)), reward, action, done

    def shuffle(self):
        perm = np.random.permutation(self.current_buffer_size)
        self.obs_buffer = self.obs_buffer[perm]
        self.reward_buffer = self.reward_buffer[perm]
        self.action_buffer = self.action_buffer[perm]

    def resetReadIndex(self):
        # ToDo: implement
        pass

    def __repr__(self):
        return f"Replay buffer: \n\t \
            buffer size: \t{self.max_buffer_size}\n\t\
            current index: \t{self.read_idx}\n\t\ "