# Stage E.11 member decision-variable inventory

Extraction only: what each member's code (strategy/members/k*/) or K9 draft computes; no result figures. Source: module docstrings and module constants (file:line in JSON `literals`), reports/stage_e0_catalog*.md only for definitions. Full per-member fields (formula, inputs, literals with file:line, availability) are in member_inventory.json (54 rows).
All clock times CT. 'bar at hh:mm' = 1-minute bar opening hh:mm; its close is known at hh:mm+1. 'fills next open' = the intent is sent on that bar, filled at the next bar's open.

## Counts per cluster (member families = one row each; CP ports counted as rows)

| Cluster | Rows | Fixed clock (calendar/time flag only) | Carry a variable | of which CP ports |
|---|---|---|---|---|
| K1 | 5 | 0 | 5 | 3 |
| K2 | 8 | 4 | 4 | 3 |
| K3 | 9 | 3 | 6 | 3 |
| K4 | 8 | 1 | 7 | 3 |
| K5 | 7 | 1 | 6 | 3 |
| K6 | 7 | 0 | 7 | 3 |
| K7 | 6 | 1 | 5 | 3 |
| K8 | 3 | 0 | 3 | 0 |
| K9 | 1 | 1 | 0 | 0 |
| total | 54 | 11 | 43 | 21 |

Non-CP rows only: 33 rows, 11 fixed clock, 22 with a variable. K8 has no CP ports; K9 is a catalog draft (no code).

## Data dependencies outside one-minute bars (flagged)

- K1-vxnband-01: VXN daily close (Cboe VXN_History.csv, embedded literal table k1/_vxn.py; spans 2019-04-30..2026-06-19). Only index-series dependency in code.
- K3-mehedge-01: Nikkei 225 daily closes (Nikkei Inc. CSV captures, embedded literal monthly log-return table k3/_mehedge_signal.py). External equity-index series.
- K6-limitcont-01: settlement proxy over the [12:59:30,13:00:00) window computed from HE/LE bars, plus exchange price-limit table (rules.price_limits, k6/_limits.py). No other Databento schema.
- Release/auction/WASDE/WPSR/NGS/FOMC/ISM/gold-auction/fix-time/expiry calendars (K2, K3, K4, K5, K6, K7, K8, K9): literal date tables, generated from reports/stage_e2b_release_calendar.json and EC-CAL. They are calendars. No released value (CPI, EIA, WASDE, etc.) is read by any member.
- K9-anncday-01 date set EC-K9: official BLS/BEA/ISM/FOMC schedules; several dates [unverified] (rescheduled by the 2025 appropriations lapse); E.11 to verify.
- Every other member reads ohlcv-1m bars only (fields used: open, high, low, close, volume in K1-vwap and K6-limitcont; trade_date, instrument_id and early_halt_ct flags as guards).

## Rows (one block per row; CP ports of K1-K7 are in the next section)

### K1-vwap-01  [K1]  fixed_clock=no
- file: strategy/members/k1/vwap.py
- traded: MNQ | read only: none
- DV `vwap_side_s_t`: s_t = sign(3*C_t*sum(vol) - sum((H+L+C)*vol)) over present 1-min bars of CT date d from 08:30 through bar t, integer ticks; if zero, carry s_(t-1) (0 before first sign); sum(vol)=0 -> no action, s not updated
  - inputs: MNQ ohlcv-1m bars of CT date d (H, L, C, volume) from 08:30; EQUITY_FULL_SESSIONS; availability: close of bar t (t+1 min CT); intent on bar t fills next open
  - literals: TP_PARTS=3 (k1/vwap.py:70); RULE_END_CT=time(14, 57) (k1/vwap.py:71); EXIT_BEFORE_C_MIN=2 (k1/vwap.py:72); MAX_ENTRIES=20 (k1/vwap.py:73); MIN_HOLD_MINUTES=1 (k1/vwap.py:74)
- entry: On each bar t in [08:30,14:57) with no order pending: flat, s_t!=0 and <20 entry intents today -> market entry q_c; position opposite to s_t and min hold met (>=1 min after the first-seen bar) -> exit then, if <20 entries, entry, both on bar t
- exit: Final market intent on first present bar >= 14:58 (fills 14:59 open); no rule intent from the 14:57 bar on; otherwise reversal on opposite s_t
- direction: position = s_t (above session VWAP -> buy, below -> sell)
- extra data: EQUITY_FULL_SESSIONS literal date table (k1/_calendar.py)

### K1-vxnband-01  [K1]  fixed_clock=no
- file: strategy/members/k1/vxnband.py
- traded: MNQ | read only: VXN index daily close (literal table)
- DV `vxn_regime_V`: V = VXN_CLOSE of the calendar date of the EQUITY_TRADE_DATES entry immediately before d (never d's own close); trade only if V<20 (strict) or V>=30
  - inputs: VXN_CLOSE table (k1/_vxn.py, generated from data/vendor/index_history/vxn/VXN_History.csv); EQUITY_TRADE_DATES; availability: prior trade date's VXN close, read on d's 08:30 bar close (08:31 CT)
  - literals: BAND_DIVISOR=1600 (k1/vxnband.py:68); VXN_LOW_CUT=Decimal(20) (k1/vxnband.py:69); VXN_HIGH_CUT=Decimal(30) (k1/vxnband.py:70); SCAN_END_CT=time(14, 29) (k1/vxnband.py:71); HOLD_MINUTES=30 (k1/vxnband.py:72); CLOSE_BEFORE_C_MIN=1 (k1/vxnband.py:73)
- DV `band_breach`: sell iff 1600*(close_t - C_prev) > C_prev*V; buy iff 1600*(close_t - C_prev) < -(C_prev*V); C_prev = close of the 14:59 bar of the most recent COMPLETE trade date; scan bars [08:30,14:29); first breach on either side uses the day's one entry
  - inputs: MNQ ohlcv-1m: prior complete day's 14:59 close, bars of d 08:30..14:28; instrument guard vs the 08:30 bar; availability: close of the breaching bar t (intent on that bar, fills next open)
  - literals: BAND_DIVISOR=1600 (k1/vxnband.py:68); VXN_LOW_CUT=Decimal(20) (k1/vxnband.py:69); VXN_HIGH_CUT=Decimal(30) (k1/vxnband.py:70); SCAN_END_CT=time(14, 29) (k1/vxnband.py:71); HOLD_MINUTES=30 (k1/vxnband.py:72); CLOSE_BEFORE_C_MIN=1 (k1/vxnband.py:73)
- entry: Market intent q_c on the first breach bar (scan [08:30,14:29)), only if VXN regime holds and guards pass; one entry per day
- exit: Market intent on first present bar >= entry-intent bar + 30 min (latest 14:58, fill 14:59); engine flatten at F as backstop
- direction: fade: SELL on upper band breach, BUY on lower band breach
- extra data: VXN daily close series (Cboe VXN_History.csv embedded as literal table k1/_vxn.py; not ohlcv-1m) | EQUITY_FULL_SESSIONS / EQUITY_TRADE_DATES literal calendars

### K2-aucpre-01  [K2]  fixed_clock=YES
- file: strategy/members/k2/aucpre.py
- traded: ZT; ZF; ZN; TN; ZB; UB (each on its own tenor's auctions; q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: SIDE=SELL (k2/aucpre.py:33); ENTRY_DECISION_OFFSET_MIN=-181 (k2/aucpre.py:34); EXIT_DECISION_OFFSET_MIN=-2 (k2/aucpre.py:35); WINDOW_START_CT=time(7, 29) (k2/aucpre.py:36); WINDOW_END_CT=time(12, 0) (k2/aucpre.py:37)
- entry: SELL q_c market intent on the bar at T_a-181 min (fills T_a-180 open); T_a = competitive close - 1 h in CT; skip if bar missing or early_halt_ct
- exit: Market intent on first bar >= T_a-2 min (fills nominally T_a-1); hold 179 min
- direction: always SELL
- extra data: Treasury auction / FOMC / ISM Services dates and times: literal tables k2/_releases.py generated from reports/stage_e2b_release_calendar.json (a calendar, not market data)

### K2-aucpost-01  [K2]  fixed_clock=YES
- file: strategy/members/k2/aucpost.py
- traded: ZT; ZF; ZN; TN; ZB; UB (own tenor) | read only: none
- DV: none (calendar/time flag only). literals: SIDE=BUY (k2/aucpost.py:33); ENTRY_DECISION_OFFSET_MIN=4 (k2/aucpost.py:34); EXIT_DECISION_OFFSET_MIN=184 (k2/aucpost.py:35); WINDOW_START_CT=time(10, 34) (k2/aucpost.py:36); WINDOW_END_CT=time(15, 6) (k2/aucpost.py:37)
- entry: BUY q_c market intent on bar T_a+4 (fills T_a+5 open); skip if bar missing or early_halt_ct
- exit: Market intent on bar T_a+184 (fills T_a+185 open); missing -> first later bar; hold 180 min
- direction: always BUY
- extra data: Treasury auction / FOMC / ISM Services dates and times: literal tables k2/_releases.py generated from reports/stage_e2b_release_calendar.json (a calendar, not market data)

### K2-fomcpost-01  [K2]  fixed_clock=YES
- file: strategy/members/k2/fomcpost.py
- traded: ZT; ZF; ZN; TN; ZB; UB | read only: none
- DV: none (calendar/time flag only). literals: SIDE=BUY (k2/fomcpost.py:34); ENTRY_DECISION_CT=time(13, 29) (k2/fomcpost.py:35); EXIT_DECISION_CT=time(15, 4) (k2/fomcpost.py:36); WINDOW_START_CT=time(13, 29) (k2/fomcpost.py:37); WINDOW_END_CT=time(15, 6) (k2/fomcpost.py:38)
- entry: On scheduled FOMC statement dates released at 13:00 CT: BUY q_c market intent on the 13:29 bar (fills 13:30)
- exit: Market intent on the 15:04 bar (fills 15:05); missing -> first later bar; hold 95 min
- direction: always BUY
- extra data: Treasury auction / FOMC / ISM Services dates and times: literal tables k2/_releases.py generated from reports/stage_e2b_release_calendar.json (a calendar, not market data)

### K2-predrift-01  [K2]  fixed_clock=no
- file: strategy/members/k2/predrift.py
- traded: ZN; ZB | read only: none
- DV `ism_predrift_s`: s = sign(close of 08:49 bar - open of 08:30 bar), integer ticks, on ISM Services release dates (T = 09:00 CT); both bars present, one instrument_id; s=0 -> no trade
  - inputs: ZN or ZB ohlcv-1m 08:30 and 08:49 bars; k2/_releases.ISM_SERVICES_DATES; availability: close of the 08:49 bar (08:50 CT)
  - literals: EXPOSURES=("ZN", "ZB") (k2/predrift.py:46); RELEASE_CT=time(9, 0) (k2/predrift.py:47); SIGNAL_START_OFFSET_MIN=-30 (k2/predrift.py:48); ENTRY_DECISION_OFFSET_MIN=-11 (k2/predrift.py:49); EXIT_DECISION_OFFSET_MIN=4 (k2/predrift.py:50); WINDOW_START_CT=time(8, 30) (k2/predrift.py:51); WINDOW_END_CT=time(9, 6) (k2/predrift.py:52)
- entry: Market intent on the 08:49 bar in direction s (fills 08:50); skip if missing or early_halt_ct
- exit: Market intent on the 09:04 bar (fills 09:05); missing -> first later bar; hold 15 min through the release; index value never read
- direction: side = sign(s): continue the 08:30-08:49 move
- extra data: Treasury auction / FOMC / ISM Services dates and times: literal tables k2/_releases.py generated from reports/stage_e2b_release_calendar.json (a calendar, not market data)

### K2-monthend-01  [K2]  fixed_clock=YES
- file: strategy/members/k2/monthend.py
- traded: ZT; ZF; ZN; TN; ZB; UB | read only: none
- DV: none (calendar/time flag only). literals: SIDE="buy" (k2/monthend.py:46); EXIT_BAR_CT=time(15, 4) (k2/monthend.py:47)
- entry: On N (last EC-CAL rates trade date of a month) and N-1, each independently: unconditional BUY q_c market intent on the 07:20 bar (fills 07:21); skip if missing or early_halt_ct
- exit: Market intent on the 15:04 bar (fills 15:05); missing -> first later bar; engine flatten at F
- direction: always BUY
- extra data: Month-end date table k2/_month_end.py (literal, from EC-CAL rates calendar)

### K3-ecbfix-01  [K3]  fixed_clock=YES
- file: strategy/members/k3/ecbfix.py
- traded: 6E (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: EXPOSURES=("6E",) (k3/ecbfix.py:52); LEG1_ENTRY_DECISION_CT="00:59" (k3/ecbfix.py:53); LEG1_EXIT_DECISION_OFFSET_MIN=-1 (k3/ecbfix.py:54); LEG2_ENTRY_DECISION_OFFSET_MIN=0 (k3/ecbfix.py:55); LEG2_EXIT_DECISION_CT="15:04" (k3/ecbfix.py:56)
- entry: Two sequential legs on each FX full-session trade date not a TARGET closing day: leg 1 SELL on the 00:59 CT bar (fills 01:00); leg 2 BUY on the bar at T_E (fills T_E+1), only if flat and leg 1 opened that date and was closed by the member's own exit
- exit: Leg 1 exit on bar T_E-1 (fills T_E); leg 2 exit on the 15:04 bar (fills 15:05); T_E = 07:15 CT (08:15 CT in C9 mismatch weeks)
- direction: leg 1 short, leg 2 long
- extra data: Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K3-ldnmom-01  [K3]  fixed_clock=no
- file: strategy/members/k3/ldnmom.py
- traded: 6E; 6J (q_c 1 each) | read only: none
- DV `ldn_pre_fix_trend_S`: S = ticks(close of bar at T_L-13) - ticks(open of bar at T_L-15) (bars 15:45,15:46,15:47 London); S=0 -> no trade; guard: both bars one instrument_id; T_L = 10:00 CT (11:00 in mismatch weeks)
  - inputs: 6E or 6J ohlcv-1m; T_L table (k3/_clocks.py); FX_FULL_SESSIONS, EW_BANK_HOLIDAYS exclusions; availability: close of the T_L-13 bar (T_L-12 CT, 09:48 standard)
  - literals: EXPOSURES=("6E", "6J") (k3/ldnmom.py:48); SIGNAL_START_OFFSET_MIN=-15 (k3/ldnmom.py:49); ENTRY_DECISION_OFFSET_MIN=-13 (k3/ldnmom.py:50); EXIT_DECISION_OFFSET_MIN=4 (k3/ldnmom.py:51)
- entry: Market intent on the T_L-13 bar (fills T_L-12 open), only on FX full sessions not E&W bank holidays
- exit: Market intent on bar T_L+4 (fills T_L+5); missing -> first later bar
- direction: BUY if S>0, SELL if S<0 (momentum)
- extra data: Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K3-ldnrev-01  [K3]  fixed_clock=no
- file: strategy/members/k3/ldnrev.py
- traded: 6E; 6J; 6S (q_c 1 each) | read only: none
- DV `ldn_month_end_M`: M = ticks(close of bar T_L-1) - ticks(close of bar T_L-11) (10-minute pre-fix move); M=0 -> no trade; guard: T_L-11, T_L-1, T_L+4 bars share one instrument_id
  - inputs: 6E/6J/6S ohlcv-1m; month-end date ME(m) from k3/_calendar.MONTH_ENDS; T_L table; availability: close of bar T_L-1 (T_L CT); entry decision bar is T_L+4
  - literals: EXPOSURES=("6E", "6J", "6S") (k3/ldnrev.py:47); SIGNAL_START_OFFSET_MIN=-11 (k3/ldnrev.py:48); SIGNAL_END_OFFSET_MIN=-1 (k3/ldnrev.py:49); ENTRY_DECISION_OFFSET_MIN=4 (k3/ldnrev.py:50); EXIT_DECISION_OFFSET_MIN=19 (k3/ldnrev.py:51)
- entry: Month-end only (ME(m) in FX_FULL_SESSIONS, not E&W bank holiday): market intent on bar T_L+4 (fills T_L+5)
- exit: Market intent on bar T_L+19 (fills T_L+20); missing -> first later bar
- direction: BUY if M<0, SELL if M>0 (contrarian)
- extra data: Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K3-mehedge-01  [K3]  fixed_clock=no
- file: strategy/members/k3/mehedge.py
- traded: 6J (q_c 1) | read only: Nikkei 225 (precomputed monthly log return, literal table)
- DV `nikkei_month_return_R_eq`: R_eq(m) = ln(P_a/P_b); P_a = Nikkei 225's last official close on a Tokyo date strictly before ME(m)'s calendar date, P_b = its last official close in month m-1; no trade if 0 or None
  - inputs: k3/_mehedge_signal.MEHEDGE_R_EQ_6J (generated from saved Nikkei Inc. daily CSV captures); ME(m) month-end FX trade date; availability: uses closes strictly before ME(m)'s date, known before the ME(m) session; entry bar T_L-61 (09:00 CT standard)
  - literals: ENTRY_BEFORE_TL_MIN=61 (k3/mehedge.py:57); EXIT_BEFORE_TL_MIN=4 (k3/mehedge.py:58); WINDOW_END_BEFORE_TL_MIN=2 (k3/mehedge.py:59)
- entry: Month-end: market intent on the bar at T_L-61 of CT date ME(m) (fills T_L-60 open); skip if bar missing
- exit: Market intent on first present bar >= T_L-4 (fills nominally T_L-3), sent whatever the instrument_id
- direction: SELL if R_eq>0, BUY if R_eq<0
- extra data: EXTERNAL Nikkei 225 daily close series (Nikkei Inc. CSV captures, via literal table k3/_mehedge_signal.py) -- not Databento ohlcv-1m | Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K3-tkypost-01  [K3]  fixed_clock=YES
- file: strategy/members/k3/tkypost.py
- traded: 6J (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: EXPOSURES=("6J",) (k3/tkypost.py:44); EXIT_DECISION_CT="00:59" (k3/tkypost.py:45)
- entry: On Tokyo business days (trade date d in FX_FULL_SESSIONS): BUY market intent on the bar at T_T on d-1 (18:55 CST / 19:55 CDT; fills T_T+1)
- exit: Market intent on the 00:59 CT bar of d (fills 01:00); missing -> first later bar
- direction: always BUY
- extra data: Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K3-tkypre-01  [K3]  fixed_clock=YES
- file: strategy/members/k3/tkypre.py
- traded: 6J (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: EXPOSURES=("6J",) (k3/tkypre.py:45); ENTRY_DECISION_CT="17:29" (k3/tkypre.py:46); EXIT_DECISION_OFFSET_MIN=-1 (k3/tkypre.py:47)
- entry: Gotobi days (Tokyo day-of-month 5,10,15,20,25,30 or last Tokyo business day): SELL market intent on the 17:29 CT bar of calendar day d-1 (fills 17:30)
- exit: Market intent on the bar at T_T-1 on d-1 (fills T_T: 18:55 CST / 19:55 CDT); missing -> first later bar
- direction: always SELL
- extra data: Fix-time tables k3/_clocks.py (T_L, T_E, T_T literal CT instants per weekday) and calendars k3/_calendar.py: calendars, not market data

### K4-apipre-01  [K4]  fixed_clock=no
- file: strategy/members/k4/apipre.py
- traded: MCL (q_c 4) | read only: none
- DV `api_tuesday_return_R_API`: R_API = ticks(close of 15:39 bar) - ticks(close of 15:24 bar), both on CT date W-1 (the Tuesday before the WPSR Wednesday W); R_API=0 -> no trade; guard: 15:24, 15:39 bars of W-1 and the 07:29 bar of W share one instrument_id
  - inputs: MCL ohlcv-1m Tuesday 15:24 and 15:39 bars; WPSR Wednesday table; ENERGY_FULL_SESSIONS; FEDERAL_MONDAY_HOLIDAYS; API_DROPPED_WEEKS; availability: close of the 15:39 bar on W-1 (15:40 CT); carried overnight to entry bar 07:29 of W
  - literals: EXPOSURES=("MCL",) (k4/apipre.py:51); SIGNAL_START_CT=time(15, 24) (k4/apipre.py:52); SIGNAL_END_CT=time(15, 39) (k4/apipre.py:53); ENTRY_DECISION_CT=time(7, 29) (k4/apipre.py:54); EXIT_DECISION_CT=time(9, 28) (k4/apipre.py:55)
- entry: Market intent on the 07:29 bar of W (fills 07:30), skip if missing or early_halt_ct
- exit: Market intent on the 09:28 bar of W (fills 09:29) before the 09:30 release; missing -> first later bar
- direction: side = sign(R_API) (continuation)
- extra data: Release tables k4/_releases.py (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL, API_DROPPED_WEEKS) from reports/stage_e2b_release_calendar.json; k4/_calendar.ENERGY_FULL_SESSIONS: calendars, not market data. Released values (API, EIA, storage) are never read

### K4-eiafade-01  [K4]  fixed_clock=no
- file: strategy/members/k4/eiafade.py
- traded: MCL (q_c 4) | read only: none
- DV `wpsr_post_release_move_M`: t0 = ticks(close of bar T_W-1), t14 = ticks(close of bar T_W+14); M=(t14-t0)/t0 requires t0>0; trade only if 200*(t14-t0) <= -t0 (M<=-0.005) or 200*(t14-t0) >= t0 (M>=+0.005); guard: both bars one instrument_id
  - inputs: MCL ohlcv-1m; WPSR rows with T_W+15 <= 13:13 CT (09:30,10:00,11:00,12:00 CT slots); availability: close of the T_W+14 bar (T_W+15 CT)
  - literals: EXPOSURES=("MCL",) (k4/eiafade.py:48); BASE_OFFSET_MIN=-1 (k4/eiafade.py:49); ENTRY_DECISION_OFFSET_MIN=14 (k4/eiafade.py:50); ENTRY_FILL_OFFSET_MIN=15 (k4/eiafade.py:51); LATEST_ENTRY_FILL_CT=time(13, 13) (k4/eiafade.py:52); EXIT_DECISION_CT=time(13, 28) (k4/eiafade.py:53); THRESHOLD_DENOMINATOR=200 (k4/eiafade.py:54)
- entry: Market intent on the T_W+14 bar (fills T_W+15 open); skip if missing or early_halt_ct
- exit: Market intent on first present bar >= 13:28 (fills nominally 13:29)
- direction: fade: BUY if M<=-0.5%, SELL if M>=+0.5%
- extra data: Release tables k4/_releases.py (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL, API_DROPPED_WEEKS) from reports/stage_e2b_release_calendar.json; k4/_calendar.ENERGY_FULL_SESSIONS: calendars, not market data. Released values (API, EIA, storage) are never read

### K4-eiamom-01  [K4]  fixed_clock=no
- file: strategy/members/k4/eiamom.py
- traded: MCL (q_c 4) | read only: none
- DV `wpsr_day_r3`: r3 = ticks(close of 09:59 bar) - ticks(close of 09:29 bar) on standard WPSR days (T_W=09:30 CT); r3=0 -> no trade; guard: 09:29, 09:59, 14:29 bars share one instrument_id
  - inputs: MCL ohlcv-1m; WPSR standard rows not in NYSE_NOT_FULL; availability: close of the 09:59 bar (10:00 CT); entry bar 14:29
  - literals: EXPOSURES=("MCL",) (k4/eiamom.py:47); SIGNAL_START_CT=time(9, 29) (k4/eiamom.py:48); SIGNAL_END_CT=time(9, 59) (k4/eiamom.py:49); ENTRY_DECISION_CT=time(14, 29) (k4/eiamom.py:50); EXIT_DECISION_CT=time(14, 58) (k4/eiamom.py:51)
- entry: Market intent on the 14:29 bar (fills 14:30); skip if missing or early_halt_ct
- exit: Market intent on first present bar >= 14:58 (fills nominally 14:59)
- direction: side = sign(r3) (continuation)
- extra data: Release tables k4/_releases.py (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL, API_DROPPED_WEEKS) from reports/stage_e2b_release_calendar.json; k4/_calendar.ENERGY_FULL_SESSIONS: calendars, not market data. Released values (API, EIA, storage) are never read

### K4-ngpre-01  [K4]  fixed_clock=YES
- file: strategy/members/k4/ngpre.py
- traded: NG (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: EXPOSURES=("NG",) (k4/ngpre.py:42); SIDE=SELL (k4/ngpre.py:43); ENTRY_DECISION_OFFSET_MIN=-91 (k4/ngpre.py:44); EXIT_DECISION_OFFSET_MIN=29 (k4/ngpre.py:45)
- entry: On every NGS release date: SELL market intent on the bar at T-91 (standard 07:59, fills 08:00); T = 09:30 or 11:00 CT per row; skip if missing or early_halt_ct
- exit: Market intent on bar T+29 (standard 09:59, fills 10:00); missing -> first later bar
- direction: always SELL
- extra data: Release tables k4/_releases.py (WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL, API_DROPPED_WEEKS) from reports/stage_e2b_release_calendar.json; k4/_calendar.ENERGY_FULL_SESSIONS: calendars, not market data. Released values (API, EIA, storage) are never read

### K4-ovr-01  [K4]  fixed_clock=no
- file: strategy/members/k4/ovr.py
- traded: MCL (q 4); NG (q 1) | read only: none
- DV `hourly_return_r_t`: r(t) = (close of bar t-1 - open of bar t-60)/open of bar t-60 (float from integer ticks), t in {09:00,10:00,11:00,12:00,13:00}; guard: both bars present, one instrument_id, open>0
  - inputs: MCL/NG ohlcv-1m bars of CT date d; availability: close of bar t-1 (t CT)
  - literals: SIGNAL_MINUTES=60 (k4/ovr.py:63); DECISION_BAR_BEFORE_T_MIN=1 (k4/ovr.py:64); EXIT_AFTER_T_MIN=58 (k4/ovr.py:65); REFERENCE_DATES=20 (k4/ovr.py:66); MIN_VALUES=80 (k4/ovr.py:67); PERCENTILE_METHOD="linear" (k4/ovr.py:69); WINDOW_END_CT=time(14, 0) (k4/ovr.py:70)
- DV `percentile_cuts_P10_P90`: P10, P90 = numpy.percentile(values,[10,90],method=linear) of r(tau) at the same five clock times over the 20 most recent ENERGY_FULL_SESSIONS dates strictly before d; need >=80 values; warm-up: no trade while any reference date precedes the first bar received
  - inputs: MCL/NG ohlcv-1m of the 20 prior full-session dates; ENERGY_FULL_SESSIONS; availability: dates strictly before d; cuts known at start of d
  - literals: SIGNAL_MINUTES=60 (k4/ovr.py:63); DECISION_BAR_BEFORE_T_MIN=1 (k4/ovr.py:64); EXIT_AFTER_T_MIN=58 (k4/ovr.py:65); REFERENCE_DATES=20 (k4/ovr.py:66); MIN_VALUES=80 (k4/ovr.py:67); PERCENTILE_METHOD="linear" (k4/ovr.py:69); WINDOW_END_CT=time(14, 0) (k4/ovr.py:70)
- entry: Entry on bar t-1 (exact bar, fills open of t), only when flat with no pending order: r(t)<=P10 buy, r(t)>=P90 sell; P10=P90=r -> no trade; early_halt_ct decision bar -> no trade at t
- exit: Market intent on first present bar >= t+58 (fills nominally t+59); engine flatten at F backstop
- direction: contrarian: buy at lower tail, sell at upper tail
- extra data: ENERGY_FULL_SESSIONS literal table (calendar)

### K5-fomc-01  [K5]  fixed_clock=no
- file: strategy/members/k5/fomc.py
- traded: MGC (q_c 1) | read only: none
- DV `fomc_5min_move_s`: s = ticks(close of 13:04 bar) - ticks(close of 12:59 bar) on FOMC statement dates (13:00 CT); both bars present, one instrument_id; s=0 -> no trade
  - inputs: MGC ohlcv-1m; FOMC_STATEMENT_DATES; availability: close of the 13:04 bar (13:05 CT)
  - literals: EXPOSURES=("MGC",) (k5/fomc.py:38); SIGNAL_START_CT=time(12, 59) (k5/fomc.py:39); ENTRY_DECISION_CT=time(13, 4) (k5/fomc.py:40); EXIT_DECISION_CT=time(13, 14) (k5/fomc.py:41)
- entry: Market intent on the 13:04 bar (fills 13:05); skip if missing or early_halt_ct
- exit: Market intent on the 13:14 bar (fills 13:15); missing -> first later bar; hold 10 min
- direction: side = sign(s) (continuation)
- extra data: Calendar/event tables k5/_releases.py (FOMC_STATEMENT_DATES, GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS with T in CT) from reports/stage_e2b_release_calendar.json plus Task 1b release check; k5/_calendar.METALS_FULL_SESSIONS: calendars, not market data

### K5-ovr-01  [K5]  fixed_clock=no
- file: strategy/members/k5/ovr.py
- traded: MGC (q 1); MHG (q 2) | read only: none
- DV `hourly_return_r_t`: r(t) = (close of bar t-1 - open of bar t-60)/open of bar t-60 at t = O+60k while t<=C: MGC 08:20,09:20,10:20,11:20,12:20; MHG 08:10,09:10,10:10,11:10; guard: both bars, one instrument_id, open>0
  - inputs: MGC/MHG ohlcv-1m; availability: close of bar t-1
  - literals: DECISION_STEP_MIN=60 (k5/ovr.py:65); SIGNAL_MINUTES=60 (k5/ovr.py:66); DECISION_BAR_BEFORE_T_MIN=1 (k5/ovr.py:67); EXIT_AFTER_T_MIN=58 (k5/ovr.py:68); REFERENCE_DATES=20 (k5/ovr.py:69); VALUE_FLOOR_PERCENT=80 (k5/ovr.py:70); PERCENTILE_METHOD="linear" (k5/ovr.py:72); WINDOW_END_AFTER_LAST_T_MIN=60 (k5/ovr.py:73)
- DV `percentile_cuts_P10_P90`: P10/P90 (numpy linear) of r(tau) at the same clock times over the 20 most recent METALS_FULL_SESSIONS dates before d; need >=80% of possible values (MGC 80 of 100, MHG 64 of 80); warm-up rule
  - inputs: MGC/MHG ohlcv-1m of 20 prior dates; METALS_FULL_SESSIONS; availability: dates strictly before d
  - literals: DECISION_STEP_MIN=60 (k5/ovr.py:65); SIGNAL_MINUTES=60 (k5/ovr.py:66); DECISION_BAR_BEFORE_T_MIN=1 (k5/ovr.py:67); EXIT_AFTER_T_MIN=58 (k5/ovr.py:68); REFERENCE_DATES=20 (k5/ovr.py:69); VALUE_FLOOR_PERCENT=80 (k5/ovr.py:70); PERCENTILE_METHOD="linear" (k5/ovr.py:72); WINDOW_END_AFTER_LAST_T_MIN=60 (k5/ovr.py:73)
- entry: Entry on bar t-1 (fills open of t), flat and no pending: r<=P10 buy, r>=P90 sell; early_halt_ct decision bar -> no trade at t
- exit: Market intent on first present bar >= t+58 (fills nominally t+59)
- direction: contrarian (buy lower tail, sell upper tail)
- extra data: METALS_FULL_SESSIONS literal table

### K5-pmfix-01  [K5]  fixed_clock=no
- file: strategy/members/k5/pmfix.py
- traded: MGC (q_c 1) | read only: none
- DV `pm_fix_move_s`: s = ticks(close of bar T_P+1) - ticks(close of bar T_P-1); T_P = CT instant of 15:00 London (09:00 CT, 10:00 CT in 5-hour weeks) on scheduled gold PM auction days; s=0 -> no trade; both bars one instrument_id
  - inputs: MGC ohlcv-1m; GOLD_PM_AUCTIONS table; availability: close of bar T_P+1 (T_P+2 CT)
  - literals: EXPOSURES=("MGC",) (k5/pmfix.py:39); SIGNAL_START_OFFSET_MIN=-1 (k5/pmfix.py:40); ENTRY_DECISION_OFFSET_MIN=1 (k5/pmfix.py:41); EXIT_DECISION_OFFSET_MIN=11 (k5/pmfix.py:42)
- entry: Market intent on bar T_P+1 (fills T_P+2); skip if missing or early_halt_ct
- exit: Market intent on bar T_P+11 (fills T_P+12); missing -> first later bar; hold 10 min
- direction: side = sign(s) (continuation)
- extra data: Calendar/event tables k5/_releases.py (FOMC_STATEMENT_DATES, GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS with T in CT) from reports/stage_e2b_release_calendar.json plus Task 1b release check; k5/_calendar.METALS_FULL_SESSIONS: calendars, not market data

### K5-preauc-01  [K5]  fixed_clock=YES
- file: strategy/members/k5/preauc.py
- traded: MGC (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: EXPOSURES=("MGC",) (k5/preauc.py:43); SIDE=SELL (k5/preauc.py:44); ENTRY_DECISION_OFFSET_MIN=-31 (k5/preauc.py:45); EXIT_DECISION_OFFSET_MIN=-2 (k5/preauc.py:46)
- entry: Scheduled gold AM auction days: unconditional SELL market intent on bar T-31 (normally 03:59, fills 04:00); T = CT instant of 10:30 London (04:30, or 05:30 in 5-hour weeks); skip if missing or early_halt_ct
- exit: Market intent on bar T-2 (04:28, fills 04:29); missing -> first later bar; hold 29 min
- direction: always SELL
- extra data: Calendar/event tables k5/_releases.py (FOMC_STATEMENT_DATES, GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS with T in CT) from reports/stage_e2b_release_calendar.json plus Task 1b release check; k5/_calendar.METALS_FULL_SESSIONS: calendars, not market data

### K6-crushgap-01  [K6]  fixed_clock=no
- file: strategy/members/k6/crushgap.py
- traded: ZS (q_c 1) | read only: ZM; ZL (signal legs; never traded)
- DV `crush_gap_G`: GPM = 0.022*P_ZM + 11*P_ZL - P_ZS in USD/bu (vendor price / vendor_price_factor, exact integer units of 0.0001 USD/bu); G(d) = GPM_open(d) [opens of ZM, ZL, ZS 08:30 bars of CT date d] - GPM_close(d-1) [closes of the three 13:14 bars of d-1 = previous EC-CAL grain trade date]; guard: each leg's 13:14 d-1 bar and 08:30 d bar exist with same instrument_id; d in GRAIN_FULL_SESSIONS
  - inputs: ZM, ZL, ZS ohlcv-1m 13:14 (d-1) and 08:30 (d) bars; vendor_price_factor/tick from rules.products; availability: open of the 08:30 bars of d (08:31 CT); entry intent on the 08:30 ZS bar, fills 08:31
  - literals: TRADED="ZS" (k6/crushgap.py:66); SIGNAL_LEGS=("ZM", "ZL") (k6/crushgap.py:67); LEGS=(TRADED, *SIGNAL_LEGS) (k6/crushgap.py:68); GPM_UNIT_USD_PER_BU=Decimal("0.0001") (k6/crushgap.py:71); FILTER_USD_PER_BU=Decimal("0.02") (k6/crushgap.py:72); CLOSE_BEFORE_C_MIN=1 (k6/crushgap.py:73); EXIT_BEFORE_C_MIN=2 (k6/crushgap.py:74); FILTER_UNITS=_exact_units(FILTER_USD_PER_BU, "the filter") (k6/crushgap.py:92)
- entry: Market intent on the 08:30 ZS bar if G<=-0.02 (SELL) or G>=+0.02 USD/bu (BUY), non-strict; never an intent on ZM/ZL
- exit: Market intent on first ZS bar >= 13:13 (fills nominally 13:14); engine flatten backstop
- direction: BUY ZS if G>=+0.02, SELL if G<=-0.02 (overnight gap continuation)
- extra data: Calendars/tables k6/_calendar.py, k6/_wasde.py (WASDE dates at 12:00 ET = 11:00 CT, from reports/stage_e2b_release_calendar.json), k6/_limits.py (LIMIT_PERIODS from rules.price_limits): calendars and rules constants, not market data

### K6-limitcont-01  [K6]  fixed_clock=no
- file: strategy/members/k6/limitcont.py
- traded: HE; LE (q_c 1 each) | read only: none
- DV `limit_close_event`: Event if S(c,d-1)-S(c,d-2) = +L(d-1) ticks (BUY) or -L(d-1) ticks (SELL) exactly, and S(c,d-2)-S(c,d-3) is neither +L(d-2) nor -L(d-2); S = D9.7 settlement proxy of a trade date (volume-weighted close of bars in the settlement window [12:59:30,13:00:00) CT, fallback close of last bar before window end); L = initial daily limit in force from LIMIT_PERIODS in ticks; every bar S uses carries the instrument_id c of d's 08:30 bar; d-1,d-2,d-3 = three prior LIVESTOCK_TRADE_DATES
  - inputs: HE/LE ohlcv-1m bars (closes, volume near 13:00) of d-1,d-2,d-3; 08:30 bar of d; LIMIT_PERIODS, DROPPED_LIMIT_DATES, settlement window (rules.price_limits); LIVESTOCK_FULL_SESSIONS; availability: d-1 proxy known at d-1 close; event known at 08:30 of d; entry bar 08:44
  - literals: EXPOSURES=("HE", "LE") (k6/limitcont.py:66); ENTRY_BAR=time(8, 44) (k6/limitcont.py:67); EXIT_LEAD_MINUTES=2 (k6/limitcont.py:68); DAYS_BACK=3 (k6/limitcont.py:69)
- entry: Market intent on the 08:44 bar (fills 08:45) if event; the 08:44 bar must exist and carry c
- exit: Market intent on first bar >= 12:58 (fills 12:59) or earlier engine D9.7 forced exit
- direction: BUY after a +limit close, SELL after a -limit close (continuation)
- extra data: Calendars/tables k6/_calendar.py, k6/_wasde.py (WASDE dates at 12:00 ET = 11:00 CT, from reports/stage_e2b_release_calendar.json), k6/_limits.py (LIMIT_PERIODS from rules.price_limits): calendars and rules constants, not market data | Settlement proxy and limit amounts come from rules.price_limits constants and ohlcv-1m bars; no separate Databento schema

### K6-wasdepost-01  [K6]  fixed_clock=no
- file: strategy/members/k6/wasdepost.py
- traded: ZC (q_c 1) | read only: none
- DV `wasde_5min_move_R`: R = close of 11:14 bar - close of 10:59 bar in ticks on WASDE dates (T=11:00 CT fixed) in GRAIN_FULL_SESSIONS; both bars one instrument_id; R=0 -> no trade
  - inputs: ZC ohlcv-1m; WASDE_DATES; availability: close of the 11:14 bar (11:15 CT)
  - literals: EXPOSURES=("ZC",) (k6/wasdepost.py:43); SIGNAL_BAR=time(10, 59) (k6/wasdepost.py:44); ENTRY_BAR=time(11, 14) (k6/wasdepost.py:45); EXIT_BAR=time(13, 13) (k6/wasdepost.py:46)
- entry: Market intent on the 11:14 bar (fills 11:15) in sign(R)
- exit: Market intent on first bar >= 13:13 (fills 13:14)
- direction: side = sign(R) (continuation)
- extra data: Calendars/tables k6/_calendar.py, k6/_wasde.py (WASDE dates at 12:00 ET = 11:00 CT, from reports/stage_e2b_release_calendar.json), k6/_limits.py (LIMIT_PERIODS from rules.price_limits): calendars and rules constants, not market data

### K6-wasdepre-01  [K6]  fixed_clock=no
- file: strategy/members/k6/wasdepre.py
- traded: ZC; ZS (q_c 1 each) | read only: none
- DV `wasde_predrift_Dr`: Dr = close of 10:29 bar - open of 08:30 bar in ticks on WASDE dates (T=11:00 CT) in GRAIN_FULL_SESSIONS; both bars one instrument_id; Dr=0 -> no trade
  - inputs: ZC or ZS ohlcv-1m; WASDE_DATES; availability: close of the 10:29 bar (10:30 CT)
  - literals: EXPOSURES=("ZC", "ZS") (k6/wasdepre.py:46); DRIFT_START_BAR=time(8, 30) (k6/wasdepre.py:47); ENTRY_BAR=time(10, 29) (k6/wasdepre.py:48); EXIT_BAR=time(11, 14) (k6/wasdepre.py:49)
- entry: Market intent on the 10:29 bar (fills 10:30) in sign(Dr)
- exit: Market intent on the 11:14 bar (fills 11:15); missing -> first later bar; through the release
- direction: side = sign(Dr) (drift continuation)
- extra data: Calendars/tables k6/_calendar.py, k6/_wasde.py (WASDE dates at 12:00 ET = 11:00 CT, from reports/stage_e2b_release_calendar.json), k6/_limits.py (LIMIT_PERIODS from rules.price_limits): calendars and rules constants, not market data

### K7-expiry-01  [K7]  fixed_clock=YES
- file: strategy/members/k7/expiry.py
- traded: MBT (q_c 1) | read only: none
- DV: none (calendar/time flag only). literals: ENTRY_FILL_BEFORE_T_MIN=300 (k7/expiry.py:53); EXIT_FILL_BEFORE_T_MIN=1 (k7/expiry.py:54); T_EXP_SLOTS=("10:00", "11:00") (k7/expiry.py:55); WINDOW_START_CT=time(5, 0) (k7/expiry.py:56); WINDOW_END_CT=time(11, 0) (k7/expiry.py:57)
- entry: On each MBTX expiry date d in CRYPTO_FULL_SESSIONS and not VENDOR_DEGRADED: BUY market intent on bar T_exp-301 (04:59 or 05:59; fills T_exp-300 open); at most one per date
- exit: Market intent on bar T_exp-2 (09:58 or 10:58; fills T_exp-1); T_exp = 16:00 London in CT (10:00, or 11:00 in mismatch weeks); missing -> first later bar
- direction: always BUY (long only)
- extra data: Calendars k7/_calendar.py (CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED, MBTX expiry table with T_exp = 16:00 London in CT): calendars, not market data | Docstring note: every MBTX date is a roll-blackout date in the research window so expected trade count is 0

### K7-montrend-01  [K7]  fixed_clock=no
- file: strategy/members/k7/montrend.py
- traded: MBT (q 1) | read only: none
- DV `hourly_tsmom_s_t`: s_t = sign(close of bar at t-1min - open of bar at t-60min) in ticks at 20 decision times t = Sunday 18:00..23:00 and Monday 00:00..13:00 (hourly); 0 if either bar missing or instrument_ids differ; bars read only with trade_date d (Monday) from Sunday 17:00 CT to Monday 13:59
  - inputs: MBT ohlcv-1m of Sunday evening / Monday; Monday trade date d in CRYPTO_FULL_SESSIONS, not VENDOR_DEGRADED; availability: close of bar t-1 (t CT)
  - literals: MONDAY=0 (k7/montrend.py:58); SUNDAY_OFFSET_DAYS=-1 (k7/montrend.py:59); FIRST_DECISION=(SUNDAY_OFFSET_DAYS, time(18, 0)) (k7/montrend.py:60); LAST_DECISION=(0, time(13, 0)) (k7/montrend.py:61); STEP_MINUTES=60 (k7/montrend.py:62); LOOKBACK_MINUTES=60 (k7/montrend.py:63); SIGNAL_END_BEFORE_T_MIN=1 (k7/montrend.py:64); FLAT_AT=(0, time(14, 0)) (k7/montrend.py:65); FINAL_EXIT_BEFORE_FLAT_MIN=1 (k7/montrend.py:66); DIRECTION=1 (k7/montrend.py:67)
- entry: On bar t if s_t!=0, account flat with no pending order, and bar t exists with the signal bars' instrument_id: entry in direction s_t (fills t+1); at most 20 entries per date
- exit: Flatten at close of bar t-1 if open position sign != s_t (fills open of t); final exit on Monday 13:59 bar (fills 14:00)
- direction: direction = s_t (momentum, DIRECTION=+1)
- extra data: Calendars k7/_calendar.py (CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED, MBTX expiry table with T_exp = 16:00 London in CT): calendars, not market data

### K7-rev2h-01  [K7]  fixed_clock=no
- file: strategy/members/k7/rev2h.py
- traded: MBT (q 1) | read only: none
- DV `two_hour_return_r`: r1 = close of 10:29 bar - open of 08:30 bar (decision 10:30); r2 = close of 12:29 bar - open of 10:30 bar (decision 12:30), ticks; 0 if either bar missing or instrument_ids differ; target = -sign(r) x q
  - inputs: MBT ohlcv-1m bars of CT date d only; CRYPTO_FULL_SESSIONS, not VENDOR_DEGRADED; availability: close of bar at decision-1 (10:30 / 12:30 CT)
  - literals: BLOCK_MINUTES=120 (k7/rev2h.py:55); BLOCKS=3 (k7/rev2h.py:56); DECISION_BLOCKS=(1, 2) (k7/rev2h.py:57); SIGNAL_END_BEFORE_T_MIN=1 (k7/rev2h.py:58); FINAL_EXIT_BEFORE_END_MIN=1 (k7/rev2h.py:59); WINDOW_END_AFTER_BLOCKS_MIN=1 (k7/rev2h.py:60); DIRECTION=-1 (k7/rev2h.py:61)
- entry: At 10:30 and 12:30 (decided on the close of the bar at decision-1): hold if target equals position; else flatten (fills decision-time open), then entry on the decision bar if flat and bar exists with signal bars' instrument_id (fills +1 min); at most 2 entries per date
- exit: Final exit: market intent on the 14:29 bar (fills 14:30)
- direction: contrarian: -sign(r) (DIRECTION=-1)
- extra data: Calendars k7/_calendar.py (CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED, MBTX expiry table with T_exp = 16:00 London in CT): calendars, not market data

### K8-flight-01 (trials H30 and HEOD; ordinals 1,2)  [K8]  fixed_clock=no
- file: strategy/members/k8/flight.py
- traded: MGC (q_c 1) | read only: MES (signal leg, never traded)
- DV `mes_5min_return_r_k`: r_k = (c1-c6)/c6, c1,c6 = closes (integer ticks) of MES bars at t_k-1 and t_k-6, for 77 five-minute blocks t_k = 08:35..14:55 (k=1 uses the 08:34 and 08:29 bars); both present with one instrument_id, c6>0
  - inputs: MES ohlcv-1m bars of CT date d; availability: close of MES bar t_k-1 (t_k CT)
  - literals: TRADED="MGC" (k8/flight.py:69); SIGNAL="MES" (k8/flight.py:70); VARIANTS=("H30", "HEOD") (k8/flight.py:71); BLOCK_CLOCK_START=time(8, 30) (k8/flight.py:75); BLOCK_MINUTES=5 (k8/flight.py:76); BLOCKS=77 (k8/flight.py:77); END_BAR_BEFORE_T_MIN=1 (k8/flight.py:78); START_BAR_BEFORE_T_MIN=6 (k8/flight.py:79); REFERENCE_DATES=20 (k8/flight.py:80); MIN_VALUES=1200 (k8/flight.py:81); TAIL_DIVISOR=200 (k8/flight.py:82); H30_INTENT_AFTER_FILL_MIN=29 (k8/flight.py:83); LAST_EXIT_BAR=time(15, 4) (k8/flight.py:84)
- DV `tail_quantile_Q_d`: Q(d) = m-th smallest of all defined r_k over the 20 most recent FLIGHT_DATES strictly before d, m = ceil(0.005 n) = (n+199)//200; need n>=1200 reference values; warm-up rule; trigger at t_k if r_k <= Q(d) and r_k < 0
  - inputs: MES ohlcv-1m of 20 prior dates (FLIGHT_DATES = equity and metals full sessions); availability: reference dates strictly before d
  - literals: TRADED="MGC" (k8/flight.py:69); SIGNAL="MES" (k8/flight.py:70); VARIANTS=("H30", "HEOD") (k8/flight.py:71); BLOCK_CLOCK_START=time(8, 30) (k8/flight.py:75); BLOCK_MINUTES=5 (k8/flight.py:76); BLOCKS=77 (k8/flight.py:77); END_BAR_BEFORE_T_MIN=1 (k8/flight.py:78); START_BAR_BEFORE_T_MIN=6 (k8/flight.py:79); REFERENCE_DATES=20 (k8/flight.py:80); MIN_VALUES=1200 (k8/flight.py:81); TAIL_DIVISOR=200 (k8/flight.py:82); H30_INTENT_AFTER_FILL_MIN=29 (k8/flight.py:83); LAST_EXIT_BAR=time(15, 4) (k8/flight.py:84)
- entry: FIRST trigger of the day not skipped by the C6 release guard on MGC uses the day's one entry: BUY MGC market intent on MGC bar t_k-1 (fills t_k open); no entry while MGC holds a position or pending order
- exit: H30: market intent on MGC bar at min(T_e+29, 15:04); HEOD: on the 15:04 bar; T_e = CT open of the bar at which the position first shows; resent while refused; engine flatten at F 15:08
- direction: always BUY MGC after an extreme negative MES 5-min move
- extra data: Calendars k8/_calendar.py (FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES) and release-guard table k8/_releases.py (GUARD_ROWS from reports/stage_e2b_release_calendar.json; C6 skip of fills within [R,R+2min)): calendars, not market data

### K8-oilcad-01  [K8]  fixed_clock=no
- file: strategy/members/k8/oilcad.py
- traded: 6C (q_c 1) | read only: MCL (signal leg, never traded)
- DV `mcl_5min_return_r_t`: r_t = (c1-c6)/c6 Python float from integer-tick closes of MCL bars at t-1 and t-6 at decision times t = 08:05,08:10,...,13:25 (65/day); both present, one instrument_id, c6>0
  - inputs: MCL ohlcv-1m; availability: close of MCL bar t-1 (t CT)
  - literals: TRADED="6C" (k8/oilcad.py:55); SIGNAL="MCL" (k8/oilcad.py:56); FIRST_DECISION_CT=time(8, 5) (k8/oilcad.py:62); LAST_DECISION_CT=time(13, 25) (k8/oilcad.py:63); STEP_MIN=5 (k8/oilcad.py:64); LAST_BAR_BEFORE_T_MIN=1 (k8/oilcad.py:65); FIRST_BAR_BEFORE_T_MIN=6 (k8/oilcad.py:66); REFERENCE_DATES=20 (k8/oilcad.py:67); MIN_VALUES=1000 (k8/oilcad.py:68); Z_THRESHOLD=2.0 (k8/oilcad.py:69); EXIT_AFTER_FILL_MIN=14 (k8/oilcad.py:70); DECISION_TIMES_CT=decision_times() (k8/oilcad.py:88)
- DV `z_score_z_t`: z_t = r_t / s(d), s(d) = statistics.stdev (n-1) of every defined r_t over the 20 most recent OILCAD_DATES strictly before d; n>=1000; s=0 -> no trade; trigger |z_t| >= 2.0
  - inputs: MCL ohlcv-1m of 20 prior dates; availability: reference strictly before d
  - literals: TRADED="6C" (k8/oilcad.py:55); SIGNAL="MCL" (k8/oilcad.py:56); FIRST_DECISION_CT=time(8, 5) (k8/oilcad.py:62); LAST_DECISION_CT=time(13, 25) (k8/oilcad.py:63); STEP_MIN=5 (k8/oilcad.py:64); LAST_BAR_BEFORE_T_MIN=1 (k8/oilcad.py:65); FIRST_BAR_BEFORE_T_MIN=6 (k8/oilcad.py:66); REFERENCE_DATES=20 (k8/oilcad.py:67); MIN_VALUES=1000 (k8/oilcad.py:68); Z_THRESHOLD=2.0 (k8/oilcad.py:69); EXIT_AFTER_FILL_MIN=14 (k8/oilcad.py:70); DECISION_TIMES_CT=decision_times() (k8/oilcad.py:88)
- entry: Market intent on the 6C bar at t-1 (fills t open) when |z_t|>=2.0, flat on 6C, 6C bar present, fill minute not in a 6C release-guard interval
- exit: Market intent closing the position on first present 6C bar >= T_e+14 (fills nominally T_e+15)
- direction: BUY if c1>c6, SELL if c1<c6 (6C follows MCL's sign)
- extra data: Calendars k8/_calendar.py (FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES) and release-guard table k8/_releases.py (GUARD_ROWS from reports/stage_e2b_release_calendar.json; C6 skip of fills within [R,R+2min)): calendars, not market data

### K8-wkndbtc-01  [K8]  fixed_clock=no
- file: strategy/members/k8/wkndbtc.py
- traded: MNQ (q_c 1) | read only: MBT (signal leg, never traded)
- DV `weekend_btc_move_G`: G = P_S/P_F - 1 signed as integer tick difference P_S - P_F; P_F = close of MBT 14:59 bar on CT date d-3 (Friday), P_S = close of MBT 17:59 bar on CT date d-1 (Sunday, trade_date d); Monday d and Friday d-3 both in WKNDBTC_DATES; both bars one instrument_id; G=0 -> no trade
  - inputs: MBT ohlcv-1m Friday 14:59 and Sunday 17:59 bars; availability: close of the MBT Sunday 17:59 bar (18:00 CT Sunday)
  - literals: TRADED="MNQ" (k8/wkndbtc.py:51); SIGNAL="MBT" (k8/wkndbtc.py:52); MONDAY=0 (k8/wkndbtc.py:57); FRIDAY_OFFSET_DAYS=-3 (k8/wkndbtc.py:58); SUNDAY_OFFSET_DAYS=-1 (k8/wkndbtc.py:59); FRIDAY_BAR_CT=time(14, 59) (k8/wkndbtc.py:60); SUNDAY_BAR_CT=time(17, 59) (k8/wkndbtc.py:61); EXIT_BAR_CT=time(14, 58) (k8/wkndbtc.py:62)
- entry: Market intent on the MNQ 17:59 bar of Sunday (trade_date d), fills 18:00 open; only with no position/pending order; skipped if 18:00 falls in an MNQ guard interval
- exit: Market intent on first present MNQ bar >= 14:58 of CT date d (fills nominally 14:59)
- direction: BUY MNQ if G>0, SELL if G<0
- extra data: Calendars k8/_calendar.py (FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES) and release-guard table k8/_releases.py (GUARD_ROWS from reports/stage_e2b_release_calendar.json; C6 skip of fills within [R,R+2min)): calendars, not market data

### K9-anncday-01  [K9]  fixed_clock=YES
- file: reports/stage_e10_catalog_K9.md (draft, no code; entry at lines 195-300)
- traded: MNQ (q_c 1); M2K (q_c 3); MYM (q_c 3) | read only: none
- DV: none (calendar/time flag only). literals: EC-K9 date set (C9: 60 dates; 58 after R-12 exclusions of early-close/halt/closure dates, in the window 2025-07-03 and 2026-04-03)
- entry: BUY q_c by market intent on the 17:59 CT bar of the evening before announcement trade date d (Sunday 17:59 when d is a Monday), fills 18:00 CT open
- exit: Market intent at 14:58 CT on d, fill 14:59; early-close, early-halt and closure dates excluded; F governs an unscheduled halt; hold about 21 h
- direction: always BUY
- extra data: EC-K9 announcement calendar: FOMC statement days, NFP, GDP first and last estimates, ISM manufacturing, earlier of CPI/PPI per month; official schedules (calendar, not ohlcv-1m); some dates [unverified: rescheduled by the 2025 appropriations lapse]; no released value read | Catalog states signal is calendar membership only

## Core ports CP1/CP2/CP3 (K1-K7; same rule text per port, instantiated per cluster)

CP1 intraday momentum: s = sign(close of bar O+29 - open of the trade date's first bar); entry on bar C-31; exit first bar >= C-2. fixed_clock no. Variable available at O+30; entry at C-30.
CP2 opening-range breakout: OR = high/low of [O,O+15); first bar in [O+15,C) whose close is >= OR_high+4 ticks (buy) or <= OR_low-4 ticks (sell); one entry/date; exit on the 75th present bar after entry (no C-2 exit). Available at the breakout bar close.
CP3 prior-close location: CLV=(C-L)/(H-L) of the previous COMPLETE daily bar built from [O,C); CLV>=0.8 buy, <=0.2 sell; entry on O bar; exit first bar >= C-2. Available at O (prior-day data).
Literals per cluster (all files k<n>/cp1.py, cp2.py, cp3.py: SIGNAL_AFTER_O_MIN=29, ENTRY_BEFORE_C_MIN=31, EXIT_BEFORE_C_MIN=2, RANGE_MINUTES=15, BUFFER_TICKS=4, HOLD_BARS=75, CLV 0.8/0.2; file:line in JSON). Library design: docs/STAGE_E_DESIGN.md D6 lines 364-366.

| Cluster | Roots (q_c) | O / C | First bar | CP1 sig / entry bar / exit bar | CP2 range, buffer (4 ticks) | CP3 daily bar |
|---|---|---|---|---|---|---|
| K1 | MNQ 1, M2K 3, MYM 3 | 08:30 / 15:00 (F 15:08) | 17:00 CT d-1 bar with trade_date d | 08:59 / 14:29 / 14:58 | [08:30,08:45); MNQ 1.00, M2K 0.40, MYM 4.0 | [08:30,15:00) close 14:59 |
| K2 | ZT ZF ZN TN ZB UB, 1 each | 07:20 / 14:00 | 17:00 CT d-1 bar with trade_date d | 07:49 / 13:29 / 13:58 | [07:20,07:35); 4 x vendor tick | [07:20,14:00) close 13:59 |
| K3 | 6E 6A 6B 6C 6J 6S 6N, 1 each | 07:20 / 14:00 (F 15:08) | 17:00 CT d-1 bar with trade_date d | 07:49 / 13:29 / 13:58 | [07:20,07:35); 0.0002 (6E 6A 6C 6S 6N), 0.0004 6B, 0.000002 6J | [07:20,14:00) close 13:59 |
| K4 | MCL 4, NG 1 | 08:00 / 13:30 | 17:00 CT d-1 bar with trade_date d | 08:29 / 12:59 / 13:28 | [08:00,08:15); MCL 0.04, NG 0.004 | [08:00,13:30) close 13:29 |
| K5 | MGC 1, MHG 2 | MGC 07:20/12:30; MHG 07:10/12:00 | 17:00 CT d-1 bar with trade_date d | MGC 07:49/11:59/12:28; MHG 07:39/11:29/11:58 | MGC [07:20,07:35) 0.40; MHG [07:10,07:25) 0.0020 | MGC close 12:29; MHG close 11:59 |
| K6 | ZC ZW ZS ZM ZL HE LE, 1 each | grains 08:30/13:15 (F 13:18); livestock 08:30/13:00 (F 13:03) | grains: earliest bar >= 19:00 CT d-1 (else 08:30); livestock: 08:30 bar of d | 08:59 / grains 12:44, livestock 12:29 / grains 13:13, livestock 12:58 | [08:30,08:45); ZC ZW ZS 1.00, ZM 0.40, ZL 0.04, HE LE 0.100 | grains close 13:14; livestock close 12:59 |
| K7 | MBT 1 | 08:30 / 15:00 (F 15:08) | 17:00 CT d-1 bar with trade_date d (not weekend bars) | 08:59 / 14:29 / 14:58 | [08:30,08:45); 20.00 USD | [08:30,15:00) close 14:59 |

## Notes for the feature builder

- Members with a decision variable computed from several legs: K6-crushgap-01 (ZM, ZL, ZS bars), K8-flight-01 (MES signal, MGC traded), K8-oilcad-01 (MCL signal, 6C traded), K8-wkndbtc-01 (MBT signal, MNQ traded).
- Rolling-reference variables (percentile or z-score over 20 prior full-session dates, strictly before d): K4-ovr-01, K5-ovr-01, K8-flight-01, K8-oilcad-01.
- Overnight-carried variables: K4-apipre-01 (Tuesday 15:24-15:39 move into Wednesday 07:29 entry), K1-cp1/K2..K7 cp1 (first bar 17:00 CT d-1), K8-wkndbtc-01 (Friday 14:59 to Sunday 17:59).
- K9-anncday-01 is a draft (R-02 user decision pending to keep or cut); no code exists; entry rule 17:59 CT the evening before d.
- Catalog json lists excluded rows (K1-predrift-01, K1-ml-01..K8-ml-01, K4-ngrev-01, K6-ovr-01) with no code; not inventoried. Catalog exposures for K4 (RBOB, ULSD), K5 (silver) and K3 mehedge/E.0 6E are not coded; code trades only the roots listed above.
- Literals filter: JSON `literals` lists module-level scalar constants of the member file (file:line); tables and long tuples (decision-time lists, TRADING_WINDOWS) are not listed and are described in the formula text.
