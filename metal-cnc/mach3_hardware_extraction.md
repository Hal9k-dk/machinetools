# Mach3 Hardware Config Extraction (for FluidNC conversion)

Source: `original_mach3_files/Mach3/` — extracted 2026-10-18.
The active CNC profile is **Mach3Mill.xml** (all values below were identical across all `xmlbackups/` backups, so this is one stable configuration).
`Mach3Turn.xml` and `Plasma.xml` are untouched stock lathe/plasma profiles (paths still point to old demo files) — treat as irrelevant.

The motion controller in use was an **XHC USB motion card** (`Device = NcUsbPod-XHC-Mach3-USB-Motion-Card`, plugin `NcUsbPod.dll`) — the same family documented in `MK100-Series-Manual.pdf`. Card I/O: 16 inputs, 16 outputs (USBINPUTS=16 / USBOUTPUTS=16), 4–6 axis step/dir, PWM spindle output. A WHB04B wireless pendant was also connected (`whbxerr.txt`).

Note: all parallel-port (LPT) step/dir/input pin tags in the XML are dead config from the stock driver — the XHC card does not use them, so ignore `Motor0StepPin=2`-style entries.

---

## Axes / Motor Tuning (Config → Motor Tuning)

Mach3 velocity values are stored in the XML divided by 60 (×60 = dialog value in mm/min).

| Axis          | Steps/mm | Max velocity | Max rate mm/min | Accel mm/s² |
| ------------- | -------- | ------------ | --------------- | ----------- |
| X (0)         | **320**  | 33.34 mm/s   | **2000 mm/min** | **400**     |
| Y (1)         | **320**  | 33.34 mm/s   | **2000 mm/min** | **400**     |
| Z (2)         | **320**  | 33.34 mm/s   | **2000 mm/min** | **400**     |
| A/Motor4 (3)  | 10       | 16.67 mm/s   | 1000 mm/min     | 400         |
| B (4) / C (5) | 88.333   | 50 mm/s      | 3000 mm/min     | 200         |

- Motors 0–3 **active** (4 steps/dir motors configured, one each for X, Y, Z, A).
- Steps of 320 steps/mm suggests e.g. 1.8° steppers × 8 microsteps × 5 mm lead screw, or 16 microsteps × 10 mm lead — verify microstep DIP settings on your drives when re-deriving calibration.
- Z has the same 320 steps/mm and 2000 mm/min as X/Y — unusual for a gantry/mine Z, so worth double-checking against the physical Z screw (possibly a lead-screw Z with high lead).

### For the 6x.config.yaml placeholders:
- `x.steps_per_mm / y.steps_per_mm / z.steps_per_mm: 320`
- `max_rate_mm_per_min: 2000` (X, Y, Z)
- `acceleration_mm_per_sec2: 400`

---

## Homing & Limit Switches

From `<Pod>` (XHC card plugin) and Mach3 homing tags:

| Axis | Home switch enabled | Home direction (GHomeWay) | Pull-off after homing (card) | Ref/homing speed |
|------|--------------------:|---------------------------|------------------------------|------------------|
| X | **Yes** (HomeLmt1=1) | **−1 (negative side)** | **+5.0 mm** | 40 |
| Y | **Yes** (HomeLmt2=1) | **−1 (negative side)** | **+5.0 mm** | 40 |
| Z | **No** (HomeLmt3=0) | +1 (stale, homing off) | −5.0 mm (configured but unused) | 40 |
| A | No (HomeLmt4=0) | −1 (stale) | +10 mm | 20 |

Card-level switch settings:
- `HomeLimitEn = 65535` → all 16 input channels enabled for home/limit duty (mask), i.e. "switch input on any channel triggers home/limit".
- `Homing = 2` (homing stage/mode setting on the card).
- `HomeDec = 1` (deceleration/homing slow-down setting).
- `SoftLmtDis = 1` → **soft limits disabled on the card** (consistent with `soft_limits: false` in the yaml).
- `RefSpeed0..2 = 40` (homing/reference feed speed used by Mach3).
- LastErrors.txt shows limit switches and E-stop were exercised in normal operation ("LimitSwitch Triggered", "ReConfiguration Estop").

**No travel limits / soft-limit ranges are stored anywhere** — soft limits were disabled, and no X/Y/Z max travel values exist in the config. (Minor hint: display/limit-ish XML fields M0Max=300, M1Max=400 exist but semantics of those fields are undocumented — possibly 300/400 mm travel for X/Y; use only as a check against measured travel.)

Switch polarity/active level is not recorded in the XML (it lives in the card's plugin UI); the curtain-style home switches on this machine class are typically 5 V NPN sensors wired active-low. Confirm by metering.

### For the yaml:
- X, Y: `limit_neg_pin` correct choice (home at negative side, pull-off/dwell +5 mm after hit).
- Z: **no home switch installed** — consider homing cycle TBD = disabled for Z or fit a switch.
- Suggested homing: X/Y cycles first, Z last; `positive_direction: false` for X and Y.

---

## Motor / Electrical

- Steppers + step/dir drives (no servos; card outputs step/dir).
- Parallel port fallback config present but unused (Port1 0x378 etc.).
- Microstepping: 320 steps/mm is consistent with 8 or 16-step microstepping — verify with drive DIPs.

## Spindle

- Controlled via the card: `SpinCW` output #7 (relay), `SpinCCW` #8; `SpinOnTime = 2 s` delay; `SpinDelayCW/CCW/Down = 1 s`.
- PWM-capable (`PWM=1`, `ModSpindleCal=16384=2^14`, PWMBase=1000), pulley ratio PULLEY=3 with ratios 1:1, preset speeds 1000/2000/4000/24000 rpm.
- No VFD/Modbus configured in Mach3 — the RS485 H100 VFD in the FluidNC yaml is new hardware, nothing to import.

## Coolant

- `Flood`/`Mist` macros mapped to OEM buttons 9/10 (stock, no custom plumbing evidence). `NoFlood=1` set → flood/mist not in actual use.

## Probe

- A probe/tool-setter was used: macro **M930** (Auto Tool Zero):
  - probe down `Z - 300` mm at feed **F200 mm/min**, then set Z DRO to gage-block height (`GetOEMDRO(1001)`).
  - So: probe travel 300 mm allowance, **probe feed 200 mm/min** is a good `probe:` feed value.
- `M933` returns to X0/Y0/A0 after setting.

## Other settings worth carrying over

- **Safe Z**: `UseSafeZ = 1`, `m_SafeZ = 10 mm`, knee travel 1300 (XCLength/YCLength/ZCLength = 1300, display values).
- Back-off after a reset/carve-end handling: `BackX=5, BackY=-5, BackZ=1, BackSpeed=20` (screenset feature).
- Arc: `arc_tolerance_mm: 0.002` in the yaml — the stock Mach3 mill value for `CVFeedRate/BlendFactor` does not translate; keep 0.002 unless machining fits show rounding.
- Work offsets last in use: X=15.6687, Y=1.0750, Z=−0.9063 (job context only, not config).
- Last production G-code: `120 46 3mm.tap`, `140 90 ny.tap` (job sizes ~120×46 mm, 3 mm material; "ny" = Norwegian "new" — consistent with plasma/cutter sheet jobs).

---

## Recommended answers for the `TBD`s in 6x.config.yaml

| Yaml path | Value from Mach3 | Confidence |
|---|---|---|
| axes.x.steps_per_mm | 320 | high (from motor tuning, verify microstepping) |
| axes.y.steps_per_mm | 320 | high |
| axes.z.steps_per_mm | 320 (verify against Z screw/drive) | medium |
| axes.{x,y}.max_rate_mm_per_min | 2000 | high |
| axes.z.max_rate_mm_per_min | 2000 (verify) | medium |
| axes.{x,y,z}.acceleration_mm_per_sec2 | 400 | high |
| axes.{x,y,z}.max_travel_mm | **not recorded** — measure physically | n/a |
| axes.x.homing.cycle | first (#1) | high (home switch present, negative side) |
| axes.y.homing.cycle | first (#1 or #2 with X) | high |
| axes.z.homing.cycle | **no Z switch** — last or disabled | high |
| axes.{x,y}.homing.positive_direction | false (homes toward negative) | high |
| axes.{x,y}.homing.mpos_mm | 5.0 after pull-off (e.g. −5 or 0 depending on convention) | medium — reconcile with pull-off +5 mm |
| axes.z limit_neg_pin | no switch installed | high |
| probe feed (M930) | 200 mm/min | high |
| flood/mist | not in use (NoFlood=1) | high |

### Not recoverable from Mach3 files (must come from MK100 manual / metering)
- Physical limit-switch wiring polarity (active high/low) — the card's active-low handling was configured in the plugin UI, and the yaml already assumes `:pu` pull-down/pull-up choices.
- E-stop wiring (exists, but config is inside the card plugin UI; yaml already has `estop_pin: gpio.35:pu`).
- Card input channel ↔ physical terminal mapping (see MK100 manual / plugin IO panel).
- Steps-per-mm *derivation* (leadscrew pitch × microstepping) — confirm with a test jog + DRO comparison on FluidNC before trusting 320.
- Probe/tool-setter polarity and which terminal (`toolsetter_pin: gpio.32` per yaml).

---

# Deep scrape round 2 (pendant, controller board, host data — 2026-10-18)

## 1. The controller board — identified from the photo (PXL_20261015_182507506.jpg)

The board inside the enclosure is printed **"MKS4-V"** with a barcode label reading
`20210816 | ARM:V3.1.3.3 V1.0 | FP:V02`, silk-screen text near the main MCU, and **HCTECH.COM** on the board edge. This is the **HCTech/XHC MKS4-V USB motion card** — consistent with the `NcUsbPod-XHC-Mach3-USB-Motion-Card` device string in Mach3 and with the XHC MKX card family. Photo observations (layout-level, not part-level):
- Left terminal-block bank: roughly 9–10 optocoupler-type channel ICs on the input side with multi-colored signal wires.
- Right terminal-block bank: roughly 7–8 channel ICs (output side) plus power terminals with red-marked leads.
- Two large TQFP MCUs (one sealed with a QC sticker), an electrolytic cap (marked "904"/"1904") and other support parts.
- At least one unused pin header along the bottom edge — not all of the card's 16-in/16-out capacity appears wired out.

For FluidNC this mainly confirms the I/O class: **optocoupler-isolated inputs (sink-type, active-low per plugin release notes)**. The yaml already assumes `:pu` inputs which is the standard FluidNC counterpart to active-low sink wiring.

## 2. Wireless USB pendant — XHC WHB04B-family, confirmed ✅

Evidence chain:
- `whbxerr.txt` logs the pendant's USB identity: composite HID `VID_10CE` (XHC Technology) with **PID_EB73**, interfaces `mi_00` (two report collections) + `mi_01`, report lengths **98 and 93 bytes**.
- `NcUsbPod.dll` contains dedicated handler strings `get whbx device …` and supports **both PID_EB73 and PID_EB93** (WHB04B / WHB04BX revisions; the log shows this installation actually talked to an **EB73 unit**).
- Plugin resource strings: dialog **"XHC-WHB04B -Configuration"**, page **"WHB04X Config"**, checkbox **"Enable Whb04"** → `HBXEN = 1` in Mach3Mill.xml (pendant enabled).
- Plugin file version: **"XHC MKX Card PlugIn for Mach3", InternalName NcPod.dll, product string "XHC-USB-Motion-Card-V2.59.1"**; its build tag references SDK flavor `ncPod-V2.50-V-V20 - Wheel` (pendant-wheel edition).
- Plugin config pages also expose: **Homing mode (No Homing / Single Stage / Dual Stage)** — matches `Homing=2` in the XML (**Dual Stage**, aligning with `homing_runs: 2` in the FluidNC yaml); **"Pulse per Rotate"** (`PulsCntPeroate=200` → handwheel **200 PPR**); fields T2/T3/T4 X/Y/Z offsets ("tool-change staging offsets"); **"Home Dec Enable"** (`HomeDec=1`); **LimitEn** (`HomeLimitEn=65535`); **Output Test**; "G code Buffer Time ms" (`GBufTime=1024`).

**Pendant key → Mach3 mapping from `<Shuttle>` in Mach3Mill.xml** (raw values; decode follows standard Mach3 OEM-button numbering):

| Pendant key index | XML code | Most likely binding |
|---|---|---|
| SHUBUTTON0 | 3 | Cycle Start |
| SHUBUTTON1 | 4 | Feed Hold / Stop |
| SHUBUTTON2–7 | 70…75 | six-function group (Rewind/Zero-All/Edit-file style block per Buttons.txt ordering) |
| SHUBUTTON8/9 | 35 / 36 | Feed-rate override + / − |
| SHUBUTTON10–15 | 0 (unmapped) | defaults |
| Macro1 & Macro3 | 930 | two pendant keys run macro **M930 = Auto Tool Zero via G31 probe** (also confirmed: `ProbeDiag.txt` exists and M930 macro probes Z−300 at F200) |
| OEM1 | 1001 | one key triggers OEM-button **1001** ("Ref All Home"-style function) |
| BUTTON0–15 (2nd bank) | 20, 49, 73, 60, 72, 24, 68, 33, 25, 36, 21, 69, 26, 55, 71, 70 | secondary mapping bank from the WHB04B config page |
| JogMode | 0 | step/continous mode default |
| InchUnit | 0 | **metric** — confirms machine is mm-based |
| JogPlugVert/Horiz | 1 / 0 | plugin jog filter |

Context from stock macros: `m999.m1s` fires four movement buttons sequentially with `IsMoving()` waits — a per-axis homing/zero routine used together with the pendant key bank.

**Wheel / MPG geometry (from Mach3Mill.xml):**
- `PulsCntPeroate = 200` → handwheel = **200 pulses per rotation** (PPR).
- `MPGVel0..6 = 100` — pendant traverse speed 100 mm/min.
- `JogInc0..3 = 1.0 / 0.1 / 0.01 / 0.001` and screen `MillJogIncs.txt = .1/.01/.001/.0001` — pendant jog step list in mm.
- `Enc0/Enc1/Enc2 = 237 / 370 / −114` — accumulated wheel tick counters (session remnants only).
- Jog-step engine strings matched in the DLL: `Jog Step/Conti/MPG`, `MPG Increase Mode`, `Cycle MPG jogging mode`, `Lockout Wheels`, `Lock/Unlock Shuttle`.

**Impact for the FluidNC conversion:** the WHB04B is a Mach3/ESP-side plugin accessory, not something to re-use in FluidNC. FluidNC swap options if you want wireless jogs: keep an XHC pendant with a dedicated WHB04 bridge box, use a Bluetooth/USB HID pendant FluidNC supports, or skip. Physical hardware on the machine (handwheel feel, knob style) is reusable only as a shell; the pendant's radio+firmware is XHC-specific.

## 3. Axis/axis-slave data (corrects any ambiguity from round 1)

- `Motor0Active..Motor3Active = 1`, Motor4/5 = 0 → exactly **4 motor channels used** (X, Y, Z, + an idle "A" channel configured but likely unused in practice — see note).
- `Slave0/1/2 = 3` — Mach3 slave-axis register; **no evidence of a slaved gantry pair** in the actual XMLs, so treat each axis as an independent single stepper (consistent with the single-motor-per-axis `i2so` pin scheme in 6x.config.yaml).
- Motor 4/5 tuning values (Vel 50, Steps 88.333) present but disabled.

## 4. Firmware-side numbers from the card/plugin round-up

- Card tech features (PlugIns Release Note v3.16.5): 4/6-axis step/dir, **8 GP outputs, 16 GP inputs**, **1 PWM spindle output**, **up to 2000 kHz step pulse**.
- Latest Mach3 plugin v3.16.5 (2020-07-24); change highlights: WHB04BX support, slave-axis home logic, "jog move disable when according limitswitch is on", "cannot reset problem when active-low input io numbers are more than 8" (proof active-low input wiring), G76 support.
- `<Pod>` block recap: `GBufTime=1024` (ms of G-code buffering), `HomeLimitEn=65535` (all limit inputs enabled), `Homing=2` (dual-stage), `HomeDec=1`, `pulseHz=4`, `PulsCntPeroate=200`, `FSlect=63`, `SpinOnTime=2` s, `SoftLmtDis=1`, `G02SYN=0`, `SaveWk=0`.

## 5. Last remembered machine positions (RunData.dat)

Doubles decoded from `RunData.dat`: **79.332 / 152.5 / 80.803 / −96.325 / −126.791 / −3.0 mm** — most plausibly last-remembered axis positions across X/Y/Z/A/B/C DROs at power-down. Read as **sanity-check reference points** (Z parked ≈ 80 mm high; Y at 152 mm), **not** as travel limits.

## 6. Tool table is empty — nothing to port

`tools.dat` decodes as 254 tool slots at a **37-byte stride**, all diameter / Z-offset / wear fields **zero** (parser artifacts look like filler ASCII but carry table structure only). ⇒ FluidNC tool table starts empty; no offsets to preserve.

## 7. Sample job confirmation

`Scorpion.tap` (GCode folder, metric `G21`, `T1M6`, **S10000 M3**, cutting `F600`, `Z-3.000` depth, part spanning ~100 × 235 mm) shows the machine was used for **spindle milling/engraving at 10,000 rpm with single-tool jobs** — corroborates `SPEED1=1000 / SPEED2=2000 / SPEED3=4000 / SPEED4=24000`-style PWM preset ladder in Mach3 settings and confirms spindle PWM usage (no VFD close-loop in Mach3-era config). Supplementary sample `roadrunner.tap` uses F60/S60 (stretch/finishing pass) with `G43H5` tool-length offsets.

Note the machine's `120 46 3mm.tap` and `140 90 ny.tap` last-run filenames (2.x mm material) suggest mixed engraving/cutting use; the MK100 manual in the root folder is actually a **VFD manual** (frequency converter, RS485 Pd-parameters, Modbus) — useful for the H100/RS485 FluidNC spindle plan rather than for the old setup.

---

# The 4th (rotary) axis — dedicated analysis (2026-10-20)

## What Mach3 stored (axis index 3 = A, 1-based tags = 4)

| Field | Value | Reading |
|---|---|---|
| `Steps3` | **10** | **10 steps per degree** — Mach3 has no rotary-specific unit; "steps per user unit" with user unit = ° for the A axis |
| `Vel3` | 16.67 | 16.67 °/s = **1000 °/min** (2.8 table rpm) |
| `Acc3` | 400 | **400 °/s²** (same accel as X/Y/Z — suggests deliberate copy, not junk) |
| `Motor3Active` | 1 | card's A step/dir output enabled |
| `AxisToMotor4` | 4 | 1:1 axis→motor, no slave |
| `HomeLmt4` | **0** | **no home/limit switch on the rotary** |
| `GHomeWay4` | −1 | homing direction "negative" configured (dormant — homing off) |
| `APullOff` | 10 | 10 (°) pull-off configured (dormant) |
| `M3Max/M3Min` | **+370 / −370** | if these limit-ish fields belong to axis 3, that's **±370° ≈ one full turn + margin** — plausible rotary range (semantics of M* fields not documented; treat as a hint) |

Additional circumstantial evidence:
- `AxisKeys6..11 = 65, 68, 87, 83, 81, 69` = keyboard keys **A, D, W, S, Q, E** — extra jog bindings beyond the stock arrows/pgup-pgdn (X/Y/Z), consistent with someone wiring jog keys for the rotary (and possibly B/C).
- `RunData.dat` 4th double = **−96.325** — if the slot order is X,Y,Z,A,B,C, the A DRO sat at ≈ −96° at last shutdown ⇒ the axis *did move at some point* (test jogs at minimum).
- `m933.m1s` (user-era, 2017-03-06) ends with `Code "G0 X0 Y0 A0"` — "return to origin" routine includes A.
- All 22+ config backups from Feb 2022 → Oct 2026 are byte-identical on these fields — the rotary tuning was set once and never touched.

## Counter-evidence (be honest about usage)

- **Zero A-words in every G-code file** in the install (including the 2022 user-made `MDITeach.tap`, which only contains `G0 G53 Z0` / `G53 X0 Y5` — machine-coordinate park, and note Y5 matches the 5 mm pull-off exactly).
- No A home/index switch, no rotary-specific encoder config.
- So: the 4th axis was **configured and electrically active, but no archived job ever rotated it** — either it was used for one-off work not kept in the folder, or it was fitted and mostly left idle.

## Mechanical derivation of "10 steps/°" (FYDM504T driver microstep table)

The drives are **FYDM504T two-phase drivers** (pulses/rev options: default/all-on = full-step 200, then 400, 800, 1600, 3200, 6400, 12800, 25600, plus 1000, 2000, 4000, 5000, 8000, 10000, 20000, 25000).

`steps/° = pulses_per_motor_rev × gear_ratio / 360 = 10` ⇒ `pulses_per_motor_rev × ratio = 3600`:

| Driver pulses/rev | Required ratio | Verdict |
|---|---|---|
| 200 (default, full-step) | **18:1** | ✅ exact, 2-stage planetary (vendor catalog sells planetary reducers) |
| 400 | **9:1** | ✅ exact, common single-stage ratio |
| 1000 | 3.6:1 | possible (3.6:1 exists in some planetary lines) |
| 2000 | 1.8:1 | less standard |
| 1600 / 3200 / 4000 | 2.25 / 1.125 / 0.9 | ❌ non-integer ratio, impossible with integer-tooth belt pulleys |
| any | direct 1:1 | ❌ would need 3600 pulses/rev, not an available setting |

**Most likely: 18:1 planetary reducer at full-step (200 pulses/rev), or 9:1 at 400 pulses/rev.** Both give exactly 10.0 steps/°.

Cross-check with the linear axes under the same driver family: 320 steps/mm ⇒ `pulses/rev = 320 × lead`:
- lead **5 mm → 1600 pulses/rev** ✅ (SW off,off,on,on — standard; SFU1605 ball screws are the classic 6040-class fit)
- lead 10 mm → 3200 ✅ also possible (SFU1610)
- leads 6.25/12.5/2.5 also map to available settings; belt-drive (GT2/20T etc.) does **not** fit 320 → machine is screw-driven.

## Carrying it into FluidNC

- FluidNC keeps the field name `steps_per_mm` even for rotary axes (one unit = one degree for an `a:` axis) → **`a: steps_per_mm: 10`**, `max_rate_mm_per_min: 1000`, `acceleration_mm_per_sec2: 400`.
- No limit/home switch existed in Mach3 → yaml choice for A: `hard_limits: false`, homing optional (`must_home` currently true would require either a switch or omitting A from homing cycles).
- `max_travel_mm` for A: use ≥360 (Mach3's hint was ±370) if you enable soft limits; FluidNC rotary soft limits are usable without a switch only after explicit homing or by disabling them (`soft_limits: false`, matching Mach3 behavior).
- Since Mach3 never home-referenced the rotary, a FluidNC `homing: positive_direction/mpos` for A must be chosen fresh (any fixed convention, e.g. home once against a DIY switch or mark and disable).
- **Verify before trusting:** jog exactly one programmed degree with a dial/indicator — expected 10 pulses/° is far below typical rotary setups (usually 100–400 steps/°); if the table moves ≈ 10× too far or too little, the driver DIP or the assumed ratio differs (e.g. drive on 200 pulses + direct-ish 1:1 would instead be 0.555 steps/°). A single measured degree settles it.
