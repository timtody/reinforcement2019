import unittest
import replaybuffer
import numpy as np

class TestBuffer(unittest.TestCase):

    def test_init(self):
        # dont use prepare buffer here
        buffer = replaybuffer.ReplayBuffer((2,2), 2)
        self.assertEqual(buffer.old_state.shape, (2,2,2))
        self.assertEqual(buffer.new_state.shape, (2,2,2))

    def test_append(self):
        max_buffer_size = 5
        buffer = replaybuffer.ReplayBuffer((2,2), max_buffer_size)
        # inputs
        old_state = np.arange(4).reshape((2, 2))
        new_state = old_state * 10
        action = 0
        reward = 1
        buffer.append(old_state, new_state, action, reward)
        self.assertEqual(np.all(buffer.old_state[0] == old_state), True)
        self.assertEqual(np.all(buffer.old_state[1] == old_state), False)
        self.assertEqual(np.all(buffer.new_state[0] == old_state), False)
        self.assertEqual(buffer.old_state.shape, (max_buffer_size,2,2))      	

    def test_next_batch(self):
        max_buffer_size = 3
        buffer = replaybuffer.ReplayBuffer((2,2), max_buffer_size=max_buffer_size)
        # inputs
        old_state = np.arange(4).reshape((2, 2))
        new_state = old_state * 10
        action = 2
        reward = 1
        self.assertEqual(buffer.empty(), True)
        self.assertEqual(buffer.full(), False)
        # test indices
        self.assertEqual(buffer.write_idx, 0)
        buffer.append(old_state, new_state, action, reward)
        self.assertEqual(buffer.write_idx, 1)
        buffer.append(old_state*2, new_state*2, action*2, reward*2)
        # test empty flag
        self.assertEqual(buffer.empty(), False)
        self.assertEqual(buffer.full(), False)
        buffer.append(old_state*3, new_state*3, action*3, reward*3)
        self.assertEqual(buffer.empty(), False)
        self.assertEqual(buffer.full(), True)
        
        self.assertEqual(buffer.write_idx, 3)
        self.assertEqual(buffer.read_idx, 0)
        # rest next_batch results (remainder size)
        old_state, new_state, action, reward = buffer.next_batch(2)
        self.assertEqual(buffer.read_idx, 2)
        self.assertEqual(old_state.shape, (2,2,2))
        self.assertEqual(new_state.shape, (2,2,2))
        self.assertEqual(np.all(action == [2,4]), True)
        self.assertEqual(np.all(reward == [1,2]), True)
        self.assertEqual(buffer.empty(), False)
        old_state, new_state, action, reward = buffer.next_batch(2)
        self.assertEqual(buffer.empty(), True)
        # test next_batch on empty
        return buffer

    def test_shuffle(self):
        # this should return true only half of the time
        max_buffer_size = 3
        buffer = replaybuffer.ReplayBuffer((2,2), max_buffer_size=max_buffer_size)
        old_state = np.arange(4).reshape((2, 2))
        new_state = old_state * 10
        action = 2
        reward = 1
        buffer.append(old_state, new_state, action, reward)
        buffer.append(old_state*2, new_state*2, action*2, reward*2)
        states_shuffled = np.array([old_state, old_state*2])
        np.random.shuffle(states_shuffled)
        buffer.shuffle()
        old_state, _, _, _ = buffer.next_batch(1)
        self.assertEqual(np.all(states_shuffled[0]==old_state), True)

    def test_reset_idx(self):
        buf = self.test_next_batch()
        self.assertEqual(buf.read_idx, 3)
        self.assertEqual(buf.write_idx, 3)
        buf._reset_read_idx()
        self.assertEqual(buf.read_idx, 0)
        buf._reset_write_idx()
        self.assertEqual(buf.write_idx, 0)
    
    def test_reset_all_idx(self):
        buf = self.test_next_batch()
        self.assertEqual(buf.read_idx, 3)
        self.assertEqual(buf.write_idx, 3)
        buf.reset()
        self.assertEqual(buf.read_idx, 0)
        self.assertEqual(buf.write_idx, 0)


if __name__ == '__main__':
    unittest.main()