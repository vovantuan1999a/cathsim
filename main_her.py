import os
from cathsim_her import CathSimEnv
from utils import evaluate_env
from utils import ALGOS
from stable_baselines3 import HerReplayBuffer
from gym.wrappers import TimeLimit
EP_LENGTH = 2000
TIMESTEPS = EP_LENGTH * 100
N_EVAL = 30

ENV_NAME = "1"
OBS_TYPE = "image_time"
TARGET = ["lcca"]
SCENE = [1]
POLICIES = ["MlpPolicy"]
algo = "ddpg"
ALGORITHMS = {f"{algo}": ALGOS[f"{algo}"]}


SAVING_PATH = f"./benchmarking/{ENV_NAME}"
MODELS_PATH = os.path.join(SAVING_PATH, "models", OBS_TYPE)
CKPT_PATH = os.path.join(SAVING_PATH, "ckpt", OBS_TYPE)
LOGS_PATH = os.path.join(SAVING_PATH, "logs", OBS_TYPE)
RESULTS_PATH = os.path.join(SAVING_PATH, "results", OBS_TYPE)
HEATMAPS_PATH = os.path.join(SAVING_PATH, "heatmaps", OBS_TYPE)

for path in [MODELS_PATH, LOGS_PATH, CKPT_PATH, RESULTS_PATH, HEATMAPS_PATH]:
    os.makedirs(path, exist_ok=True)


def train_algorithms(algorithms: dict = ALGORITHMS,
                     policies: list = POLICIES,
                     timesteps: int = TIMESTEPS):

    for algorithm_name, algorithm in algorithms.items():
        for policy in policies:
            for scene in SCENE:
                for target in TARGET:

                    fname = f"{algorithm_name}_HER-{scene}-{target}-{policy}"

                    env = CathSimEnv(scene=scene,
                                     obs_type=OBS_TYPE)

                    # env = TimeLimit(env, max_episode_steps=EP_LENGTH)

                    model_path = os.path.join(MODELS_PATH, fname)

                    if os.path.exists(f"{model_path}.zip"):
                        print("...loading_env...")
                        model = algorithm.load(model_path, env=env)
                    else:
                        model = algorithm(
                            "MultiInputPolicy",
                            env,
                            replay_buffer_class=HerReplayBuffer,
                            replay_buffer_kwargs=dict(
                                goal_selection_strategy="future",
                                max_episode_length=2000,
                            ),
                            verbose=1,
                            buffer_size=int(1e6),
                            seed=42,
                            tensorboard_log=LOGS_PATH,
                        )

                    model.learn(total_timesteps=timesteps,
                                reset_num_timesteps=False,
                                tb_log_name=fname)

                    model.save(model_path)


def test_algorithms(algorithms: dict = ALGORITHMS,
                    policies: list = POLICIES,
                    n_eval: int = 30,
                    render: bool = False,
                    verbose: bool = True):

    for algorithm_name, algorithm in algorithms.items():
        for policy in policies:
            for scene in SCENE:
                for target in TARGET:

                    fname = f"{algorithm_name}-{scene}-{target}-{policy}"

                    env = CathSimEnv(scene=scene,
                                     obs_type=OBS_TYPE,
                                     ep_length=EP_LENGTH)

                    model_path = os.path.join(MODELS_PATH, fname)
                    if os.path.exists(f"{model_path}.zip"):
                        print(f"...loading {algorithm_name}...")

                        model = algorithm.load(model_path, env=env)

                        evaluate_env(model=model, env=env,
                                     n_episodes=n_eval,
                                     render=render,
                                     deterministic=False,
                                     saving_path=RESULTS_PATH,
                                     fname=fname)


if __name__ == "__main__":

    train_algorithms()
    test_algorithms()
