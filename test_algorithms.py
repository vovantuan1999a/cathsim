import os
from cathsim import CathSimEnv
from utils import evaluate_env
from utils import ALGOS
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from gym.wrappers import TimeLimit

EP_LENGTH = 2000
TIMESTEPS = EP_LENGTH * 300
N_EVAL = 30

ENV_NAME = "3"
OBS_TYPE = ["internal"]
TARGET = ["bca", "lcca"]
SCENE = [1, 2]
algo = "ppo"
ALGORITHMS = {f"{algo}": ALGOS[f"{algo}"]}
device = "cpu"


SAVING_PATH = f"./benchmarking/{ENV_NAME}"


def test_algorithms(algorithms: dict = ALGORITHMS,
                    n_eval: int = 30,
                    render: bool = False,
                    verbose: bool = True):

    for obs_type in OBS_TYPE:
        MODELS_PATH = os.path.join(SAVING_PATH, "models", obs_type)
        RESULTS_PATH = os.path.join(SAVING_PATH, "results", obs_type)

        for algorithm_name, algorithm in algorithms.items():
            for scene in SCENE:
                for target in TARGET:
                    policy = "MlpPolicy"
                    if obs_type != "internal":
                        policy = "CnnPolicy"

                    fname = f"{algorithm_name}-{scene}-{target}-{policy}"

                    n_frames = 1
                    if obs_type == "image_time":
                        obs_type = "image"
                        n_frames = 4
                    env = CathSimEnv(scene=scene,
                                     obs_type=obs_type,
                                     target=target,
                                     n_frames=n_frames)
                    print(env.observation_space.shape)

                    env = TimeLimit(env, max_episode_steps=EP_LENGTH)

                    model_path = os.path.join(MODELS_PATH, fname)

                    if os.path.exists(f"{model_path}.zip"):
                        print(f"...loading {fname}...")

                        model = algorithm.load(
                            model_path, env=env, device=device)

                        evaluate_env(model=model, env=env,
                                     n_episodes=n_eval,
                                     render=render,
                                     deterministic=False,
                                     saving_path=RESULTS_PATH,
                                     fname=fname)


if __name__ == "__main__":
    test_algorithms()