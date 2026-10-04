# src/rtt/utils/seed.py
import os
import random

import numpy as np
import torch


def seed_everything(seed: int, deterministic: bool = False) -> None:

    """Put every random number generator into a known state."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if deterministic:
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)
        pass