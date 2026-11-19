"""Parametric bathroom furniture vision: natural bamboo cabinetry with matte-black accents.

Modules included in this vision:
  - Wall C floating bamboo counter, compact semi-recessed basin, matte-black faucet & bottle trap,
    under-counter LED channel, and hidden 24V LED driver near the A-C corner cable.
  - Wall C full-width glued stepped mirror with factory cutout for the 3-gang power outlets.
  - Wall C stepped upper cabinets (255 mm deep) with 110 mm top valance, ducted exhaust vent &
    flush black linear grille, Wall D trim scribe filler, and recessed under-cabinet LED channels.
  - Wall A concealed-cistern upper cabinet (189 mm deep, double doors + matching 110 mm valance).
  - Wall B washing-machine cabinet (550 mm deep flush with pipe cover, 508 mm cat clearance,
    double doors + matching 110 mm valance).
  - Optional stylized loafing cat perched on top of the washing machine.
"""

import math

import cadquery as cq

import config as cfg


def _color(rgba: tuple[float, float, float, float]) -> cq.Color:
    return cq.Color(rgba[0], rgba[1], rgba[2], rgba[3])


def _box_from_bounds(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    zmin: float,
    zmax: float,
) -> cq.Workplane:
    """Create an axis-aligned box spanning exact [xmin..xmax, ymin..ymax, zmin..zmax] bounds."""
    return (
        cq.Workplane("XY")
        .box(
            xmax - xmin,
            ymax - ymin,
            zmax - zmin,
            centered=(False, False, False),
        )
        .translate((xmin, ymin, zmin))
    )


def _build_carcass(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    zmin: float,
    zmax: float,
    open_face: str,
    shelf_zs: tuple[float, ...] = (),
) -> cq.Workplane:
    """Build a 5-sided open-front cabinet carcass with internal horizontal shelves."""
    t = cfg.CABINET_PANEL_THICKNESS
    outer = _box_from_bounds(xmin, xmax, ymin, ymax, zmin, zmax)

    ix0, ix1 = xmin + t, xmax - t
    iy0, iy1 = ymin + t, ymax - t
    iz0, iz1 = zmin + t, zmax - t

    if open_face == "+Y":
        iy1 = ymax + cfg.CLEARANCE_TOLERANCE
    elif open_face == "-Y":
        iy0 = ymin - cfg.CLEARANCE_TOLERANCE
    elif open_face == "-X":
        ix0 = xmin - cfg.CLEARANCE_TOLERANCE
    else:
        raise ValueError(f"Unsupported open_face: {open_face}")

    carcass = outer.cut(_box_from_bounds(ix0, ix1, iy0, iy1, iz0, iz1))

    # Add horizontal internal shelves slightly inset from the open face
    s_x0, s_x1 = xmin + t, xmax - t
    s_y0, s_y1 = ymin + t, ymax - t
    if open_face == "+Y":
        s_y1 = ymax - cfg.CLEARANCE_TOLERANCE
    elif open_face == "-Y":
        s_y0 = ymin + cfg.CLEARANCE_TOLERANCE
    elif open_face == "-X":
        s_x0 = xmin + cfg.CLEARANCE_TOLERANCE

    for sz in shelf_zs:
        shelf = _box_from_bounds(s_x0, s_x1, s_y0, s_y1, sz, sz + t)
        carcass = carcass.union(shelf)

    return carcass


def _add_led_channel_along_x(
    asm: cq.Assembly,
    name_prefix: str,
    x0: float,
    x1: float,
    y_front: float,
    z_top: float,
) -> None:
    """Add a recessed matte-black aluminum LED profile and warm-white diffuser strip along X."""
    y1 = y_front - cfg.LED_FRONT_INSET
    y0 = y1 - cfg.LED_PROFILE_WIDTH
    z_prof_bot = z_top - cfg.LED_PROFILE_HEIGHT
    profile = _box_from_bounds(x0, x1, y0, y1, z_prof_bot, z_top)
    asm.add(profile, name=f"{name_prefix}_profile", color=_color(cfg.COLOR_BLACK_METAL))

    strip = _box_from_bounds(
        x0 + 2.0,
        x1 - 2.0,
        y0 + 3.0,
        y1 - 3.0,
        z_prof_bot - cfg.LED_STRIP_HEIGHT,
        z_prof_bot,
    )
    asm.add(strip, name=f"{name_prefix}_strip", color=_color(cfg.COLOR_LED_WARM))


def build_wall_c_counter_and_basin() -> cq.Assembly:
    """Build Wall C floating bamboo counter, semi-recessed basin, black faucet, trap & LEDs."""
    asm = cq.Assembly(name="wall_c_counter_and_basin")

    # 1. Floating bamboo countertop (D to A) with cutout for semi-recessed basin
    basin_x0 = cfg.BASIN_CENTER_X - 0.5 * cfg.BASIN_WIDTH_X
    basin_x1 = cfg.BASIN_CENTER_X + 0.5 * cfg.BASIN_WIDTH_X

    counter_raw = _box_from_bounds(
        0.0,
        cfg.ROOM_LENGTH_X,
        0.0,
        cfg.COUNTER_DEPTH_Y,
        cfg.COUNTER_BOTTOM_Z,
        cfg.COUNTER_TOP_Z,
    )
    basin_cutout = _box_from_bounds(
        basin_x0 + cfg.CLEARANCE_TOLERANCE,
        basin_x1 - cfg.CLEARANCE_TOLERANCE,
        0.0,
        cfg.COUNTER_DEPTH_Y + cfg.CLEARANCE_TOLERANCE,
        cfg.COUNTER_BOTTOM_Z - cfg.CLEARANCE_TOLERANCE,
        cfg.COUNTER_TOP_Z + cfg.CLEARANCE_TOLERANCE,
    )
    counter = counter_raw.cut(basin_cutout)
    asm.add(counter, name="bamboo_counter", color=_color(cfg.COLOR_BAMBOO_COUNTER))

    # 2. Under-counter LED strips (split cleanly around the recessed basin underside)
    _add_led_channel_along_x(
        asm,
        "counter_led_left",
        cfg.LED_END_MARGIN,
        basin_x0 - cfg.LED_END_MARGIN,
        cfg.COUNTER_DEPTH_Y,
        cfg.COUNTER_BOTTOM_Z,
    )
    _add_led_channel_along_x(
        asm,
        "counter_led_right",
        basin_x1 + cfg.LED_END_MARGIN,
        cfg.ROOM_LENGTH_X - cfg.LED_END_MARGIN,
        cfg.COUNTER_DEPTH_Y,
        cfg.COUNTER_BOTTOM_Z,
    )

    # 3. Slim hidden 24V LED driver tucked tightly under counter near A-C corner cable
    drv_x1 = cfg.ROOM_LENGTH_X - cfg.LED_DRIVER_OFFSET_FROM_WALL_A_X
    drv_x0 = drv_x1 - cfg.LED_DRIVER_LENGTH_X
    drv_y0 = cfg.LED_DRIVER_OFFSET_FROM_WALL_C_Y
    drv_y1 = drv_y0 + cfg.LED_DRIVER_DEPTH_Y
    led_driver = _box_from_bounds(
        drv_x0,
        drv_x1,
        drv_y0,
        drv_y1,
        cfg.COUNTER_BOTTOM_Z - cfg.LED_DRIVER_HEIGHT_Z,
        cfg.COUNTER_BOTTOM_Z,
    )
    asm.add(led_driver, name="led_driver_24v", color=_color(cfg.COLOR_BLACK_METAL))

    # 4. Compact semi-recessed white ceramic basin (rounded front corners, hollowed bowl)
    outer_sketch = (
        cq.Sketch()
        .rect(cfg.BASIN_WIDTH_X, cfg.BASIN_DEPTH_Y)
        .vertices(">Y")
        .fillet(cfg.BASIN_FRONT_CORNER_RADIUS)
    )
    basin_outer = (
        cq.Workplane("XY")
        .placeSketch(outer_sketch)
        .extrude(cfg.BASIN_TOTAL_HEIGHT_Z)
        .translate(
            (cfg.BASIN_CENTER_X, 0.5 * cfg.BASIN_DEPTH_Y, cfg.BASIN_BOTTOM_Z)
        )
    )

    cav_w = cfg.BASIN_WIDTH_X - 2.0 * cfg.BASIN_WALL_THICKNESS
    cav_d = cfg.BASIN_DEPTH_Y - cfg.BASIN_REAR_DECK_Y - cfg.BASIN_WALL_THICKNESS
    cav_r = max(15.0, cfg.BASIN_FRONT_CORNER_RADIUS - cfg.BASIN_WALL_THICKNESS)
    cavity_sketch = cq.Sketch().rect(cav_w, cav_d).vertices(">Y").fillet(cav_r)
    cavity_y_center = cfg.BASIN_REAR_DECK_Y + 0.5 * cav_d
    basin_cavity = (
        cq.Workplane("XY")
        .placeSketch(cavity_sketch)
        .extrude(cfg.BASIN_CAVITY_DEPTH_Z + cfg.CLEARANCE_TOLERANCE)
        .translate(
            (
                cfg.BASIN_CENTER_X,
                cavity_y_center,
                cfg.BASIN_RIM_TOP_Z - cfg.BASIN_CAVITY_DEPTH_Z,
            )
        )
    )
    basin = basin_outer.cut(basin_cavity)
    asm.add(basin, name="semi_recessed_basin", color=_color(cfg.COLOR_CERAMIC))

    # Drain click-clack plug on bowl floor
    drain_plug = (
        cq.Workplane("XY")
        .workplane(offset=cfg.BASIN_RIM_TOP_Z - cfg.BASIN_CAVITY_DEPTH_Z)
        .center(cfg.BASIN_CENTER_X, cfg.SIPHON_CENTER_Y)
        .circle(28.0)
        .extrude(3.0)
    )
    asm.add(drain_plug, name="basin_drain_plug", color=_color(cfg.COLOR_BLACK_METAL))

    # 5. Matte-black single-lever basin faucet on rear ceramic deck
    faucet_body = (
        cq.Workplane("XY")
        .workplane(offset=cfg.BASIN_RIM_TOP_Z)
        .center(cfg.BASIN_CENTER_X, cfg.FAUCET_Y)
        .circle(0.5 * cfg.FAUCET_BODY_DIAMETER)
        .extrude(cfg.FAUCET_BODY_HEIGHT_Z)
    )
    faucet_spout = (
        cq.Workplane("XZ")
        .workplane(offset=-cfg.FAUCET_Y)
        .center(cfg.BASIN_CENTER_X, cfg.FAUCET_SPOUT_Z)
        .circle(0.5 * cfg.FAUCET_SPOUT_DIAMETER)
        .extrude(-cfg.FAUCET_SPOUT_LENGTH_Y)
    )
    lever_z0 = cfg.BASIN_RIM_TOP_Z + cfg.FAUCET_BODY_HEIGHT_Z
    faucet_lever = _box_from_bounds(
        cfg.BASIN_CENTER_X - 0.5 * cfg.FAUCET_LEVER_WIDTH_X,
        cfg.BASIN_CENTER_X + 0.5 * cfg.FAUCET_LEVER_WIDTH_X,
        cfg.FAUCET_Y - 12.0,
        cfg.FAUCET_Y - 12.0 + cfg.FAUCET_LEVER_LENGTH_Y,
        lever_z0,
        lever_z0 + cfg.FAUCET_LEVER_THICKNESS_Z,
    )
    faucet = faucet_body.union(faucet_spout).union(faucet_lever)
    asm.add(faucet, name="basin_faucet_black", color=_color(cfg.COLOR_BLACK_METAL))

    # 6. Matte-black decorative bottle siphon & wall waste pipe into Wall C drain stub
    tailpiece = (
        cq.Workplane("XY")
        .workplane(offset=cfg.SIPHON_BOTTLE_TOP_Z)
        .center(cfg.BASIN_CENTER_X, cfg.SIPHON_CENTER_Y)
        .circle(0.5 * cfg.SIPHON_PIPE_DIAMETER)
        .extrude(cfg.BASIN_BOTTOM_Z - cfg.SIPHON_BOTTLE_TOP_Z)
    )
    bottle = (
        cq.Workplane("XY")
        .workplane(offset=cfg.SIPHON_BOTTLE_BOTTOM_Z)
        .center(cfg.BASIN_CENTER_X, cfg.SIPHON_CENTER_Y)
        .circle(0.5 * cfg.SIPHON_BOTTLE_DIAMETER)
        .extrude(cfg.SIPHON_BOTTLE_TOP_Z - cfg.SIPHON_BOTTLE_BOTTOM_Z)
    )
    wall_pipe = (
        cq.Workplane("XZ")
        .center(cfg.BASIN_CENTER_X, cfg.SINK_DRAIN_Z)
        .circle(0.5 * cfg.SIPHON_PIPE_DIAMETER)
        .extrude(-cfg.SIPHON_CENTER_Y)
    )
    escutcheon = (
        cq.Workplane("XZ")
        .center(cfg.BASIN_CENTER_X, cfg.SINK_DRAIN_Z)
        .circle(0.5 * cfg.SIPHON_ESCUTCHEON_DIAMETER)
        .extrude(-cfg.SIPHON_ESCUTCHEON_THICKNESS)
    )
    siphon = tailpiece.union(bottle).union(wall_pipe).union(escutcheon)
    asm.add(siphon, name="bottle_siphon_black", color=_color(cfg.COLOR_BLACK_METAL))

    return asm


def build_wall_c_mirror() -> cq.Assembly:
    """Build full Wall D-to-A glued stepped mirror with factory cutout for 3-gang outlets."""
    asm = cq.Assembly(name="wall_c_mirror")

    left_pane = _box_from_bounds(
        cfg.MIRROR_SIDE_MARGIN_X,
        cfg.UPPER_C_STEP_X,
        0.0,
        cfg.MIRROR_THICKNESS_Y,
        cfg.MIRROR_BOTTOM_Z,
        cfg.UPPER_C_LEFT_BOTTOM_Z - cfg.MIRROR_TOP_CLEARANCE_Z,
    )
    right_pane = _box_from_bounds(
        cfg.UPPER_C_STEP_X,
        cfg.ROOM_LENGTH_X - cfg.MIRROR_SIDE_MARGIN_X,
        0.0,
        cfg.MIRROR_THICKNESS_Y,
        cfg.MIRROR_BOTTOM_Z,
        cfg.UPPER_C_RIGHT_BOTTOM_Z - cfg.MIRROR_TOP_CLEARANCE_Z,
    )
    mirror_raw = left_pane.union(right_pane)

    # Factory cutout for the Wall C 3-gang black power outlet box
    m = cfg.MIRROR_OUTLET_CUTOUT_MARGIN
    outlet_cutout = _box_from_bounds(
        cfg.OUTLET_C_START_X - m,
        cfg.OUTLET_C_START_X + cfg.OUTLET_C_WIDTH_X + m,
        -cfg.CLEARANCE_TOLERANCE,
        cfg.MIRROR_THICKNESS_Y + cfg.CLEARANCE_TOLERANCE,
        cfg.OUTLET_C_BOTTOM_Z - m,
        cfg.OUTLET_C_BOTTOM_Z + cfg.OUTLET_C_HEIGHT_Z + m,
    )
    mirror = mirror_raw.cut(outlet_cutout)
    asm.add(mirror, name="glued_stepped_mirror", color=_color(cfg.COLOR_MIRROR))

    return asm


def build_wall_c_upper_cabinets() -> cq.Assembly:
    """Build Wall C stepped upper cabinets: uniform 255 mm front + true L-shaped 288 mm blind-corner."""
    asm = cq.Assembly(name="wall_c_upper_cabinets")

    t = cfg.CABINET_PANEL_THICKNESS
    gap = cfg.CABINET_DOOR_GAP
    y_front = cfg.UPPER_C_DEPTH_Y                      # 255.0 mm continuous flush front
    y_carcass = y_front - t                            # 237.0 mm
    y_corner_return = cfg.UPPER_C_CORNER_RETURN_DEPTH_Y  # 288.0 mm flush against toilet cabinet
    valance_z0 = cfg.ROOM_HEIGHT_Z - cfg.CABINET_TOP_VALANCE_HEIGHT_Z

    left_x0 = cfg.UPPER_C_LEFT_FILLER_X                # 20.0 mm
    left_x1 = cfg.UPPER_C_STEP_X                       # 980.0 mm
    right_x0 = cfg.UPPER_C_STEP_X                      # 980.0 mm
    toilet_front_x = cfg.ROOM_LENGTH_X - cfg.TOILET_CAB_DEPTH_X  # 1451.0 mm

    # 1A. Left/basin carcass (x = 20..980, y = 0..237, z = 1850..2385)
    left_carcass = _build_carcass(
        left_x0,
        left_x1,
        0.0,
        y_carcass,
        cfg.UPPER_C_LEFT_BOTTOM_Z,
        cfg.ROOM_HEIGHT_Z,
        open_face="+Y",
        shelf_zs=(cfg.UPPER_C_LEFT_SHELF_Z,),
    )
    asm.add(
        left_carcass,
        name="upper_c_left_carcass",
        color=_color(cfg.COLOR_BAMBOO_CARCASS),
    )

    # 1B. True L-shaped blind-corner carcass (x = 980..1640, z = 1500..2385):
    # Main arm is 237 mm deep behind the 18 mm door (y = 0..237); short L-base behind the
    # toilet cabinet (x = 1451..1640) expands cleanly to y = 288 mm with 18 mm walls & L-shelves.
    z_r0, z_r1 = cfg.UPPER_C_RIGHT_BOTTOM_Z, cfg.ROOM_HEIGHT_Z
    corner_outer = _box_from_bounds(
        right_x0, cfg.ROOM_LENGTH_X, 0.0, y_carcass, z_r0, z_r1
    ).union(
        _box_from_bounds(
            toilet_front_x, cfg.ROOM_LENGTH_X, y_carcass, y_corner_return, z_r0, z_r1
        )
    )
    # Hollow out the main open span (x = 998..1451 open to +Y, x = 1451..1622 inside main arm)
    # plus the deeper L-leg cavity (x = 1469..1622, y = 18..270), keeping an 18 mm return wall
    # at x = 1451..1469 (flush with toilet cabinet front) and 18 mm cheek at y = 270..288.
    main_open_cavity = _box_from_bounds(
        right_x0 + t,
        toilet_front_x,
        t,
        y_carcass + cfg.CLEARANCE_TOLERANCE,
        z_r0 + t,
        z_r1 - t,
    )
    main_blind_cavity = _box_from_bounds(
        toilet_front_x - cfg.CLEARANCE_TOLERANCE,
        cfg.ROOM_LENGTH_X - t,
        t,
        y_carcass,
        z_r0 + t,
        z_r1 - t,
    )
    l_leg_cavity = _box_from_bounds(
        toilet_front_x + t,
        cfg.ROOM_LENGTH_X - t,
        t,
        y_corner_return - t,
        z_r0 + t,
        z_r1 - t,
    )
    corner_carcass = (
        corner_outer.cut(main_open_cavity).cut(main_blind_cavity).cut(l_leg_cavity)
    )

    # Proper L-shaped internal shelves filling both the main arm and the deeper blind L-leg
    for sz in cfg.UPPER_C_RIGHT_SHELF_ZS:
        shelf_main = _box_from_bounds(
            right_x0 + t,
            cfg.ROOM_LENGTH_X - t,
            t,
            y_carcass - cfg.CLEARANCE_TOLERANCE,
            sz,
            sz + t,
        )
        shelf_l_leg = _box_from_bounds(
            toilet_front_x + t,
            cfg.ROOM_LENGTH_X - t,
            t,
            y_corner_return - t,
            sz,
            sz + t,
        )
        corner_carcass = corner_carcass.union(shelf_main.union(shelf_l_leg))

    asm.add(
        corner_carcass,
        name="upper_c_corner_carcass_L",
        color=_color(cfg.COLOR_BAMBOO_CARCASS),
    )

    # 2. Fixed bamboo scribe filler at Wall D (notched cleanly around 12 mm door trim)
    left_filler_raw = _box_from_bounds(
        0.0,
        left_x0,
        0.0,
        y_front,
        cfg.UPPER_C_LEFT_BOTTOM_Z,
        cfg.ROOM_HEIGHT_Z,
    )
    door_trim_notch = _box_from_bounds(
        -cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_FRAME_PROTRUSION + cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_TRIM_OFFSET_Y,
        y_front + cfg.CLEARANCE_TOLERANCE,
        cfg.UPPER_C_LEFT_BOTTOM_Z - cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_HEIGHT_Z + cfg.DOOR_FRAME_WIDTH + cfg.CLEARANCE_TOLERANCE,
    )
    left_filler = left_filler_raw.cut(door_trim_notch)
    asm.add(
        left_filler, name="upper_c_wall_d_scribe", color=_color(cfg.COLOR_BAMBOO_FRONT)
    )

    # 3. ONE unbroken 110 mm static ceiling valance across all of Wall C (x = 20..1451)
    # with flush matte-black louvered exhaust vent grille + internal duct
    vent_cx = cfg.VENT_C_OFFSET_FROM_WALL_D_X + 0.5 * cfg.VENT_GRILLE_WIDTH_X
    grille_x0 = vent_cx - 0.5 * cfg.VENT_FRONT_GRILLE_WIDTH_X
    grille_x1 = vent_cx + 0.5 * cfg.VENT_FRONT_GRILLE_WIDTH_X
    grille_cz = valance_z0 + 0.5 * cfg.CABINET_TOP_VALANCE_HEIGHT_Z
    grille_z0 = grille_cz - 0.5 * cfg.VENT_FRONT_GRILLE_HEIGHT_Z
    grille_z1 = grille_cz + 0.5 * cfg.VENT_FRONT_GRILLE_HEIGHT_Z

    valance_raw = _box_from_bounds(
        left_x0,
        toilet_front_x,
        y_carcass,
        y_front,
        valance_z0,
        cfg.ROOM_HEIGHT_Z,
    )
    grille_cutout = _box_from_bounds(
        grille_x0,
        grille_x1,
        y_carcass - cfg.CLEARANCE_TOLERANCE,
        y_front + cfg.CLEARANCE_TOLERANCE,
        grille_z0,
        grille_z1,
    )
    asm.add(
        valance_raw.cut(grille_cutout),
        name="upper_c_top_valance",
        color=_color(cfg.COLOR_BAMBOO_FRONT),
    )

    grille_outer = _box_from_bounds(
        grille_x0,
        grille_x1,
        y_carcass,
        y_front + cfg.VENT_FRONT_GRILLE_PROTRUSION,
        grille_z0,
        grille_z1,
    )
    grille_inner = _box_from_bounds(
        grille_x0 + 8.0,
        grille_x1 - 8.0,
        y_carcass - cfg.CLEARANCE_TOLERANCE,
        y_front + cfg.VENT_FRONT_GRILLE_PROTRUSION + cfg.CLEARANCE_TOLERANCE,
        grille_z0 + 8.0,
        grille_z1 - 8.0,
    )
    grille_frame = grille_outer.cut(grille_inner)
    for slat_i in range(1, 4):
        sz = grille_z0 + slat_i * (cfg.VENT_FRONT_GRILLE_HEIGHT_Z / 4.0)
        slat = _box_from_bounds(
            grille_x0 + 6.0,
            grille_x1 - 6.0,
            y_front - 6.0,
            y_front + cfg.VENT_FRONT_GRILLE_PROTRUSION,
            sz - 2.0,
            sz + 2.0,
        )
        grille_frame = grille_frame.union(slat)
    asm.add(
        grille_frame,
        name="upper_c_vent_grille_black",
        color=_color(cfg.COLOR_BLACK_METAL),
    )

    wall_vent_z1 = cfg.ROOM_HEIGHT_Z - cfg.VENT_TOP_MARGIN_Z
    wall_vent_z0 = wall_vent_z1 - cfg.VENT_GRILLE_HEIGHT_Z
    duct_riser = _box_from_bounds(
        vent_cx - 0.5 * cfg.VENT_DUCT_WIDTH_X,
        vent_cx + 0.5 * cfg.VENT_DUCT_WIDTH_X,
        cfg.VENT_PROTRUSION,
        cfg.VENT_PROTRUSION + cfg.VENT_DUCT_HEIGHT_Z,
        wall_vent_z0,
        grille_z1,
    )
    duct_horiz = _box_from_bounds(
        vent_cx - 0.5 * cfg.VENT_DUCT_WIDTH_X,
        vent_cx + 0.5 * cfg.VENT_DUCT_WIDTH_X,
        cfg.VENT_PROTRUSION,
        y_carcass,
        grille_z0,
        grille_z1,
    )
    asm.add(
        duct_riser.union(duct_horiz),
        name="upper_c_exhaust_duct",
        color=_color(cfg.COLOR_DUCT),
    )

    # 4A. Left hinged bamboo doors (2 doors over doorway + basin) with matching black bar handles
    door_z_top = cfg.CABINET_DOOR_TOP_Z
    left_mid = 0.5 * (left_x0 + left_x1)
    left_doors = (
        ("upper_c_door_L1", left_x0 + 0.5 * gap, left_mid - 0.5 * gap, True),
        ("upper_c_door_L2", left_mid + 0.5 * gap, left_x1 - 0.5 * gap, False),
    )
    for d_name, dx0, dx1, handle_on_right in left_doors:
        door = _box_from_bounds(
            dx0, dx1, y_carcass, y_front, cfg.UPPER_C_LEFT_BOTTOM_Z, door_z_top
        )
        asm.add(door, name=d_name, color=_color(cfg.COLOR_BAMBOO_FRONT))
        hx_center = (
            dx1 - cfg.HANDLE_EDGE_OFFSET
            if handle_on_right
            else dx0 + cfg.HANDLE_EDGE_OFFSET
        )
        hz0 = cfg.UPPER_C_LEFT_BOTTOM_Z + cfg.HANDLE_BASE_OFFSET_Z
        handle = _box_from_bounds(
            hx_center - 0.5 * cfg.HANDLE_WIDTH,
            hx_center + 0.5 * cfg.HANDLE_WIDTH,
            y_front,
            y_front + cfg.HANDLE_PROTRUSION,
            hz0,
            hz0 + cfg.HANDLE_LENGTH_Z,
        )
        asm.add(handle, name=f"{d_name}_handle", color=_color(cfg.COLOR_BLACK_METAL))

    # 4B. Single blind-corner hinged bamboo door (x = 981.5..1449.5, flush at y = 255 mm)
    # Hinged on the left (x = 981.5) with matching protruding matte-black bar handle at y = 255..277
    # (leaves 11 mm clearance before toilet_cab_door_R swing plane at y = 288 mm!).
    cd_x0 = right_x0 + 0.5 * gap
    cd_x1 = toilet_front_x - 0.5 * gap
    corner_door = _box_from_bounds(
        cd_x0, cd_x1, y_carcass, y_front, cfg.UPPER_C_RIGHT_BOTTOM_Z, door_z_top
    )
    asm.add(corner_door, name="upper_c_door_corner", color=_color(cfg.COLOR_BAMBOO_FRONT))

    chx_center = cd_x1 - cfg.HANDLE_EDGE_OFFSET
    chz0 = cfg.UPPER_C_RIGHT_BOTTOM_Z + cfg.HANDLE_BASE_OFFSET_Z
    corner_handle = _box_from_bounds(
        chx_center - 0.5 * cfg.HANDLE_WIDTH,
        chx_center + 0.5 * cfg.HANDLE_WIDTH,
        y_front,
        y_front + cfg.HANDLE_PROTRUSION,
        chz0,
        chz0 + cfg.HANDLE_LENGTH_Z,
    )
    asm.add(
        corner_handle,
        name="upper_c_door_corner_handle",
        color=_color(cfg.COLOR_BLACK_METAL),
    )

    # 5. Aligned recessed under-cabinet LED channels above mirror (same Y inset across Wall C)
    _add_led_channel_along_x(
        asm,
        "upper_c_led_left",
        left_x0 + 10.0,
        left_x1 - 15.0,
        y_front,
        cfg.UPPER_C_LEFT_BOTTOM_Z,
    )
    _add_led_channel_along_x(
        asm,
        "upper_c_led_right",
        right_x0 + 15.0,
        cfg.ROOM_LENGTH_X - 15.0,
        y_front,
        cfg.UPPER_C_RIGHT_BOTTOM_Z,
    )

    return asm


def build_wall_a_toilet_cabinet() -> cq.Assembly:
    """Build Wall A upper cabinet flush with cistern ledge (double doors + 110 mm valance)."""
    asm = cq.Assembly(name="wall_a_toilet_cabinet")

    t = cfg.CABINET_PANEL_THICKNESS
    gap = cfg.CABINET_DOOR_GAP
    x_front = cfg.ROOM_LENGTH_X - cfg.TOILET_CAB_DEPTH_X
    x_carcass_front = x_front + t
    y0, y1 = cfg.TOILET_CAB_Y0, cfg.TOILET_CAB_Y1
    z0, z1 = cfg.TOILET_CAB_BOTTOM_Z, cfg.ROOM_HEIGHT_Z
    valance_z0 = z1 - cfg.CABINET_TOP_VALANCE_HEIGHT_Z

    carcass = _build_carcass(
        x_carcass_front,
        cfg.ROOM_LENGTH_X,
        y0,
        y1,
        z0,
        z1,
        open_face="-X",
        shelf_zs=cfg.TOILET_CAB_SHELF_ZS,
    )
    asm.add(carcass, name="toilet_cab_carcass", color=_color(cfg.COLOR_BAMBOO_CARCASS))

    valance = _box_from_bounds(x_front, x_carcass_front, y0, y1, valance_z0, z1)
    asm.add(valance, name="toilet_cab_valance", color=_color(cfg.COLOR_BAMBOO_FRONT))

    # Double hinged doors (each ~365 mm wide — clears Lamp 3 by >90 mm!)
    y_mid = 0.5 * (y0 + y1)
    doors = (
        ("toilet_cab_door_R", y0 + 0.5 * gap, y_mid - 0.5 * gap, True),
        ("toilet_cab_door_L", y_mid + 0.5 * gap, y1 - 0.5 * gap, False),
    )
    for d_name, dy0, dy1, handle_at_high_y in doors:
        door = _box_from_bounds(
            x_front, x_carcass_front, dy0, dy1, z0 + 0.5 * gap, cfg.CABINET_DOOR_TOP_Z
        )
        asm.add(door, name=d_name, color=_color(cfg.COLOR_BAMBOO_FRONT))

        hy_center = (
            dy1 - cfg.HANDLE_EDGE_OFFSET
            if handle_at_high_y
            else dy0 + cfg.HANDLE_EDGE_OFFSET
        )
        hz0 = z0 + cfg.HANDLE_BASE_OFFSET_Z
        handle = _box_from_bounds(
            x_front - cfg.HANDLE_PROTRUSION,
            x_front,
            hy_center - 0.5 * cfg.HANDLE_WIDTH,
            hy_center + 0.5 * cfg.HANDLE_WIDTH,
            hz0,
            hz0 + cfg.HANDLE_LENGTH_Z,
        )
        asm.add(handle, name=f"{d_name}_handle", color=_color(cfg.COLOR_BLACK_METAL))

    return asm


def build_wall_b_washer_cabinet() -> cq.Assembly:
    """Build Wall B washing machine cabinet flush with 550 mm pipe cover (double doors + valance)."""
    asm = cq.Assembly(name="wall_b_washer_cabinet")

    t = cfg.CABINET_PANEL_THICKNESS
    gap = cfg.CABINET_DOOR_GAP
    x0, x1 = cfg.WASHER_CAB_X0, cfg.WASHER_CAB_X1
    y_front = cfg.ROOM_DEPTH_Y - cfg.WASHER_CAB_DEPTH_Y
    y_carcass_front = y_front + t
    z0, z1 = cfg.WASHER_CAB_BOTTOM_Z, cfg.ROOM_HEIGHT_Z
    valance_z0 = z1 - cfg.CABINET_TOP_VALANCE_HEIGHT_Z

    carcass = _build_carcass(
        x0,
        x1,
        y_carcass_front,
        cfg.ROOM_DEPTH_Y,
        z0,
        z1,
        open_face="-Y",
        shelf_zs=cfg.WASHER_CAB_SHELF_ZS,
    )
    asm.add(carcass, name="washer_cab_carcass", color=_color(cfg.COLOR_BAMBOO_CARCASS))

    valance = _box_from_bounds(x0, x1, y_front, y_carcass_front, valance_z0, z1)
    asm.add(valance, name="washer_cab_valance", color=_color(cfg.COLOR_BAMBOO_FRONT))

    # Double hinged doors (each ~311 mm wide — clears Lamp 1 by 176 mm!)
    x_mid = 0.5 * (x0 + x1)
    doors = (
        ("washer_cab_door_L", x0 + 0.5 * gap, x_mid - 0.5 * gap, True),
        ("washer_cab_door_R", x_mid + 0.5 * gap, x1 - 0.5 * gap, False),
    )
    for d_name, dx0, dx1, handle_on_right in doors:
        door = _box_from_bounds(
            dx0, dx1, y_front, y_carcass_front, z0 + 0.5 * gap, cfg.CABINET_DOOR_TOP_Z
        )
        asm.add(door, name=d_name, color=_color(cfg.COLOR_BAMBOO_FRONT))

        hx_center = (
            dx1 - cfg.HANDLE_EDGE_OFFSET
            if handle_on_right
            else dx0 + cfg.HANDLE_EDGE_OFFSET
        )
        hz0 = z0 + cfg.HANDLE_BASE_OFFSET_Z
        handle = _box_from_bounds(
            hx_center - 0.5 * cfg.HANDLE_WIDTH,
            hx_center + 0.5 * cfg.HANDLE_WIDTH,
            y_front - cfg.HANDLE_PROTRUSION,
            y_front,
            hz0,
            hz0 + cfg.HANDLE_LENGTH_Z,
        )
        asm.add(handle, name=f"{d_name}_handle", color=_color(cfg.COLOR_BLACK_METAL))

    return asm


def build_washer_cat() -> cq.Assembly:
    """Build a cute stylized loafing cat on a folded mat atop the washing machine."""
    cat_asm = cq.Assembly(name="washer_cat")

    z_base = cfg.WM_TOTAL_HEIGHT_Z
    z_mat_top = z_base + cfg.CAT_MAT_THICKNESS_Z

    def _place(shape: cq.Workplane) -> cq.Workplane:
        return shape.rotate((0, 0, 0), (0, 0, 1), cfg.CAT_YAW_DEG).translate(
            (cfg.CAT_CENTER_X, cfg.CAT_CENTER_Y, z_mat_top)
        )

    # 1. Cozy folded blanket mat on top of the washing machine
    mat_sketch = (
        cq.Sketch().rect(cfg.CAT_MAT_WIDTH_X, cfg.CAT_MAT_DEPTH_Y).vertices().fillet(25.0)
    )
    mat = (
        cq.Workplane("XY")
        .placeSketch(mat_sketch)
        .extrude(cfg.CAT_MAT_THICKNESS_Z)
        .rotate((0, 0, 0), (0, 0, 1), cfg.CAT_YAW_DEG)
        .translate((cfg.CAT_CENTER_X, cfg.CAT_CENTER_Y, z_base))
    )
    cat_asm.add(mat, name="cat_blanket_mat", color=_color(cfg.COLOR_CAT_MAT))

    # 2. Plump loafing torso built via multi-section smooth ellipse loft (100% OCCT-safe!)
    rx = 0.5 * cfg.CAT_BODY_WIDTH   # 75 mm
    ry = 0.5 * cfg.CAT_BODY_LENGTH  # 120 mm
    h = cfg.CAT_BODY_HEIGHT         # 110 mm
    torso = (
        cq.Workplane("XY")
        .ellipse(rx * 0.90, ry * 0.92)
        .workplane(offset=h * 0.22)
        .ellipse(rx * 1.00, ry * 1.00)
        .workplane(offset=h * 0.36)
        .ellipse(rx * 0.92, ry * 0.94)
        .workplane(offset=h * 0.28)
        .ellipse(rx * 0.62, ry * 0.68)
        .workplane(offset=h * 0.14)
        .ellipse(rx * 0.20, ry * 0.26)
        .loft(ruled=False)
    )
    cat_asm.add(_place(torso), name="cat_torso", color=_color(cfg.COLOR_CAT_FUR))

    # 3. Round head nestled at front-top (-Y)
    head_y = -ry + 22.0
    head_z = h + 14.0
    head = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, head_y, head_z))
        .sphere(cfg.CAT_HEAD_RADIUS)
    )
    cat_asm.add(_place(head), name="cat_head", color=_color(cfg.COLOR_CAT_FUR))

    # 4. Pointed triangular ears + cute pink inner ear accents
    ear_base_z = head_z + 0.60 * cfg.CAT_HEAD_RADIUS
    for label, side in (("L", -1.0), ("R", 1.0)):
        ear = (
            cq.Workplane("XY")
            .circle(cfg.CAT_EAR_BASE_RADIUS)
            .workplane(offset=cfg.CAT_EAR_HEIGHT)
            .circle(2.5)
            .loft()
            .rotate((0, 0, 0), (0, 1, 0), side * 16.0)
            .translate((side * 26.0, head_y + 4.0, ear_base_z))
        )
        cat_asm.add(_place(ear), name=f"cat_ear_{label}", color=_color(cfg.COLOR_CAT_FUR))

        inner_ear = (
            cq.Workplane("XY")
            .circle(0.55 * cfg.CAT_EAR_BASE_RADIUS)
            .workplane(offset=0.68 * cfg.CAT_EAR_HEIGHT)
            .circle(1.5)
            .loft()
            .rotate((0, 0, 0), (0, 1, 0), side * 16.0)
            .translate((side * 26.0, head_y - 3.5, ear_base_z + 3.0))
        )
        cat_asm.add(
            _place(inner_ear),
            name=f"cat_inner_ear_{label}",
            color=_color(cfg.COLOR_CAT_NOSE),
        )

    # 5. Two plump tucked front paws peeking beneath the chest
    for label, side in (("L", -1.0), ("R", 1.0)):
        paw = (
            cq.Workplane("XY")
            .ellipse(18.0, 24.0)
            .workplane(offset=14.0)
            .ellipse(16.0, 22.0)
            .workplane(offset=10.0)
            .ellipse(7.0, 10.0)
            .loft()
            .translate((side * 28.0, -ry - 4.0, 0.0))
        )
        cat_asm.add(_place(paw), name=f"cat_paw_{label}", color=_color(cfg.COLOR_CAT_FUR))

    # 6. Curled tail wrapping neatly around the right (+X) flank (smooth revolved torus arc)
    tail_r = cfg.CAT_TAIL_RADIUS
    arc_r = rx + tail_r + 2.0  # wraps snugly along +X body curve
    arc_cy = 18.0              # centered slightly toward rear haunch
    tail_arc = (
        cq.Workplane("XZ")
        .center(arc_r, tail_r)
        .circle(tail_r)
        .revolve(155.0, (-arc_r, 0.0, 0.0), (-arc_r, 1.0, 0.0))
        .rotate((0, 0, 0), (0, 0, 1), -68.0)
        .translate((0.0, arc_cy, 0.0))
    )
    cat_asm.add(_place(tail_arc), name="cat_tail", color=_color(cfg.COLOR_CAT_FUR))

    # Spherical rounded tail tip at the front end of the revolved arc
    tip_angle = math.radians(-68.0)
    tail_tip = (
        cq.Workplane("XY")
        .transformed(
            offset=(arc_r * math.cos(tip_angle), arc_cy + arc_r * math.sin(tip_angle), tail_r)
        )
        .sphere(tail_r)
    )
    cat_asm.add(_place(tail_tip), name="cat_tail_tip", color=_color(cfg.COLOR_CAT_FUR))

    # 7. Glossy dark eyes & tiny pink nose facing -Y
    eye_y = head_y - cfg.CAT_HEAD_RADIUS * math.cos(math.radians(22.0))
    eye_z = head_z + 8.0
    for label, side in (("L", -1.0), ("R", 1.0)):
        eye = (
            cq.Workplane("XY")
            .transformed(offset=(side * 19.0, eye_y, eye_z))
            .sphere(6.0)
        )
        cat_asm.add(_place(eye), name=f"cat_eye_{label}", color=_color(cfg.COLOR_BLACK_METAL))

    nose = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, head_y - cfg.CAT_HEAD_RADIUS - 1.0, head_z - 5.0))
        .sphere(5.5)
    )
    cat_asm.add(_place(nose), name="cat_nose", color=_color(cfg.COLOR_CAT_NOSE))

    return cat_asm


def build_vanity() -> cq.Assembly | None:
    """Return the complete bamboo & matte-black furniture vision assembly when enabled."""
    if not cfg.ENABLE_VANITY:
        return None

    furniture = cq.Assembly(name="furniture_vision")
    furniture.add(build_wall_c_counter_and_basin(), name="wall_c_counter_and_basin")
    furniture.add(build_wall_c_mirror(), name="wall_c_mirror")
    furniture.add(build_wall_c_upper_cabinets(), name="wall_c_upper_cabinets")
    furniture.add(build_wall_a_toilet_cabinet(), name="wall_a_toilet_cabinet")
    furniture.add(build_wall_b_washer_cabinet(), name="wall_b_washer_cabinet")

    if cfg.ENABLE_CAT:
        furniture.add(build_washer_cat(), name="washer_cat")

    return furniture
