from src.allocation.reinforcement_solution import DQNAgentConfiguration

import numpy as np

def train_dqn(env, possible_branches, episodes=1000, batch_size=32):
    state_size = env.get_state().shape[0]
    max_action_size = possible_branches # All branches in RA-PST are possible actions
    agent = DQNAgentConfiguration(state_size, max_action_size)
    
    for e in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        
        while True:
            possible_actions = env.get_possible_actions()
            action = agent.act(state, possible_actions)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            
            if done:
                print(f"Episode: {e}/{episodes}, score: {reward}, e: {agent.epsilon:.2}")
                break
                
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
    
    return agent

# Train the DQN agent

agent = train_dqn(env)