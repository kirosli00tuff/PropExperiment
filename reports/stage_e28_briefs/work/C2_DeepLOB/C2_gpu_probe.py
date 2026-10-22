"""C2 compute probe: DeepLOB-family models on SYNTHETIC random tensors only (no market data).

Measures parameter count, peak GPU memory, training throughput and single-sample inference
latency on this machine (RTX 3050 Laptop 4 GB, CPU). Prints a short summary.
"""
import os
import time

import torch
import torch.nn as nn

os.nice(10)
torch.set_num_threads(4)


class DeepLOB(nn.Module):
    """DeepLOB per Zhang, Zohren, Roberts (2019) Fig. 3; `ch` conv filters, `bn` batchnorm."""

    def __init__(self, ch=16, inc=32, bn=False, lstm=64):
        super().__init__()
        act = lambda: nn.LeakyReLU(0.01)

        def conv(cin, cout, k, s=(1, 1)):
            layers = [nn.Conv2d(cin, cout, k, stride=s), act()]
            if bn:
                layers.append(nn.BatchNorm2d(cout))
            return layers

        def tpad(k):  # pad time dim so length stays 100 ('same' in Keras)
            return nn.ZeroPad2d((0, 0, (k - 1) // 2, k // 2))

        self.b1 = nn.Sequential(*conv(1, ch, (1, 2), (1, 2)), tpad(4), *conv(ch, ch, (4, 1)), tpad(4), *conv(ch, ch, (4, 1)))
        self.b2 = nn.Sequential(*conv(ch, ch, (1, 2), (1, 2)), tpad(4), *conv(ch, ch, (4, 1)), tpad(4), *conv(ch, ch, (4, 1)))
        self.b3 = nn.Sequential(*conv(ch, ch, (1, 10)), tpad(4), *conv(ch, ch, (4, 1)), tpad(4), *conv(ch, ch, (4, 1)))
        self.i1 = nn.Sequential(*conv(ch, inc, (1, 1)), tpad(3), *conv(inc, inc, (3, 1)))
        self.i2 = nn.Sequential(*conv(ch, inc, (1, 1)), tpad(5), *conv(inc, inc, (5, 1)))
        self.i3 = nn.Sequential(nn.MaxPool2d((3, 1), stride=1, padding=(1, 0)), *conv(ch, inc, (1, 1)))
        self.lstm = nn.LSTM(3 * inc, lstm, batch_first=True)
        self.fc = nn.Linear(lstm, 3)

    def forward(self, x):  # x: (B,1,100,40)
        x = self.b3(self.b2(self.b1(x)))
        x = torch.cat([self.i1(x), self.i2(x), self.i3(x)], 1)  # (B,3*inc,100,1)
        x = x.squeeze(-1).permute(0, 2, 1)
        out, _ = self.lstm(x)
        return self.fc(out[:, -1])


class TransLOBLike(nn.Module):
    """Approximation of Wallbridge (2020): 5 dilated causal conv (14 ch), LayerNorm, +1 time
    encoding, 2 shared-weight transformer blocks (3 heads), FF 64, softmax head."""

    def __init__(self):
        super().__init__()
        self.convs = nn.ModuleList([nn.Conv1d(40 if i == 0 else 14, 14, 2, dilation=d) for i, d in enumerate([1, 2, 4, 8, 16])])
        self.ln = nn.LayerNorm(14)
        self.block = nn.TransformerEncoderLayer(15, 3, dim_feedforward=60, dropout=0.0, batch_first=True)
        self.head = nn.Sequential(nn.Flatten(), nn.Linear(100 * 15, 64), nn.ReLU(), nn.Dropout(0.1), nn.Linear(64, 3))
        self.register_buffer("mask", torch.triu(torch.full((100, 100), float("-inf")), 1))

    def forward(self, x):  # x: (B,1,100,40)
        h = x.squeeze(1).permute(0, 2, 1)  # (B,40,100)
        for c in self.convs:
            h = torch.relu(c(nn.functional.pad(h, (c.dilation[0], 0))))
        h = self.ln(h.permute(0, 2, 1))
        t = torch.linspace(-1, 1, 100, device=x.device).expand(h.shape[0], 100).unsqueeze(-1)
        h = torch.cat([h, t], -1)
        for _ in range(2):
            h = self.block(h, src_mask=self.mask)
        return self.head(h)


def nparams(m):
    return sum(p.numel() for p in m.parameters() if p.requires_grad)


def train_probe(m, dev, bs, steps):
    m = m.to(dev).train()
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    lossf = nn.CrossEntropyLoss()
    x = torch.randn(bs, 1, 100, 40, device=dev)
    y = torch.randint(0, 3, (bs,), device=dev)
    if dev == "cuda":
        torch.cuda.reset_peak_memory_stats()
    for i in range(steps + 3):
        if i == 3:
            if dev == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()
        opt.zero_grad()
        lossf(m(x), y).backward()
        opt.step()
    if dev == "cuda":
        torch.cuda.synchronize()
    dt = time.perf_counter() - t0
    peak = torch.cuda.max_memory_allocated() / 2**20 if dev == "cuda" else float("nan")
    return bs * steps / dt, peak


@torch.no_grad()
def infer_probe(m, dev, reps=200):
    m = m.to(dev).eval()
    x = torch.randn(1, 1, 100, 40, device=dev)
    for _ in range(10):
        m(x)
    ts = []
    for _ in range(reps):
        if dev == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        m(x)
        if dev == "cuda":
            torch.cuda.synchronize()
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return 1e3 * ts[len(ts) // 2], 1e3 * ts[int(0.99 * len(ts))]


def main():
    torch.manual_seed(0)
    models = {
        "DeepLOB-paper(16ch,noBN)": lambda: DeepLOB(16, 32, False),
        "DeepLOB-PyTorch(32ch,BN,inc64)": lambda: DeepLOB(32, 64, True),
        "TransLOB-like": TransLOBLike,
    }
    print("gpu:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none")
    for name, mk in models.items():
        p = nparams(mk())
        line = [name, f"params={p}"]
        for bs, steps in [(32, 150), (256, 40)]:
            sps, peak = train_probe(mk(), "cuda", bs, steps)
            line.append(f"gpu_bs{bs}: {sps:,.0f} samp/s peakMiB={peak:.0f}")
        sps_cpu, _ = train_probe(mk(), "cpu", 32, 20)
        line.append(f"cpu4t_bs32: {sps_cpu:,.0f} samp/s")
        g50, g99 = infer_probe(mk(), "cuda")
        c50, c99 = infer_probe(mk(), "cpu")
        line.append(f"infer1 gpu p50={g50:.2f}ms p99={g99:.2f}ms cpu p50={c50:.2f}ms p99={c99:.2f}ms")
        print(" | ".join(line), flush=True)


if __name__ == "__main__":
    main()
