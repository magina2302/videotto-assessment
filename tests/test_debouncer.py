"""Tests for speaker ID debouncing."""

from src.debouncer import debounce_speaker_ids


class TestDebounceSpeakerIds:
    """Unit tests for debounce_speaker_ids."""

    def test_short_middle_run_replaced_by_previous_stable_run(self):
        """A short middle run should be replaced by the previous stable speaker."""
        speaker_ids = [0] * 10 + [1] * 3 + [0] * 10

        result = debounce_speaker_ids(speaker_ids, min_hold_frames=5)

        assert result == [0] * 23

    def test_short_first_run_replaced_by_next_stable_run(self):
        """A short first run should fall back to the next stable speaker."""
        speaker_ids = [1] * 3 + [0] * 10

        result = debounce_speaker_ids(speaker_ids, min_hold_frames=5)

        assert result == [0] * 13

    def test_none_segments_are_untouched(self):
        """None runs should never be modified."""
        speaker_ids = [None] * 4 + [0] * 10 + [None] * 2

        result = debounce_speaker_ids(speaker_ids, min_hold_frames=5)

        assert result == [None] * 4 + [0] * 10 + [None] * 2

    def test_stable_runs_remain_unchanged(self):
        """Runs that already meet the minimum hold should stay unchanged."""
        speaker_ids = [0] * 6 + [1] * 5 + [0] * 7

        result = debounce_speaker_ids(speaker_ids, min_hold_frames=5)

        assert result == speaker_ids