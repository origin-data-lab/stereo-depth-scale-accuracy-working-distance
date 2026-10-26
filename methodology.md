# Methodology
1. Detection: OpenCV ArucoDetector + CharucoDetector (DICT_5X5_100 9×6 board; DICT_4X4_50 5×3 board), markers clustered spatially before board interpolation.
2. Undistortion: OpenCV fisheye (equidistant) with factory intrinsics, rescaled from 800×600 to 1600×1200 (fx·2, cx·2+0.5).
3. Triangulation: cv2.triangulatePoints with factory extrinsics (cam1←cam0).
4. Scale: median 3D distance between adjacent corners per frame ÷ ruler square size (A4 29.1667 mm; far 53.40 × 53.33 mm).
5. Subsets: centre-frontal = board centre <300 px from principal point and tilt <15°; edges = |u−cx| > 450 px.
6. Statistics: median, IQR, bootstrap (500) CI of the median per 0.1 m bin.
7. Tape: manual hold windows (listed in script); stereo plane distance median per hold; linear fit stereo = a·tape + b.
