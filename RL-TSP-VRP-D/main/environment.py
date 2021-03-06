import gym



#from logger import TrainingLogger, TestingLogger

'''
überbegriff für travelling salesman und vehicle routing problem
'''
class CustomEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {
    'render.modes': ['human'],
    }

    def __init__(self, 
            name,
            max_steps_per_episode,
            simulation,
            visualizor,
            obs_encoder,
            act_decoder,
            reward_calc,
            ):

        super(CustomEnv, self).__init__()

        self.name = name
        self.max_steps_per_episode = max_steps_per_episode

        # Init simulator
        self.simulation = simulation

        # Init visulizor:
        self.visualizor = visualizor
        
        # Init state and action interpreter
        self.act_decoder = act_decoder
        self.obs_encoder = obs_encoder
        
        # Init reward calculator
        self.reward_calc = reward_calc

        # Init Logger (move to train process)
        #self.logger        = TrainingLogger()
        #self.test_logger   = TestingLogger()

        # Init gym spaces:
        self.reset()
        #self.action_space      = self.act_decoder.action_space()
        #self.observation_space = self.obs_encoder.obs_space()

        # Init Counter:
        self.count_episodes    = 0
        self.count_total_steps = 0

    def step(self, actions):
        
        # take action:
        self.simulation.temp_db.init_step()
        self.act_decoder.decode_actions(actions)
        done = self.simulation.finish_step()
        self.simulation.temp_db.finish_step()

        # new state:
        observation = self.obs_encoder.observe_state()

        # reward:
        #reward = self.reward_calc.reward_function()
        reward = 0

        self.count_steps_of_episode += 1
        self.count_total_steps      += 1

        done = done or self.max_steps_per_episode <= self.count_steps_of_episode

        if done:
            self.count_episodes     += 1

        return observation, reward, done, {}


    def reset(self):

        # reset counter:
        self.count_steps_of_episode = 0

        self.simulation.reset_simulation()

        # Init first state:
        observation = self.obs_encoder.observe_state()

        return observation
        
    def render(self, mode='human', close=False):
        if mode == 'human':
            self.visualizor.visualize_step(self.count_episodes, self.count_steps_of_episode)

        if close == True:
            self.visualizor.close()


