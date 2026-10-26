# DM Series Two-Phase Stepper Driver — DM548M

> English translation of the Dongfang Digital Machine (东方数字机) DM548M datasheet, printed from
> `东方数字机.com/ProductDetail/6857826.html`.
> Source PDF: `DM548M驱动器.pdf` (7 pages). Pages 2–6 of the PDF are blank print artifacts
> (no text layer); the product photo, mounting-dimensions diagram and wiring diagrams exist
> only as images and are described in text below. Section order follows the original.

---

## Product Overview

| Item | Specification |
|---|---|
| Model | DM548M |
| Power supply voltage | DC12–40 V |
| Control mode | Pulse control |
| Output current | 0.6–4.8 A, 8 settings selectable |
| Digital inputs | 3 |
| Digital outputs | 1 |
| Microstepping | 6 settings selectable, max. subdivision 6400 |
| Selectable speed | 800 rpm |
| Pulse width | Default 400 kHz / 100 kHz selectable |
| Compatible motors | 42 / 57 / 60 mm |
| Application | Industrial control |

## Application Fields

Industrial control.

## Product Mounting Dimensions

The source contains a mounting-dimensions diagram (`DM548M安装尺寸图`), but it is an image only — no dimensioned drawing was captured as text. See the original PDF for the diagram.

## Driver Wiring Method

- Common-anode wiring (active low)
- Common-cathode wiring (active high)
- Drive power: DC12–40 V

Note: the control-system common terminal is +3.3 V–+24 V universal; the drive power supply is 9–42 V DC.
- 12 V signal: in series with a 1 kΩ resistor.
- 24 V signal: in series with a 2 kΩ resistor.

The wiring diagrams are images only in the source; see the original PDF.

## Running Current Setting

DIP switches 4, 5 and 6 on the driver board correspond to S4, S5 and S6.

| Peak current | S4 | S5 | S6 |
|---|---|---|---|
| 0.6 A | NO | NO | NO |
| 1.2 A | NO | OFF | NO |
| 1.8 A | NO | NO | OFF |
| 2.4 A | NO | OFF | OFF |
| 3.0 A | OFF | NO | NO |
| 3.6 A | OFF | OFF | NO |
| 4.2 A | OFF | NO | OFF |
| 4.8 A | OFF | OFF | OFF |

## Microstep Subdivision Setting

The subdivision number is set by the DIP switches on the driver board. The user can set it according to the subdivision-selection-table data on the driver's outer casing (best done with the power off). The step angle after subdivision is calculated as follows:

step angle = motor intrinsic step angle / subdivision number

Example: a motor with an intrinsic step angle of 1.8°, at 4 subdivisions, has a step angle of 1.8° / 4 = 0.45°.

DIP switches 1, 2 and 3 on the driver board correspond to S1, S2 and S3.

| Subdivision | S1 | S2 | S3 |
|---|---|---|---|
| 200 | ON | ON | OFF |
| 400 | ON | OFF | ON |
| 800 | ON | OFF | OFF |
| 1600 | OFF | ON | OFF |
| 3200 | OFF | OFF | ON |
| 6400 | OFF | OFF | OFF |

## Common Faults

**Reminder:** Do not miswire 220 V, otherwise there is no warranty. It is recommended to configure the DIP switches with no power applied.

| Fault | Possible cause | Remedy |
|---|---|---|
| Alarm indicator off | Motor wiring incorrect | Check and connect the wires properly |
| Alarm indicator off | Voltage too high or too low | Check the power supply |
| Motor does not turn, and no holding torque | Motor connections incorrect | Correct the motor connections |
| Motor does not turn, and no holding torque | Offline enable / RESET signal active | Deactivate RESET |
| Motor does not turn, but has holding torque | No pulse signal input | Adjust the pulse width and signal level |
| Motor does not turn, but has holding torque | Subdivision too small | Select the subdivision correctly |
| Motor does not turn, but has holding torque | Current set too small | Select the current correctly |
| Motor does not turn, but has holding torque | Driver is protected | Power off, then power on again |
| Motor rotation direction wrong | Power phase sequence wired incorrectly | Swap any two phase wires (e.g. swap A+ and A−) |
| Motor rotation direction wrong | Motor wire has an open circuit | Recheck and connect correctly |
| Motor rotation direction wrong | Direction signal input incorrect | Change the direction setting |
| Motor torque too small | Phase current set too small | Set the phase current correctly |
| Motor torque too small | Acceleration too fast | Reduce the acceleration value |
| Motor torque too small | Motor stalled | Clear the mechanical fault |
| Motor torque too small | Driver and motor mismatched | Use a suitable driver |
| Position incorrect | Signal subject to interference | Eliminate the interference |
| Position incorrect | Subdivision incorrect | Set the subdivision correctly |
| Position incorrect | Current too small | Increase the current |
| Position incorrect | Motor wire connection poor | Check and connect correctly |
| Motor stalls during acceleration | Acceleration time too short | Lengthen the acceleration time |
| Motor stalls during acceleration | Motor torque too small | Select a suitable torque motor |
| Motor stalls during acceleration | Voltage or current too low | Increase the voltage or increase the current |

---

## Site page furniture (not part of the datasheet)

| Original | Translation |
|---|---|
| 首页 > 两相步进驱动器 > DM548M | Home > Two-Phase Stepper Drivers > DM548M |
| 立即询盘 | Send inquiry / Request quotation |
| 分享 | Share |
| 产品详情 | Product details |
| 上一个 : DM545M | Previous: DM545M |
| 下一个 : DM560L | Next: DM560L |
| Copyright © 东方机电有限公司 2022 All Rights Reserved | Copyright © Dongfang Electromechanical Co., Ltd. 2022 All Rights Reserved |

---

## Translation notes / caveats

- Pages 2–6 of the PDF are blank print artifacts (the page images failed to render as text); they contain no data. The product photo, mounting-dimensions diagram and wiring diagrams exist only as images and are described above rather than reproduced.
- In the running-current table the source prints switch states as "NO" and "OFF". "NO" (normally open) is unusual for a DIP switch; treat NO and OFF as the two switch positions and verify against the physical driver before wiring.
- Row "6400" of the microstep table is printed as `OFF | OFF | OF` — the final `OF` is read as `OFF`.
- Fault-table row 8 reads "断电后中新上电", interpreted here as "power off, then power on again" (likely `重新上电`).
- The first two fault rows both list "alarm indicator off" (警报指示灯灭); this may be a source typo (one may intend "on").
- Compatible motor frame sizes are given as 42 / 57 / 60 mm. 57 mm is the industry-standard NEMA 23 size (the source writes 57).
- Terminology: 细分 = microstepping/subdivision; 脉冲控制 = pulse control; 共阳极/共阴极 = common anode / common cathode.
