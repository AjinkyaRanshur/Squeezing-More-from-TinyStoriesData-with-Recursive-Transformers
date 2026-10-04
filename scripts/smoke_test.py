# scripts/smoke_test.py
import hashlib
from datetime import datetime

import torch
from torch import nn

from rtt.utils.manifest import write_manifest
from rtt.utils.seed import seed_everything


def param_hash(model: nn.Module) -> str:
    """Fingerprint of every weight. Same hash = bit-identical weights."""
    fingerprint=torch.cat([p.detach().flatten().cpu() for p in model.parameters()])
    data=fingerprint.numpy().tobytes()
    return hashlib.sha256(data).hexdigest()



def train(seed: int, device: str) -> tuple[float, str]:
    X = torch.randn(256, 32, device=device)
    seed_everything(seed)
    y = X.sum(dim=1, keepdim=True).sin()
    model=nn.Sequential(nn.Linear(32,64),nn.ReLU(),nn.Linear(64,1)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-2)
    for step in range(20):
        optimizer.zero_grad()
        loss=nn.functional.mse_loss(model(X),y)
        loss.backward()
        optimizer.step()

    return loss.item(), param_hash(model)


def main() -> None:
    devices = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
    for device in devices:
        loss_a,hash_a= train(0,device)
        loss_b,hash_b= train(0,device)
        loss_c,hash_c= train(1,device)
        print(device)
        print(loss_a,hash_a)
        print(loss_b,hash_b)
        print(loss_c,hash_c)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = write_manifest(f"runs/smoke_{stamp}", {"script": "smoke_test"}, seed=0)
    print("manifest:", path)


if __name__ == "__main__":
    main()