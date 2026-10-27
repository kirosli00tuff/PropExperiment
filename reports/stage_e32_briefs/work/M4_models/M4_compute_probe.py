"""M4 compute probe on SYNTHETIC random data only (no market data is read).

Times one fit of each model family at row counts that match a 39-month ZM discovery
window sampled at 1-minute and 10-second decision points (see M4_ess.out).
Run: nice -n 10 uv run python M4_compute_probe.py > M4_compute_probe.out
"""
import os
import time
import json
import numpy as np

os.nice(10)
THREADS = 8
os.environ.setdefault("OMP_NUM_THREADS", str(THREADS))
RNG = np.random.default_rng(20261027)
P = 30  # features
RES = {}


def synth(n, p=P):
    x = RNG.standard_normal((n, p), dtype=np.float32)
    logit = 0.05 * x[:, 0] - 0.03 * x[:, 1]
    y = (RNG.random(n) < 1 / (1 + np.exp(-logit))).astype(np.int8)
    return x, y


def timed(name, fn):
    t0 = time.perf_counter()
    out = fn()
    dt = time.perf_counter() - t0
    RES[name] = round(dt, 3)
    print(f"{name}: {dt:.2f} s", flush=True)
    return out


def probe_linear(n):
    from sklearn.linear_model import LogisticRegression
    x, y = synth(n)
    timed(f"logit_L2_lbfgs_n{n}", lambda: LogisticRegression(C=1.0, max_iter=200).fit(x, y))
    timed(f"logit_enet_saga_n{n}", lambda: LogisticRegression(
        penalty="elasticnet", l1_ratio=0.5, C=0.1, solver="saga", max_iter=50, tol=1e-3).fit(x, y))


def probe_lgbm(n, rounds=500):
    import lightgbm as lgb
    x, y = synth(n)
    params = dict(objective="binary", max_depth=3, num_leaves=8, learning_rate=0.05,
                  min_data_in_leaf=500, lambda_l2=10.0, num_threads=THREADS, verbose=-1,
                  deterministic=True, force_row_wise=True, seed=1)
    ds = lgb.Dataset(x, y, free_raw_data=False)
    timed(f"lgbm_d3_{rounds}r_n{n}", lambda: lgb.train(params, ds, num_boost_round=rounds))
    mc = dict(params, monotone_constraints=[1, -1, 1, -1, 1] + [0] * (P - 5),
              monotone_constraints_method="intermediate")
    ds2 = lgb.Dataset(x, y, free_raw_data=False)
    timed(f"lgbm_d3_mono_{rounds}r_n{n}", lambda: lgb.train(mc, ds2, num_boost_round=rounds))


def probe_rls(n, lam=0.999):
    x, y = synth(n)
    yf = y.astype(np.float64) - 0.5
    xd = x.astype(np.float64)

    def run():
        theta = np.zeros(P)
        pm = np.eye(P) * 100.0
        for t in range(n):
            phi = xd[t]
            pphi = pm @ phi
            k = pphi / (lam + phi @ pphi)
            theta += k * (yf[t] - phi @ theta)
            pm = (pm - np.outer(k, pphi)) / lam
        return theta
    timed(f"rls_forget_p{P}_n{n}", run)


def probe_torch(seq_len=128, batch=256, steps=60):
    import torch
    import torch.nn as nn
    if not torch.cuda.is_available():
        RES["torch"] = "no cuda"
        return
    dev = torch.device("cuda")
    torch.set_num_threads(4)

    class Block(nn.Module):
        def __init__(self, cin, cout, d, k=3):
            super().__init__()
            self.pad = (k - 1) * d
            self.c1 = nn.Conv1d(cin, cout, k, dilation=d)
            self.c2 = nn.Conv1d(cout, cout, k, dilation=d)
            self.res = nn.Conv1d(cin, cout, 1) if cin != cout else nn.Identity()

        def forward(self, x):
            h = torch.relu(self.c1(nn.functional.pad(x, (self.pad, 0))))
            h = torch.relu(self.c2(nn.functional.pad(h, (self.pad, 0))))
            return torch.relu(h + self.res(x))

    class TCN(nn.Module):
        def __init__(self, ch=32, levels=6):
            super().__init__()
            layers, cin = [], P
            for i in range(levels):
                layers.append(Block(cin, ch, 2 ** i))
                cin = ch
            self.net = nn.Sequential(*layers)
            self.head = nn.Linear(ch, 1)

        def forward(self, x):  # x: (B, P, T)
            return self.head(self.net(x)[:, :, -1])

    class TinyTF(nn.Module):
        def __init__(self, d=64, heads=4, layers=2):
            super().__init__()
            self.inp = nn.Linear(P, d)
            self.pos = nn.Parameter(torch.zeros(1, seq_len, d))
            enc = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.1, batch_first=True)
            self.enc = nn.TransformerEncoder(enc, layers)
            self.head = nn.Linear(d, 1)

        def forward(self, x):  # x: (B, P, T)
            h = self.inp(x.transpose(1, 2)) + self.pos
            return self.head(self.enc(h)[:, -1])

    for name, model in [("tcn32x6", TCN()), ("tinytf_d64_l2", TinyTF())]:
        model = model.to(dev)
        nparam = sum(p.numel() for p in model.parameters())
        opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
        lossf = nn.BCEWithLogitsLoss()
        xb = torch.randn(batch, P, seq_len, device=dev)
        yb = (torch.rand(batch, 1, device=dev) < 0.5).float()
        torch.cuda.reset_peak_memory_stats()
        for i in range(steps + 10):
            if i == 10:
                torch.cuda.synchronize()
                t0 = time.perf_counter()
            opt.zero_grad()
            loss = lossf(model(xb), yb)
            loss.backward()
            opt.step()
        torch.cuda.synchronize()
        dt = time.perf_counter() - t0
        RES[f"{name}_params"] = nparam
        RES[f"{name}_train_samples_per_s"] = round(steps * batch / dt)
        RES[f"{name}_peak_mib"] = round(torch.cuda.max_memory_allocated() / 2**20)
        print(name, nparam, RES[f"{name}_train_samples_per_s"], RES[f"{name}_peak_mib"], flush=True)


if __name__ == "__main__":
    t_start = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    probe_linear(1_000_000)
    probe_lgbm(1_000_000)
    probe_lgbm(5_000_000)
    probe_rls(200_000)
    probe_torch()
    RES["started"] = t_start
    RES["ended"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    RES["threads"] = THREADS
    print(json.dumps(RES))
