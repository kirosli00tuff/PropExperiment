# Stage E.5 Task C3: NGS release check, confirmation window 2019-05-06..2024-02-29

Worker: ReleaseChecker-OpusMed, 2026-09-27 12:36-13:30 PDT. Rows checked: every row of `NGS` in strategy/members/k4/_releases.py dated 2019-05-06..2024-02-29 (252 rows; all 252 match reports/stage_e2b_release_calendar.json; 251 were [unverified] there). Rules: reports/stage_e0_catalog_K4.md lines 135-170 (C9). Full rows: reports/stage_e5_ngs_check.json. The lead filters to S_NG and decides drops/corrections; this report draws no conclusion about any member.

## Method

- Actual publication: for each row, the first Wayback capture of ir.eia.gov/ngs/ngs.html taken after the release and before the next one (CDX listing saved), fetched in `id_` form; the page's own "Released: <date> at <time> | Next Release: <date>" line was parsed. The served capture timestamp was recorded (8 were served from a capture seconds to hours after the requested one; all still inside the window and stating the release). For the two weeks without such a capture, EIA's Natural Gas Weekly Update (NGWU) page for that date (saved by E.2b) was used.
- Schedule: ir.eia.gov/ngs/schedule.html, one capture per content digest 2019-01..2024-07 from the CDX listing (21 captures, including catalog captures 20190111124957, 20200128214849, 20210104203613, 20220114160745, 20230210074654, 20240607000738). For each release the LAST capture before the release was mapped to its saved page by digest.

## Counts per verdict

| verdict | count |
|---|---|
| keep | 247 |
| drop_actual_differs | 5 |
| updated | 0 |
| unverifiable | 0 |

Per year:

| year | rows | keep | drop_actual_differs | updated | unverifiable |
|---|---|---|---|---|---|
| 2019 | 34 | 33 | 1 | 0 | 0 |
| 2020 | 53 | 51 | 2 | 0 | 0 |
| 2021 | 52 | 51 | 1 | 0 | 0 |
| 2022 | 52 | 52 | 0 | 0 | 0 |
| 2023 | 52 | 51 | 1 | 0 | 0 |
| 2024 | 9 | 9 | 0 | 0 | 0 |

time_basis: stated 250, schedule 1 (2020-02-13: date verified via NGWU, time from the schedule), none 1 (2023-11-09: no release).

## Every non-keep row

| date (table) | table ET (CT) | schedule entry (last capture before release) | actual | verdict | source |
|---|---|---|---|---|---|
| 2019-12-26 | 10:30 (09:30) | exception row for this week: 2019-12-27 Friday 10:30 ET (no row for 2019-12-26); capture 20191129075548 | 2019-12-27 10:30 | drop_actual_differs | https://web.archive.org/web/20191228020346/https://ir.eia.gov/ngs/ngs.html (saved data/vendor/release_pages/e5/ngs_week_2019-12-26_20191228020346.html): "for week ending December 20, 2019 | Released: December 27, 2019 at 10:30 a.m. | Next Release: January 3, 2 |
| 2020-01-02 | 10:30 (09:30) | exception row for this week: 2020-01-03 Friday 10:30 ET (no row for 2020-01-02); capture 20191229152905 | 2020-01-03 10:30 | drop_actual_differs | https://web.archive.org/web/20200104053637/https://ir.eia.gov/ngs/ngs.html (saved data/vendor/release_pages/e5/ngs_week_2020-01-02_20200104053637.html): "for week ending December 27, 2019 | Released: January 3, 2020 at 10:30 a.m. | Next Release: January 9, 202 |
| 2020-11-12 | 10:30 (09:30) | exception row for this week: 2020-11-13 Friday 10:30 ET (no row for 2020-11-12); capture 20201031145739 | 2020-11-13 10:30 | drop_actual_differs | https://web.archive.org/web/20201113155744/https://ir.eia.gov/ngs/ngs.html (saved data/vendor/release_pages/e5/ngs_week_2020-11-12_20201113155744.html): "for week ending November 6, 2020 | Released: November 13, 2020 at 10:30 a.m. | Next Release: November 19,  |
| 2021-01-21 | 10:30 (09:30) | exception row for this week: 2021-01-22 Friday 10:30 ET (no row for 2021-01-21); capture 20210118172825 | 2021-01-22 10:30 | drop_actual_differs | https://web.archive.org/web/20210122171117/https://ir.eia.gov/ngs/ngs.html (saved data/vendor/release_pages/e5/ngs_week_2021-01-21_20210122171117.html): "for week ending January 15, 2021 | Released: January 22, 2021 at 10:30 a.m. | Next Release: January 28, 20 |
| 2023-11-09 | 10:30 (09:30) | standard: 10:30 a.m. (Eastern time) on Thursdays (no exception row for this week); capture 20230708153227 | no release  | drop_actual_differs | https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2023/11_09/ (saved by E.2b, data/vendor/release_pages/eia/ngwu/ngwu_2023_11_09.html): NGWU "Release date: November 9, 2023"; Storage section: "EIA will not publish weekly natural gas inventories data this w |

Notes for the lead on these rows (facts, no decision):
- 2019-12-26, 2020-01-02, 2020-11-12, 2021-01-21: EIA released on the day after the table date (Friday 10:30 ET), exactly as the schedule capture before each release listed (rows 12/27/2019, 1/3/2020, 11/13/2020, 1/22/2021). The frozen table and calendar carry the standing-Thursday date instead, and hold no row for the actual date. The mismatch is between the table and EIA, not between EIA's schedule and its publication. Whether to drop these or correct them is for the lead.
- 2023-11-09: no WNGSR that week. NGWU 2023-11-09: "EIA will not publish weekly natural gas inventories data this week. Please see our October 19 press release for more detail." The WNGSR of 2023-11-02 states "Next Release: November 16, 2023". The schedule captures (20230708153227, 20231124164907) show no exception for the week.

## "(Updated)" markers

None. No schedule capture 2019-01-11..2024-07-20 contains "(Updated)". Mid-year schedule changes without the marker (none alters a verdict, since each shows in a capture well before the release):

| release | change | latest capture without | earliest capture showing |
|---|---|---|---|
| 2019-07-03 | row "7/5/2019 Friday 10:30 a.m." replaced by "7/3/2019 Wednesday 12:00 p.m." | 20190510201330 (digest VGTIZ, saved as 20190111124957) | 20190613010741 |
| 2020-12-23 | row "12/23/2020 Wednesday 12:00 p.m." added | 20201121084027 | 20201217153516 |
| 2020-11-13 / 2020-11-25 | rows added to the table for 2020 | 20191116004327 (digest YAMY6, saved as 20190714105626) | 20191129075548 |

Holiday/exception rows confirmed as keep (actual equals the exception row): 2019-07-03 Wed 12:00, 2019-11-27 Wed 12:00, 2020-11-25 Wed 12:00, 2020-12-23 Wed 12:00, 2021-11-10 Wed 12:00, 2021-11-24 Wed 12:00, 2022-11-23 Wed 12:00, 2023-07-07 Fri 10:30, 2023-11-22 Wed 12:00 (ET).

## Schedule captures used

| capture | effective | exception rows | saved |
|---|---|---|---|
| 20190111124957 | 20190111124957 | 12 | data/vendor/release_pages/e5/ngs_sched_20190111124957.html |
| 20190613010741 | 20190613010741 | 12 | data/vendor/release_pages/e5/ngs_sched_20190613010741.html |
| 20190714105626 | 20190714105626 | 12 | data/vendor/release_pages/e5/ngs_sched_20190714105626.html |
| 20191129075548 | 20191129075548 | 7 | data/vendor/release_pages/e5/ngs_sched_20191129075548.html |
| 20191229152905 | 20191229152905 | 7 | data/vendor/release_pages/e5/ngs_sched_20191229152905.html |
| 20200128214849 | 20200128214849 | 7 | data/vendor/release_pages/e5/ngs_sched_20200128214849.html |
| 20201121084027 | 20201121084027 | 6 | data/vendor/release_pages/e5/ngs_sched_20201121084027.html |
| 20201217153516 | 20201217153516 | 7 | data/vendor/release_pages/e5/ngs_sched_20201217153516.html |
| 20201224001827 | 20201224001827 | 7 | data/vendor/release_pages/e5/ngs_sched_20201224001827.html |
| 20210104203613 | 20210104203613 | 7 | data/vendor/release_pages/e5/ngs_sched_20210104203613.html |
| 20210319031602 | 20210319031602 | 7 | data/vendor/release_pages/e5/ngs_sched_20210319031602.html |
| 20211102183454 | 20211102183454 | 4 | data/vendor/release_pages/e5/ngs_sched_20211102183454.html |
| 20211111015940 | 20211111015940 | 4 | data/vendor/release_pages/e5/ngs_sched_20211111015940.html |
| 20211216230557 | 20211216230557 | 4 | data/vendor/release_pages/e5/ngs_sched_20211216230557.html |
| 20220114160745 | 20220114160745 | 4 | data/vendor/release_pages/e5/ngs_sched_20220114160745.html |
| 20221106051100 | 20221106051100 | 6 | data/vendor/release_pages/e5/ngs_sched_20221106051100.html |
| 20230210074654 | 20230210074654 | 6 | data/vendor/release_pages/e5/ngs_sched_20230210074654.html |
| 20230708153227 | 20230708153227 | 6 | data/vendor/release_pages/e5/ngs_sched_20230708153227.html |
| 20231208131519 | 20231208131519 | 11 | data/vendor/release_pages/e5/ngs_sched_20231208131519.html |
| 20240607000738 | 20240607000738 | 11 | data/vendor/release_pages/e5/ngs_sched_20240607000738.html |
| 20240720000603 | 20240720000603 | 11 | data/vendor/release_pages/e5/ngs_sched_20240720000603.html |

## Sources

300 sources (URL, effective capture, fetch time PDT, saved path, sha256 in the JSON `sources`). Every URL:

- http://web.archive.org/web/20190510024751id_/http://ir.eia.gov/ngs/ngs.html (effective 20190510024751; data/vendor/release_pages/e5/ngs_week_2019-05-09_20190510024751.html)
- http://web.archive.org/web/20190517062601id_/http://ir.eia.gov/ngs/ngs.html (effective 20190517062601; data/vendor/release_pages/e5/ngs_week_2019-05-16_20190517062601.html)
- http://web.archive.org/web/20190524095505id_/http://ir.eia.gov/ngs/ngs.html (effective 20190524095505; data/vendor/release_pages/e5/ngs_week_2019-05-23_20190524095505.html)
- http://web.archive.org/web/20190531140707id_/http://ir.eia.gov/ngs/ngs.html (effective 20190531140707; data/vendor/release_pages/e5/ngs_week_2019-05-30_20190531140707.html)
- http://web.archive.org/web/20190606173659id_/http://ir.eia.gov/ngs/ngs.html (effective 20190606173659; data/vendor/release_pages/e5/ngs_week_2019-06-06_20190606173659.html)
- http://web.archive.org/web/20190613205742id_/http://ir.eia.gov/ngs/ngs.html (effective 20190613205742; data/vendor/release_pages/e5/ngs_week_2019-06-13_20190613205742.html)
- http://web.archive.org/web/20190620231500id_/http://ir.eia.gov/ngs/ngs.html (effective 20190620231500; data/vendor/release_pages/e5/ngs_week_2019-06-20_20190620231500.html)
- http://web.archive.org/web/20190628032655id_/http://ir.eia.gov/ngs/ngs.html (effective 20190628032655; data/vendor/release_pages/e5/ngs_week_2019-06-27_20190628032655.html)
- http://web.archive.org/web/20190704044001id_/http://ir.eia.gov/ngs/ngs.html (effective 20190704044001; data/vendor/release_pages/e5/ngs_week_2019-07-03_20190704044001.html)
- http://web.archive.org/web/20190712071650id_/http://ir.eia.gov/ngs/ngs.html (effective 20190712071650; data/vendor/release_pages/e5/ngs_week_2019-07-11_20190712071650.html)
- http://web.archive.org/web/20190719101313id_/http://ir.eia.gov/ngs/ngs.html (effective 20190719101313; data/vendor/release_pages/e5/ngs_week_2019-07-18_20190719101313.html)
- http://web.archive.org/web/20190726140549id_/http://ir.eia.gov/ngs/ngs.html (effective 20190726140549; data/vendor/release_pages/e5/ngs_week_2019-07-25_20190726140549.html)
- http://web.archive.org/web/20190801232040id_/http://ir.eia.gov/ngs/ngs.html (effective 20190801232040; data/vendor/release_pages/e5/ngs_week_2019-08-01_20190801232040.html)
- http://web.archive.org/web/20190809033344id_/http://ir.eia.gov/ngs/ngs.html (effective 20190809033344; data/vendor/release_pages/e5/ngs_week_2019-08-08_20190809033344.html)
- http://web.archive.org/web/20190816061437id_/http://ir.eia.gov/ngs/ngs.html (effective 20190816061437; data/vendor/release_pages/e5/ngs_week_2019-08-15_20190816061437.html)
- http://web.archive.org/web/20190823093548id_/http://ir.eia.gov/ngs/ngs.html (effective 20190823093548; data/vendor/release_pages/e5/ngs_week_2019-08-22_20190823093548.html)
- https://web.archive.org/web/20190830130415id_/http://ir.eia.gov/ngs/ngs.html (effective 20190830130415; data/vendor/release_pages/e5/ngs_week_2019-08-29_20190830130415.html)
- https://web.archive.org/web/20190905154648id_/http://ir.eia.gov/ngs/ngs.html (effective 20190905154648; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190905154648.html)
- https://web.archive.org/web/20190906164010id_/http://ir.eia.gov/ngs/ngs.html (effective 20190906164010; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190906164010.html)
- https://web.archive.org/web/20190907165142id_/http://ir.eia.gov/ngs/ngs.html (effective 20190907165142; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190907165142.html)
- https://web.archive.org/web/20190908170531id_/http://ir.eia.gov/ngs/ngs.html (effective 20190908170531; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190908170531.html)
- https://web.archive.org/web/20190909172831id_/http://ir.eia.gov/ngs/ngs.html (effective 20190909172831; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190909172831.html)
- https://web.archive.org/web/20190910174335id_/http://ir.eia.gov/ngs/ngs.html (effective 20190910174335; data/vendor/release_pages/e5/ngs_week_2019-09-05_20190910174335.html)
- https://web.archive.org/web/20190912190750id_/http://ir.eia.gov/ngs/ngs.html (effective 20190912190750; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190912190750.html)
- https://web.archive.org/web/20190913192903id_/http://ir.eia.gov/ngs/ngs.html (effective 20190913192903; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190913192903.html)
- https://web.archive.org/web/20190914194852id_/http://ir.eia.gov/ngs/ngs.html (effective 20190914194852; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190914194852.html)
- https://web.archive.org/web/20190915202335id_/http://ir.eia.gov/ngs/ngs.html (effective 20190915202335; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190915202335.html)
- https://web.archive.org/web/20190916210228id_/http://ir.eia.gov/ngs/ngs.html (effective 20190916210228; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190916210228.html)
- https://web.archive.org/web/20190917142728id_/http://ir.eia.gov/ngs/ngs.html (effective 20190917142728; data/vendor/release_pages/e5/ngs_week_2019-09-12_20190917142728.html)
- https://web.archive.org/web/20190919221122id_/http://ir.eia.gov/ngs/ngs.html (effective 20190919221122; data/vendor/release_pages/e5/ngs_week_2019-09-19_20190919221122.html)
- https://web.archive.org/web/20190920222824id_/http://ir.eia.gov/ngs/ngs.html (effective 20190920222824; data/vendor/release_pages/e5/ngs_week_2019-09-19_20190920222824.html)
- https://web.archive.org/web/20190921225853id_/http://ir.eia.gov/ngs/ngs.html (effective 20190921225853; data/vendor/release_pages/e5/ngs_week_2019-09-19_20190921225853.html)
- https://web.archive.org/web/20190927020110id_/http://ir.eia.gov/ngs/ngs.html (effective 20190927020110; data/vendor/release_pages/e5/ngs_week_2019-09-26_20190927020110.html)
- https://web.archive.org/web/20191004064157id_/http://ir.eia.gov/ngs/ngs.html (effective 20191004064157; data/vendor/release_pages/e5/ngs_week_2019-10-03_20191004064157.html)
- https://web.archive.org/web/20191011112848id_/http://ir.eia.gov/ngs/ngs.html (effective 20191011112848; data/vendor/release_pages/e5/ngs_week_2019-10-10_20191011112848.html)
- https://web.archive.org/web/20191017155157id_/http://ir.eia.gov/ngs/ngs.html (effective 20191017155157; data/vendor/release_pages/e5/ngs_week_2019-10-17_20191017155157.html)
- https://web.archive.org/web/20191024192833id_/http://ir.eia.gov/ngs/ngs.html (effective 20191024192833; data/vendor/release_pages/e5/ngs_week_2019-10-24_20191024192833.html)
- https://web.archive.org/web/20191031182242id_/http://ir.eia.gov/ngs/ngs.html (effective 20191031182242; data/vendor/release_pages/e5/ngs_week_2019-10-31_20191031182242.html)
- https://web.archive.org/web/20191108073126id_/http://ir.eia.gov/ngs/ngs.html (effective 20191108073126; data/vendor/release_pages/e5/ngs_week_2019-11-07_20191108073126.html)
- https://web.archive.org/web/20191114224622id_/http://ir.eia.gov/ngs/ngs.html (effective 20191114224622; data/vendor/release_pages/e5/ngs_week_2019-11-14_20191114224622.html)
- https://web.archive.org/web/20191122024645id_/http://ir.eia.gov/ngs/ngs.html (effective 20191122024645; data/vendor/release_pages/e5/ngs_week_2019-11-21_20191122024645.html)
- https://web.archive.org/web/20191128062926id_/http://ir.eia.gov/ngs/ngs.html (effective 20191128062926; data/vendor/release_pages/e5/ngs_week_2019-11-27_20191128062926.html)
- https://web.archive.org/web/20191206104258id_/http://ir.eia.gov/ngs/ngs.html (effective 20191206104258; data/vendor/release_pages/e5/ngs_week_2019-12-05_20191206104258.html)
- https://web.archive.org/web/20191212163039id_/http://ir.eia.gov/ngs/ngs.html (effective 20191212163039; data/vendor/release_pages/e5/ngs_week_2019-12-12_20191212163039.html)
- https://web.archive.org/web/20191219184034id_/http://ir.eia.gov/ngs/ngs.html (effective 20191219184034; data/vendor/release_pages/e5/ngs_week_2019-12-19_20191219184034.html)
- https://web.archive.org/web/20191227011324id_/http://ir.eia.gov/ngs/ngs.html (effective 20191227011324; data/vendor/release_pages/e5/ngs_week_2019-12-26_20191227011324.html)
- https://web.archive.org/web/20191228020346id_/http://ir.eia.gov/ngs/ngs.html (effective 20191228020346; data/vendor/release_pages/e5/ngs_week_2019-12-26_20191228020346.html)
- https://web.archive.org/web/20200103052454id_/http://ir.eia.gov/ngs/ngs.html (effective 20200103052454; data/vendor/release_pages/e5/ngs_week_2020-01-02_20200103052454.html)
- https://web.archive.org/web/20200104053637id_/http://ir.eia.gov/ngs/ngs.html (effective 20200104053637; data/vendor/release_pages/e5/ngs_week_2020-01-02_20200104053637.html)
- https://web.archive.org/web/20200109190702id_/http://ir.eia.gov/ngs/ngs.html (effective 20200109190702; data/vendor/release_pages/e5/ngs_week_2020-01-09_20200109190702.html)
- https://web.archive.org/web/20200117000002id_/http://ir.eia.gov/ngs/ngs.html (effective 20200117000002; data/vendor/release_pages/e5/ngs_week_2020-01-16_20200117000002.html)
- https://web.archive.org/web/20200124215955id_/http://ir.eia.gov/ngs/ngs.html (effective 20200124215955; data/vendor/release_pages/e5/ngs_week_2020-01-23_20200124215955.html)
- https://web.archive.org/web/20200131024018id_/http://ir.eia.gov/ngs/ngs.html (effective 20200131024018; data/vendor/release_pages/e5/ngs_week_2020-01-30_20200131024018.html)
- https://web.archive.org/web/20200208103108id_/http://ir.eia.gov/ngs/ngs.html (effective 20200208103108; data/vendor/release_pages/e5/ngs_week_2020-02-06_20200208103108.html)
- https://web.archive.org/web/20200221001756id_/http://ir.eia.gov/ngs/ngs.html (effective 20200221001756; data/vendor/release_pages/e5/ngs_week_2020-02-20_20200221001756.html)
- https://web.archive.org/web/20200228031619id_/http://ir.eia.gov/ngs/ngs.html (effective 20200228031619; data/vendor/release_pages/e5/ngs_week_2020-02-27_20200228031619.html)
- https://web.archive.org/web/20200306064633id_/http://ir.eia.gov/ngs/ngs.html (effective 20200306064633; data/vendor/release_pages/e5/ngs_week_2020-03-05_20200306064633.html)
- https://web.archive.org/web/20200313111053id_/http://ir.eia.gov/ngs/ngs.html (effective 20200313111053; data/vendor/release_pages/e5/ngs_week_2020-03-12_20200313111053.html)
- https://web.archive.org/web/20200320135340id_/http://ir.eia.gov/ngs/ngs.html (effective 20200320135340; data/vendor/release_pages/e5/ngs_week_2020-03-19_20200320135340.html)
- https://web.archive.org/web/20200326163511id_/http://ir.eia.gov/ngs/ngs.html (effective 20200326163511; data/vendor/release_pages/e5/ngs_week_2020-03-26_20200326163511.html)
- https://web.archive.org/web/20200402221026id_/http://ir.eia.gov/ngs/ngs.html (effective 20200402221026; data/vendor/release_pages/e5/ngs_week_2020-04-02_20200402221026.html)
- https://web.archive.org/web/20200410022108id_/http://ir.eia.gov/ngs/ngs.html (effective 20200410022108; data/vendor/release_pages/e5/ngs_week_2020-04-09_20200410022108.html)
- https://web.archive.org/web/20200417054148id_/http://ir.eia.gov/ngs/ngs.html (effective 20200417054148; data/vendor/release_pages/e5/ngs_week_2020-04-16_20200417054148.html)
- https://web.archive.org/web/20200423222041id_/http://ir.eia.gov/ngs/ngs.html (effective 20200423222041; data/vendor/release_pages/e5/ngs_week_2020-04-23_20200423222041.html)
- https://web.archive.org/web/20200430145347id_/http://ir.eia.gov/ngs/ngs.html (effective 20200430145347; data/vendor/release_pages/e5/ngs_week_2020-04-30_20200430145347.html)
- https://web.archive.org/web/20200507182454id_/http://ir.eia.gov/ngs/ngs.html (effective 20200507182454; data/vendor/release_pages/e5/ngs_week_2020-05-07_20200507182454.html)
- https://web.archive.org/web/20200514230935id_/http://ir.eia.gov/ngs/ngs.html (effective 20200514230935; data/vendor/release_pages/e5/ngs_week_2020-05-14_20200514230935.html)
- https://web.archive.org/web/20200522034359id_/http://ir.eia.gov/ngs/ngs.html (effective 20200522034359; data/vendor/release_pages/e5/ngs_week_2020-05-21_20200522034359.html)
- https://web.archive.org/web/20200529085204id_/http://ir.eia.gov/ngs/ngs.html (effective 20200529085204; data/vendor/release_pages/e5/ngs_week_2020-05-28_20200529085204.html)
- https://web.archive.org/web/20200604151755id_/http://ir.eia.gov/ngs/ngs.html (effective 20200604151755; data/vendor/release_pages/e5/ngs_week_2020-06-04_20200604151755.html)
- https://web.archive.org/web/20200611172424id_/http://ir.eia.gov/ngs/ngs.html (effective 20200611172424; data/vendor/release_pages/e5/ngs_week_2020-06-11_20200611172424.html)
- https://web.archive.org/web/20200618164905id_/http://ir.eia.gov/ngs/ngs.html (effective 20200618164905; data/vendor/release_pages/e5/ngs_week_2020-06-18_20200618164905.html)
- https://web.archive.org/web/20200626005424id_/http://ir.eia.gov/ngs/ngs.html (effective 20200626005424; data/vendor/release_pages/e5/ngs_week_2020-06-25_20200626005424.html)
- https://web.archive.org/web/20200703042126id_/http://ir.eia.gov/ngs/ngs.html (effective 20200703042126; data/vendor/release_pages/e5/ngs_week_2020-07-02_20200703042126.html)
- https://web.archive.org/web/20200710182003id_/http://ir.eia.gov/ngs/ngs.html (effective 20200710182003; data/vendor/release_pages/e5/ngs_week_2020-07-09_20200710182003.html)
- https://web.archive.org/web/20200716224746id_/http://ir.eia.gov/ngs/ngs.html (effective 20200716224746; data/vendor/release_pages/e5/ngs_week_2020-07-16_20200716224746.html)
- https://web.archive.org/web/20200724030346id_/http://ir.eia.gov/ngs/ngs.html (effective 20200724030346; data/vendor/release_pages/e5/ngs_week_2020-07-23_20200724030346.html)
- https://web.archive.org/web/20200731074808id_/http://ir.eia.gov/ngs/ngs.html (effective 20200731074808; data/vendor/release_pages/e5/ngs_week_2020-07-30_20200731074808.html)
- https://web.archive.org/web/20200807115816id_/http://ir.eia.gov/ngs/ngs.html (effective 20200807115816; data/vendor/release_pages/e5/ngs_week_2020-08-06_20200807115816.html)
- https://web.archive.org/web/20200813155342id_/http://ir.eia.gov/ngs/ngs.html (effective 20200813155342; data/vendor/release_pages/e5/ngs_week_2020-08-13_20200813155342.html)
- https://web.archive.org/web/20200820192348id_/http://ir.eia.gov/ngs/ngs.html (effective 20200820192348; data/vendor/release_pages/e5/ngs_week_2020-08-20_20200820192348.html)
- https://web.archive.org/web/20200827223828id_/http://ir.eia.gov/ngs/ngs.html (effective 20200827223828; data/vendor/release_pages/e5/ngs_week_2020-08-27_20200827223828.html)
- https://web.archive.org/web/20200904015353id_/http://ir.eia.gov/ngs/ngs.html (effective 20200904015353; data/vendor/release_pages/e5/ngs_week_2020-09-03_20200904015353.html)
- https://web.archive.org/web/20200910190702id_/http://ir.eia.gov/ngs/ngs.html (effective 20200910190702; data/vendor/release_pages/e5/ngs_week_2020-09-10_20200910190702.html)
- https://web.archive.org/web/20200917192603id_/http://ir.eia.gov/ngs/ngs.html (effective 20200917192603; data/vendor/release_pages/e5/ngs_week_2020-09-17_20200917192603.html)
- https://web.archive.org/web/20200925060517id_/http://ir.eia.gov/ngs/ngs.html (effective 20200925060517; data/vendor/release_pages/e5/ngs_week_2020-09-24_20200925060517.html)
- https://web.archive.org/web/20201002100347id_/http://ir.eia.gov/ngs/ngs.html (effective 20201002100347; data/vendor/release_pages/e5/ngs_week_2020-10-01_20201002100347.html)
- https://web.archive.org/web/20201009140436id_/http://ir.eia.gov/ngs/ngs.html (effective 20201009140436; data/vendor/release_pages/e5/ngs_week_2020-10-08_20201009140436.html)
- https://web.archive.org/web/20201015182125id_/http://ir.eia.gov/ngs/ngs.html (effective 20201015182125; data/vendor/release_pages/e5/ngs_week_2020-10-15_20201015182125.html)
- https://web.archive.org/web/20201022230812id_/http://ir.eia.gov/ngs/ngs.html (effective 20201022230812; data/vendor/release_pages/e5/ngs_week_2020-10-22_20201022230812.html)
- https://web.archive.org/web/20201030030459id_/http://ir.eia.gov/ngs/ngs.html (effective 20201030030459; data/vendor/release_pages/e5/ngs_week_2020-10-29_20201030030459.html)
- https://web.archive.org/web/20201105153134id_/http://ir.eia.gov/ngs/ngs.html (effective 20201105153134; data/vendor/release_pages/e5/ngs_week_2020-11-05_20201105153134.html)
- https://web.archive.org/web/20201113155744id_/http://ir.eia.gov/ngs/ngs.html (effective 20201113155744; data/vendor/release_pages/e5/ngs_week_2020-11-12_20201113155744.html)
- https://web.archive.org/web/20201119153105id_/http://ir.eia.gov/ngs/ngs.html (effective 20201119153105; data/vendor/release_pages/e5/ngs_week_2020-11-19_20201119153105.html)
- https://web.archive.org/web/20201125170101id_/http://ir.eia.gov/ngs/ngs.html (effective 20201125170101; data/vendor/release_pages/e5/ngs_week_2020-11-25_20201125170101.html)
- https://web.archive.org/web/20201203153134id_/http://ir.eia.gov/ngs/ngs.html (effective 20201203153134; data/vendor/release_pages/e5/ngs_week_2020-12-03_20201203153134.html)
- https://web.archive.org/web/20201210153101id_/http://ir.eia.gov/ngs/ngs.html (effective 20201210153101; data/vendor/release_pages/e5/ngs_week_2020-12-10_20201210153101.html)
- https://web.archive.org/web/20201217153711id_/http://ir.eia.gov/ngs/ngs.html (effective 20201217153711; data/vendor/release_pages/e5/ngs_week_2020-12-17_20201217153711.html)
- https://web.archive.org/web/20201223150316id_/http://ir.eia.gov/ngs/ngs.html (effective 20201223150316; data/vendor/release_pages/e5/ngs_week_2020-12-23_20201223150316.html)
- https://web.archive.org/web/20201223155858id_/http://ir.eia.gov/ngs/ngs.html (effective 20201223155858; data/vendor/release_pages/e5/ngs_week_2020-12-23_20201223155858.html)
- https://web.archive.org/web/20201223170104id_/http://ir.eia.gov/ngs/ngs.html (effective 20201223170104; data/vendor/release_pages/e5/ngs_week_2020-12-23_20201223170104.html)
- https://web.archive.org/web/20201231153147id_/https://ir.eia.gov/ngs/ngs.html (effective 20201231153147; data/vendor/release_pages/e5/ngs_week_2020-12-31_20201231153147.html)
- https://web.archive.org/web/20210107153207id_/https://ir.eia.gov/ngs/ngs.html (effective 20210107153207; data/vendor/release_pages/e5/ngs_week_2021-01-07_20210107153207.html)
- https://web.archive.org/web/20210114153113id_/https://ir.eia.gov/ngs/ngs.html (effective 20210114153113; data/vendor/release_pages/e5/ngs_week_2021-01-14_20210114153113.html)
- https://web.archive.org/web/20210121195639id_/http://ir.eia.gov/ngs/ngs.html (effective 20210121195641; data/vendor/release_pages/e5/ngs_week_2021-01-21_20210121195639.html)
- https://web.archive.org/web/20210121195641id_/https://ir.eia.gov/ngs/ngs.html (effective 20210121195641; data/vendor/release_pages/e5/ngs_week_2021-01-21_20210121195641.html)
- https://web.archive.org/web/20210122171117id_/https://ir.eia.gov/ngs/ngs.html (effective 20210122171117; data/vendor/release_pages/e5/ngs_week_2021-01-21_20210122171117.html)
- https://web.archive.org/web/20210128153140id_/https://ir.eia.gov/ngs/ngs.html (effective 20210128153140; data/vendor/release_pages/e5/ngs_week_2021-01-28_20210128153140.html)
- https://web.archive.org/web/20210204153116id_/https://ir.eia.gov/ngs/ngs.html (effective 20210204153116; data/vendor/release_pages/e5/ngs_week_2021-02-04_20210204153116.html)
- https://web.archive.org/web/20210211153100id_/https://ir.eia.gov/ngs/ngs.html (effective 20210211153100; data/vendor/release_pages/e5/ngs_week_2021-02-11_20210211153100.html)
- https://web.archive.org/web/20210218153116id_/https://ir.eia.gov/ngs/ngs.html (effective 20210218153116; data/vendor/release_pages/e5/ngs_week_2021-02-18_20210218153116.html)
- https://web.archive.org/web/20210226075947id_/https://ir.eia.gov/ngs/ngs.html (effective 20210226075947; data/vendor/release_pages/e5/ngs_week_2021-02-25_20210226075947.html)
- https://web.archive.org/web/20210304153112id_/https://ir.eia.gov/ngs/ngs.html (effective 20210304153112; data/vendor/release_pages/e5/ngs_week_2021-03-04_20210304153112.html)
- https://web.archive.org/web/20210311153103id_/https://ir.eia.gov/ngs/ngs.html (effective 20210311153103; data/vendor/release_pages/e5/ngs_week_2021-03-11_20210311153103.html)
- https://web.archive.org/web/20210318143126id_/https://ir.eia.gov/ngs/ngs.html (effective 20210318143126; data/vendor/release_pages/e5/ngs_week_2021-03-18_20210318143126.html)
- https://web.archive.org/web/20210325143442id_/https://ir.eia.gov/ngs/ngs.html (effective 20210325143442; data/vendor/release_pages/e5/ngs_week_2021-03-25_20210325143442.html)
- https://web.archive.org/web/20210401143148id_/https://ir.eia.gov/ngs/ngs.html (effective 20210401143148; data/vendor/release_pages/e5/ngs_week_2021-04-01_20210401143148.html)
- https://web.archive.org/web/20210408143108id_/https://ir.eia.gov/ngs/ngs.html (effective 20210408143108; data/vendor/release_pages/e5/ngs_week_2021-04-08_20210408143108.html)
- https://web.archive.org/web/20210415143221id_/https://ir.eia.gov/ngs/ngs.html (effective 20210415143221; data/vendor/release_pages/e5/ngs_week_2021-04-15_20210415143221.html)
- https://web.archive.org/web/20210422143250id_/https://ir.eia.gov/ngs/ngs.html (effective 20210422143250; data/vendor/release_pages/e5/ngs_week_2021-04-22_20210422143250.html)
- https://web.archive.org/web/20210429143113id_/https://ir.eia.gov/ngs/ngs.html (effective 20210429143113; data/vendor/release_pages/e5/ngs_week_2021-04-29_20210429143113.html)
- https://web.archive.org/web/20210506155641id_/https://ir.eia.gov/ngs/ngs.html (effective 20210506155641; data/vendor/release_pages/e5/ngs_week_2021-05-06_20210506155641.html)
- https://web.archive.org/web/20210513143556id_/https://ir.eia.gov/ngs/ngs.html (effective 20210513143556; data/vendor/release_pages/e5/ngs_week_2021-05-13_20210513143556.html)
- https://web.archive.org/web/20210520144136id_/https://ir.eia.gov/ngs/ngs.html (effective 20210520144136; data/vendor/release_pages/e5/ngs_week_2021-05-20_20210520144136.html)
- https://web.archive.org/web/20210530215239id_/http://ir.eia.gov/ngs/ngs.html (effective 20210530215240; data/vendor/release_pages/e5/ngs_week_2021-05-27_20210530215239.html)
- https://web.archive.org/web/20210603143334id_/https://ir.eia.gov/ngs/ngs.html (effective 20210603143334; data/vendor/release_pages/e5/ngs_week_2021-06-03_20210603143334.html)
- https://web.archive.org/web/20210610150817id_/https://ir.eia.gov/ngs/ngs.html (effective 20210610150817; data/vendor/release_pages/e5/ngs_week_2021-06-10_20210610150817.html)
- https://web.archive.org/web/20210617143555id_/https://ir.eia.gov/ngs/ngs.html (effective 20210617143555; data/vendor/release_pages/e5/ngs_week_2021-06-17_20210617143555.html)
- https://web.archive.org/web/20210624211204id_/https://ir.eia.gov/ngs/ngs.html (effective 20210624211204; data/vendor/release_pages/e5/ngs_week_2021-06-24_20210624211204.html)
- https://web.archive.org/web/20210702025255id_/https://ir.eia.gov/ngs/ngs.html (effective 20210702025255; data/vendor/release_pages/e5/ngs_week_2021-07-01_20210702025255.html)
- https://web.archive.org/web/20210708144436id_/https://ir.eia.gov/ngs/ngs.html (effective 20210708144436; data/vendor/release_pages/e5/ngs_week_2021-07-08_20210708144436.html)
- https://web.archive.org/web/20210715145327id_/https://ir.eia.gov/ngs/ngs.html (effective 20210715145327; data/vendor/release_pages/e5/ngs_week_2021-07-15_20210715145327.html)
- https://web.archive.org/web/20210722160807id_/https://ir.eia.gov/ngs/ngs.html (effective 20210722160807; data/vendor/release_pages/e5/ngs_week_2021-07-22_20210722160807.html)
- https://web.archive.org/web/20210729143352id_/https://ir.eia.gov/ngs/ngs.html (effective 20210729143352; data/vendor/release_pages/e5/ngs_week_2021-07-29_20210729143352.html)
- https://web.archive.org/web/20210806113950id_/https://ir.eia.gov/ngs/ngs.html (effective 20210806113950; data/vendor/release_pages/e5/ngs_week_2021-08-05_20210806113950.html)
- https://web.archive.org/web/20210812144545id_/https://ir.eia.gov/ngs/ngs.html (effective 20210812144545; data/vendor/release_pages/e5/ngs_week_2021-08-12_20210812144545.html)
- https://web.archive.org/web/20210819143302id_/https://ir.eia.gov/ngs/ngs.html (effective 20210819143302; data/vendor/release_pages/e5/ngs_week_2021-08-19_20210819143302.html)
- https://web.archive.org/web/20210826184350id_/https://ir.eia.gov/ngs/ngs.html (effective 20210826184350; data/vendor/release_pages/e5/ngs_week_2021-08-26_20210826184350.html)
- https://web.archive.org/web/20210902144304id_/https://ir.eia.gov/ngs/ngs.html (effective 20210902144304; data/vendor/release_pages/e5/ngs_week_2021-09-02_20210902144304.html)
- https://web.archive.org/web/20210909174025id_/https://ir.eia.gov/ngs/ngs.html (effective 20210909174025; data/vendor/release_pages/e5/ngs_week_2021-09-09_20210909174025.html)
- https://web.archive.org/web/20210916170911id_/https://ir.eia.gov/ngs/ngs.html (effective 20210916170911; data/vendor/release_pages/e5/ngs_week_2021-09-16_20210916170911.html)
- https://web.archive.org/web/20210923210156id_/https://ir.eia.gov/ngs/ngs.html (effective 20210923210156; data/vendor/release_pages/e5/ngs_week_2021-09-23_20210923210156.html)
- https://web.archive.org/web/20210930181325id_/https://ir.eia.gov/ngs/ngs.html (effective 20210930181325; data/vendor/release_pages/e5/ngs_week_2021-09-30_20210930181325.html)
- https://web.archive.org/web/20211007144312id_/https://ir.eia.gov/ngs/ngs.html (effective 20211007144312; data/vendor/release_pages/e5/ngs_week_2021-10-07_20211007144312.html)
- https://web.archive.org/web/20211014143318id_/https://ir.eia.gov/ngs/ngs.html (effective 20211014143318; data/vendor/release_pages/e5/ngs_week_2021-10-14_20211014143318.html)
- https://web.archive.org/web/20211021143335id_/https://ir.eia.gov/ngs/ngs.html (effective 20211021143335; data/vendor/release_pages/e5/ngs_week_2021-10-21_20211021143335.html)
- https://web.archive.org/web/20211029090602id_/https://ir.eia.gov/ngs/ngs.html (effective 20211029090602; data/vendor/release_pages/e5/ngs_week_2021-10-28_20211029090602.html)
- https://web.archive.org/web/20211104145432id_/https://ir.eia.gov/ngs/ngs.html (effective 20211104145432; data/vendor/release_pages/e5/ngs_week_2021-11-04_20211104145432.html)
- https://web.archive.org/web/20211110200640id_/https://ir.eia.gov/ngs/ngs.html (effective 20211110200640; data/vendor/release_pages/e5/ngs_week_2021-11-10_20211110200640.html)
- https://web.archive.org/web/20211118172246id_/https://ir.eia.gov/ngs/ngs.html (effective 20211118172246; data/vendor/release_pages/e5/ngs_week_2021-11-18_20211118172246.html)
- https://web.archive.org/web/20211124203246id_/https://ir.eia.gov/ngs/ngs.html (effective 20211124203246; data/vendor/release_pages/e5/ngs_week_2021-11-24_20211124203246.html)
- https://web.archive.org/web/20211202153317id_/https://ir.eia.gov/ngs/ngs.html (effective 20211202153317; data/vendor/release_pages/e5/ngs_week_2021-12-02_20211202153317.html)
- https://web.archive.org/web/20211209153727id_/https://ir.eia.gov/ngs/ngs.html (effective 20211209153727; data/vendor/release_pages/e5/ngs_week_2021-12-09_20211209153727.html)
- https://web.archive.org/web/20211216153627id_/https://ir.eia.gov/ngs/ngs.html (effective 20211216153627; data/vendor/release_pages/e5/ngs_week_2021-12-16_20211216153627.html)
- https://web.archive.org/web/20211223153631id_/https://ir.eia.gov/ngs/ngs.html (effective 20211223153631; data/vendor/release_pages/e5/ngs_week_2021-12-23_20211223153631.html)
- https://web.archive.org/web/20211230153738id_/https://ir.eia.gov/ngs/ngs.html (effective 20211230153738; data/vendor/release_pages/e5/ngs_week_2021-12-30_20211230153738.html)
- https://web.archive.org/web/20220106153659id_/https://ir.eia.gov/ngs/ngs.html (effective 20220106153659; data/vendor/release_pages/e5/ngs_week_2022-01-06_20220106153659.html)
- https://web.archive.org/web/20220113153719id_/https://ir.eia.gov/ngs/ngs.html (effective 20220113153719; data/vendor/release_pages/e5/ngs_week_2022-01-13_20220113153719.html)
- https://web.archive.org/web/20220120160804id_/http://ir.eia.gov/ngs/ngs.html (effective 20220120211810; data/vendor/release_pages/e5/ngs_week_2022-01-20_20220120160804.html)
- https://web.archive.org/web/20220127153656id_/https://ir.eia.gov/ngs/ngs.html (effective 20220127153656; data/vendor/release_pages/e5/ngs_week_2022-01-27_20220127153656.html)
- https://web.archive.org/web/20220203153639id_/https://ir.eia.gov/ngs/ngs.html (effective 20220203153639; data/vendor/release_pages/e5/ngs_week_2022-02-03_20220203153639.html)
- https://web.archive.org/web/20220210154611id_/https://ir.eia.gov/ngs/ngs.html (effective 20220210154611; data/vendor/release_pages/e5/ngs_week_2022-02-10_20220210154611.html)
- https://web.archive.org/web/20220217153830id_/https://ir.eia.gov/ngs/ngs.html (effective 20220217153830; data/vendor/release_pages/e5/ngs_week_2022-02-17_20220217153830.html)
- https://web.archive.org/web/20220224194453id_/https://ir.eia.gov/ngs/ngs.html (effective 20220224194453; data/vendor/release_pages/e5/ngs_week_2022-02-24_20220224194453.html)
- https://web.archive.org/web/20220303153649id_/https://ir.eia.gov/ngs/ngs.html (effective 20220303153649; data/vendor/release_pages/e5/ngs_week_2022-03-03_20220303153649.html)
- https://web.archive.org/web/20220310153131id_/https://ir.eia.gov/ngs/ngs.html (effective 20220310153131; data/vendor/release_pages/e5/ngs_week_2022-03-10_20220310153131.html)
- https://web.archive.org/web/20220317180018id_/https://ir.eia.gov/ngs/ngs.html (effective 20220317180018; data/vendor/release_pages/e5/ngs_week_2022-03-17_20220317180018.html)
- https://web.archive.org/web/20220324175412id_/https://ir.eia.gov/ngs/ngs.html (effective 20220324175412; data/vendor/release_pages/e5/ngs_week_2022-03-24_20220324175412.html)
- https://web.archive.org/web/20220331143209id_/https://ir.eia.gov/ngs/ngs.html (effective 20220331143209; data/vendor/release_pages/e5/ngs_week_2022-03-31_20220331143209.html)
- https://web.archive.org/web/20220407145320id_/https://ir.eia.gov/ngs/ngs.html (effective 20220407145320; data/vendor/release_pages/e5/ngs_week_2022-04-07_20220407145320.html)
- https://web.archive.org/web/20220415002504id_/https://ir.eia.gov/ngs/ngs.html (effective 20220415002504; data/vendor/release_pages/e5/ngs_week_2022-04-14_20220415002504.html)
- https://web.archive.org/web/20220422102446id_/https://ir.eia.gov/ngs/ngs.html (effective 20220422102446; data/vendor/release_pages/e5/ngs_week_2022-04-21_20220422102446.html)
- https://web.archive.org/web/20220428231032id_/https://ir.eia.gov/ngs/ngs.html (effective 20220428231032; data/vendor/release_pages/e5/ngs_week_2022-04-28_20220428231032.html)
- https://web.archive.org/web/20220505212613id_/https://ir.eia.gov/ngs/ngs.html (effective 20220505212613; data/vendor/release_pages/e5/ngs_week_2022-05-05_20220505212613.html)
- https://web.archive.org/web/20220513003932id_/https://ir.eia.gov/ngs/ngs.html (effective 20220513003932; data/vendor/release_pages/e5/ngs_week_2022-05-12_20220513003932.html)
- https://web.archive.org/web/20220520113059id_/https://ir.eia.gov/ngs/ngs.html (effective 20220520113059; data/vendor/release_pages/e5/ngs_week_2022-05-19_20220520113059.html)
- https://web.archive.org/web/20220526200100id_/https://ir.eia.gov/ngs/ngs.html (effective 20220526200100; data/vendor/release_pages/e5/ngs_week_2022-05-26_20220526200100.html)
- https://web.archive.org/web/20220603044544id_/https://ir.eia.gov/ngs/ngs.html (effective 20220603044544; data/vendor/release_pages/e5/ngs_week_2022-06-02_20220603044544.html)
- https://web.archive.org/web/20220610130455id_/https://ir.eia.gov/ngs/ngs.html (effective 20220610130455; data/vendor/release_pages/e5/ngs_week_2022-06-09_20220610130455.html)
- https://web.archive.org/web/20220616163445id_/https://ir.eia.gov/ngs/ngs.html (effective 20220616163445; data/vendor/release_pages/e5/ngs_week_2022-06-16_20220616163445.html)
- https://web.archive.org/web/20220624062620id_/https://ir.eia.gov/ngs/ngs.html (effective 20220624062620; data/vendor/release_pages/e5/ngs_week_2022-06-23_20220624062620.html)
- https://web.archive.org/web/20220630145549id_/https://ir.eia.gov/ngs/ngs.html (effective 20220630145549; data/vendor/release_pages/e5/ngs_week_2022-06-30_20220630145549.html)
- https://web.archive.org/web/20220707195434id_/https://ir.eia.gov/ngs/ngs.html (effective 20220707195434; data/vendor/release_pages/e5/ngs_week_2022-07-07_20220707195434.html)
- https://web.archive.org/web/20220714233711id_/https://ir.eia.gov/ngs/ngs.html (effective 20220714233711; data/vendor/release_pages/e5/ngs_week_2022-07-14_20220714233711.html)
- https://web.archive.org/web/20220722120459id_/https://ir.eia.gov/ngs/ngs.html (effective 20220722120459; data/vendor/release_pages/e5/ngs_week_2022-07-21_20220722120459.html)
- https://web.archive.org/web/20220728161231id_/https://ir.eia.gov/ngs/ngs.html (effective 20220728161231; data/vendor/release_pages/e5/ngs_week_2022-07-28_20220728161231.html)
- https://web.archive.org/web/20220804175433id_/http://ir.eia.gov/ngs/ngs.html (effective 20220804202509; data/vendor/release_pages/e5/ngs_week_2022-08-04_20220804175433.html)
- https://web.archive.org/web/20220812001752id_/https://ir.eia.gov/ngs/ngs.html (effective 20220812001752; data/vendor/release_pages/e5/ngs_week_2022-08-11_20220812001752.html)
- https://web.archive.org/web/20220818230754id_/http://ir.eia.gov/ngs/ngs.html (effective 20220818230908; data/vendor/release_pages/e5/ngs_week_2022-08-18_20220818230754.html)
- https://web.archive.org/web/20220825194851id_/https://ir.eia.gov/ngs/ngs.html (effective 20220825194851; data/vendor/release_pages/e5/ngs_week_2022-08-25_20220825194851.html)
- https://web.archive.org/web/20220901160904id_/https://ir.eia.gov/ngs/ngs.html (effective 20220901160904; data/vendor/release_pages/e5/ngs_week_2022-09-01_20220901160904.html)
- https://web.archive.org/web/20220908225610id_/https://ir.eia.gov/ngs/ngs.html (effective 20220908225610; data/vendor/release_pages/e5/ngs_week_2022-09-08_20220908225610.html)
- https://web.archive.org/web/20220916063609id_/https://ir.eia.gov/ngs/ngs.html (effective 20220916063609; data/vendor/release_pages/e5/ngs_week_2022-09-15_20220916063609.html)
- https://web.archive.org/web/20220922203719id_/https://ir.eia.gov/ngs/ngs.html (effective 20220922203719; data/vendor/release_pages/e5/ngs_week_2022-09-22_20220922203719.html)
- https://web.archive.org/web/20220929155113id_/https://ir.eia.gov/ngs/ngs.html (effective 20220929155113; data/vendor/release_pages/e5/ngs_week_2022-09-29_20220929155113.html)
- https://web.archive.org/web/20221006152318id_/https://ir.eia.gov/ngs/ngs.html (effective 20221006152318; data/vendor/release_pages/e5/ngs_week_2022-10-06_20221006152318.html)
- https://web.archive.org/web/20221013194111id_/https://ir.eia.gov/ngs/ngs.html (effective 20221013194111; data/vendor/release_pages/e5/ngs_week_2022-10-13_20221013194111.html)
- https://web.archive.org/web/20221020150536id_/https://ir.eia.gov/ngs/ngs.html (effective 20221020150536; data/vendor/release_pages/e5/ngs_week_2022-10-20_20221020150536.html)
- https://web.archive.org/web/20221028033336id_/https://ir.eia.gov/ngs/ngs.html (effective 20221028033336; data/vendor/release_pages/e5/ngs_week_2022-10-27_20221028033336.html)
- https://web.archive.org/web/20221104092950id_/https://ir.eia.gov/ngs/ngs.html (effective 20221104092950; data/vendor/release_pages/e5/ngs_week_2022-11-03_20221104092950.html)
- https://web.archive.org/web/20221110144636id_/http://ir.eia.gov/ngs/ngs.html (effective 20221110161631; data/vendor/release_pages/e5/ngs_week_2022-11-10_20221110144636.html)
- https://web.archive.org/web/20221117222022id_/https://ir.eia.gov/ngs/ngs.html (effective 20221117222022; data/vendor/release_pages/e5/ngs_week_2022-11-17_20221117222022.html)
- https://web.archive.org/web/20221124060223id_/https://ir.eia.gov/ngs/ngs.html (effective 20221124060223; data/vendor/release_pages/e5/ngs_week_2022-11-23_20221124060223.html)
- https://web.archive.org/web/20221202100017id_/https://ir.eia.gov/ngs/ngs.html (effective 20221202100017; data/vendor/release_pages/e5/ngs_week_2022-12-01_20221202100017.html)
- https://web.archive.org/web/20221209143602id_/https://ir.eia.gov/ngs/ngs.html (effective 20221209143602; data/vendor/release_pages/e5/ngs_week_2022-12-08_20221209143602.html)
- https://web.archive.org/web/20221216011107id_/https://ir.eia.gov/ngs/ngs.html (effective 20221216011107; data/vendor/release_pages/e5/ngs_week_2022-12-15_20221216011107.html)
- https://web.archive.org/web/20221223074151id_/https://ir.eia.gov/ngs/ngs.html (effective 20221223074151; data/vendor/release_pages/e5/ngs_week_2022-12-22_20221223074151.html)
- https://web.archive.org/web/20221230153040id_/https://ir.eia.gov/ngs/ngs.html (effective 20221230153040; data/vendor/release_pages/e5/ngs_week_2022-12-29_20221230153040.html)
- https://web.archive.org/web/20230106054534id_/https://ir.eia.gov/ngs/ngs.html (effective 20230106054534; data/vendor/release_pages/e5/ngs_week_2023-01-05_20230106054534.html)
- https://web.archive.org/web/20230113085541id_/https://ir.eia.gov/ngs/ngs.html (effective 20230113085541; data/vendor/release_pages/e5/ngs_week_2023-01-12_20230113085541.html)
- https://web.archive.org/web/20230119223949id_/https://ir.eia.gov/ngs/ngs.html (effective 20230119223949; data/vendor/release_pages/e5/ngs_week_2023-01-19_20230119223949.html)
- https://web.archive.org/web/20230127172405id_/http://ir.eia.gov/ngs/ngs.html (effective 20230127172414; data/vendor/release_pages/e5/ngs_week_2023-01-26_20230127172405.html)
- https://web.archive.org/web/20230202195154id_/https://ir.eia.gov/ngs/ngs.html (effective 20230202195154; data/vendor/release_pages/e5/ngs_week_2023-02-02_20230202195154.html)
- https://web.archive.org/web/20230210005742id_/https://ir.eia.gov/ngs/ngs.html (effective 20230210005742; data/vendor/release_pages/e5/ngs_week_2023-02-09_20230210005742.html)
- https://web.archive.org/web/20230217011503id_/https://ir.eia.gov/ngs/ngs.html (effective 20230217011503; data/vendor/release_pages/e5/ngs_week_2023-02-16_20230217011503.html)
- https://web.archive.org/web/20230223160745id_/https://ir.eia.gov/ngs/ngs.html (effective 20230223160745; data/vendor/release_pages/e5/ngs_week_2023-02-23_20230223160745.html)
- https://web.archive.org/web/20230302155340id_/https://ir.eia.gov/ngs/ngs.html (effective 20230302155340; data/vendor/release_pages/e5/ngs_week_2023-03-02_20230302155340.html)
- https://web.archive.org/web/20230309161434id_/https://ir.eia.gov/ngs/ngs.html (effective 20230309161434; data/vendor/release_pages/e5/ngs_week_2023-03-09_20230309161434.html)
- https://web.archive.org/web/20230316220248id_/https://ir.eia.gov/ngs/ngs.html (effective 20230316220248; data/vendor/release_pages/e5/ngs_week_2023-03-16_20230316220248.html)
- https://web.archive.org/web/20230324230740id_/https://ir.eia.gov/ngs/ngs.html (effective 20230324230740; data/vendor/release_pages/e5/ngs_week_2023-03-23_20230324230740.html)
- https://web.archive.org/web/20230330203946id_/https://ir.eia.gov/ngs/ngs.html (effective 20230330203946; data/vendor/release_pages/e5/ngs_week_2023-03-30_20230330203946.html)
- https://web.archive.org/web/20230406222450id_/https://ir.eia.gov/ngs/ngs.html (effective 20230406222450; data/vendor/release_pages/e5/ngs_week_2023-04-06_20230406222450.html)
- https://web.archive.org/web/20230414053011id_/https://ir.eia.gov/ngs/ngs.html (effective 20230414053011; data/vendor/release_pages/e5/ngs_week_2023-04-13_20230414053011.html)
- https://web.archive.org/web/20230421072551id_/https://ir.eia.gov/ngs/ngs.html (effective 20230421072551; data/vendor/release_pages/e5/ngs_week_2023-04-20_20230421072551.html)
- https://web.archive.org/web/20230428140405id_/https://ir.eia.gov/ngs/ngs.html (effective 20230428140405; data/vendor/release_pages/e5/ngs_week_2023-04-27_20230428140405.html)
- https://web.archive.org/web/20230504220214id_/https://ir.eia.gov/ngs/ngs.html (effective 20230504220214; data/vendor/release_pages/e5/ngs_week_2023-05-04_20230504220214.html)
- https://web.archive.org/web/20230512150441id_/https://ir.eia.gov/ngs/ngs.html (effective 20230512150441; data/vendor/release_pages/e5/ngs_week_2023-05-11_20230512150441.html)
- https://web.archive.org/web/20230519060607id_/https://ir.eia.gov/ngs/ngs.html (effective 20230519060607; data/vendor/release_pages/e5/ngs_week_2023-05-18_20230519060607.html)
- https://web.archive.org/web/20230525153449id_/https://ir.eia.gov/ngs/ngs.html (effective 20230525153449; data/vendor/release_pages/e5/ngs_week_2023-05-25_20230525153449.html)
- https://web.archive.org/web/20230601161321id_/https://ir.eia.gov/ngs/ngs.html (effective 20230601161321; data/vendor/release_pages/e5/ngs_week_2023-06-01_20230601161321.html)
- https://web.archive.org/web/20230608172646id_/https://ir.eia.gov/ngs/ngs.html (effective 20230608172646; data/vendor/release_pages/e5/ngs_week_2023-06-08_20230608172646.html)
- https://web.archive.org/web/20230616080023id_/https://ir.eia.gov/ngs/ngs.html (effective 20230616080023; data/vendor/release_pages/e5/ngs_week_2023-06-15_20230616080023.html)
- https://web.archive.org/web/20230628112148id_/https://ir.eia.gov/ngs/ngs.html (effective 20230628112148; data/vendor/release_pages/e5/ngs_week_2023-06-22_20230628112148.html)
- https://web.archive.org/web/20230629191441id_/https://ir.eia.gov/ngs/ngs.html (effective 20230629191441; data/vendor/release_pages/e5/ngs_week_2023-06-29_20230629191441.html)
- https://web.archive.org/web/20230708052433id_/http://ir.eia.gov/ngs/ngs.html (effective 20230708052435; data/vendor/release_pages/e5/ngs_week_2023-07-07_20230708052433.html)
- https://web.archive.org/web/20230714071122id_/https://ir.eia.gov/ngs/ngs.html (effective 20230714071122; data/vendor/release_pages/e5/ngs_week_2023-07-13_20230714071122.html)
- https://web.archive.org/web/20230721144833id_/https://ir.eia.gov/ngs/ngs.html (effective 20230721144833; data/vendor/release_pages/e5/ngs_week_2023-07-20_20230721144833.html)
- https://web.archive.org/web/20230728010225id_/https://ir.eia.gov/ngs/ngs.html (effective 20230728010225; data/vendor/release_pages/e5/ngs_week_2023-07-27_20230728010225.html)
- https://web.archive.org/web/20230804050421id_/https://ir.eia.gov/ngs/ngs.html (effective 20230804050421; data/vendor/release_pages/e5/ngs_week_2023-08-03_20230804050421.html)
- https://web.archive.org/web/20230810202902id_/https://ir.eia.gov/ngs/ngs.html (effective 20230810202902; data/vendor/release_pages/e5/ngs_week_2023-08-10_20230810202902.html)
- https://web.archive.org/web/20230817145343id_/https://ir.eia.gov/ngs/ngs.html (effective 20230817145343; data/vendor/release_pages/e5/ngs_week_2023-08-17_20230817145343.html)
- https://web.archive.org/web/20230824155529id_/https://ir.eia.gov/ngs/ngs.html (effective 20230824155529; data/vendor/release_pages/e5/ngs_week_2023-08-24_20230824155529.html)
- https://web.archive.org/web/20230901014328id_/https://ir.eia.gov/ngs/ngs.html (effective 20230901014328; data/vendor/release_pages/e5/ngs_week_2023-08-31_20230901014328.html)
- https://web.archive.org/web/20230908121600id_/https://ir.eia.gov/ngs/ngs.html (effective 20230908121600; data/vendor/release_pages/e5/ngs_week_2023-09-07_20230908121600.html)
- https://web.archive.org/web/20230914215759id_/https://ir.eia.gov/ngs/ngs.html (effective 20230914215759; data/vendor/release_pages/e5/ngs_week_2023-09-14_20230914215759.html)
- https://web.archive.org/web/20230922024956id_/https://ir.eia.gov/ngs/ngs.html (effective 20230922024956; data/vendor/release_pages/e5/ngs_week_2023-09-21_20230922024956.html)
- https://web.archive.org/web/20230929082224id_/https://ir.eia.gov/ngs/ngs.html (effective 20230929082224; data/vendor/release_pages/e5/ngs_week_2023-09-28_20230929082224.html)
- https://web.archive.org/web/20231005235150id_/https://ir.eia.gov/ngs/ngs.html (effective 20231005235150; data/vendor/release_pages/e5/ngs_week_2023-10-05_20231005235150.html)
- https://web.archive.org/web/20231013053144id_/https://ir.eia.gov/ngs/ngs.html (effective 20231013053144; data/vendor/release_pages/e5/ngs_week_2023-10-12_20231013053144.html)
- https://web.archive.org/web/20231020002851id_/https://ir.eia.gov/ngs/ngs.html (effective 20231020002851; data/vendor/release_pages/e5/ngs_week_2023-10-19_20231020002851.html)
- https://web.archive.org/web/20231026145218id_/https://ir.eia.gov/ngs/ngs.html (effective 20231026145218; data/vendor/release_pages/e5/ngs_week_2023-10-26_20231026145218.html)
- https://web.archive.org/web/20231103010226id_/https://ir.eia.gov/ngs/ngs.html (effective 20231103010226; data/vendor/release_pages/e5/ngs_week_2023-11-02_20231103010226.html)
- https://web.archive.org/web/20231110072740id_/https://ir.eia.gov/ngs/ngs.html (effective 20231110072740; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231110072740.html)
- https://web.archive.org/web/20231111080914id_/https://ir.eia.gov/ngs/ngs.html (effective 20231111080914; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231111080914.html)
- https://web.archive.org/web/20231111111827id_/https://ir.eia.gov/ngs/ngs.html (effective 20231111111827; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231111111827.html)
- https://web.archive.org/web/20231112115229id_/https://ir.eia.gov/ngs/ngs.html (effective 20231112115229; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231112115229.html)
- https://web.archive.org/web/20231113122638id_/https://ir.eia.gov/ngs/ngs.html (effective 20231113122638; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231113122638.html)
- https://web.archive.org/web/20231114125548id_/https://ir.eia.gov/ngs/ngs.html (effective 20231114125548; data/vendor/release_pages/e5/ngs_week_2023-11-09_20231114125548.html)
- https://web.archive.org/web/20231117144124id_/https://ir.eia.gov/ngs/ngs.html (effective 20231117144124; data/vendor/release_pages/e5/ngs_week_2023-11-16_20231117144124.html)
- https://web.archive.org/web/20231122214645id_/https://ir.eia.gov/ngs/ngs.html (effective 20231122214645; data/vendor/release_pages/e5/ngs_week_2023-11-22_20231122214645.html)
- https://web.archive.org/web/20231201045923id_/https://ir.eia.gov/ngs/ngs.html (effective 20231201045923; data/vendor/release_pages/e5/ngs_week_2023-11-30_20231201045923.html)
- https://web.archive.org/web/20231208105706id_/https://ir.eia.gov/ngs/ngs.html (effective 20231208105706; data/vendor/release_pages/e5/ngs_week_2023-12-07_20231208105706.html)
- https://web.archive.org/web/20231214181604id_/http://ir.eia.gov/ngs/ngs.html (effective 20231214181617; data/vendor/release_pages/e5/ngs_week_2023-12-14_20231214181604.html)
- https://web.archive.org/web/20231221205514id_/https://ir.eia.gov/ngs/ngs.html (effective 20231221205514; data/vendor/release_pages/e5/ngs_week_2023-12-21_20231221205514.html)
- https://web.archive.org/web/20231229085602id_/https://ir.eia.gov/ngs/ngs.html (effective 20231229085602; data/vendor/release_pages/e5/ngs_week_2023-12-28_20231229085602.html)
- https://web.archive.org/web/20240105042124id_/https://ir.eia.gov/ngs/ngs.html (effective 20240105042124; data/vendor/release_pages/e5/ngs_week_2024-01-04_20240105042124.html)
- https://web.archive.org/web/20240111163002id_/https://ir.eia.gov/ngs/ngs.html (effective 20240111163002; data/vendor/release_pages/e5/ngs_week_2024-01-11_20240111163002.html)
- https://web.archive.org/web/20240119013129id_/https://ir.eia.gov/ngs/ngs.html (effective 20240119013129; data/vendor/release_pages/e5/ngs_week_2024-01-18_20240119013129.html)
- https://web.archive.org/web/20240126063235id_/https://ir.eia.gov/ngs/ngs.html (effective 20240126063235; data/vendor/release_pages/e5/ngs_week_2024-01-25_20240126063235.html)
- https://web.archive.org/web/20240201170228id_/https://ir.eia.gov/ngs/ngs.html (effective 20240201170228; data/vendor/release_pages/e5/ngs_week_2024-02-01_20240201170228.html)
- https://web.archive.org/web/20240209010435id_/https://ir.eia.gov/ngs/ngs.html (effective 20240209010435; data/vendor/release_pages/e5/ngs_week_2024-02-08_20240209010435.html)
- https://web.archive.org/web/20240216063700id_/https://ir.eia.gov/ngs/ngs.html (effective 20240216063700; data/vendor/release_pages/e5/ngs_week_2024-02-15_20240216063700.html)
- https://web.archive.org/web/20240222143816id_/https://ir.eia.gov/ngs/ngs.html (effective 20240222143816; data/vendor/release_pages/e5/ngs_week_2024-02-22_20240222143816.html)
- https://web.archive.org/web/20240223152808id_/https://ir.eia.gov/ngs/ngs.html (effective 20240223152808; data/vendor/release_pages/e5/ngs_week_2024-02-22_20240223152808.html)
- https://web.archive.org/web/20240229205216id_/https://ir.eia.gov/ngs/ngs.html (effective 20240229205216; data/vendor/release_pages/e5/ngs_week_2024-02-29_20240229205216.html)
- https://web.archive.org/web/20190111124957id_/https://ir.eia.gov/ngs/schedule.html (effective 20190111124957; data/vendor/release_pages/e5/ngs_sched_20190111124957.html)
- https://web.archive.org/web/20190613010741id_/https://ir.eia.gov/ngs/schedule.html (effective 20190613010741; data/vendor/release_pages/e5/ngs_sched_20190613010741.html)
- https://web.archive.org/web/20190714105626id_/https://ir.eia.gov/ngs/schedule.html (effective 20190714105626; data/vendor/release_pages/e5/ngs_sched_20190714105626.html)
- https://web.archive.org/web/20191129075548id_/https://ir.eia.gov/ngs/schedule.html (effective 20191129075548; data/vendor/release_pages/e5/ngs_sched_20191129075548.html)
- https://web.archive.org/web/20191229152905id_/https://ir.eia.gov/ngs/schedule.html (effective 20191229152905; data/vendor/release_pages/e5/ngs_sched_20191229152905.html)
- https://web.archive.org/web/20200128214849id_/https://ir.eia.gov/ngs/schedule.html (effective 20200128214849; data/vendor/release_pages/e5/ngs_sched_20200128214849.html)
- https://web.archive.org/web/20201121084027id_/https://ir.eia.gov/ngs/schedule.html (effective 20201121084027; data/vendor/release_pages/e5/ngs_sched_20201121084027.html)
- https://web.archive.org/web/20201217153516id_/https://ir.eia.gov/ngs/schedule.html (effective 20201217153516; data/vendor/release_pages/e5/ngs_sched_20201217153516.html)
- https://web.archive.org/web/20201224001827id_/https://ir.eia.gov/ngs/schedule.html (effective 20201224001827; data/vendor/release_pages/e5/ngs_sched_20201224001827.html)
- https://web.archive.org/web/20210104203613id_/https://ir.eia.gov/ngs/schedule.html (effective 20210104203613; data/vendor/release_pages/e5/ngs_sched_20210104203613.html)
- https://web.archive.org/web/20210319031602id_/https://ir.eia.gov/ngs/schedule.html (effective 20210319031602; data/vendor/release_pages/e5/ngs_sched_20210319031602.html)
- https://web.archive.org/web/20211102183454id_/https://ir.eia.gov/ngs/schedule.html (effective 20211102183454; data/vendor/release_pages/e5/ngs_sched_20211102183454.html)
- https://web.archive.org/web/20211111015940id_/https://ir.eia.gov/ngs/schedule.html (effective 20211111015940; data/vendor/release_pages/e5/ngs_sched_20211111015940.html)
- https://web.archive.org/web/20211216230557id_/https://ir.eia.gov/ngs/schedule.html (effective 20211216230557; data/vendor/release_pages/e5/ngs_sched_20211216230557.html)
- https://web.archive.org/web/20220114160745id_/https://ir.eia.gov/ngs/schedule.html (effective 20220114160745; data/vendor/release_pages/e5/ngs_sched_20220114160745.html)
- https://web.archive.org/web/20221106051100id_/https://ir.eia.gov/ngs/schedule.html (effective 20221106051100; data/vendor/release_pages/e5/ngs_sched_20221106051100.html)
- https://web.archive.org/web/20230210074654id_/https://ir.eia.gov/ngs/schedule.html (effective 20230210074654; data/vendor/release_pages/e5/ngs_sched_20230210074654.html)
- https://web.archive.org/web/20230708153227id_/https://ir.eia.gov/ngs/schedule.html (effective 20230708153227; data/vendor/release_pages/e5/ngs_sched_20230708153227.html)
- https://web.archive.org/web/20231208131519id_/https://ir.eia.gov/ngs/schedule.html (effective 20231208131519; data/vendor/release_pages/e5/ngs_sched_20231208131519.html)
- https://web.archive.org/web/20240607000738id_/https://ir.eia.gov/ngs/schedule.html (effective 20240607000738; data/vendor/release_pages/e5/ngs_sched_20240607000738.html)
- https://web.archive.org/web/20240720000603id_/https://ir.eia.gov/ngs/schedule.html (effective 20240720000603; data/vendor/release_pages/e5/ngs_sched_20240720000603.html)
- https://web.archive.org/cdx/search/cdx?url=ir.eia.gov/ngs/ngs.html&from=20190501&to=20240310&fl=timestamp,statuscode,digest,original (effective None; data/vendor/release_pages/e5/cdx_ngs_html_2019_2024.txt)
- https://web.archive.org/cdx/search/cdx?url=ir.eia.gov/ngs/schedule.html&from=2019&to=2024&fl=timestamp,statuscode,digest,original (effective None; data/vendor/release_pages/e5/cdx_ngs_schedule_2019_2024.txt)
- https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2020/02_13/ (effective direct (live EIA page, fetched by E.2b; reused, not re-fetched); data/vendor/release_pages/eia/ngwu/ngwu_2020_02_13.html)
- https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2023/11_09/ (effective direct (live EIA page, fetched by E.2b; reused, not re-fetched); data/vendor/release_pages/eia/ngwu/ngwu_2023_11_09.html)

## Log (failed fetches and notes, PDT)

- 2026-09-27T12:39:50-0700 fetch failed HTTP 000 http://web.archive.org/web/20190830130415id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 80 after 39 ms: Could not connect to server (try 1)
- 2026-09-27T12:39:58-0700 fetch failed HTTP 000 http://web.archive.org/web/20190830130415id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 80 after 42 ms: Could not connect to server (try 2)
- 2026-09-27T12:40:06-0700 fetch failed HTTP 000 http://web.archive.org/web/20190831134323id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 80 after 34 ms: Could not connect to server (try 1)
- 2026-09-27T12:40:14-0700 fetch failed HTTP 000 http://web.archive.org/web/20190831134323id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 80 after 34 ms: Could not connect to server (try 2)
- 2026-09-27T12:40:22-0700 fetch failed HTTP 000 http://web.archive.org/web/20190901105002id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 80 after 31 ms: Could not connect to server (try 1)
- 2026-09-27T12:38:20-0700 CDX schedule.html 2019-2024 HTTP 503 Temporarily Offline (http)
- 2026-09-27T12:38:32-0700 CDX schedule.html 2019-2024 HTTP 503 Temporarily Offline (http, retry)
- 2026-09-27T12:40:11-0700 CDX schedule.html 2019-2024 connect refused (http); crawler paused, pacing slowed to 5 s, switched to https
- 2026-09-27T12:41:00-0700 CDX schedule.html 2019-2024 HTTP 504 Gateway Time-out (https)
- 2026-09-27T12:43:39-0700 fetch failed HTTP 000 https://web.archive.org/web/20191024192833id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 34 ms: Could not connect to server (try 1)
- 2026-09-27T12:44:15-0700 fetch failed HTTP 000 https://web.archive.org/web/20191031182242id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 37 ms: Could not connect to server (try 1)
- 2026-09-27T12:45:03-0700 fetch failed HTTP 000 https://web.archive.org/web/20191122024645id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 32 ms: Could not connect to server (try 1)
- 2026-09-27T12:47:19-0700 fetch failed HTTP 000 https://web.archive.org/web/20200326163511id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 33 ms: Could not connect to server (try 1)
- 2026-09-27T12:48:12-0700 fetch failed HTTP 000 https://web.archive.org/web/20200423222041id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 40 ms: Could not connect to server (try 1)
- 2026-09-27T12:50:02-0700 fetch failed HTTP 000 https://web.archive.org/web/20200731074808id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 41 ms: Could not connect to server (try 1)
- 2026-09-27T12:51:26-0700 fetch failed HTTP 000 https://web.archive.org/web/20201002100347id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 39 ms: Could not connect to server (try 1)
- 2026-09-27T12:53:24-0700 fetch failed HTTP 000 https://web.archive.org/web/20201231153108id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 45 ms: Could not connect to server (try 1)
- 2026-09-27T12:53:54-0700 fetch failed HTTP 000 https://web.archive.org/web/20201231153108id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 42 ms: Could not connect to server (try 2)
- 2026-09-27T12:56:07-0700 fetch failed HTTP 500 https://web.archive.org/web/20210415143221id_/https://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T12:56:55-0700 fetch failed HTTP 000 https://web.archive.org/web/20210506155641id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 35 ms: Could not connect to server (try 1)
- 2026-09-27T12:57:32-0700 fetch failed HTTP 500 https://web.archive.org/web/20210513143038id_/https://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T12:58:03-0700 fetch failed HTTP 500 https://web.archive.org/web/20210513143038id_/https://ir.eia.gov/ngs/ngs.html  (try 2)
- 2026-09-27T12:58:46-0700 fetch failed HTTP 500 https://web.archive.org/web/20210527151013id_/http://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T12:59:17-0700 fetch failed HTTP 500 https://web.archive.org/web/20210527151013id_/http://ir.eia.gov/ngs/ngs.html  (try 2)
- 2026-09-27T12:59:48-0700 fetch failed HTTP 500 https://web.archive.org/web/20210530215239id_/http://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T13:01:42-0700 fetch failed HTTP 500 https://web.archive.org/web/20210902144304id_/https://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T13:05:20-0700 fetch failed HTTP 000 https://web.archive.org/web/20220407145320id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 36 ms: Could not connect to server (try 1)
- 2026-09-27T13:05:56-0700 fetch failed HTTP 000 https://web.archive.org/web/20220415002504id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 38 ms: Could not connect to server (try 1)
- 2026-09-27T13:07:23-0700 fetch failed HTTP 000 https://web.archive.org/web/20220624062620id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 62 ms: Could not connect to server (try 1)
- 2026-09-27T13:09:06-0700 fetch failed HTTP 000 https://web.archive.org/web/20220908225610id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 45 ms: Could not connect to server (try 1)
- 2026-09-27T13:10:28-0700 fetch failed HTTP 000 https://web.archive.org/web/20221110144636id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 33 ms: Could not connect to server (try 1)
- 2026-09-27T13:12:15-0700 fetch failed HTTP 000 https://web.archive.org/web/20230210005742id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 37 ms: Could not connect to server (try 1)
- 2026-09-27T13:13:09-0700 fetch failed HTTP 000 https://web.archive.org/web/20230309161434id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 63 ms: Could not connect to server (try 1)
- 2026-09-27T13:14:36-0700 fetch failed HTTP 000 https://web.archive.org/web/20230519060607id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 33 ms: Could not connect to server (try 1)
- 2026-09-27T13:15:46-0700 fetch failed HTTP 000 https://web.archive.org/web/20230708052433id_/http://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 42 ms: Could not connect to server (try 1)
- 2026-09-27T13:16:45-0700 fetch failed HTTP 500 https://web.archive.org/web/20230810202902id_/https://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T13:17:45-0700 fetch failed HTTP 500 https://web.archive.org/web/20230914215759id_/https://ir.eia.gov/ngs/ngs.html  (try 1)
- 2026-09-27T13:20:37-0700 fetch failed HTTP 000 https://web.archive.org/web/20240126063235id_/https://ir.eia.gov/ngs/ngs.html curl: (7) Failed to connect to web.archive.org port 443 after 38 ms: Could not connect to server (try 1)
- 2026-09-27T12:44:00-0700 parser bug: "September" dates were not parsed on the first pass (2019-09-05, 2019-09-12 logged as nocapture); fixed and rerun from cached pages; final results use the fixed parser
- 2026-09-27T13:20:00-0700 ngs.html crawl done: 252 rows, 250 with a capture stating the release; 2020-02-13 and 2023-11-09 had no capture stating that release (2020-02-13: no CDX capture between 2020-02-13 and 2020-02-21; 2023-11-09: captures 20231110..20231114 still show the 2023-11-02 release)
- 2026-09-27T13:23:00-0700 schedule.html: 21 captures fetched, one per content digest 2019-01..2024-07 plus catalog captures; no "(Updated)" text in any of them
- effective-timestamp check: 8 ngs.html captures were served from a capture 2 s to 5 h after the requested one (2021-05-27, 2022-01-20, 2022-08-04, 2022-08-18, 2022-11-10, 2023-01-26, 2023-07-07, 2023-12-14); each served capture is still after the release and before the next one, and the page content states the release date; actual_source cites the effective capture
