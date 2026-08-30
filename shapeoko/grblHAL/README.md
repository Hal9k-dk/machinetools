Built from 76f9f40f5df706eac6f3c30cc4c9475c5017d4da

Shapeoko coordinate system: (0, 0) is upper right corner (X/Y/Z are always negative)

Bitsetter calibration:

# Disable parking motion
M56P0
# Spindle off
N0 M5
# Home
$h
# Move to Bitsetter position
N0G0X-0.5000Y-817.5000Z-5.0000
# Dwell 5 ms
N0G4P0.005
# Dwell
N0G4P0.005
# Z = -15
N0G0Z-15.0000
# Probe towards (fast)
N0G38.2Z-155.0000F800.0
# Dwell
N0G4P0.005
# Z move
N0G0Z-60.9000
# Probe towards (slow)
N0G38.2Z-67.9000F200.0
# Dwell
N0G4P0.005
# Z move
N0G0Z-5.0000
