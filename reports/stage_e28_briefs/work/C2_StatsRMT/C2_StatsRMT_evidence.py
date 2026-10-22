"""Verify every evidence-table quote against its saved file and emit the markdown table."""
import re, sys, unicodedata
from pathlib import Path

PAGES = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_StatsRMT")
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^a-z0-9]", "", s)

def source_text(name):
    if name == "screening/stage_e_verdict.py":
        return norm((REPO / name).read_text(errors="ignore"))
    texts = []
    stem = name[:-4] if name.endswith(".txt") else name
    for cand in (PAGES / name, PAGES / (stem + ".raw.txt"), PAGES / (name + ".txt")):
        if cand.exists():
            texts.append(norm(cand.read_text(errors="ignore")))
    return " ".join(texts)

ROWS = [
 ("DSR deflates by the number of independent trials and the variance of trial results", "Bailey and López de Prado 2014", "the number of independent trials carried out (N); ii) the variance of the backtest results", "bailey_lopezdeprado_2014_dsr.txt"),
 ("DSR's N means independent trials, not raw trials", "Bailey and López de Prado 2014", "It is critical to understand that the N used to compute", "bailey_lopezdeprado_2014_dsr.txt"),
 ("DSR paper links its correction to shrinkage and regression to the mean", "Bailey and López de Prado 2014", "regression to the mean", "bailey_lopezdeprado_2014_dsr.txt"),
 ("Program's DSR uses the population variance of trial Sharpe ratios", "repo code", "the Sharpe variance over ``variance_over`` (population variance)", "screening/stage_e_verdict.py"),
 ("Top S&P eigenvalue far above the MP edge", "Laloux et al. 1999", "25 times larger than the predicted", "laloux_1999_noise_dressing.txt"),
 ("MP fits most of the S&P spectrum; top 6% exceed the edge", "Laloux et al. 1999", "accounts quite satisfactorily for 94% of the spectrum, while the 6% highest eigenvalues still exceed the theoretical upper edge", "laloux_1999_noise_dressing.txt"),
 ("Most US stock correlation eigenvalues lie in the RMT band", "Plerou et al. 2002", "a majority of the eigenvalues of C fall within the RMT bounds", "plerou_2002_rmt.txt"),
 ("Cleaning lowers out-of-sample risk on stock panels", "Bun, Bouchaud and Potters 2017", "it is always better to use a cleaned correlation matrix", "bun_bouchaud_potters_2017_cleaning.txt"),
 ("Effective q differs from N/T in financial data", "Bun, Bouchaud and Potters 2017", "one often observes empirically, especially with financial data, that the value of q = N/T", "bun_bouchaud_potters_2017_cleaning.txt"),
 ("RIE best in all but one case; LW linear wins once", "Bun, Bouchaud and Potters 2017", "in all cases but one (Minimum risk portfolio in Japan, where the LW linear shrinkage outperforms)", "bun_bouchaud_potters_2017_cleaning.txt"),
 ("Negative: no estimator beats sample covariance long-only with T > N", "Pantaleo et al. 2011", "when short selling is not allowed and T > N , the considered methods are unable to outperform the sample covariance in terms of realized risk", "pantaleo_2011_covariance.txt"),
 ("Sample covariance should not be used for optimization", "Ledoit and Wolf 2004 (JPM)", "nobody should be using the sample covariance matrix for the purpose of portfolio optimization", "ledoit_wolf_2004_honey.txt"),
 ("Shrinkage cuts tracking error, raises information ratio", "Ledoit and Wolf 2004 (JPM)", "shrinkage reduces tracking error relative to a benchmark index, and substantially increases the realized information ratio of the active portfolio manager", "ledoit_wolf_2004_honey.txt"),
 ("Optimal shrinkage intensity derivation (first-order condition)", "Ledoit and Wolf 2004 (JMVA)", "The first order condition is", "ledoit_wolf_2004_jmva.txt"),
 ("Nonlinear shrinkage dominates linear in stock backtests", "Ledoit and Wolf 2017", "In backtests with historical stock return data, it performs better than previous proposals and, in particular, it dominates linear shrinkage.", "ledoit_wolf_2017_goldilocks.txt"),
 ("Analytical NLS is fast and scales to p = 10,000", "Ledoit and Wolf 2020", "typically 1,000 times faster with the same accuracy, and accommodates covariance matrices of dimension up to 10, 000", "ledoit_wolf_analytical_nls.txt"),
 ("Oracle nonlinear formula is due to Ledoit and Péché", "Ledoit and Wolf 2020", "was first discovered by Ledoit and Péché (2011, Theorem 3)", "ledoit_wolf_analytical_nls.txt"),
 ("Largest estimates overstate their means (selection bias)", "Efron 2011", "The largest few of the zi ’s are likely to substantially overestimate their corresponding µi ’s, this being an example of selection bias, or regression to the mean.", "efron_2011_tweedie.txt"),
 ("Normal prior gives Tweedie posterior mean (1 - 1/V) z", "Efron 2011", "Tweedie’s formula becomes E{µ|z} = (1 − 1/V )z.", "efron_2011_tweedie.txt"),
 ("James-Stein replaces 1/V by an unbiased estimate", "Efron 2011", "substitutes the unbiased estimator", "efron_2011_tweedie.txt"),
 ("EB bias correction worked in Efron's examples", "Efron 2011", "the empirical Bayes bias correction lˆi0 was quite effective in both groups", "efron_2011_tweedie.txt"),
 ("Shrinkage toward the prior is what removes false discoveries", "Jensen, Kelly and Pedersen 2021 (WP)", "Reduction of false discoveries is achieved first by shrinking estimates toward the prior.", "jensen_kelly_pedersen_2021_replication.txt"),
 ("Hierarchical model shrinks toward cluster means", "Jensen, Kelly and Pedersen 2021 (WP)", "each alpha is shrunk toward its cluster mean (i.e., toward related factors), in addition to being shrunk toward the prior of zero.", "jensen_kelly_pedersen_2021_replication.txt"),
 ("Joint estimation increases discoveries", "Jensen, Kelly and Pedersen 2021 (WP)", "the increased precision from joint estimation has the opposite effect of enhancing statistical power and thus increases discoveries.", "jensen_kelly_pedersen_2021_replication.txt"),
 ("Factors replicate out-of-sample internationally", "Jensen, Kelly and Pedersen 2021 (WP)", "covering 93 countries", "jensen_kelly_pedersen_2021_replication.txt"),
 ("Naive inference on the selected best is biased", "Andrews, Kitagawa and McCloskey 2018 (WP)", "conventional estimates are biased and conventional confidence intervals are unreliable", "andrews_kitagawa_mccloskey_2018_winners.txt"),
 ("Winners problem covers the best backtested strategy", "Andrews, Kitagawa and McCloskey 2018 (WP)", "the best-performing investment strategy based on historical data", "andrews_kitagawa_mccloskey_2018_winners.txt"),
 ("EB shrinkage of published anomalies is only 10-15%", "Chen and Zimmermann (arXiv 2209.13623)", "the average correction (shrinkage) accounts for only 10 to 15 percent of in-sample mean returns", "chen_zimmermann_pubbias_eb.txt"),
 ("EB-selected data-mined strategies earn out of sample (gross)", "Chen and Dim (arXiv 2311.10685v3)", "earns out-of-sample returns of 5.7% per year over the 1983-2020 sample", "chen_dim_high_throughput.txt"),
 ("Negative: EB accuracy worse post-2004", "Chen and Dim (arXiv 2311.10685v3)", "Post-2004, EB has more difficulty with accuracy", "chen_dim_high_throughput.txt"),
 ("Popular multiple-testing methods miss OOS performers", "Chen and Dim (arXiv 2311.10685v3)", "Multiple testing methods popular in finance fail to identify most out-of-sample performers", "chen_dim_high_throughput.txt"),
 ("EB and FDR are strongly identified from published data", "Chen (arXiv 2204.10275)", "empirical Bayes shrinkage and the FDR) can be strongly identified", "chen_tstat_hurdles.txt"),
 ("Multiple-testing haircut is nonlinear", "Harvey and Liu 2015", "the multiple testing haircut is nonlinear. The highest Sharpe ratios are only moderately penalized, while the marginal Sharpe ratios are heavily penalized.", "harvey_liu_2015_backtesting.txt"),
 ("BMA improves out-of-sample prediction (non-finance)", "Hoeting et al. 1999", "In these examples, BMA provides improved out-ofsample predictive performance.", "hoeting_1999_bma.txt"),
 ("BMA beats model selection for stock-return predictability", "Avramov 2002 (2001 draft)", "the out-of-sample performance of the Bayesian approach is superior to that of model selection criteria", "avramov_2002_bma_draft.txt"),
 ("Shannon's uniqueness theorem for H", "Shannon 1948", "three above assumptions is of the form", "shannon_1948.txt"),
 ("Stock price changes near maximal entropy", "Fiedor 2014", "the average estimated entropy rate of daily price changes is equal to 2.04 (CTW) or 1.92 (Lempel-Ziv) out of the theoretical maximum of 2", "fiedor_2014_frequency_predictability.txt"),
 ("Predictability is not profitability", "Fiedor 2014", "We propose that predictability is a prerequisite for profitability", "fiedor_2014_frequency_predictability.txt"),
 ("LZ and CTW estimates agree", "Fiedor 2014", "both used algorithms are indeed highly correlated", "fiedor_2014_frequency_predictability.txt"),
 ("LZ estimator definition", "Fiedor 2014", "denotes the length of the shortest substring starting from time i that has not yet been observed prior to time i", "fiedor_2014_frequency_predictability.txt"),
 ("ApEn needs about 1000 points", "Pincus 1991 (abstract only)", "can classify complex systems, given at least 1000 data values", "pincus_1991_apen_pmc.html.txt"),
 ("ApEn is biased", "Delgado-Bonal and Marshak 2019", "Due to its theoretical definition, ApEn is a biased statistic", "delgado_bonal_2019_apen_sampen.txt"),
 ("SampEn excludes self-matches", "Delgado-Bonal and Marshak 2019", "SampEn does not allow self-counting while ApEn does", "delgado_bonal_2019_apen_sampen.txt"),
 ("ApEn/SampEn rankings flip with tolerance r", "Delgado-Bonal and Marshak 2019", "If we chose r = 0.08 σ , then the order of the randomness would be 1888 > 1878 > 1938", "delgado_bonal_2019_apen_sampen.txt"),
 ("KSG MI estimator is data efficient and low bias", "Kraskov, Stögbauer and Grassberger 2004", "adaptive (the resolution is higher where data are more numerous), and have minimal bias", "kraskov_2004_mi.txt"),
 ("MI has no direction", "Schreiber 2000", "symmetric under the exchange of I and J and therefore does not contain any directional sense", "schreiber_2000_transfer_entropy.txt"),
 ("TE is directional", "Schreiber 2000", "is now explicitly non-symmetric since it measures the degree of dependence of I on J and not vice versa", "schreiber_2000_transfer_entropy.txt"),
 ("Gaussian TE equals Granger causality up to factor 2", "Barnett, Barrett and Seth 2009", "Granger causality and transfer entropy are equivalent up to a factor of 2", "barnett_2009_granger_te.txt"),
 ("Markov bootstrap null for TE", "Dimpfl and Peter 2012 (WP)", "whereby the dependencies between J and I are destroyed, but the dynamics of the series J is retained", "dimpfl_peter_2012_te.txt"),
 ("TE p-values give the lead-lag timescale", "Bongiorno and Challet 2022 (arXiv 2206.10173)", "allows to measure the timescale at which information transfer is maximal and vanishes", "te_leadlag_pvalues_2022.txt"),
 ("Lead-lag predicts 60% of lagger moves", "Huth and Abergel 2014", "We reach 60% of accuracy when forecasting the next midquote variation of the lagger using only the past information of the leader", "huth_abergel_2014_leadlag.txt"),
 ("Negative: lead-lag does not pay the spread with market orders", "Huth and Abergel 2014", "a naive strategy based on market orders cannot make any profit of this effect because of the bid/ask spread", "huth_abergel_2014_leadlag.txt"),
 ("Lead-lag may still help market making", "Huth and Abergel 2014", "it could be used for other trading purposes such as market-making or best execution", "huth_abergel_2014_leadlag.txt"),
 ("Stock response to index-future move about 1 s", "Huth and Abergel 2014", "the average response time of a stock after a move of the index future is of the order of one second", "huth_abergel_2014_leadlag.txt"),
 ("Cloud GPU price: RTX 4090", "RunPod pricing page (fetched 2026-10-21)", "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr", "runpod_pricing.html.txt"),
 ("Cloud GPU price: A100 PCIe 80 GB", "RunPod pricing page (fetched 2026-10-21)", "A100 PCIe 80 GB VRAM 117 GB RAM 8 vCPUs $ 1.79 /hr", "runpod_pricing.html.txt"),
 ("Cloud GPU price: H100 PCIe", "RunPod pricing page (fetched 2026-10-21)", "H100 PCIe 80 GB VRAM 188 GB RAM 16 vCPUs $ 2.89 /hr", "runpod_pricing.html.txt"),
 ("Cloud GPU price: A100 PCIe 40 GB per GPU-hour", "Lambda pricing page (fetched 2026-10-21)", "NVIDIA A100 PCIe 40 GB 120 900 GiB 1 TiB SSD $1.99", "lambda_pricing.html.txt"),
]

def main():
    bad = 0
    lines = ["| # | Claim | Source | Verbatim quote | Saved file |", "|---|---|---|---|---|"]
    for i, (claim, src, q, f) in enumerate(ROWS, 1):
        ok = norm(q) in source_text(f)
        if not ok:
            bad += 1
            print("FAIL", i, f, q[:80], file=sys.stderr)
        lines.append(f"| {i} | {claim} | {src} | \"{q.replace('|', '/')}\" | `{f}` |")
    Path(__file__).with_name("C2_StatsRMT_evidence_table.md").write_text("\n".join(lines) + "\n")
    print(f"rows={len(ROWS)} failed={bad}")

if __name__ == "__main__":
    main()
