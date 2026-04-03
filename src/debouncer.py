"""
Speaker ID debouncing for stable camera tracking.

Removes rapid speaker-ID bounces that cause jarring crop window snaps.
"""


def debounce_speaker_ids(speaker_track_ids, min_hold_frames=15):
    """
    Remove rapid speaker-ID bounces shorter than min_hold_frames.

    Speaker detection sometimes flickers the active-speaker label during
    crosstalk or brief classification uncertainty, producing 1-10 frame
    segments that cause jarring rapid-fire crop snaps. This pre-filter
    replaces those short segments with the surrounding stable speaker ID
    so the downstream dead-zone tracker never sees them.

    Algorithm:
      1. Run-length encode the raw IDs into (track_id, start, length) runs.
      2. For any run shorter than min_hold_frames, replace it with the
         previous stable run's ID (or the next stable run if it's the first).
      3. Expand back to a per-frame list.

    Args:
        speaker_track_ids: Per-frame list of speaker IDs (int or None).
            None means no speaker detected at that frame.
        min_hold_frames: Minimum frames a speaker must hold to be "stable".

    Returns:
        Same-length list with short flicker runs replaced by nearest stable ID.
        None segments are never modified.

    Examples:
        >>> debounce_speaker_ids([0]*50 + [1]*3 + [0]*50, min_hold_frames=10)
        [0]*103  # The 3-frame speaker-1 segment is replaced by speaker 0

        >>> debounce_speaker_ids([None]*10 + [0]*50, min_hold_frames=15)
        [None]*10 + [0]*50  # None segments are untouched
    """
    #raise NotImplementedError("TODO: Implement this function — see docstring for spec")

    if not speaker_track_ids: #handles empty input
        return []

    #1. Run-length encode the raw IDs into (track_id, start, length) runs.
    runs = []
    start = 0
    current = speaker_track_ids[0]  #current speaker ID for the run being built

    for i in range(1, len(speaker_track_ids)):
        if speaker_track_ids[i] != current:  #close the current run when the speaker ID changes
            runs.append((current, start, i - start))
            current = speaker_track_ids[i] #start tracking the new speaker ID
            start = i

    runs.append((current, start, len(speaker_track_ids) - start)) #append the last run, which reaches the end of the list

    #run should contain all the consecutive ID segments

    #2. For any run shorter than min_hold_frames, replace it with the previous stable run's ID (or the next stable run if it's the first).
    new_runs = runs.copy() #edit a copy so replacement decisions are based on the original runs

    for i, (track_id, start, length) in enumerate(runs):
        #never modify None segments
        if track_id is None:
            continue

        #keep the stable runs unchanged
        if length >= min_hold_frames:
            continue

        replacement = None

        #search backwards for the nearest previous stable run that isn't none
        for j in range(i - 1, -1, -1):
            prev_id, _prev_start, prev_len = runs[j]
            if prev_id is not None and prev_len >= min_hold_frames:
                replacement = prev_id
                break

        # if no previous stable run exists, use the next stable run that isn't none 
        if replacement is None:
            for j in range(i + 1, len(runs)):
                next_id, _next_start, next_len = runs[j]
                if next_id is not None and next_len >= min_hold_frames:
                    replacement = next_id
                    break

        #only replace if a stable neighbor exists --> if not leave it unchanged
        if replacement is not None:
            new_runs[i] = (replacement, start, length)

    #3. Expand back to a per-frame list.
    result = []
    for track_id, _start, length in new_runs:
        result.extend([track_id] * length)

    return result