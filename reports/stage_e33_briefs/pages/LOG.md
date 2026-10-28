# Stage E.33 pages log

One row per saved page or derived view: URL (or local source), UTC time, sha256, file, note.

| url_or_source | utc | sha256 | file | note |
|---|---|---|---|---|
| local: reports/stage_e32_briefs/pages/M5a_validation/bailey_lopezdeprado_2014_dsr.pdf (sha256 ca4a1e834a2954b84eb560776e903329cd9cef318d458aadf6d67bc8166d10b5; E.32 fetched https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf 2026-10-27T06:05:48Z) | 2026-10-27T22:16:26Z | 3fd93ac0c65ecb383d164843e2b7485652e86bd43007ec434b150ccdb35e9f82 | StatsCost/dsr2014_p9_numerical_example_inputs.png | StatsCostCoder: pdftoppm -r 170 page 9, cropped; the example inputs are Cambria Math glyphs that pdftotext drops; read from the rendered page (N = 100, V = 1/2, T=1250, skew -3, kurt 10) |
| local: same PDF | 2026-10-27T22:16:26Z | 07c18f501dd89ba713e514e64d9cd011395bb4bc000cddd23d4d2a4b4a5c8527 | StatsCost/dsr2014_p10_numerical_example_outputs.png | StatsCostCoder: page 10, cropped; SR0 ~ 0.1132, DSR ~ 0.9004, N=46 0.9505, normal N=88 0.9505 |
| local: reports/stage_e32_briefs/pages/M5a_validation/bailey_borwein_ldp_zhu_2017_pbo.pdf (sha256 d8bfbadaaedb430d9dec929646d92f3580fdf18238f34121ae7738fa1c69a63d; E.32 fetched https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf 2026-10-27T06:05:50Z) | 2026-10-27T22:16:26Z | 6e5978cc314fc45907265aa0e9423a6d87dbb26ae069c6608ac4f20dc9aaf75d | StatsCost/pbo2017_p11_eq2_3_combinations.png | StatsCostCoder: pdftoppm -r 150 page 11, cropped; confirms the printed "12, 780" (Eq. 2.3 gives 12,870) is in the PDF, not a text-extraction error |
