"""Basic tests for the face tracking module."""

from src.tracker import track_face_crop


class TestTrackFaceCropBasics:
    """Basic sanity tests for track_face_crop."""

    def test_empty_input(self):
        """Empty bbox list returns empty output."""
        compressed, scene_cuts = track_face_crop([])
        assert compressed == []
        assert scene_cuts == []

    def test_single_frame_with_face(self):
        """One frame with a face returns one crop position."""
        # Face centered at (320, 180) in a 640x360 frame
        bboxes = [(300, 160, 340, 200)]
        compressed, scene_cuts = track_face_crop(bboxes, video_width=640, video_height=360)

        assert len(compressed) == 1
        assert compressed[0][2] == 1  # frame count
        assert compressed[0][0] > 0   # valid x coordinate
        assert compressed[0][1] > 0   # valid y coordinate
        assert scene_cuts == []

    def test_no_face_before_first_detection(self):
        """Frames with None bbox before first face return (-1, -1) sentinel."""
        bboxes = [None, None, None, (300, 160, 340, 200), (300, 160, 340, 200)]
        compressed, scene_cuts = track_face_crop(bboxes, video_width=640, video_height=360)

        # First segment should be the no-face sentinel
        assert compressed[0][0] == -1
        assert compressed[0][1] == -1
        assert compressed[0][2] == 3  # 3 no-face frames

    def test_deadzone_prevents_small_movement(self):
        """Small face motion inside the dead zone should not move the crop."""
        #test for bug_1
        
        bboxes = [
            (300, 160, 340, 200),  # center = (320, 180)
            (302, 160, 342, 200),  # center = (322, 180)
            (304, 160, 344, 200),  # center = (324, 180)
        ]

        compressed, scene_cuts = track_face_crop(       
            bboxes,
            video_width=640,
            video_height=360,
            deadzone_ratio=0.10,
        )

        assert len(compressed) == 1
        assert compressed[0][2] == 3
        assert scene_cuts == []


    def test_scene_cut_snaps_immediately(self):
        """A scene boundary should snap immediately to the new face position."""
        #test for bug_2

        bboxes = [
            (300, 160, 340, 200),  # center = (320, 180)
            (300, 160, 340, 200),  # center = (320, 180)
            (500, 160, 540, 200),  # center = (520, 180) on scene cut
        ]

        face_scenes = [(2, 10)]

        compressed, scene_cuts = track_face_crop(
            bboxes,
            video_width=640,
            video_height=360,
            face_scenes=face_scenes,
            smoothing=0.25,
        )

        assert scene_cuts == [2]
        assert len(compressed) == 2
        assert compressed[0][2] == 2  # first two frames
        assert compressed[1][2] == 1  # snapped frame

        crop_w = 360 * 9.0 / 16.0
        expected_x = 520
        max_cx = 640 - crop_w / 2.0
        expected_x = min(max_cx, expected_x)

        assert compressed[1][0] == expected_x