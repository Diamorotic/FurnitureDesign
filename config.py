"""Top-level dimensions, coordinates, rough-ins, and tolerances (all in mm).

Coordinate system (interior finished tile-to-tile corner origin):
  - Origin (0, 0, 0): Interior floor corner where Wall D meets Wall C.
  - +X: From Wall D (x = 0, entrance door) toward Wall A (x = ROOM_LENGTH_X, toilet/shower).
  - +Y: From Wall C (y = 0, outlets/sink rough-ins) toward Wall B (y = ROOM_DEPTH_Y, washer/shower).
  - +Z: From finished floor (z = 0) up toward suspended ceiling (z = ROOM_HEIGHT_Z).

Values marked with `# [ASSUMED]` were estimated from 1:10 blueprint scale,
standard fixtures, or `BathroomPhoto.jpg` and can be verified/updated later.
"""

# =============================================================================
# 1. ROOM INTERIOR BOUNDS & TILE/BOARD SHELL THICKNESSES (mm)
# =============================================================================
# Note: Wall C is 1640 mm near ceiling (1645 mm mid, 1653 mm floor); Wall B is 1648 mm.
# Using 1640 mm ensures upper/ceiling-touching cabinets will never be designed too wide.
ROOM_LENGTH_X = 1640.0        # [AT CEILING] (WallC.jpg: 164 cm)
ROOM_DEPTH_Y = 1710.0         # TopView.jpg & WallA.jpg: 171 cm
ROOM_HEIGHT_Z = 2385.0        # WallA.jpg: 842 + 339 + 82 + 770 + 352 = 2385 mm

# Non-zero visual sheet thicknesses placed strictly OUTSIDE the interior room volume
# (3D CAD solids require >0 thickness; these represent the finished tile/GK layers).
WALL_TILE_THICKNESS = 10.0    # Ceramic wall tile thickness (outside interior bounds)
FLOOR_TILE_THICKNESS = 8.0    # Ceramic floor tile thickness (below z = 0)
CEILING_BOARD_THICKNESS = 12.5  # Suspended plasterboard thickness (above z = ROOM_HEIGHT_Z)

# =============================================================================
# 2. WALL D — ENTRANCE DOOR & HEATING-PIPE COVER (x = 0)
# =============================================================================
DOOR_TRIM_OFFSET_Y = 200.0    # From Wall C (y = 0) to outer door frame trim (TopView.jpg: 20 cm)
DOOR_FRAME_WIDTH = 60.0       # Frame trim width (TopView.jpg: 26 cm - 20 cm = 6 cm)
DOOR_OFFSET_Y = 260.0         # Clear opening start from Wall C (TopView.jpg: 26 cm)
DOOR_WIDTH_Y = 702.0          # Clear door hole width excluding frame (70.2 cm; 73.2 cm w/ rebate)
DOOR_HEIGHT_Z = 2010.0        # Clear door hole height excluding frame (201 cm)
DOOR_FRAME_PROTRUSION = 12.0  # [ASSUMED] Trim relief proud of wall tile
DOOR_LEAF_THICKNESS = 40.0    # [ASSUMED] Door leaf thickness
DOOR_OPEN_ANGLE_DEG = 25.0    # [ASSUMED] Visual outward swing angle (hinged at y = DOOR_OFFSET_Y)

# Full-height plasterboard heating-pipe cover in D-B corner (TopView.jpg: 17.3 x 55 cm)
PIPE_COVER_WIDTH_X = 173.0
PIPE_COVER_DEPTH_Y = 550.0    # Measured from Wall B (y = 1710 down to y = 1160)
PIPE_COVER_HEIGHT_Z = ROOM_HEIGHT_Z  # Goes all the way up to the ceiling

# =============================================================================
# 3. WALL B — WASHING MACHINE, POWER SOCKETS & SHOWER ENCLOSURE (y = ROOM_DEPTH_Y)
# =============================================================================
# Washing machine (back toward Wall B, front porthole door facing -Y toward Wall C)
WM_START_X = PIPE_COVER_WIDTH_X  # 173.0 mm (starts right after pipe cover)
WM_ENVELOPE_WIDTH_X = 633.0   # Allocated width before shower glass (TopView.jpg: 63.3 / 63.6 cm)
WM_BODY_WIDTH_X = 600.0       # Standard cabinet width (WallA.jpg: 60 cm)
WM_BACK_GAP_Y = 100.0         # Hose gap from Wall B (WallA.jpg: 10 cm)
WM_FRONT_FROM_WALL_B = 678.0  # Distance from Wall B to cabinet front (TopView.jpg: 67.8 cm)
WM_BODY_DEPTH_Y = WM_FRONT_FROM_WALL_B - WM_BACK_GAP_Y  # 578.0 mm cabinet depth
WM_PAD_HEIGHT_Z = 30.0        # Anti-vibration mat height (WallA.jpg: 3 cm)
WM_TOTAL_HEIGHT_Z = 842.0     # Total height from floor including mat (WallA.jpg: 84.2 cm)
WM_DOOR_DIAMETER = 460.0      # [ASSUMED] Front-loader porthole outer ring diameter
WM_DOOR_PROTRUSION_Y = 42.0   # [ASSUMED] Porthole protrusion into room (-Y) beyond 678 mm line
WM_DOOR_CENTER_Z = 470.0      # [ASSUMED] Porthole center height from floor

# 2-gang electrical outlet panel on Wall B above washing machine (TopView.jpg & WallA.jpg)
OUTLET_B_OFFSET_FROM_PIPE_COVER_X = 133.0  # 133 mm away from corner pipe cover (x = 306 mm)
OUTLET_B_WIDTH_X = 151.0                   # 151 mm wide (2-gang panel)
OUTLET_B_HEIGHT_Z = 82.0                   # 82 mm tall (WallA.jpg: 8.2 cm)
OUTLET_B_TOP_FROM_CEILING_Z = 1122.0       # Top is 1122 mm below ceiling (WallA.jpg: 112.2 cm)
OUTLET_B_DEPTH_Y = 18.0                    # [ASSUMED] Same 18 mm depth as Wall C outlets

# Walk-in glass shower enclosure (corner of Wall A & Wall B)
SHOWER_START_X = WM_START_X + WM_ENVELOPE_WIDTH_X  # 806.0 mm
SHOWER_WIDTH_X = ROOM_LENGTH_X - SHOWER_START_X    # 834.0 mm at ceiling (842 mm at Wall B)
SHOWER_DEPTH_Y = 685.0                             # Along Wall A from Wall B (TopView.jpg: 68.5 cm)
SHOWER_FRONT_Y = ROOM_DEPTH_Y - SHOWER_DEPTH_Y     # 1025.0 mm
SHOWER_GLASS_HEIGHT_Z = ROOM_HEIGHT_Z - 352.0      # 2033.0 mm (WallA.jpg: 35.2 cm below ceiling)
SHOWER_GLASS_THICKNESS = 8.0                       # [ASSUMED] 8 mm tempered glass
SHOWER_PROFILE_SIZE = 20.0                         # [ASSUMED] Matte black aluminum frame width

# Shower floor drain (TopView.jpg hatched area)
SHOWER_DRAIN_SIZE_X = 120.0    # [ASSUMED] Drain grate X width
SHOWER_DRAIN_SIZE_Y = 120.0    # [ASSUMED] Drain grate Y length
SHOWER_DRAIN_CENTER_X = 1350.0  # [ASSUMED] Scaled from 1:10 TopView.jpg
SHOWER_DRAIN_CENTER_Y = 1380.0  # [ASSUMED] Scaled from 1:10 TopView.jpg
SHOWER_DRAIN_THICKNESS = 2.0

# =============================================================================
# 4. WALL A — CISTERN LEDGE & WALL-HUNG TOILET (x = ROOM_LENGTH_X)
# =============================================================================
# Concealed cistern boxing / tiled ledge (touches shower glass, does NOT enter shower)
CISTERN_DEPTH_X = 189.0          # TopView.jpg & WallC.jpg: 18.9 cm from Wall A
CISTERN_GAP_FROM_WALL_C = 288.0  # TopView.jpg & WallA.jpg: 28.8 cm gap to Wall C
CISTERN_WIDTH_Y = 735.0          # WallA.jpg: 73.5 cm (ends at y = 1023 mm against shower)
CISTERN_HEIGHT_Z = 1195.0        # WallA.jpg: 119.5 cm

# Flush plate on front face of cistern boxing (x = ROOM_LENGTH_X - CISTERN_DEPTH_X)
FLUSH_PLATE_OFFSET_FROM_RIGHT_Y = 285.0  # WallA.jpg: 28.5 cm from right edge of cistern
FLUSH_PLATE_WIDTH_Y = 157.0              # WallA.jpg: 15.7 cm
FLUSH_PLATE_HEIGHT_Z = 195.0             # WallA.jpg: 19.5 cm
FLUSH_PLATE_TOP_MARGIN_Z = 75.0          # WallA.jpg: 7.5 cm below top of cistern
FLUSH_PLATE_PROTRUSION_X = 8.0           # [ASSUMED] Plate thickness

# Wall-hung toilet bowl & lid
TOILET_PROJECTION_X = 495.0      # TopView.jpg: 49.5 cm from cistern front face
TOILET_WIDTH_Y = 375.0           # TopView.jpg: 37.5 cm
# Centered with flush plate along Y: 288 + 285 + 157/2 = 651.5 mm
TOILET_CENTER_Y = (
    CISTERN_GAP_FROM_WALL_C
    + FLUSH_PLATE_OFFSET_FROM_RIGHT_Y
    + FLUSH_PLATE_WIDTH_Y / 2.0
)
TOILET_BOTTOM_Z = 115.0          # WallA.jpg: 11.5 cm floor clearance
TOILET_BOWL_HEIGHT_Z = 330.0     # WallA.jpg: 33.0 cm ceramic bowl height (rim at 445 mm)
TOILET_SEAT_HEIGHT_Z = 60.0      # WallA.jpg: 6.0 cm seat + lid height (top at 505 mm)

# =============================================================================
# 5. VENTS, WALL C OUTLETS & SINK PLUMBING ROUGH-INS
# =============================================================================
# Ceiling ventilation grille on Wall C (WallC.jpg: 78 cm from Wall A, 70.9 cm from Wall D)
VENT_C_OFFSET_FROM_WALL_D_X = 709.0
VENT_GRILLE_WIDTH_X = 161.0      # WallC.jpg: 16.1 cm
VENT_GRILLE_HEIGHT_Z = 151.0     # Verified: 151 mm tall
VENT_TOP_MARGIN_Z = 117.0        # WallC.jpg: 11.7 cm from ceiling to top of grille
VENT_PROTRUSION = 6.0            # [ASSUMED] Frame relief from wall

# Second ventilation grille on Wall B inside shower (~25 cm from Wall A, same height as Wall C)
VENT_B_OFFSET_FROM_WALL_A_X = 250.0  # [ASSUMED] ~25 cm from Wall A
VENT_B_WIDTH_X = VENT_GRILLE_WIDTH_X  # [ASSUMED] Same 161 mm width as Wall C vent

# 3-gang electrical outlet panel on Wall C (TopView.jpg: 22.5 x 1.8 cm; WallC.jpg: 22.5 x 8.5 cm)
OUTLET_C_START_X = 215.0         # [ASSUMED] Scaled from 1:10 WallC.jpg & TopView.jpg
OUTLET_C_WIDTH_X = 225.0
OUTLET_C_HEIGHT_Z = 85.0
OUTLET_C_DEPTH_Y = 18.0
OUTLET_C_BOTTOM_Z = 1185.0       # WallC.jpg: 118.5 cm from floor

# Sink plumbing rough-ins on Wall C (measured: outer edges 210 mm, centers 151 mm, left edge 588 mm)
SINK_VALVE_SIZE_X = 59.0         # Derived from 210 - 151 = 59 mm rosette width
SINK_VALVE_SIZE_Z = 59.0         # [ASSUMED] Matching circular/square rosette height
SINK_WATER_LEFT_EDGE_X = 588.0   # Measured: left outer edge of left water outlet from Wall D
SINK_WATER_CENTER_SPACING = 151.0  # Measured: center-to-center spacing between water outlets
SINK_WATER_HOT_X = SINK_WATER_LEFT_EDGE_X + 0.5 * SINK_VALVE_SIZE_X  # 617.5 mm
SINK_WATER_COLD_X = SINK_WATER_HOT_X + SINK_WATER_CENTER_SPACING     # 768.5 mm
SINK_DRAIN_X = 0.5 * (SINK_WATER_HOT_X + SINK_WATER_COLD_X)          # 693.0 mm (centered)
SINK_DRAIN_DIAMETER = 50.0       # [ASSUMED] Standard 50 mm DN50 waste hole
SINK_DRAIN_BOTTOM_Z = 495.0      # Measured: bottom edge of sewage hole above floor
SINK_DRAIN_Z = SINK_DRAIN_BOTTOM_Z + 0.5 * SINK_DRAIN_DIAMETER       # 520.0 mm
SINK_WATER_Z = SINK_DRAIN_Z      # [ASSUMED] Aligned horizontally with drain per WallC.jpg
SINK_VALVE_PROTRUSION_Y = 65.0   # [ASSUMED] Valve projection from Wall C (TopView.jpg)
SINK_DRAIN_PROTRUSION_Y = 45.0   # [ASSUMED] Waste stub projection from Wall C

# Under-counter LED electrical cable stub near floor in A-C corner
LED_CABLE_HEIGHT_Z = 300.0              # ~30 cm above floor in A-C corner
LED_CABLE_OFFSET_FROM_WALL_A_X = 25.0   # [ASSUMED] Slight offset from Wall A onto Wall C
LED_CABLE_DIAMETER = 12.0               # [ASSUMED] Visual cable marker diameter
LED_CABLE_PROTRUSION_Y = 50.0           # [ASSUMED] Stub protrusion into room from Wall C

# =============================================================================
# 6. CEILING LAMPS (TopView.jpg, WallA.jpg, WallC.jpg, BathroomPhoto.jpg)
# =============================================================================
LAMP_DIAMETER = 87.0             # TopView.jpg: d = 8.7 cm
LAMP_HEIGHT_Z = 94.0             # TopView.jpg & WallC.jpg: h = 9.4 cm
LAMP_1_NEAR_Y = 586.0            # TopView.jpg: 58.6 cm from Wall C to near edge
LAMP_2_NEAR_Y = 581.0            # TopView.jpg: 58.1 cm from Wall C to near edge
LAMP_3_NEAR_Y = 579.0            # TopView.jpg: 57.9 cm from Wall C to near edge

# [ASSUMED] Lamp 1 & Lamp 3 anchored at 364 mm end offsets; Lamp 2 centered between them.
LAMP_1_CENTER_X = 364.0 + LAMP_DIAMETER / 2.0
LAMP_3_CENTER_X = (ROOM_LENGTH_X - CISTERN_DEPTH_X) - 364.0 - LAMP_DIAMETER / 2.0
LAMP_2_CENTER_X = 0.5 * (LAMP_1_CENTER_X + LAMP_3_CENTER_X)

LAMP_CENTERS_XY = (
    (LAMP_1_CENTER_X, LAMP_1_NEAR_Y + LAMP_DIAMETER / 2.0),
    (LAMP_2_CENTER_X, LAMP_2_NEAR_Y + LAMP_DIAMETER / 2.0),
    (LAMP_3_CENTER_X, LAMP_3_NEAR_Y + LAMP_DIAMETER / 2.0),
)

# =============================================================================
# 7. FURNITURE TOGGLES & CLEARANCE TOLERANCES (mm)
# =============================================================================
ENABLE_VANITY = False            # Keep False while inspecting bare existing 3D room first

CLEARANCE_TOLERANCE = 2.0        # General assembly clearance tolerance
MIN_WALKWAY_CLEARANCE = 500.0    # Minimum comfortable passage width in front of fixtures

# =============================================================================
# 8. VIEWER COLORS & TRANSPARENCIES (RGBA in 0..1)
# =============================================================================
WALL_ALPHA = 0.22
CEILING_ALPHA = 0.08
SHOWER_GLASS_ALPHA = 0.28

COLOR_FLOOR = (0.83, 0.80, 0.75, 1.0)
COLOR_WALL = (0.93, 0.92, 0.89, WALL_ALPHA)
COLOR_CEILING = (0.96, 0.96, 0.96, CEILING_ALPHA)
COLOR_CISTERN = (0.94, 0.93, 0.91, 1.0)
COLOR_CERAMIC = (0.98, 0.98, 0.99, 1.0)
COLOR_CHROME = (0.78, 0.80, 0.82, 1.0)
COLOR_SHOWER_GLASS = (0.72, 0.88, 0.92, SHOWER_GLASS_ALPHA)
COLOR_BLACK_METAL = (0.14, 0.14, 0.16, 1.0)
COLOR_DOOR_WOOD = (0.62, 0.43, 0.26, 0.85)
COLOR_WASHER_BODY = (0.95, 0.96, 0.97, 1.0)
COLOR_WASHER_DOOR = (0.16, 0.17, 0.19, 1.0)
COLOR_HOT_WATER = (0.85, 0.24, 0.20, 1.0)
COLOR_COLD_WATER = (0.18, 0.48, 0.85, 1.0)
COLOR_DRAIN_PIPE = (0.45, 0.47, 0.50, 1.0)
COLOR_VENT = (0.90, 0.90, 0.90, 1.0)
COLOR_ELECTRICAL_CABLE = (0.95, 0.65, 0.10, 1.0)
