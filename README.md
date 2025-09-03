# Cocotb triggers
[Cocotb Documentation](https://docs.cocotb.org/en/stable/triggers.html#timing) is not very clear about how the Triggers/Timers work. So I made this example hoping it will help others. I prompted an LLM to explain the example (sorry, not enough time to write the tutorial).

## User prompt

Explain to me, in depth, how each trigger work. NextTimeStep, ReadOnly, RisingEdge and ReadWrite. Explain to me in a tutorial/forum way. Use my example and explain what happened in the example. Explain in detail the simulation phases.

---

## Assistant answer

Awesome example — it hits *exactly* the places where cocotb’s triggers interact with the HDL scheduler. Below is a didactic “forum-style” walkthrough of:

1. what each trigger really means,  
2. how a simulator advances within a single time unit (delta cycles), and  
3. what’s happening in **your code** line-by-line (including why some lines “seem late” or “hang”).

---

## How simulators step through time (the mental model)

At one timestamp (say `T = 10 ns`) the simulator runs several **regions** (a.k.a. *delta cycles*) before it moves to the next timestamp:

1. **Event / Active region**  
   - Edges are detected (e.g., `posedge clk`).  
   - `always @(...)` / processes run; **blocking** assignments update immediately; **non-blocking** (`<=`) are scheduled for later.

2. **NBA (non-blocking assignment) update**  
   - All `<=` updates are **committed** (flops/regs take their new value).

3. **Read/Write region (RW)**  
   - Everything for time `T` is settled; it’s safe to **read** current values and also **schedule writes** that will take effect in a later delta or at the next time.

4. **Read-Only region (RO)**  
   - Final chance at time `T` to **observe** settled values.  
   - Writes are **illegal** (or deferred) in this region.

5. **Advance time** (to `T + dt`)  
   - Next time slot begins.

> Cocotb maps to these regions with its triggers:  
> - `RisingEdge(sig)` — resumes **as soon as the edge happens**, i.e., **before** NBAs commit.  
> - `ReadWrite()` — resumes in **RW** (after NBAs committed). You may read settled values and drive new ones.  
> - `ReadOnly()` — resumes in **RO** (after NBAs committed). You may **only read**.  
> - `NextTimeStep()` — **forces** the simulator to leave the current time slot and go to the next timestamp.

---

## What each trigger guarantees

### `RisingEdge(signal)`
- Fires when the edge is detected (Active region).  
- **NBAs not committed yet.** If a flop does `q <= d` on that edge, right after `RisingEdge` you’ll still see the *old* `q` until NBAs commit.  
- Idiom: `await RisingEdge(clk); await ReadOnly();` to read **stable** post-edge values.

### `ReadWrite()`
- Enters **RW** after everything at time `T` has executed (including NBAs).  
- **Safe to read settled values** *and* **drive** signals for the next delta/time.  
- Good place to “queue” stimulus for the next cycle.

### `ReadOnly()`
- Enters **RO**; all updates for time `T` are done.  
- **Only read** — attempting to “go back” and write in the same time slot is illegal and can deadlock/hang.

### `NextTimeStep()`
- Skips any remaining deltas and **jumps to the next timestamp**.  
- Stronger than `Timer(0)` (which is just “another delta at the same time”).

---

## Using your code as a tutorial

I’ll annotate each block with what the simulator is doing.

> Assume a DFF in HDL like:
```verilog
always @(posedge clk) q <= d;
```

### 1) Start clock, drive `d`, then **first** `RisingEdge`
```python
cocotb.start_soon(Clock(dut.clk, 1, units="ns").start())

dut.d.value = 1
...
await RisingEdge(dut.clk)
dut._log.info("After first rising edge d is updated, but q is not")
```

- You assign `d` in Python. Cocotb **queues** that write; the HDL won’t see it until you `await` and the sim enters RW/RO.  
- `await RisingEdge(clk)` returns **at the edge**, *before* NBA commit.  
- At this instant:
  - `clk` is high ✅
  - HDL has already **sampled** `d` for this edge (using the **old** HDL value, because your write hasn’t propagated yet).
  - NBAs that set `q` haven’t committed → **`q` still shows the previous value**.

### 2) **Second** `RisingEdge` → `q` finally reflects the earlier `d`
```python
await RisingEdge(dut.clk)
dut._log.info("After second rising edge q is updated")
```
- Your earlier write to `d` became visible to HDL **after** you yielded the first time.  
- The flop samples *that* `d` on the **next** edge → `q` changes there.

> **Takeaway:** If you drive `d` and immediately wait the same cycle’s `posedge`, you’re **too late** for that edge. The DFF will pick it up **next** edge.

---

### 3) Edge → `ReadOnly()` in the **same** time slot
```python
dut.d.value = 1 - dut.d.value
await RisingEdge(dut.clk)
...
await ReadOnly()
dut._log.info("After ReadOnly q is updated")
```
- `RisingEdge` returns at the edge (pre-NBA).  
- `ReadOnly()` returns **after NBAs**: `q` is now **committed** for this edge.  
- This is the canonical “sample stable values after an edge” pattern:
```python
await RisingEdge(clk)
await ReadOnly()
sample_all_signals()
```

---

### 4) Edge → `NextTimeStep()`
```python
await RisingEdge(dut.clk)
...
await NextTimeStep()
dut._log.info("After NextTimeStep q is updated")
```
- `NextTimeStep()` forces time to advance; by then all NBAs of the previous time slot have committed, so `q` is updated.  
- This is “coarser” than `ReadOnly()` (you skip to the next timestamp instead of staying in the same one).

---

### 5) Edge → `ReadWrite()`
```python
await RisingEdge(dut.clk)
...
await ReadWrite()
dut._log.info("After ReadWrite q is updated")
```
- `ReadWrite()` also occurs **after** NBAs commit.  
- You’ll see the same stable, updated `q` as with `ReadOnly()`, **but** here you’re allowed to drive new values for future deltas/cycles.

---

### 6) `ReadOnly()` **without** a clock edge
```python
dut.d.value = 1 - dut.d.value
await ReadOnly()
dut._log.info("After ReadOnly d is updated, but q is not")
```
- You change `d` and then immediately `await ReadOnly()`.  
- That lets the queued write flush to HDL by the end of this time slot, so **`d` is now visible in HDL**.  
- No clock edge happened → the flop didn’t sample `d` → **`q` stays the same**.

---

### 7) Edge → change `d` → `ReadWrite()`
```python
await RisingEdge(dut.clk)

dut.d.value = 1 - dut.d.value
await ReadWrite()
dut._log.info("After ReadWrite d is not updated")
```
- Ordering matters: the **edge already happened**, so the flop **already sampled** the *previous* `d`.  
- Your write to `d` occurs **after** the sampling point (in the same time slot, later region).  
- At `ReadWrite()` you’ll see `q` reflecting the *edge’s* sampling (not your new `d`), and your new `d` is only for **future** edges.  
- If your log message literally says “d is not updated”, clarify the meaning:  
  - In Python, `dut.d.value` shows your new value immediately.  
  - In HDL, the flop can’t use it for the **already-passed** edge; it will be seen **next** edge.

---

### 8) Change `d` → `NextTimeStep()`
```python
dut.d.value = 1 - dut.d.value
await NextTimeStep()
dut._log.info("After NextTimeStep d is updated")
```
- Advancing time guarantees the drive to `d` is now fully applied in HDL.  
- Still no edge → `q` won’t change yet.

---

### 9) `ReadOnly()` then `ReadWrite()` → **deadlock/hang**
```python
await ReadOnly()
dut._log.info("ReadWrite after ReadOnly crashes the simulation.")
await ReadWrite()
```
- Once you’re in **RO** for time `T`, there is **no RW left** at time `T`.  
- Waiting for `ReadWrite()` without advancing time means you’re asking the simulator to go **backwards** in the same slot → there’s nothing to wake you up → **hang**.  
- **Fix**: advance time or an event **between** them:
```python
await ReadOnly()
await NextTimeStep()        # or await Timer(0) or await RisingEdge(clk)
await ReadWrite()
```

---

## Practical recipes (copy/paste)

**Sample stable output right after a clock edge**
```python
await RisingEdge(dut.clk)
await ReadOnly()
# read q, status signals, buses — everything has settled for this edge
```

**Drive something for “next cycle”**
```python
await RisingEdge(dut.clk)  # do protocol step on edge
await ReadWrite()          # safe to both read settled state and drive next inputs
dut.req.value = 1
```

**Change a value and guarantee HDL sees it**
```python
dut.d.value = 0
await ReadOnly()       # or await NextTimeStep()
# Now HDL has your drive
```

**Never do this (will hang)**
```python
await ReadOnly()
await ReadWrite()      # ❌ illegal ordering in the same time slot
```

---

## TL;DR mapping

- **RisingEdge(sig)** → *Edge detected* (pre-NBA).  
- **ReadWrite()** → *End of time T, post-NBA, read & write allowed*.  
- **ReadOnly()** → *End of time T, post-NBA, read-only*.  
- **NextTimeStep()** → *Jump to time T+dt* (stronger than just another delta).

Once you internalize that **`RisingEdge` is *before* flops commit**, and **`ReadOnly`/`ReadWrite` are *after* they commit**, your logs and waveforms will line up perfectly with expectations.

---

If you want, I can also generate a compact timeline diagram (ASCII) for a single clock tick showing the order of RisingEdge → NBAs → ReadWrite → ReadOnly → NextTimeStep, formatted as markdown so you can paste it into your docs. Would you like that?  
