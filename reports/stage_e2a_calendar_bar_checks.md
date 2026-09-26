# Stage E.2a calendar bar checks (step-4b style, per group)

Generated 2026-09-25T09:46:34.350603+00:00. Research window 2025-04-01..2026-06-19. Evidence is CT minutes and bar counts only. No calendar module was edited: every calendar question is for the lead.

- (a) every weekday with no bar in its regular session span is a listed full closure
- (b) every weekday whose last bar before the day-session close C opens before C minus one minute is a listed early halt whose halt time equals the observed last minute plus one
- (c) every listed 2025-2026 entry inside the window is observed (early halt, full closure, LATE_OPENS)
- classification: seen on the group's most liquid contract (highest ohlcv-1m record count) -> calendar_question; seen only on thinner contracts -> thin_trading (never a calendar error, never fixed by a fake early close)

2025-11-28 CME Globex outage (documented_cme_outage): L-4 revised (01:21 PDT): no closed window in any group; the outage is a reported gap run; LATE_OPENS is checked only (the first bar of 2025-11-28 at or after 07:30 CT). The equity module does not list it; its gap runs there are the same documented outage. Source: data/calendars/rates.py LATE_OPEN_SOURCES[2025-11-28], https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate=2025-11-26&toEventDate=2025-11-28&isProtected&_t=1769649703060, quote: "globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... {"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:15","marketEventType":"closed"}]}

Note: MBT (the only crypto contract, so every discrepancy is a calendar question by the rule): the Friday early stops at 09:58-10:00 CT (10:58-11:00 CT on 2025-10-31 and 2026-03-27) fall on the last Friday of each month, the expiry day of CME's monthly bitcoin futures; each is followed by a vendor roll on the next UTC date (rolls in stage_e2a_bars.json), so the volume-ranked series holds the expiring contract after its last trade. Diagnosis for the lead: contract expiry in the continuous series, not a calendar entry; every such Friday lies inside the roll blackout (splice trade date and the two sessions before).

Calendar questions without a lead ruling: none

Totals by classification: {'thin_trading': 340, 'calendar_question': 31}

| Group | Status | Contracts | Most liquid | Entries checked | Observed on most liquid | Thin trading | Calendar questions |
|---|---|---|---|---|---|---|---|
| equity | complete | M2K, MNQ, MYM, NQ, RTY, YM | MNQ | 17 | 17 | 0 | 0 |
| rates | complete | TN, UB, ZB, ZF, ZN, ZT | ZN | 16 | 16 | 0 | 0 |
| fx | complete | 6A, 6B, 6C, 6E, 6J, 6N, 6S, E7, M6A, M6B, M6E | 6E | 9 | 9 | 240 | 6 |
| energy | complete | CL, HO, MCL, MNG, NG, QG, QM, RB | CL | 16 | 16 | 85 | 0 |
| metals | complete | GC, HG, MGC, MHG, SI, SIL | MGC | 16 | 16 | 15 | 10 |
| grains | complete | ZC, ZL, ZM, ZS, ZW | ZL | 18 | 18 | 0 | 0 |
| livestock | complete | HE, LE | LE | 15 | 15 | 0 | 0 |
| crypto | complete | MBT | MBT | 9 | 7 | 0 | 15 |

## equity

Most liquid: MNQ. Entries checked: 2025-04-18 full_closure, 2025-05-26 early_halt, 2025-06-19 early_halt, 2025-07-03 early_halt, 2025-07-04 early_halt, 2025-09-01 early_halt, 2025-11-27 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 early_halt, 2026-02-16 early_halt, 2026-04-03 early_halt, 2026-05-25 early_halt, 2026-06-19 early_halt, 2025-11-28 late_open

### Calendar questions

- none

### Per contract

- **M2K**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:43, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:44 CT, 646 minutes
- **MNQ**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes
- **MYM**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes
- **NQ**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes
- **RTY**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes
- **YM**: weekdays 319, entries observed 17/17, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes

## rates

Most liquid: ZN. Entries checked: 2025-04-18 full_closure, 2025-05-26 early_halt, 2025-06-19 early_halt, 2025-07-04 early_halt, 2025-09-01 early_halt, 2025-11-27 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 early_halt, 2026-02-16 early_halt, 2026-04-03 early_halt, 2026-05-25 early_halt, 2026-06-19 early_halt, 2025-11-28 late_open

### Calendar questions

- none

### Per contract

- **TN**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1202, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1137, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **UB**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1265, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1161, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **ZB**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1208, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1132, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **ZF**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 1 (2026-03-13 Fri 16:00 CT, close minute True)
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1229, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1220, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **ZN**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 1 (2026-03-13 Fri 16:00 CT, close minute True)
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1294, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1280, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **ZT**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 1 (2026-03-13 Fri 16:00 CT, close minute True)
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-05-23 (listed without an entry): bars_in_session 1124, first_bar_ct Thu 05-22 17:00, last_bar_ct Fri 05-23 15:59, last_bar_before_1400_ct Fri 05-23 13:59
  - bars on 2026-05-22 (listed without an entry): bars_in_session 1195, first_bar_ct Thu 05-21 17:00, last_bar_ct Fri 05-22 15:59, last_bar_before_1400_ct Fri 05-22 13:59
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes

## fx

Most liquid: 6E. Entries checked: 2025-04-18 full_closure, 2025-07-04 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-04-03 early_halt, 2026-06-19 early_halt, 2025-11-28 late_open

### Calendar questions

- 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:53 (implied halt Thu 11-27 13:54); no calendar entry; next bar Thu 11-27 14:00; 1233 bars in the session (also on: 6C, 6S, E7, M6A, M6E). **Lead ruling:** L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.

### Per contract

- **6A**: weekdays 319, entries observed 9/9, discrepancies 2, bars inside a scheduled closure 0
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:58 (implied halt Mon 09-01 13:59); no calendar entry; next bar Mon 09-01 14:00; 1147 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-16 13:57 (implied halt Mon 02-16 13:58); no calendar entry; next bar Mon 02-16 14:01; 1221 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **6B**: weekdays 319, entries observed 8/9, discrepancies 4, bars inside a scheduled closure 0
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-26 13:58 (implied halt Mon 05-26 13:59); no calendar entry; next bar Mon 05-26 14:07; 1180 bars in the session
  - [thin_trading] 2025-09-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-12 13:53 (implied halt Fri 09-12 13:54); no calendar entry; next bar Fri 09-12 14:00; 664 bars in the session
  - [thin_trading] 2025-12-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 12-24 12:43 (implied halt Wed 12-24 12:44); listed early_halt 12:45 (Christmas Eve); next bar Thu 12-25 17:00; 1036 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: last bar Wed 12-24 12:43 != expected Wed 12-24 12:44
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **6C**: weekdays 319, entries observed 7/9, discrepancies 7, bars inside a scheduled closure 0
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-26 13:58 (implied halt Mon 05-26 13:59); no calendar entry; next bar Mon 05-26 14:00; 1177 bars in the session
  - [thin_trading] 2025-06-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-13 13:57 (implied halt Fri 06-13 13:58); no calendar entry; next bar Fri 06-13 14:01; 733 bars in the session
  - [thin_trading] 2025-06-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-19 13:58 (implied halt Thu 06-19 13:59); no calendar entry; next bar Thu 06-19 14:00; 1177 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:57 (implied halt Mon 09-01 13:58); no calendar entry; next bar Mon 09-01 14:00; 862 bars in the session
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:58 (implied halt Thu 11-27 13:59); no calendar entry; next bar Thu 11-27 14:03; 906 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - [thin_trading] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-28 13:42 (implied halt Fri 11-28 13:43); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 505 bars in the session
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:42 != expected Fri 11-28 13:44
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **6E**: weekdays 319, entries observed 9/9, discrepancies 1, bars inside a scheduled closure 0
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:53 (implied halt Thu 11-27 13:54); no calendar entry; next bar Thu 11-27 14:00; 1233 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:49, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:50 CT, 640 minutes
- **6J**: weekdays 319, entries observed 9/9, discrepancies 3, bars inside a scheduled closure 0
  - [thin_trading] 2025-06-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-13 13:58 (implied halt Fri 06-13 13:59); no calendar entry; next bar Fri 06-13 14:00; 961 bars in the session
  - [thin_trading] 2025-09-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-12 13:52 (implied halt Fri 09-12 13:53); no calendar entry; next bar Fri 09-12 14:00; 763 bars in the session
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 13:58 (implied halt Fri 06-12 13:59); no calendar entry; next bar Fri 06-12 14:00; 820 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **6N**: weekdays 319, entries observed 7/9, discrepancies 4, bars inside a scheduled closure 0
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-26 13:56 (implied halt Mon 05-26 13:57); no calendar entry; next bar Mon 05-26 14:00; 1143 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:58 (implied halt Mon 09-01 13:59); no calendar entry; next bar Mon 09-01 14:00; 1010 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: first bar after Thu 12-25 17:02 != reopen Thu 12-25 17:00
  - [thin_trading] 2025-12-25 listed_entry_not_observed: Christmas Day, full closure: first bar after Thu 12-25 17:02 != reopen Thu 12-25 17:00
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **6S**: weekdays 319, entries observed 5/9, discrepancies 9, bars inside a scheduled closure 0
  - [thin_trading] 2025-06-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-13 13:55 (implied halt Fri 06-13 13:56); no calendar entry; next bar Fri 06-13 14:01; 521 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:54 (implied halt Mon 09-01 13:55); no calendar entry; next bar Mon 09-01 14:00; 958 bars in the session
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:58 (implied halt Thu 11-27 13:59); no calendar entry; next bar Thu 11-27 14:00; 909 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - [thin_trading] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-28 13:42 (implied halt Fri 11-28 13:43); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 467 bars in the session
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:42 != expected Fri 11-28 13:44
  - [thin_trading] 2025-12-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 12-24 12:43 (implied halt Wed 12-24 12:44); listed early_halt 12:45 (Christmas Eve); next bar Thu 12-25 17:02; 938 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: last bar Wed 12-24 12:43 != expected Wed 12-24 12:44; first bar after Thu 12-25 17:02 != reopen Thu 12-25 17:00
  - [thin_trading] 2025-12-25 listed_entry_not_observed: Christmas Day, full closure: first bar after Thu 12-25 17:02 != reopen Thu 12-25 17:00
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 13:58 (implied halt Fri 06-12 13:59); no calendar entry; next bar Fri 06-12 14:09; 424 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:43, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:44 CT, 646 minutes
- **E7**: weekdays 319, entries observed 3/9, discrepancies 86, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 04-14 13:58 (implied halt Mon 04-14 13:59); no calendar entry; next bar Mon 04-14 14:00; 1142 bars in the session
  - [thin_trading] 2025-05-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 05-08 13:55 (implied halt Thu 05-08 13:56); no calendar entry; next bar Thu 05-08 14:00; 1032 bars in the session
  - [thin_trading] 2025-05-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-14 13:56 (implied halt Wed 05-14 13:57); no calendar entry; next bar Wed 05-14 14:00; 905 bars in the session
  - [thin_trading] 2025-05-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 05-15 13:58 (implied halt Thu 05-15 13:59); no calendar entry; next bar Thu 05-15 14:02; 768 bars in the session
  - [thin_trading] 2025-05-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 05-16 13:57 (implied halt Fri 05-16 13:58); no calendar entry; next bar Fri 05-16 14:00; 733 bars in the session
  - [thin_trading] 2025-05-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-19 13:56 (implied halt Mon 05-19 13:57); no calendar entry; next bar Mon 05-19 14:00; 768 bars in the session
  - [thin_trading] 2025-05-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 05-23 13:57 (implied halt Fri 05-23 13:58); no calendar entry; next bar Fri 05-23 14:00; 806 bars in the session
  - [thin_trading] 2025-05-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-28 13:56 (implied halt Wed 05-28 13:57); no calendar entry; next bar Wed 05-28 14:02; 803 bars in the session
  - [thin_trading] 2025-06-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 06-04 13:57 (implied halt Wed 06-04 13:58); no calendar entry; next bar Wed 06-04 14:04; 791 bars in the session
  - [thin_trading] 2025-06-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 06-11 13:57 (implied halt Wed 06-11 13:58); no calendar entry; next bar Wed 06-11 14:00; 745 bars in the session
  - [thin_trading] 2025-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-12 13:58 (implied halt Thu 06-12 13:59); no calendar entry; next bar Thu 06-12 14:00; 855 bars in the session
  - [thin_trading] 2025-06-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-13 13:56 (implied halt Fri 06-13 13:57); no calendar entry; next bar Fri 06-13 14:34; 258 bars in the session
  - [thin_trading] 2025-06-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 06-16 13:58 (implied halt Mon 06-16 13:59); no calendar entry; next bar Mon 06-16 14:01; 747 bars in the session
  - [thin_trading] 2025-06-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 06-17 13:55 (implied halt Tue 06-17 13:56); no calendar entry; next bar Tue 06-17 14:01; 883 bars in the session
  - [thin_trading] 2025-06-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-20 13:57 (implied halt Fri 06-20 13:58); no calendar entry; next bar Fri 06-20 14:00; 845 bars in the session
  - [thin_trading] 2025-06-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 06-24 13:56 (implied halt Tue 06-24 13:57); no calendar entry; next bar Tue 06-24 14:05; 909 bars in the session
  - [thin_trading] 2025-06-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-27 13:58 (implied halt Fri 06-27 13:59); no calendar entry; next bar Fri 06-27 14:00; 849 bars in the session
  - [thin_trading] 2025-07-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 07-09 13:47 (implied halt Wed 07-09 13:48); no calendar entry; next bar Wed 07-09 14:07; 686 bars in the session
  - [thin_trading] 2025-07-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-10 13:58 (implied halt Thu 07-10 13:59); no calendar entry; next bar Thu 07-10 14:05; 652 bars in the session
  - [thin_trading] 2025-07-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-14 13:57 (implied halt Mon 07-14 13:58); no calendar entry; next bar Mon 07-14 14:07; 683 bars in the session
  - [thin_trading] 2025-07-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 07-15 13:57 (implied halt Tue 07-15 13:58); no calendar entry; next bar Tue 07-15 14:01; 704 bars in the session
  - [thin_trading] 2025-07-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-17 13:57 (implied halt Thu 07-17 13:58); no calendar entry; next bar Thu 07-17 14:03; 675 bars in the session
  - [thin_trading] 2025-07-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 07-18 13:57 (implied halt Fri 07-18 13:58); no calendar entry; next bar Fri 07-18 14:02; 755 bars in the session
  - [thin_trading] 2025-07-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 07-22 13:56 (implied halt Tue 07-22 13:57); no calendar entry; next bar Tue 07-22 14:00; 650 bars in the session
  - [thin_trading] 2025-07-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 07-23 13:51 (implied halt Wed 07-23 13:52); no calendar entry; next bar Wed 07-23 14:00; 725 bars in the session
  - [thin_trading] 2025-07-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 07-29 13:53 (implied halt Tue 07-29 13:54); no calendar entry; next bar Tue 07-29 14:00; 844 bars in the session
  - [thin_trading] 2025-08-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 08-08 13:57 (implied halt Fri 08-08 13:58); no calendar entry; next bar Fri 08-08 14:03; 646 bars in the session
  - [thin_trading] 2025-08-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 08-15 13:58 (implied halt Fri 08-15 13:59); no calendar entry; next bar Fri 08-15 14:02; 565 bars in the session
  - [thin_trading] 2025-08-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 08-19 13:58 (implied halt Tue 08-19 13:59); no calendar entry; next bar Tue 08-19 14:05; 669 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:57 (implied halt Mon 09-01 13:58); no calendar entry; next bar Mon 09-01 14:01; 515 bars in the session
  - [thin_trading] 2025-09-05 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-05 13:58 (implied halt Fri 09-05 13:59); no calendar entry; next bar Fri 09-05 14:00; 726 bars in the session
  - [thin_trading] 2025-09-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 09-10 13:39 (implied halt Wed 09-10 13:40); no calendar entry; next bar Wed 09-10 14:03; 667 bars in the session
  - [thin_trading] 2025-09-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-12 13:54 (implied halt Fri 09-12 13:55); no calendar entry; next bar Fri 09-12 14:07; 178 bars in the session
  - [thin_trading] 2025-09-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-19 13:58 (implied halt Fri 09-19 13:59); no calendar entry; next bar Fri 09-19 14:01; 844 bars in the session
  - [thin_trading] 2025-09-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-22 13:57 (implied halt Mon 09-22 13:58); no calendar entry; next bar Mon 09-22 14:00; 848 bars in the session
  - [thin_trading] 2025-09-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 09-25 13:56 (implied halt Thu 09-25 13:57); no calendar entry; next bar Thu 09-25 14:00; 885 bars in the session
  - [thin_trading] 2025-10-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 10-07 13:57 (implied halt Tue 10-07 13:58); no calendar entry; next bar Tue 10-07 14:00; 762 bars in the session
  - [thin_trading] 2025-10-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 10-08 13:58 (implied halt Wed 10-08 13:59); no calendar entry; next bar Wed 10-08 14:00; 826 bars in the session
  - [thin_trading] 2025-10-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 10-13 13:58 (implied halt Mon 10-13 13:59); no calendar entry; next bar Mon 10-13 14:00; 735 bars in the session
  - [thin_trading] 2025-10-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 10-14 13:51 (implied halt Tue 10-14 13:52); no calendar entry; next bar Tue 10-14 14:12; 792 bars in the session
  - [thin_trading] 2025-10-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 10-15 13:50 (implied halt Wed 10-15 13:51); no calendar entry; next bar Wed 10-15 14:00; 734 bars in the session
  - [thin_trading] 2025-10-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 10-23 13:53 (implied halt Thu 10-23 13:54); no calendar entry; next bar Thu 10-23 14:00; 604 bars in the session
  - [thin_trading] 2025-10-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 10-24 13:56 (implied halt Fri 10-24 13:57); no calendar entry; next bar Fri 10-24 14:01; 637 bars in the session
  - [thin_trading] 2025-11-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 11-04 13:58 (implied halt Tue 11-04 13:59); no calendar entry; next bar Tue 11-04 14:00; 719 bars in the session
  - [thin_trading] 2025-11-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-07 13:57 (implied halt Fri 11-07 13:58); no calendar entry; next bar Fri 11-07 14:00; 694 bars in the session
  - [thin_trading] 2025-11-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 11-10 13:57 (implied halt Mon 11-10 13:58); no calendar entry; next bar Mon 11-10 14:00; 659 bars in the session
  - [thin_trading] 2025-11-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 11-12 13:54 (implied halt Wed 11-12 13:55); no calendar entry; next bar Wed 11-12 14:06; 596 bars in the session
  - [thin_trading] 2025-11-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 11-19 13:57 (implied halt Wed 11-19 13:58); no calendar entry; next bar Wed 11-19 14:02; 725 bars in the session
  - [thin_trading] 2025-11-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-20 13:51 (implied halt Thu 11-20 13:52); no calendar entry; next bar Thu 11-20 14:04; 705 bars in the session
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:45 (implied halt Thu 11-27 13:46); no calendar entry; next bar Thu 11-27 14:32; 498 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - [thin_trading] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-28 13:39 (implied halt Fri 11-28 13:40); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 243 bars in the session
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:39 != expected Fri 11-28 13:44
  - [thin_trading] 2025-12-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 12-04 13:58 (implied halt Thu 12-04 13:59); no calendar entry; next bar Thu 12-04 14:00; 594 bars in the session
  - [thin_trading] 2025-12-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 12-12 13:21 (implied halt Fri 12-12 13:22); no calendar entry; next bar Fri 12-12 14:29; 136 bars in the session
  - [thin_trading] 2025-12-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 12-16 13:55 (implied halt Tue 12-16 13:56); no calendar entry; next bar Tue 12-16 14:00; 629 bars in the session
  - [thin_trading] 2025-12-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 12-18 13:48 (implied halt Thu 12-18 13:49); no calendar entry; next bar Thu 12-18 14:22; 596 bars in the session
  - [thin_trading] 2025-12-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 12-24 12:42 (implied halt Wed 12-24 12:43); listed early_halt 12:45 (Christmas Eve); next bar Thu 12-25 17:01; 476 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: last bar Wed 12-24 12:42 != expected Wed 12-24 12:44; first bar after Thu 12-25 17:01 != reopen Thu 12-25 17:00
  - [thin_trading] 2025-12-25 listed_entry_not_observed: Christmas Day, full closure: first bar after Thu 12-25 17:01 != reopen Thu 12-25 17:00
  - [thin_trading] 2025-12-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 12-26 13:45 (implied halt Fri 12-26 13:46); no calendar entry; next bar Fri 12-26 14:00; 550 bars in the session
  - [thin_trading] 2025-12-31 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 12-31 13:58 (implied halt Wed 12-31 13:59); no calendar entry; next bar Wed 12-31 14:00; 620 bars in the session
  - [thin_trading] 2026-01-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 01-07 13:46 (implied halt Wed 01-07 13:47); no calendar entry; next bar Wed 01-07 14:00; 602 bars in the session
  - [thin_trading] 2026-01-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 01-08 13:57 (implied halt Thu 01-08 13:58); no calendar entry; next bar Thu 01-08 14:02; 528 bars in the session
  - [thin_trading] 2026-01-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 01-16 13:58 (implied halt Fri 01-16 13:59); no calendar entry; next bar Fri 01-16 14:00; 482 bars in the session
  - [thin_trading] 2026-01-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 01-19 13:58 (implied halt Mon 01-19 13:59); no calendar entry; next bar Mon 01-19 14:01; 592 bars in the session
  - [thin_trading] 2026-01-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 01-22 13:58 (implied halt Thu 01-22 13:59); no calendar entry; next bar Thu 01-22 14:05; 631 bars in the session
  - [thin_trading] 2026-01-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 01-29 13:57 (implied halt Thu 01-29 13:58); no calendar entry; next bar Thu 01-29 14:00; 1064 bars in the session
  - [thin_trading] 2026-02-05 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 02-05 13:55 (implied halt Thu 02-05 13:56); no calendar entry; next bar Thu 02-05 14:02; 831 bars in the session
  - [thin_trading] 2026-02-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 02-06 13:58 (implied halt Fri 02-06 13:59); no calendar entry; next bar Fri 02-06 14:02; 741 bars in the session
  - [thin_trading] 2026-02-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-09 13:58 (implied halt Mon 02-09 13:59); no calendar entry; next bar Mon 02-09 14:00; 855 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-16 13:57 (implied halt Mon 02-16 13:58); no calendar entry; next bar Mon 02-16 14:01; 385 bars in the session
  - [thin_trading] 2026-02-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 02-24 13:54 (implied halt Tue 02-24 13:55); no calendar entry; next bar Tue 02-24 14:02; 710 bars in the session
  - [thin_trading] 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 02-25 13:46 (implied halt Wed 02-25 13:47); no calendar entry; next bar Wed 02-25 14:01; 709 bars in the session
  - [thin_trading] 2026-03-02 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 03-02 13:57 (implied halt Mon 03-02 13:58); no calendar entry; next bar Mon 03-02 14:00; 1061 bars in the session
  - [thin_trading] 2026-03-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 03-13 13:57 (implied halt Fri 03-13 13:58); no calendar entry; next bar Fri 03-13 14:11; 243 bars in the session
  - [thin_trading] 2026-04-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 04-03 10:12 (implied halt Fri 04-03 10:13); listed early_halt 10:15 (Good Friday (abbreviated, jobs report)); next bar Sun 04-05 17:00; 251 bars in the session
  - [thin_trading] 2026-04-03 listed_entry_not_observed: Good Friday (abbreviated, jobs report), early halt 10:15: last bar Fri 04-03 10:12 != expected Fri 04-03 10:14
  - [thin_trading] 2026-04-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 04-06 13:58 (implied halt Mon 04-06 13:59); no calendar entry; next bar Mon 04-06 14:00; 748 bars in the session
  - [thin_trading] 2026-04-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 04-27 13:58 (implied halt Mon 04-27 13:59); no calendar entry; next bar Mon 04-27 14:00; 639 bars in the session
  - [thin_trading] 2026-04-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 04-28 13:57 (implied halt Tue 04-28 13:58); no calendar entry; next bar Tue 04-28 14:00; 690 bars in the session
  - [thin_trading] 2026-05-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-12 13:58 (implied halt Tue 05-12 13:59); no calendar entry; next bar Tue 05-12 14:00; 719 bars in the session
  - [thin_trading] 2026-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-26 13:55 (implied halt Tue 05-26 13:56); no calendar entry; next bar Tue 05-26 14:00; 583 bars in the session
  - [thin_trading] 2026-06-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 06-09 13:55 (implied halt Tue 06-09 13:56); no calendar entry; next bar Tue 06-09 14:00; 787 bars in the session
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 12:48 (implied halt Fri 06-12 12:49); no calendar entry; next bar Fri 06-12 14:48; 166 bars in the session
  - [thin_trading] 2026-06-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-19 11:58 (implied halt Fri 06-19 11:59); listed early_halt 12:00 (Juneteenth); next bar —; 664 bars in the session
  - [thin_trading] 2026-06-19 listed_entry_not_observed: Juneteenth, early halt 12:00: last bar Fri 06-19 11:58 != expected Fri 06-19 11:59
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:28, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:29 CT, 661 minutes
- **M6A**: weekdays 319, entries observed 7/9, discrepancies 64, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-02 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 04-02 13:57 (implied halt Wed 04-02 13:58); no calendar entry; next bar Wed 04-02 14:01; 1048 bars in the session
  - [thin_trading] 2025-04-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 04-17 13:57 (implied halt Thu 04-17 13:58); no calendar entry; next bar Thu 04-17 14:00; 1104 bars in the session
  - [thin_trading] 2025-05-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 05-16 13:58 (implied halt Fri 05-16 13:59); no calendar entry; next bar Fri 05-16 14:00; 985 bars in the session
  - [thin_trading] 2025-05-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-19 13:58 (implied halt Mon 05-19 13:59); no calendar entry; next bar Mon 05-19 14:00; 1014 bars in the session
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-26 13:52 (implied halt Mon 05-26 13:53); no calendar entry; next bar Mon 05-26 14:05; 906 bars in the session
  - [thin_trading] 2025-06-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 06-04 13:58 (implied halt Wed 06-04 13:59); no calendar entry; next bar Wed 06-04 14:00; 978 bars in the session
  - [thin_trading] 2025-06-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-06 13:58 (implied halt Fri 06-06 13:59); no calendar entry; next bar Fri 06-06 14:00; 841 bars in the session
  - [thin_trading] 2025-06-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-13 13:41 (implied halt Fri 06-13 13:42); no calendar entry; next bar Fri 06-13 14:11; 270 bars in the session
  - [thin_trading] 2025-06-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 06-16 13:57 (implied halt Mon 06-16 13:58); no calendar entry; next bar Mon 06-16 14:00; 957 bars in the session
  - [thin_trading] 2025-06-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-19 13:58 (implied halt Thu 06-19 13:59); no calendar entry; next bar Thu 06-19 14:02; 1012 bars in the session
  - [thin_trading] 2025-06-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 06-24 13:56 (implied halt Tue 06-24 13:57); no calendar entry; next bar Tue 06-24 14:00; 1093 bars in the session
  - [thin_trading] 2025-07-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-03 13:56 (implied halt Thu 07-03 13:57); no calendar entry; next bar Thu 07-03 14:00; 840 bars in the session
  - [thin_trading] 2025-07-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-07 13:58 (implied halt Mon 07-07 13:59); no calendar entry; next bar Mon 07-07 14:00; 1008 bars in the session
  - [thin_trading] 2025-07-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-10 13:57 (implied halt Thu 07-10 13:58); no calendar entry; next bar Thu 07-10 14:00; 977 bars in the session
  - [thin_trading] 2025-07-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 07-25 13:58 (implied halt Fri 07-25 13:59); no calendar entry; next bar Fri 07-25 14:01; 913 bars in the session
  - [thin_trading] 2025-07-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-28 13:57 (implied halt Mon 07-28 13:58); no calendar entry; next bar Mon 07-28 14:00; 964 bars in the session
  - [thin_trading] 2025-08-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 08-08 13:58 (implied halt Fri 08-08 13:59); no calendar entry; next bar Fri 08-08 14:01; 759 bars in the session
  - [thin_trading] 2025-08-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 08-19 13:57 (implied halt Tue 08-19 13:58); no calendar entry; next bar Tue 08-19 14:00; 771 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:56 (implied halt Mon 09-01 13:57); no calendar entry; next bar Mon 09-01 14:00; 579 bars in the session
  - [thin_trading] 2025-09-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-08 13:58 (implied halt Mon 09-08 13:59); no calendar entry; next bar Mon 09-08 14:00; 769 bars in the session
  - [thin_trading] 2025-09-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-09 13:55 (implied halt Tue 09-09 13:56); no calendar entry; next bar Tue 09-09 14:02; 762 bars in the session
  - [thin_trading] 2025-09-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 09-11 13:58 (implied halt Thu 09-11 13:59); no calendar entry; next bar Thu 09-11 14:00; 734 bars in the session
  - [thin_trading] 2025-09-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-12 13:47 (implied halt Fri 09-12 13:48); no calendar entry; next bar Fri 09-12 14:01; 234 bars in the session
  - [thin_trading] 2025-09-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-16 13:58 (implied halt Tue 09-16 13:59); no calendar entry; next bar Tue 09-16 14:01; 745 bars in the session
  - [thin_trading] 2025-09-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-23 13:58 (implied halt Tue 09-23 13:59); no calendar entry; next bar Tue 09-23 14:00; 754 bars in the session
  - [thin_trading] 2025-09-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 09-25 13:56 (implied halt Thu 09-25 13:57); no calendar entry; next bar Thu 09-25 14:00; 799 bars in the session
  - [thin_trading] 2025-10-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 10-07 13:58 (implied halt Tue 10-07 13:59); no calendar entry; next bar Tue 10-07 14:03; 713 bars in the session
  - [thin_trading] 2025-10-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 10-20 13:58 (implied halt Mon 10-20 13:59); no calendar entry; next bar Mon 10-20 14:00; 771 bars in the session
  - [thin_trading] 2025-10-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 10-22 13:56 (implied halt Wed 10-22 13:57); no calendar entry; next bar Wed 10-22 14:00; 810 bars in the session
  - [thin_trading] 2025-10-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 10-24 13:53 (implied halt Fri 10-24 13:54); no calendar entry; next bar Fri 10-24 14:00; 664 bars in the session
  - [thin_trading] 2025-10-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 10-28 13:57 (implied halt Tue 10-28 13:58); no calendar entry; next bar Tue 10-28 14:08; 747 bars in the session
  - [thin_trading] 2025-10-31 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 10-31 13:57 (implied halt Fri 10-31 13:58); no calendar entry; next bar Fri 10-31 14:00; 681 bars in the session
  - [thin_trading] 2025-11-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 11-04 13:57 (implied halt Tue 11-04 13:58); no calendar entry; next bar Tue 11-04 14:00; 776 bars in the session
  - [thin_trading] 2025-11-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-07 13:56 (implied halt Fri 11-07 13:57); no calendar entry; next bar Fri 11-07 14:01; 725 bars in the session
  - [thin_trading] 2025-11-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-13 13:58 (implied halt Thu 11-13 13:59); no calendar entry; next bar Thu 11-13 14:00; 830 bars in the session
  - [thin_trading] 2025-11-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 11-17 13:57 (implied halt Mon 11-17 13:58); no calendar entry; next bar Mon 11-17 14:00; 791 bars in the session
  - [thin_trading] 2025-11-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 11-18 13:56 (implied halt Tue 11-18 13:57); no calendar entry; next bar Tue 11-18 14:01; 861 bars in the session
  - [thin_trading] 2025-11-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-20 13:58 (implied halt Thu 11-20 13:59); no calendar entry; next bar Thu 11-20 14:00; 850 bars in the session
  - [thin_trading] 2025-11-21 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-21 13:57 (implied halt Fri 11-21 13:58); no calendar entry; next bar Fri 11-21 14:00; 816 bars in the session
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:56 (implied halt Thu 11-27 13:57); no calendar entry; next bar Thu 11-27 14:35; 554 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - [thin_trading] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-28 13:41 (implied halt Fri 11-28 13:42); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 296 bars in the session
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:41 != expected Fri 11-28 13:44
  - [thin_trading] 2025-12-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 12-08 13:57 (implied halt Mon 12-08 13:58); no calendar entry; next bar Mon 12-08 14:05; 640 bars in the session
  - [thin_trading] 2025-12-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 12-09 13:58 (implied halt Tue 12-09 13:59); no calendar entry; next bar Tue 12-09 14:00; 665 bars in the session
  - [thin_trading] 2025-12-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 12-12 13:43 (implied halt Fri 12-12 13:44); no calendar entry; next bar Fri 12-12 14:14; 221 bars in the session
  - [thin_trading] 2025-12-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 12-22 13:58 (implied halt Mon 12-22 13:59); no calendar entry; next bar Mon 12-22 14:00; 694 bars in the session
  - [thin_trading] 2026-01-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 01-09 13:54 (implied halt Fri 01-09 13:55); no calendar entry; next bar Fri 01-09 14:01; 706 bars in the session
  - [thin_trading] 2026-01-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 01-13 13:51 (implied halt Tue 01-13 13:52); no calendar entry; next bar Tue 01-13 14:00; 683 bars in the session
  - [thin_trading] 2026-01-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 01-16 13:57 (implied halt Fri 01-16 13:58); no calendar entry; next bar Fri 01-16 14:00; 642 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-16 13:52 (implied halt Mon 02-16 13:53); no calendar entry; next bar Mon 02-16 14:02; 723 bars in the session
  - [thin_trading] 2026-02-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 02-24 13:58 (implied halt Tue 02-24 13:59); no calendar entry; next bar Tue 02-24 14:01; 927 bars in the session
  - [thin_trading] 2026-02-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 02-26 13:58 (implied halt Thu 02-26 13:59); no calendar entry; next bar Thu 02-26 14:00; 966 bars in the session
  - [thin_trading] 2026-03-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 03-11 13:58 (implied halt Wed 03-11 13:59); no calendar entry; next bar Wed 03-11 14:00; 1071 bars in the session
  - [thin_trading] 2026-03-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 03-17 13:58 (implied halt Tue 03-17 13:59); no calendar entry; next bar Tue 03-17 14:00; 1056 bars in the session
  - [thin_trading] 2026-03-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 03-24 13:58 (implied halt Tue 03-24 13:59); no calendar entry; next bar Tue 03-24 14:00; 1139 bars in the session
  - [thin_trading] 2026-04-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 04-14 13:57 (implied halt Tue 04-14 13:58); no calendar entry; next bar Tue 04-14 14:00; 948 bars in the session
  - [thin_trading] 2026-05-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-06 13:58 (implied halt Wed 05-06 13:59); no calendar entry; next bar Wed 05-06 14:00; 988 bars in the session
  - [thin_trading] 2026-05-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-19 13:56 (implied halt Tue 05-19 13:57); no calendar entry; next bar Tue 05-19 14:00; 857 bars in the session
  - [thin_trading] 2026-05-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-25 13:51 (implied halt Mon 05-25 13:52); no calendar entry; next bar Mon 05-25 14:05; 571 bars in the session
  - [thin_trading] 2026-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-26 13:58 (implied halt Tue 05-26 13:59); no calendar entry; next bar Tue 05-26 14:00; 644 bars in the session
  - [thin_trading] 2026-06-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-04 13:58 (implied halt Thu 06-04 13:59); no calendar entry; next bar Thu 06-04 14:00; 664 bars in the session
  - [thin_trading] 2026-06-05 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-05 13:58 (implied halt Fri 06-05 13:59); no calendar entry; next bar Fri 06-05 14:00; 822 bars in the session
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 13:50 (implied halt Fri 06-12 13:51); no calendar entry; next bar Fri 06-12 14:05; 209 bars in the session
  - [thin_trading] 2026-06-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 06-15 13:56 (implied halt Mon 06-15 13:57); no calendar entry; next bar Mon 06-15 14:03; 639 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:47, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:48 CT, 642 minutes
- **M6B**: weekdays 319, entries observed 6/9, discrepancies 57, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-02 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 04-02 13:56 (implied halt Wed 04-02 13:57); no calendar entry; next bar Wed 04-02 14:04; 590 bars in the session
  - [thin_trading] 2025-04-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 04-17 13:57 (implied halt Thu 04-17 13:58); no calendar entry; next bar Thu 04-17 14:00; 759 bars in the session
  - [thin_trading] 2025-04-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 04-24 13:56 (implied halt Thu 04-24 13:57); no calendar entry; next bar Thu 04-24 14:01; 652 bars in the session
  - [thin_trading] 2025-05-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-19 13:58 (implied halt Mon 05-19 13:59); no calendar entry; next bar Mon 05-19 14:02; 712 bars in the session
  - [thin_trading] 2025-05-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-20 13:54 (implied halt Tue 05-20 13:55); no calendar entry; next bar Tue 05-20 14:03; 708 bars in the session
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-26 13:57 (implied halt Mon 05-26 13:58); no calendar entry; next bar Mon 05-26 14:03; 577 bars in the session
  - [thin_trading] 2025-05-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-28 13:58 (implied halt Wed 05-28 13:59); no calendar entry; next bar Wed 05-28 14:07; 727 bars in the session
  - [thin_trading] 2025-06-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 06-03 13:58 (implied halt Tue 06-03 13:59); no calendar entry; next bar Tue 06-03 14:08; 588 bars in the session
  - [thin_trading] 2025-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-12 13:57 (implied halt Thu 06-12 13:58); no calendar entry; next bar Thu 06-12 14:00; 702 bars in the session
  - [thin_trading] 2025-06-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 06-16 13:56 (implied halt Mon 06-16 13:57); no calendar entry; next bar Mon 06-16 14:00; 578 bars in the session
  - [thin_trading] 2025-06-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 06-19 13:58 (implied halt Thu 06-19 13:59); no calendar entry; next bar Thu 06-19 14:04; 729 bars in the session
  - [thin_trading] 2025-07-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-03 13:55 (implied halt Thu 07-03 13:56); no calendar entry; next bar Thu 07-03 14:03; 766 bars in the session
  - [thin_trading] 2025-07-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-14 13:58 (implied halt Mon 07-14 13:59); no calendar entry; next bar Mon 07-14 14:01; 744 bars in the session
  - [thin_trading] 2025-07-21 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-21 13:56 (implied halt Mon 07-21 13:57); no calendar entry; next bar Mon 07-21 14:00; 666 bars in the session
  - [thin_trading] 2025-07-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 07-24 13:56 (implied halt Thu 07-24 13:57); no calendar entry; next bar Thu 07-24 14:01; 681 bars in the session
  - [thin_trading] 2025-07-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 07-28 13:58 (implied halt Mon 07-28 13:59); no calendar entry; next bar Mon 07-28 14:00; 798 bars in the session
  - [thin_trading] 2025-08-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 08-11 13:58 (implied halt Mon 08-11 13:59); no calendar entry; next bar Mon 08-11 14:05; 634 bars in the session
  - [thin_trading] 2025-08-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 08-12 13:58 (implied halt Tue 08-12 13:59); no calendar entry; next bar Tue 08-12 14:03; 591 bars in the session
  - [thin_trading] 2025-08-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 08-15 13:55 (implied halt Fri 08-15 13:56); no calendar entry; next bar Fri 08-15 14:00; 523 bars in the session
  - [thin_trading] 2025-08-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 08-26 13:56 (implied halt Tue 08-26 13:57); no calendar entry; next bar Tue 08-26 14:00; 626 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-01 13:58 (implied halt Mon 09-01 13:59); no calendar entry; next bar Mon 09-01 14:19; 421 bars in the session
  - [thin_trading] 2025-09-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 09-03 13:46 (implied halt Wed 09-03 13:47); no calendar entry; next bar Wed 09-03 14:00; 678 bars in the session
  - [thin_trading] 2025-09-09 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-09 13:58 (implied halt Tue 09-09 13:59); no calendar entry; next bar Tue 09-09 14:02; 617 bars in the session
  - [thin_trading] 2025-09-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-12 13:51 (implied halt Fri 09-12 13:52); no calendar entry; next bar Fri 09-12 14:01; 200 bars in the session
  - [thin_trading] 2025-09-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-19 13:58 (implied halt Fri 09-19 13:59); no calendar entry; next bar Fri 09-19 14:00; 703 bars in the session
  - [thin_trading] 2025-09-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 09-22 13:57 (implied halt Mon 09-22 13:58); no calendar entry; next bar Mon 09-22 14:00; 647 bars in the session
  - [thin_trading] 2025-09-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-23 13:57 (implied halt Tue 09-23 13:58); no calendar entry; next bar Tue 09-23 14:01; 577 bars in the session
  - [thin_trading] 2025-09-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 09-25 13:57 (implied halt Thu 09-25 13:58); no calendar entry; next bar Thu 09-25 14:00; 668 bars in the session
  - [thin_trading] 2025-09-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 09-30 13:58 (implied halt Tue 09-30 13:59); no calendar entry; next bar Tue 09-30 14:00; 590 bars in the session
  - [thin_trading] 2025-10-02 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 10-02 13:56 (implied halt Thu 10-02 13:57); no calendar entry; next bar Thu 10-02 14:00; 537 bars in the session
  - [thin_trading] 2025-10-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 10-06 13:56 (implied halt Mon 10-06 13:57); no calendar entry; next bar Mon 10-06 14:00; 636 bars in the session
  - [thin_trading] 2025-10-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 10-14 13:53 (implied halt Tue 10-14 13:54); no calendar entry; next bar Tue 10-14 14:03; 603 bars in the session
  - [thin_trading] 2025-10-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 10-22 13:58 (implied halt Wed 10-22 13:59); no calendar entry; next bar Wed 10-22 14:00; 628 bars in the session
  - [thin_trading] 2025-10-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 10-27 13:57 (implied halt Mon 10-27 13:58); no calendar entry; next bar Mon 10-27 14:00; 536 bars in the session
  - [thin_trading] 2025-11-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 11-11 13:58 (implied halt Tue 11-11 13:59); no calendar entry; next bar Tue 11-11 14:00; 595 bars in the session
  - [thin_trading] 2025-11-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 11-17 13:58 (implied halt Mon 11-17 13:59); no calendar entry; next bar Mon 11-17 14:00; 628 bars in the session
  - [thin_trading] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 11-28 13:41 (implied halt Fri 11-28 13:42); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 248 bars in the session
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:41 != expected Fri 11-28 13:44
  - [thin_trading] 2025-12-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 12-08 13:56 (implied halt Mon 12-08 13:57); no calendar entry; next bar Mon 12-08 14:00; 495 bars in the session
  - [thin_trading] 2025-12-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 12-12 13:45 (implied halt Fri 12-12 13:46); no calendar entry; next bar Fri 12-12 14:11; 175 bars in the session
  - [thin_trading] 2026-01-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 01-15 13:56 (implied halt Thu 01-15 13:57); no calendar entry; next bar Thu 01-15 14:01; 590 bars in the session
  - [thin_trading] 2026-01-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 01-19 13:50 (implied halt Mon 01-19 13:51); no calendar entry; next bar Mon 01-19 14:04; 558 bars in the session
  - [thin_trading] 2026-02-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 02-12 13:57 (implied halt Thu 02-12 13:58); no calendar entry; next bar Thu 02-12 14:01; 748 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-16 13:57 (implied halt Mon 02-16 13:58); no calendar entry; next bar Mon 02-16 14:03; 415 bars in the session
  - [thin_trading] 2026-02-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 02-17 13:58 (implied halt Tue 02-17 13:59); no calendar entry; next bar Tue 02-17 14:01; 727 bars in the session
  - [thin_trading] 2026-03-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 03-12 13:57 (implied halt Thu 03-12 13:58); no calendar entry; next bar Thu 03-12 14:00; 633 bars in the session
  - [thin_trading] 2026-04-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 04-03 10:12 (implied halt Fri 04-03 10:13); listed early_halt 10:15 (Good Friday (abbreviated, jobs report)); next bar Sun 04-05 17:00; 323 bars in the session
  - [thin_trading] 2026-04-03 listed_entry_not_observed: Good Friday (abbreviated, jobs report), early halt 10:15: last bar Fri 04-03 10:12 != expected Fri 04-03 10:14
  - [thin_trading] 2026-04-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 04-28 13:55 (implied halt Tue 04-28 13:56); no calendar entry; next bar Tue 04-28 14:00; 635 bars in the session
  - [thin_trading] 2026-05-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 05-08 13:53 (implied halt Fri 05-08 13:54); no calendar entry; next bar Fri 05-08 14:01; 594 bars in the session
  - [thin_trading] 2026-05-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-11 13:57 (implied halt Mon 05-11 13:58); no calendar entry; next bar Mon 05-11 14:00; 655 bars in the session
  - [thin_trading] 2026-05-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-13 13:58 (implied halt Wed 05-13 13:59); no calendar entry; next bar Wed 05-13 14:03; 637 bars in the session
  - [thin_trading] 2026-05-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 05-22 13:51 (implied halt Fri 05-22 13:52); no calendar entry; next bar Fri 05-22 14:00; 477 bars in the session
  - [thin_trading] 2026-05-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 05-25 13:38 (implied halt Mon 05-25 13:39); no calendar entry; next bar Mon 05-25 14:27; 358 bars in the session
  - [thin_trading] 2026-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Tue 05-26 13:57 (implied halt Tue 05-26 13:58); no calendar entry; next bar Tue 05-26 14:03; 527 bars in the session
  - [thin_trading] 2026-05-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Wed 05-27 13:58 (implied halt Wed 05-27 13:59); no calendar entry; next bar Wed 05-27 14:00; 465 bars in the session
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 13:57 (implied halt Fri 06-12 13:58); no calendar entry; next bar Fri 06-12 14:15; 127 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **M6E**: weekdays 319, entries observed 9/9, discrepancies 9, bars inside a scheduled closure 0
  - [thin_trading] 2025-09-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 09-19 13:58 (implied halt Fri 09-19 13:59); no calendar entry; next bar Fri 09-19 14:00; 1265 bars in the session
  - [calendar_question] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 11-27 13:55 (implied halt Thu 11-27 13:56); no calendar entry; next bar Thu 11-27 14:00; 965 bars in the session Lead ruling: L-5: thin holiday trading (Thanksgiving, FX keeps its regular hours); no calendar change.
  - [thin_trading] 2025-12-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 12-12 13:49 (implied halt Fri 12-12 13:50); no calendar entry; next bar Fri 12-12 14:04; 506 bars in the session
  - [thin_trading] 2026-01-08 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 01-08 13:58 (implied halt Thu 01-08 13:59); no calendar entry; next bar Thu 01-08 14:00; 1160 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Mon 02-16 13:57 (implied halt Mon 02-16 13:58); no calendar entry; next bar Mon 02-16 14:01; 960 bars in the session
  - [thin_trading] 2026-03-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 03-13 13:57 (implied halt Fri 03-13 13:58); no calendar entry; next bar Fri 03-13 14:01; 631 bars in the session
  - [thin_trading] 2026-03-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 03-27 13:58 (implied halt Fri 03-27 13:59); no calendar entry; next bar Fri 03-27 14:00; 1232 bars in the session
  - [thin_trading] 2026-05-14 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Thu 05-14 13:58 (implied halt Thu 05-14 13:59); no calendar entry; next bar Thu 05-14 14:00; 1061 bars in the session
  - [thin_trading] 2026-06-12 early_stop_not_a_listed_early_halt_at_that_time: last bar before 14:00 CT Fri 06-12 13:56 (implied halt Fri 06-12 13:57); no calendar entry; next bar Fri 06-12 14:01; 456 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:47, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:48 CT, 642 minutes

## energy

Most liquid: CL. Entries checked: 2025-04-18 full_closure, 2025-05-26 early_halt, 2025-06-19 early_halt, 2025-07-04 early_halt, 2025-09-01 early_halt, 2025-11-27 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 early_halt, 2026-02-16 early_halt, 2026-04-03 full_closure, 2026-05-25 early_halt, 2026-06-19 early_halt, 2025-11-28 late_open

### Calendar questions

- none

### Per contract

- **CL**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:47, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:48 CT, 642 minutes
- **HO**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:46, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:47 CT, 643 minutes
- **MCL**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:46, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:47 CT, 643 minutes
- **MNG**: weekdays 319, entries observed 15/16, discrepancies 12, bars inside a scheduled closure 0
  - [thin_trading] 2025-05-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 05-23 13:26 (implied halt Fri 05-23 13:27); no calendar entry; next bar Fri 05-23 13:30; 550 bars in the session
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 05-26 13:28 (implied halt Mon 05-26 13:29); listed early_halt 13:30 (Memorial Day); next bar Mon 05-26 17:00; 638 bars in the session
  - [thin_trading] 2025-05-26 listed_entry_not_observed: Memorial Day, early halt 13:30: last bar Mon 05-26 13:28 != expected Mon 05-26 13:29
  - [thin_trading] 2025-07-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 07-25 13:28 (implied halt Fri 07-25 13:29); no calendar entry; next bar Fri 07-25 13:47; 440 bars in the session
  - [thin_trading] 2025-08-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 08-25 13:28 (implied halt Mon 08-25 13:29); no calendar entry; next bar Mon 08-25 13:31; 603 bars in the session
  - [thin_trading] 2025-08-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 08-26 13:28 (implied halt Tue 08-26 13:29); no calendar entry; next bar Tue 08-26 19:00; 263 bars in the session
  - [thin_trading] 2025-09-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 09-23 13:28 (implied halt Tue 09-23 13:29); no calendar entry; next bar Tue 09-23 13:30; 713 bars in the session
  - [thin_trading] 2025-10-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 10-28 13:28 (implied halt Tue 10-28 13:29); no calendar entry; next bar Tue 10-28 19:00; 259 bars in the session
  - [thin_trading] 2026-01-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 01-27 13:28 (implied halt Tue 01-27 13:29); no calendar entry; next bar Tue 01-27 18:00; 229 bars in the session
  - [thin_trading] 2026-03-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 03-25 13:28 (implied halt Wed 03-25 13:29); no calendar entry; next bar Wed 03-25 13:36; 494 bars in the session
  - [thin_trading] 2026-04-22 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 04-22 13:28 (implied halt Wed 04-22 13:29); no calendar entry; next bar Wed 04-22 13:30; 770 bars in the session
  - [thin_trading] 2026-05-21 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 05-21 13:28 (implied halt Thu 05-21 13:29); no calendar entry; next bar Thu 05-21 13:30; 769 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:46, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:47 CT, 643 minutes
- **NG**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:46, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:47 CT, 643 minutes
- **QG**: weekdays 319, entries observed 11/16, discrepancies 40, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 04-23 13:28 (implied halt Wed 04-23 13:29); no calendar entry; next bar Wed 04-23 13:35; 282 bars in the session
  - [thin_trading] 2025-04-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 04-29 13:28 (implied halt Tue 04-29 13:29); no calendar entry; next bar Tue 04-29 13:30; 623 bars in the session
  - [thin_trading] 2025-05-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 05-01 13:28 (implied halt Thu 05-01 13:29); no calendar entry; next bar Thu 05-01 13:30; 579 bars in the session
  - [thin_trading] 2025-05-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 05-19 13:28 (implied halt Mon 05-19 13:29); no calendar entry; next bar Mon 05-19 13:30; 542 bars in the session
  - [thin_trading] 2025-05-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 05-26 13:28 (implied halt Mon 05-26 13:29); listed early_halt 13:30 (Memorial Day); next bar Mon 05-26 17:00; 376 bars in the session
  - [thin_trading] 2025-05-26 listed_entry_not_observed: Memorial Day, early halt 13:30: last bar Mon 05-26 13:28 != expected Mon 05-26 13:29
  - [thin_trading] 2025-06-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 06-10 13:28 (implied halt Tue 06-10 13:29); no calendar entry; next bar Tue 06-10 13:30; 553 bars in the session
  - [thin_trading] 2025-07-03 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 07-03 13:28 (implied halt Thu 07-03 13:29); no calendar entry; next bar Thu 07-03 13:33; 579 bars in the session
  - [thin_trading] 2025-07-04 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 07-04 11:54 (implied halt Fri 07-04 11:55); listed early_halt 12:00 (Independence Day); next bar Sun 07-06 17:00; 312 bars in the session
  - [thin_trading] 2025-07-04 listed_entry_not_observed: Independence Day, early halt 12:00: last bar Fri 07-04 11:54 != expected Fri 07-04 11:59
  - [thin_trading] 2025-07-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 07-16 13:28 (implied halt Wed 07-16 13:29); no calendar entry; next bar Wed 07-16 13:30; 512 bars in the session
  - [thin_trading] 2025-07-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 07-23 13:28 (implied halt Wed 07-23 13:29); no calendar entry; next bar Wed 07-23 13:30; 510 bars in the session
  - [thin_trading] 2025-07-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 07-24 13:28 (implied halt Thu 07-24 13:29); no calendar entry; next bar Thu 07-24 13:30; 324 bars in the session
  - [thin_trading] 2025-08-13 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 08-13 13:28 (implied halt Wed 08-13 13:29); no calendar entry; next bar Wed 08-13 13:30; 505 bars in the session
  - [thin_trading] 2025-08-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 08-20 13:28 (implied halt Wed 08-20 13:29); no calendar entry; next bar Wed 08-20 13:31; 387 bars in the session
  - [thin_trading] 2025-09-11 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 09-11 13:28 (implied halt Thu 09-11 13:29); no calendar entry; next bar Thu 09-11 13:30; 464 bars in the session
  - [thin_trading] 2025-09-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 09-23 13:28 (implied halt Tue 09-23 13:29); no calendar entry; next bar Tue 09-23 13:30; 282 bars in the session
  - [thin_trading] 2025-09-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 09-24 13:21 (implied halt Wed 09-24 13:22); no calendar entry; next bar Wed 09-24 13:35; 192 bars in the session
  - [thin_trading] 2025-10-02 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 10-02 13:28 (implied halt Thu 10-02 13:29); no calendar entry; next bar Thu 10-02 13:30; 551 bars in the session
  - [thin_trading] 2025-10-07 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 10-07 13:28 (implied halt Tue 10-07 13:29); no calendar entry; next bar Tue 10-07 13:30; 573 bars in the session
  - [thin_trading] 2025-10-23 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 10-23 13:28 (implied halt Thu 10-23 13:29); no calendar entry; next bar Thu 10-23 13:30; 549 bars in the session
  - [thin_trading] 2025-11-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 11-19 13:27 (implied halt Wed 11-19 13:28); no calendar entry; next bar Wed 11-19 13:30; 578 bars in the session
  - [thin_trading] 2025-11-21 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 11-21 13:27 (implied halt Fri 11-21 13:28); no calendar entry; next bar Fri 11-21 13:32; 282 bars in the session
  - [thin_trading] 2025-12-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 12-16 13:28 (implied halt Tue 12-16 13:29); no calendar entry; next bar Tue 12-16 13:32; 699 bars in the session
  - [thin_trading] 2025-12-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 12-24 12:40 (implied halt Wed 12-24 12:41); listed early_halt 12:45 (Christmas Eve); next bar Thu 12-25 17:00; 406 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: last bar Wed 12-24 12:40 != expected Wed 12-24 12:44
  - [thin_trading] 2026-02-05 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 02-05 13:28 (implied halt Thu 02-05 13:29); no calendar entry; next bar Thu 02-05 13:30; 838 bars in the session
  - [thin_trading] 2026-02-16 listed_entry_not_observed: Presidents Day, early halt 13:30: first bar after Mon 02-16 17:01 != reopen Mon 02-16 17:00
  - [thin_trading] 2026-02-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 02-19 13:28 (implied halt Thu 02-19 13:29); no calendar entry; next bar Thu 02-19 13:37; 656 bars in the session
  - [thin_trading] 2026-03-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 03-17 13:28 (implied halt Tue 03-17 13:29); no calendar entry; next bar Tue 03-17 13:30; 471 bars in the session
  - [thin_trading] 2026-03-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 03-24 13:11 (implied halt Tue 03-24 13:12); no calendar entry; next bar Tue 03-24 13:30; 244 bars in the session
  - [thin_trading] 2026-03-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 03-25 13:25 (implied halt Wed 03-25 13:26); no calendar entry; next bar Wed 03-25 13:33; 181 bars in the session
  - [thin_trading] 2026-04-06 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 04-06 13:28 (implied halt Mon 04-06 13:29); no calendar entry; next bar Mon 04-06 13:31; 474 bars in the session
  - [thin_trading] 2026-04-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 04-15 13:28 (implied halt Wed 04-15 13:29); no calendar entry; next bar Wed 04-15 13:30; 304 bars in the session
  - [thin_trading] 2026-04-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 04-17 13:28 (implied halt Fri 04-17 13:29); no calendar entry; next bar Fri 04-17 13:30; 454 bars in the session
  - [thin_trading] 2026-04-20 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 04-20 13:28 (implied halt Mon 04-20 13:29); no calendar entry; next bar Mon 04-20 13:30; 332 bars in the session
  - [thin_trading] 2026-05-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 05-01 13:28 (implied halt Fri 05-01 13:29); no calendar entry; next bar Fri 05-01 13:30; 369 bars in the session
  - [thin_trading] 2026-05-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 05-25 13:24 (implied halt Mon 05-25 13:25); listed early_halt 13:30 (Memorial Day); next bar Mon 05-25 17:02; 343 bars in the session
  - [thin_trading] 2026-05-25 listed_entry_not_observed: Memorial Day, early halt 13:30: last bar Mon 05-25 13:24 != expected Mon 05-25 13:29; first bar after Mon 05-25 17:02 != reopen Mon 05-25 17:00
  - [thin_trading] 2026-06-10 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 06-10 13:28 (implied halt Wed 06-10 13:29); no calendar entry; next bar Wed 06-10 13:30; 469 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:44, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 17:31 CT, 42 minutes
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:45 CT, 645 minutes
- **QM**: weekdays 319, entries observed 8/16, discrepancies 33, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 04-17 13:28 (implied halt Thu 04-17 13:29); no calendar entry; next bar Thu 04-17 13:30; 279 bars in the session
  - [thin_trading] 2025-06-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 06-17 13:28 (implied halt Tue 06-17 13:29); no calendar entry; next bar Tue 06-17 13:30; 509 bars in the session
  - [thin_trading] 2025-06-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 06-18 13:20 (implied halt Wed 06-18 13:21); no calendar entry; next bar Wed 06-18 19:00; 104 bars in the session
  - [thin_trading] 2025-06-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 06-19 13:28 (implied halt Thu 06-19 13:29); listed early_halt 13:30 (Juneteenth); next bar Thu 06-19 17:00; 842 bars in the session
  - [thin_trading] 2025-06-19 listed_entry_not_observed: Juneteenth, early halt 13:30: last bar Thu 06-19 13:28 != expected Thu 06-19 13:29
  - [thin_trading] 2025-07-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 07-16 13:28 (implied halt Wed 07-16 13:29); no calendar entry; next bar Wed 07-16 13:30; 692 bars in the session
  - [thin_trading] 2025-08-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 08-18 13:28 (implied halt Mon 08-18 13:29); no calendar entry; next bar Mon 08-18 14:00; 267 bars in the session
  - [thin_trading] 2025-08-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 08-19 13:27 (implied halt Tue 08-19 13:28); no calendar entry; next bar Tue 08-19 19:00; 79 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 09-01 13:28 (implied halt Mon 09-01 13:29); listed early_halt 13:30 (Labor Day); next bar Mon 09-01 17:00; 485 bars in the session
  - [thin_trading] 2025-09-01 listed_entry_not_observed: Labor Day, early halt 13:30: last bar Mon 09-01 13:28 != expected Mon 09-01 13:29
  - [thin_trading] 2025-09-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 09-18 13:28 (implied halt Thu 09-18 13:29); no calendar entry; next bar Thu 09-18 13:34; 256 bars in the session
  - [thin_trading] 2025-09-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 09-19 13:09 (implied halt Fri 09-19 13:10); no calendar entry; next bar Sun 09-21 17:00; 78 bars in the session
  - [thin_trading] 2025-10-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 10-17 13:28 (implied halt Fri 10-17 13:29); no calendar entry; next bar Fri 10-17 13:30; 312 bars in the session
  - [thin_trading] 2025-11-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Tue 11-18 13:28 (implied halt Tue 11-18 13:29); no calendar entry; next bar Tue 11-18 13:45; 191 bars in the session
  - [thin_trading] 2025-11-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 11-19 13:12 (implied halt Wed 11-19 13:13); no calendar entry; next bar Wed 11-19 18:01; 110 bars in the session
  - [thin_trading] 2025-11-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 11-27 13:27 (implied halt Thu 11-27 13:28); listed early_halt 13:30 (Thanksgiving Day); next bar Thu 11-27 17:00; 410 bars in the session
  - [thin_trading] 2025-11-27 listed_entry_not_observed: Thanksgiving Day, early halt 13:30: last bar Thu 11-27 13:27 != expected Thu 11-27 13:29
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:43 != expected Fri 11-28 13:44
  - [thin_trading] 2025-12-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 12-17 13:28 (implied halt Wed 12-17 13:29); no calendar entry; next bar Wed 12-17 13:58; 212 bars in the session
  - [thin_trading] 2025-12-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 12-19 13:28 (implied halt Fri 12-19 13:29); no calendar entry; next bar Fri 12-19 13:30; 608 bars in the session
  - [thin_trading] 2025-12-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 12-24 12:41 (implied halt Wed 12-24 12:42); listed early_halt 12:45 (Christmas Eve); next bar Thu 12-25 17:00; 431 bars in the session
  - [thin_trading] 2025-12-24 listed_entry_not_observed: Christmas Eve, early halt 12:45: last bar Wed 12-24 12:41 != expected Wed 12-24 12:44
  - [thin_trading] 2026-01-05 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 01-05 13:28 (implied halt Mon 01-05 13:29); no calendar entry; next bar Mon 01-05 13:30; 787 bars in the session
  - [thin_trading] 2026-01-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 01-16 13:12 (implied halt Fri 01-16 13:13); no calendar entry; next bar Sun 01-18 17:00; 81 bars in the session
  - [thin_trading] 2026-02-16 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 02-16 13:25 (implied halt Mon 02-16 13:26); listed early_halt 13:30 (Presidents Day); next bar Mon 02-16 17:00; 483 bars in the session
  - [thin_trading] 2026-02-16 listed_entry_not_observed: Presidents Day, early halt 13:30: last bar Mon 02-16 13:25 != expected Mon 02-16 13:29
  - [thin_trading] 2026-02-18 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 02-18 13:28 (implied halt Wed 02-18 13:29); no calendar entry; next bar Wed 02-18 13:31; 250 bars in the session
  - [thin_trading] 2026-02-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 02-19 13:26 (implied halt Thu 02-19 13:27); no calendar entry; next bar Thu 02-19 18:01; 142 bars in the session
  - [thin_trading] 2026-03-19 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Thu 03-19 13:25 (implied halt Thu 03-19 13:26); no calendar entry; next bar Thu 03-19 19:00; 287 bars in the session
  - [thin_trading] 2026-05-15 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Fri 05-15 13:28 (implied halt Fri 05-15 13:29); no calendar entry; next bar Fri 05-15 13:30; 421 bars in the session
  - [thin_trading] 2026-05-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Mon 05-25 13:26 (implied halt Mon 05-25 13:27); listed early_halt 13:30 (Memorial Day); next bar Mon 05-25 17:00; 948 bars in the session
  - [thin_trading] 2026-05-25 listed_entry_not_observed: Memorial Day, early halt 13:30: last bar Mon 05-25 13:26 != expected Mon 05-25 13:29
  - [thin_trading] 2026-06-17 early_stop_not_a_listed_early_halt_at_that_time: last bar before 13:30 CT Wed 06-17 13:28 (implied halt Wed 06-17 13:29); no calendar entry; next bar Wed 06-17 13:36; 292 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:41, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:42 CT, 648 minutes
- **RB**: weekdays 319, entries observed 16/16, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:46, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:47 CT, 643 minutes

## metals

Most liquid: MGC. Entries checked: 2025-04-18 full_closure, 2025-05-26 early_halt, 2025-06-19 early_halt, 2025-07-04 early_halt, 2025-09-01 early_halt, 2025-11-27 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 early_halt, 2026-02-16 early_halt, 2026-04-03 full_closure, 2026-05-25 early_halt, 2026-06-19 early_halt, 2025-11-28 late_open

### Calendar questions

- 2025-05-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 05-29 12:27 (implied halt Thu 05-29 12:28); no calendar entry; next bar Thu 05-29 12:31; 936 bars in the session (also on: none). **Lead ruling:** L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
- 2025-07-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 07-30 12:24 (implied halt Wed 07-30 12:25); no calendar entry; next bar Wed 07-30 12:35; 836 bars in the session (also on: none). **Lead ruling:** L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
- 2025-11-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 11-26 12:26 (implied halt Wed 11-26 12:27); no calendar entry; next bar Wed 11-26 12:30; 1007 bars in the session (also on: none). **Lead ruling:** L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
- 2026-01-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 01-29 12:28 (implied halt Thu 01-29 12:29); no calendar entry; next bar Thu 01-29 12:31; 970 bars in the session (also on: GC). **Lead ruling:** L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
- 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 02-25 12:00 (implied halt Wed 02-25 12:01); no calendar entry; next bar Wed 02-25 13:45; 1276 bars in the session (also on: GC, SI, SIL). **Lead ruling:** L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar entry.
- 2026-05-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 05-28 12:20 (implied halt Thu 05-28 12:21); no calendar entry; next bar Thu 05-28 12:31; 876 bars in the session (also on: none). **Lead ruling:** L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.

### Per contract

- **GC**: weekdays 319, entries observed 16/16, discrepancies 2, bars inside a scheduled closure 0
  - [calendar_question] 2026-01-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 01-29 12:27 (implied halt Thu 01-29 12:28); no calendar entry; next bar Thu 01-29 12:30; 951 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - [calendar_question] 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 02-25 12:00 (implied halt Wed 02-25 12:01); no calendar entry; next bar Wed 02-25 13:45; 1275 bars in the session Lead ruling: L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar entry.
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **HG**: weekdays 319, entries observed 12/16, discrepancies 3, bars inside a scheduled closure 0
  - [thin_trading] 2025-06-19 listed_entry_not_observed: Juneteenth, early halt 13:30: last bar Thu 06-19 13:28 != expected Thu 06-19 13:29
  - [thin_trading] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 13:39 != expected Fri 11-28 13:44
  - [thin_trading] 2026-05-25 listed_entry_not_observed: Memorial Day, early halt 13:30: last bar Mon 05-25 13:25 != expected Mon 05-25 13:29
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **MGC**: weekdays 319, entries observed 16/16, discrepancies 6, bars inside a scheduled closure 0
  - [calendar_question] 2025-05-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 05-29 12:27 (implied halt Thu 05-29 12:28); no calendar entry; next bar Thu 05-29 12:31; 936 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - [calendar_question] 2025-07-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 07-30 12:24 (implied halt Wed 07-30 12:25); no calendar entry; next bar Wed 07-30 12:35; 836 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - [calendar_question] 2025-11-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 11-26 12:26 (implied halt Wed 11-26 12:27); no calendar entry; next bar Wed 11-26 12:30; 1007 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - [calendar_question] 2026-01-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 01-29 12:28 (implied halt Thu 01-29 12:29); no calendar entry; next bar Thu 01-29 12:31; 970 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - [calendar_question] 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Wed 02-25 12:00 (implied halt Wed 02-25 12:01); no calendar entry; next bar Wed 02-25 13:45; 1276 bars in the session Lead ruling: L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar entry.
  - [calendar_question] 2026-05-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:30 CT Thu 05-28 12:20 (implied halt Thu 05-28 12:21); no calendar entry; next bar Thu 05-28 12:31; 876 bars in the session Lead ruling: L-7: thin trading at the settlement minute; C lies inside metals' 23-hour session, so the early-stop test does not apply there. No calendar change.
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **MHG**: weekdays 319, entries observed 15/16, discrepancies 4, bars inside a scheduled closure 0
  - [thin_trading] 2025-06-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:00 CT Thu 06-26 11:55 (implied halt Thu 06-26 11:56); no calendar entry; next bar Thu 06-26 19:00; 381 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:00 CT Mon 09-01 11:56 (implied halt Mon 09-01 11:57); listed early_halt 13:30 (Labor Day); next bar Mon 09-01 12:00; 789 bars in the session
  - [thin_trading] 2025-09-01 listed_entry_not_observed: Labor Day, early halt 13:30: last bar Mon 09-01 13:24 != expected Mon 09-01 13:29
  - [thin_trading] 2025-11-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:00 CT Tue 11-25 11:53 (implied halt Tue 11-25 11:54); no calendar entry; next bar Tue 11-25 18:00; 416 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **SI**: weekdays 319, entries observed 16/16, discrepancies 4, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Tue 04-29 12:20 (implied halt Tue 04-29 12:21); no calendar entry; next bar Tue 04-29 12:29; 376 bars in the session
  - [thin_trading] 2025-06-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Fri 06-27 12:23 (implied halt Fri 06-27 12:24); no calendar entry; next bar Fri 06-27 12:25; 628 bars in the session
  - [calendar_question] 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Wed 02-25 11:59 (implied halt Wed 02-25 12:00); no calendar entry; next bar Wed 02-25 13:45; 1110 bars in the session Lead ruling: L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar entry.
  - [thin_trading] 2026-04-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Wed 04-29 12:09 (implied halt Wed 04-29 12:10); no calendar entry; next bar Wed 04-29 13:01; 299 bars in the session
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes
- **SIL**: weekdays 319, entries observed 16/16, discrepancies 6, bars inside a scheduled closure 0
  - [thin_trading] 2025-04-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Tue 04-29 12:19 (implied halt Tue 04-29 12:20); no calendar entry; next bar Tue 04-29 12:31; 255 bars in the session
  - [thin_trading] 2025-06-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Fri 06-27 12:05 (implied halt Fri 06-27 12:06); no calendar entry; next bar Fri 06-27 12:32; 476 bars in the session
  - [thin_trading] 2025-08-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Thu 08-28 12:15 (implied halt Thu 08-28 12:16); no calendar entry; next bar Thu 08-28 12:34; 294 bars in the session
  - [thin_trading] 2025-08-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Fri 08-29 11:53 (implied halt Fri 08-29 11:54); no calendar entry; next bar Fri 08-29 12:50; 37 bars in the session
  - [thin_trading] 2025-09-01 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Mon 09-01 12:23 (implied halt Mon 09-01 12:24); listed early_halt 13:30 (Labor Day); next bar Mon 09-01 12:25; 1182 bars in the session
  - [calendar_question] 2026-02-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 12:25 CT Wed 02-25 11:59 (implied halt Wed 02-25 12:00); no calendar entry; next bar Wed 02-25 13:45; 1239 bars in the session Lead ruling: L-7: an unscheduled halt (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps), unsourced; recorded, not a calendar entry.
  - note 2026-06-19: Juneteenth, early halt 12:00: the reopen after this halt is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:48, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:49 CT, 641 minutes

## grains

Most liquid: ZL. Entries checked: 2025-04-18 full_closure, 2025-05-26 full_closure, 2025-06-19 full_closure, 2025-07-04 full_closure, 2025-09-01 full_closure, 2025-11-27 full_closure, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 full_closure, 2026-02-16 full_closure, 2026-04-03 full_closure, 2026-05-25 full_closure, 2026-06-19 full_closure, 2025-11-28 scheduled_late_open, 2025-12-26 scheduled_late_open, 2026-01-02 scheduled_late_open

### Calendar questions

- none

### Per contract

- **ZC**: weekdays 319, entries observed 18/18, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 11-26 13:19, first_bar_at_or_after_ct Fri 11-28 08:30, scheduled True
  - bars on 2025-12-26 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-24 12:04, first_bar_at_or_after_ct Fri 12-26 08:30, scheduled True
  - bars on 2026-01-02 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-31 13:19, first_bar_at_or_after_ct Fri 01-02 08:30, scheduled True
- **ZL**: weekdays 319, entries observed 18/18, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 11-26 13:19, first_bar_at_or_after_ct Fri 11-28 08:30, scheduled True
  - bars on 2025-12-26 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-24 12:04, first_bar_at_or_after_ct Fri 12-26 08:30, scheduled True
  - bars on 2026-01-02 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-31 13:19, first_bar_at_or_after_ct Fri 01-02 08:30, scheduled True
- **ZM**: weekdays 319, entries observed 18/18, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 11-26 13:19, first_bar_at_or_after_ct Fri 11-28 08:30, scheduled True
  - bars on 2025-12-26 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-24 12:04, first_bar_at_or_after_ct Fri 12-26 08:30, scheduled True
  - bars on 2026-01-02 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-31 13:19, first_bar_at_or_after_ct Fri 01-02 08:30, scheduled True
- **ZS**: weekdays 319, entries observed 18/18, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 11-26 13:19, first_bar_at_or_after_ct Fri 11-28 08:30, scheduled True
  - bars on 2025-12-26 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-24 12:04, first_bar_at_or_after_ct Fri 12-26 08:30, scheduled True
  - bars on 2026-01-02 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-31 13:19, first_bar_at_or_after_ct Fri 01-02 08:30, scheduled True
- **ZW**: weekdays 319, entries observed 18/18, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 11-26 13:19, first_bar_at_or_after_ct Fri 11-28 08:30, scheduled True
  - bars on 2025-12-26 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-24 12:04, first_bar_at_or_after_ct Fri 12-26 08:30, scheduled True
  - bars on 2026-01-02 (late open, checked only (ruling L-4)): late_open_ct 08:30, last_bar_before_ct Wed 12-31 13:19, first_bar_at_or_after_ct Fri 01-02 08:30, scheduled True

## livestock

Most liquid: LE. Entries checked: 2025-04-18 full_closure, 2025-05-26 full_closure, 2025-06-19 full_closure, 2025-07-04 full_closure, 2025-09-01 full_closure, 2025-11-27 full_closure, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-01-19 full_closure, 2026-02-16 full_closure, 2026-04-03 full_closure, 2026-05-25 full_closure, 2026-06-19 full_closure

### Calendar questions

- none

### Per contract

- **HE**: weekdays 319, entries observed 15/15, discrepancies 0, bars inside a scheduled closure 0
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable
- **LE**: weekdays 319, entries observed 15/15, discrepancies 0, bars inside a scheduled closure 1 (2025-04-17 Thu 13:05 CT, close minute True)
  - note 2026-06-19: Juneteenth, full closure: the reopen after this closure is past the data end Sat 06-20 19:00: not observable

## crypto

Most liquid: MBT. Entries checked: 2025-04-18 full_closure, 2025-07-04 early_halt, 2025-11-28 early_halt, 2025-12-24 early_halt, 2025-12-25 full_closure, 2026-01-01 full_closure, 2026-04-03 early_halt, 2025-11-28 late_open, 2026-06-01 delayed_start

### Calendar questions

- 2025-04-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 04-25 09:57 (implied halt Fri 04-25 09:58); no calendar entry; next bar Sun 04-27 17:00; 383 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-05-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 05-30 09:59 (implied halt Fri 05-30 10:00); no calendar entry; next bar Sun 06-01 17:00; 430 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-06-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 06-27 09:57 (implied halt Fri 06-27 09:58); no calendar entry; next bar Sun 06-29 17:00; 418 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-07-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 07-25 09:59 (implied halt Fri 07-25 10:00); no calendar entry; next bar Sun 07-27 17:00; 697 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-08-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 08-29 09:59 (implied halt Fri 08-29 10:00); no calendar entry; next bar Sun 08-31 17:00; 506 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-09-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 09-26 09:59 (implied halt Fri 09-26 10:00); no calendar entry; next bar Sun 09-28 17:00; 428 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-10-31 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 10-31 10:59 (implied halt Fri 10-31 11:00); no calendar entry; next bar Sun 11-02 17:00; 580 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 11-28 09:59 (implied halt Fri 11-28 10:00); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 199 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 09:59 != expected Fri 11-28 13:44 (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2025-12-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 12-26 09:59 (implied halt Fri 12-26 10:00); no calendar entry; next bar Sun 12-28 17:00; 552 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2026-01-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 01-30 09:58 (implied halt Fri 01-30 09:59); no calendar entry; next bar Sun 02-01 17:00; 566 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2026-02-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 02-27 09:59 (implied halt Fri 02-27 10:00); no calendar entry; next bar Sun 03-01 17:00; 627 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2026-03-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 03-27 10:59 (implied halt Fri 03-27 11:00); no calendar entry; next bar Sun 03-29 17:00; 535 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2026-04-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 04-24 09:58 (implied halt Fri 04-24 09:59); no calendar entry; next bar Sun 04-26 17:00; 463 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
- 2026-05-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 05-29 09:59 (implied halt Fri 05-29 10:00); no calendar entry; next bar Sat 05-30 04:39; 447 bars in the session (also on: none). **Lead ruling:** L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.

### Per contract

- **MBT**: weekdays 319, entries observed 7/9, discrepancies 15, bars inside a scheduled closure 0
  - [calendar_question] 2025-04-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 04-25 09:57 (implied halt Fri 04-25 09:58); no calendar entry; next bar Sun 04-27 17:00; 383 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-05-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 05-30 09:59 (implied halt Fri 05-30 10:00); no calendar entry; next bar Sun 06-01 17:00; 430 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-06-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 06-27 09:57 (implied halt Fri 06-27 09:58); no calendar entry; next bar Sun 06-29 17:00; 418 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-07-25 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 07-25 09:59 (implied halt Fri 07-25 10:00); no calendar entry; next bar Sun 07-27 17:00; 697 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-08-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 08-29 09:59 (implied halt Fri 08-29 10:00); no calendar entry; next bar Sun 08-31 17:00; 506 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-09-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 09-26 09:59 (implied halt Fri 09-26 10:00); no calendar entry; next bar Sun 09-28 17:00; 428 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-10-31 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 10-31 10:59 (implied halt Fri 10-31 11:00); no calendar entry; next bar Sun 11-02 17:00; 580 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-11-28 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 11-28 09:59 (implied halt Fri 11-28 10:00); listed early_halt 13:45 (Day after Thanksgiving); next bar Sun 11-30 17:00; 199 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-11-28 listed_entry_not_observed: Day after Thanksgiving, early halt 13:45: last bar Fri 11-28 09:59 != expected Fri 11-28 13:44 Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2025-12-26 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 12-26 09:59 (implied halt Fri 12-26 10:00); no calendar entry; next bar Sun 12-28 17:00; 552 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2026-01-30 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 01-30 09:58 (implied halt Fri 01-30 09:59); no calendar entry; next bar Sun 02-01 17:00; 566 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2026-02-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 02-27 09:59 (implied halt Fri 02-27 10:00); no calendar entry; next bar Sun 03-01 17:00; 627 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2026-03-27 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 03-27 10:59 (implied halt Fri 03-27 11:00); no calendar entry; next bar Sun 03-29 17:00; 535 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2026-04-24 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 04-24 09:58 (implied halt Fri 04-24 09:59); no calendar entry; next bar Sun 04-26 17:00; 463 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - [calendar_question] 2026-05-29 early_stop_not_a_listed_early_halt_at_that_time: last bar before 15:00 CT Fri 05-29 09:59 (implied halt Fri 05-29 10:00); no calendar entry; next bar Sat 05-30 04:39; 447 bars in the session Lead ruling: L-11: monthly contract expiry while the volume-ranked series holds the expiring contract (the last Friday of the month, and 2026-05-29); not a calendar error; every such date lies inside a roll blackout.
  - note 2026-06-19: booked forward to 2026-06-22 (outside the window): its bars are dropped (counted only), so rules (1)-(2) do not check this day
  - bars on 2025-11-28 (late open, checked only (ruling L-4)): late_open_ct 07:30, last_bar_before_ct Thu 11-27 20:35, first_bar_at_or_after_ct Fri 11-28 07:30, scheduled False
  - bars on 2026-06-01 (late open, checked only (ruling L-4)): scheduled True, delayed_open_ct Fri 05-29 16:30, closed_from_ct Fri 05-29 16:00, first_bar_at_or_after_ct Sat 05-30 04:39
  - [documented_cme_outage] gap run from 2025-11-27 Thu 20:36 CT, 654 minutes
