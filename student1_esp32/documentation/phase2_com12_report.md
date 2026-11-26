# Phase 2 / Mission 1 Report — COM Port (`COM12`) Measured Results

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R  
**Date:** 2026-11-26  
**Source Data:** `student1_esp32/benchmarks/mission1_throughput.csv`, `student1_esp32/logs/mission1_pipe_results.json`

---

## 1. COM Port (`COM12`, WCH USB-UART Bridge) Measurements (3 Repeats Each)

### Speed=0 Throughput vs Baud (`16 kHz`, `i16`, `samples_per_packet=320`, `64,000 B` payload)
| Baud Rate | Theoretical 10-bit Max | Mean Board Throughput | Std Dev | Wire Efficiency | Gaps / Bad CRC / UART Errors |
|---|---|---|---|---|---|
| `115,200` | `11,520 B/s` | `11,376.7 B/s` | `0.9 B/s` | `98.8%` | `0 / 0 / 0` |
| `921,600` | `92,160 B/s` | `90,909.0 B/s` | `105.3 B/s` | `98.6%` | `0 / 0 / 0` |
| `2,000,000` | `200,000 B/s` | `194,726.7 B/s` | `279.5 B/s` | `97.4%` | `0 / 0 / 0` |

### Data-Type Comparison (`speed=0`, `921,600` baud, `16 kHz`, `samples_per_packet=320`)
| Format | Payload Size (2 s) | Mean Board Throughput | Effective Samples / s |
|---|---|---|---|
| `f32` | `128,000 B` | `91,756.0 B/s` | `22,939 samples/s` |
| `i16` | `64,000 B` | `90,823.0 B/s` | `45,412 samples/s` |
| `i8` | `32,000 B` | `89,302.0 B/s` | `89,302 samples/s` |

### Real-Time Table (`speed=1.0`, 1.0 s clip, `320 spp`)
| Config | Payload | `115,200` baud Board Time | Can `115,200` Keep Up? | `921,600` baud Board Time | Can `921,600` Keep Up? |
|---|---|---|---|---|---|
| `16 kHz f32` | `64,000 B` | `5,570 ms` | **No** | `993 ms` | **Yes** |
| `16 kHz i16` | `32,000 B` | `2,809 ms` | **No** | `987 ms` | **Yes** |
| `16 kHz i8`  | `16,000 B` | `1,428 ms` | **No** | `983 ms` | **Yes** |
| `8 kHz i16`  | `16,000 B` | `1,400 ms` | **No** | `966 ms` | **Yes** |
| `8 kHz i8`   | `8,000 B`  | `980 ms`   | **Yes** | `963 ms` | **Yes** |

### Packet Size Effect (`921,600` baud, `16 kHz i16`, `32,000 B`)
| `samples_per_packet` | Packets Sent | Payload / Frame | Mean Board Throughput |
|---|---|---|---|
| `8` | `2,000` | `16 B` (+13 B header/CRC) | `51,254.7 B/s` |
| `64` | `250` | `128 B` (+13 B header/CRC) | `84,359.0 B/s` |
| `320` | `50` | `640 B` (+13 B header/CRC) | `90,909.0 B/s` |
| `1024` | `16` | `2048 B` (+13 B header/CRC) | `92,219.0 B/s` |

---

## 2. Pending Physical Run
- **Native USB Port (`USB` / `COM11`):** Not yet tested in Mission 1 benchmark (cable was not connected on `USB` port during this run). Once plugged in, re-run `mission1_pipe_benchmark.py --com-port COM12 --usb-port <USB_PORT>` to generate the combined `COM` vs `USB` comparison table and plots.
