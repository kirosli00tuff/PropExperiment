"""RankingReviewer-FableXHigh: re-run EconCoder's pair economics (A3_funnel/A3_models/A3_run, unchanged) for a few
pairs, with (a) a different base seed and (b) alternative Topstep fees. EconCoder's modules are imported, not edited.

Usage: python3 rr_econ_rerun.py <job> where job in {seedA, seedB, altfee}
  seedA : seed 20261022, pairs topstep QG, topstep QM, tradeify QG, mffu QM
  seedB : seed 20261022, pairs lucid QG, tradeify QM, topstep MNQ
  altfee: original seed 20261021, topstep QG and QM at F_rt = 3.70 (LFA page, read as per round turn) and 7.40 (per side)
Writes rr_econ_<job>.json in this folder. nice 10.
"""
import copy
import json
import os
import sys
import time

os.nice(10)
HERE = os.path.dirname(os.path.abspath(__file__))
ECON = os.path.abspath(os.path.join(HERE, '..', 'A3_econ'))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))   # prop_econ/ lives at the repo root
sys.path.insert(0, ECON)
sys.path.insert(0, REPO)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
sys.dont_write_bytecode = True
import A3_funnel as F  # noqa: E402  (EconCoder's module, read-only)
import A3_run as R  # noqa: E402

JOBS = {
    'seedA': {'seed': 20261022, 'pairs': [('topstep', 'QG'), ('topstep', 'QM'), ('tradeify', 'QG'), ('mffu', 'QM')],
              'fees': None},
    'seedB': {'seed': 20261022, 'pairs': [('lucid', 'QG'), ('tradeify', 'QM'), ('topstep', 'MNQ')], 'fees': None},
    'altfee': {'seed': 20261021, 'pairs': [('topstep', 'QG'), ('topstep', 'QM')], 'fees': [3.70, 7.40]},
    # Lucid at the spec's 'u' rule (highest fee for the product at the other four firms): QG 4.00 (tradeify), QM 5.40 (tradeify)
    'lucidalt': {'seed': 20261021, 'pairs': [('lucid', 'QG'), ('lucid', 'QM')], 'fees': 'u_rule'},
}
U_RULE = {('lucid', 'QG'): 4.00, ('lucid', 'QM'): 5.40}


def main(job):
    spec = JOBS[job]
    F.BASE_SEED = spec['seed']          # every derive_seed call reads the module global at call time
    assert F.phase_seed('attempt', 'z') == F.derive_seed(spec['seed'], 'e28a3', 'attempt', 'z')
    inputs = json.loads(R.INPUTS.read_text())
    fp = R._fingerprint()
    firms = sorted({f for f, _ in spec['pairs']})
    t0 = time.time()
    R.build_state(firms)
    print(f'{time.strftime("%H:%M:%S")} job {job} seed {spec["seed"]} state built in {time.time() - t0:.1f}s', flush=True)
    rows = []
    for firm, code in spec['pairs']:
        fees = [U_RULE[(firm, code)]] if spec['fees'] == 'u_rule' else (spec['fees'] or [None])
        for fee in fees:
            inp = copy.deepcopy(inputs)
            if fee is not None:
                p = next(x for x in inp['pairs'] if x['firm'] == firm and x['code'] == code)
                p['F_rt_usd'] = fee
                p['fee_src'] = {'source_file': 'reports/stage_e28_briefs/pages/A2_topstep/ts_8284229.html.txt',
                                'quote': 'In the Trading Combine, a $3.70/lot simulated fee is charged',
                                'unit': 'USD per round trip' if fee == 3.70 else 'USD per round trip (3.70 per side read)',
                                'note': 'reviewer alternative'}
            t1 = time.time()
            rec = R.run_pair(firm, code, inp, fp, R._STATE)
            rec.pop('evaluations', None)
            rec['reviewer_seed'] = spec['seed']
            rec['reviewer_fee_override'] = fee
            rows.append(rec)
            print(f'{time.strftime("%H:%M:%S")} {firm} {code} fee={fee} {time.time() - t1:.0f}s '
                  f'mu*_lim {rec["mu_star_lim"]} mu*_mkt {rec["mu_star_mkt"]} mu10K {rec["mu10K"]} '
                  f'cost/att {rec["cost_per_attempt_usd"]}', flush=True)
            with open(os.path.join(HERE, f'rr_econ_{job}.json'), 'w') as fh:
                json.dump({'job': job, 'seed': spec['seed'], 'fingerprint': fp, 'rows': rows}, fh, indent=1)
    print(f'{time.strftime("%H:%M:%S")} job {job} done in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
