# Camera Tracking Stabilizer

A dead-zone camera tracking system for portrait (9:16) video output. Given per-frame face bounding boxes, the tracker computes a smooth, stable crop position that keeps the speaker's face properly framed within a vertical crop window.

The core algorithm uses a **dead-zone** approach: the crop window only moves when the face exits an inner region (the dead zone). This prevents the crop from chasing every small face movement and produces inherently stable output. When the face does exit the dead zone, an **exponential smoothing** filter produces a gradual, natural-looking pan. Scene cuts and speaker switches trigger an instant snap rather than a smooth pan.

## Quick Start

```bash
python -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Project Structure

```
camera-tracking-test/
├── README.md
├── requirements.txt
├── run.py                       # CLI runner — runs tracker and prints output
├── visualize.py                 # Renders cropped portrait video from tracker output
├── src/
│   ├── __init__.py
│   ├── tracker.py               # Dead-zone tracking algorithm
│   ├── debouncer.py             # Speaker ID debouncer (stub — needs implementation)
│   └── compression.py           # RLE compression utilities
├── tests/
│   ├── __init__.py
│   ├── test_tracker.py
│   └── test_compression.py
└── sample_data/
    ├── clip_a.mp4
    ├── clip_a.json
    ├── clip_b.mp4
    └── clip_b.json
```

## Your Tasks

### 1. Bug Finding and Fixing

There are bugs in `src/tracker.py` that cause the crop output to behave incorrectly. Use the provided tools and sample data to identify the issues, find the root causes, and fix them.

### 2. Feature Implementation

`src/debouncer.py` contains a stub function (`debounce_speaker_ids`) that needs to be implemented. Read the docstring carefully for the full specification.

### 3. Tests

Write regression tests for the bugs you find. Your tests should fail on the original buggy code and pass on your fixed version. Also write tests for your debouncer implementation.

## What to Submit

This repo was provided as a GitHub template. Push your changes to the repo you created from it, then share the link with us. Include a brief writeup (in a NOTES.md, in this README, or in your commit messages) covering:

- What you found (root cause of each bug)
- What you fixed and why
- Any design decisions in your debouncer implementation
- Anything else you noticed or would improve given more time

## Time

Please spend no more than **2-3 hours**. We value a working solution over a perfect one.

## What We're Evaluating

- **Does it work?** Did you ship working fixes and a correct debouncer?
- **Debugging process**: How did you find and diagnose the bugs?
- **Code quality**: Is your code clean, well-tested, and consistent with the existing style?
- **Communication**: Did you document your findings and reasoning?


# NOTES

## What I found

### Bug 1: Dead-zone condition was ineffective
Crop position changes frequently even during small face movements. But crop should remain stable unless face exits dead zone. This is because movement condition uses `abs(dx) > 0` instead of dead-zone threshold. Dead-zone behavior is effectively disabled, causing unnecessary movement.

### Bug 2: Scene cuts were not applied as hard transitions
Scene cuts are detected but crop transitions remain smooth. Scene cuts are detected but crop transitions remain smooth. This is because snap condition only logs frame but does not override smoothing logic. This violates expected behavior of hard cuts.

---

## What I fixed

### Fix 1: Correct dead-zone behavior
Replaced the movement condition to compare against `dz_half_w` and `dz_half_h`, ensuring the crop only moves when the face exits the dead-zone.

### Fix 2: Proper snap handling for scene changes
Introduced an early return (`continue`) after snapping to the new face position, ensuring smoothing is skipped entirely on scene cuts and speaker switches.

### Fix 3: Implemented `debounce_speaker_ids`
Implemented a run-length encoding based debouncer to remove short-lived speaker flickers before tracking.

---

## Debouncer design decisions

- **Stability defined by duration**: A speaker is considered stable only if their run length ≥ `min_hold_frames`, aligning with the temporal consistency requirement.
- **Preference for temporal continuity**: Short runs are replaced using the nearest *previous stable* speaker when possible, preserving continuity in conversational flow.
- **Fallback strategy**: If no prior stable run exists, the next stable run is used instead to handle early-frame flickers.
- **Strict handling of `None`**: `None` segments are treated as “no detection” rather than noise and are left untouched to avoid introducing artificial speaker labels.

---

## Tests added

### Tracker regression tests

- `test_deadzone_prevents_small_movement`  
  Verifies that small face motion inside the dead-zone does not trigger crop movement.

- `test_scene_cut_snaps_immediately`  
  Ensures scene boundaries result in an immediate crop jump without smoothing.

---

### Debouncer tests

- `test_short_middle_run_replaced_by_previous_stable_run`  
  Confirms that short flicker runs in the middle are replaced by a stable preceding speaker.

- `test_short_first_run_replaced_by_next_stable_run`  
  Verifies fallback to the next stable run when no prior stable run exists.

- `test_none_segments_are_untouched`  
  Ensures `None` segments are preserved exactly and not modified.

- `test_stable_runs_remain_unchanged`  
  Confirms that runs meeting the stability threshold are not altered.

---

## Additional observations

- The crop remains vertically fixed in the provided examples because the portrait crop height matches the input frame height, effectively constraining vertical movement.
- Debouncing significantly reduces false-positive speaker switches, which in turn improves the stability of the downstream tracking and reduces unnecessary snap events.
- Empirically, debouncing reduced the number of scene/speaker-triggered snaps in clip_b (from multiple rapid switches down to a few stable transitions), improving temporal consistency.
- Overall, the combination of dead-zone correction and speaker debouncing significantly improves both spatial stability and temporal coherence of the camera motion.


