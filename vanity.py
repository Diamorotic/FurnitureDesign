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
    """Build Wall C stepped upper cabinets (255 mm deep), 110 mm valance, ducted vent & LEDs."""
    asm = cq.Assembly(name="wall_c_upper_cabinets")

    t = cfg.CABINET_PANEL_THICKNESS
    gap = cfg.CABINET_DOOR_GAP
    y_carcass_front = cfg.UPPER_C_DEPTH_Y - t
    valance_z0 = cfg.ROOM_HEIGHT_Z - cfg.CABINET_TOP_VALANCE_HEIGHT_Z

    # 1. Carcasses (left/basin bay + right/toilet bay)
    left_x0 = cfg.UPPER_C_LEFT_FILLER_X
    left_x1 = cfg.UPPER_C_STEP_X
    right_x0 = cfg.UPPER_C_STEP_X
    right_x1 = cfg.ROOM_LENGTH_X - cfg.UPPER_C_RIGHT_FILLER_X

    left_carcass = _build_carcass(
        left_x0,
        left_x1,
        0.0,
        y_carcass_front,
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

    right_carcass = _build_carcass(
        right_x0,
        right_x1,
        0.0,
        y_carcass_front,
        cfg.UPPER_C_RIGHT_BOTTOM_Z,
        cfg.ROOM_HEIGHT_Z,
        open_face="+Y",
        shelf_zs=cfg.UPPER_C_RIGHT_SHELF_ZS,
    )
    asm.add(
        right_carcass,
        name="upper_c_right_carcass",
        color=_color(cfg.COLOR_BAMBOO_CARCASS),
    )

    # 2. Fixed bamboo scribe fillers at Wall D (notched for 12 mm door trim) and Wall A
    left_filler_raw = _box_from_bounds(
        0.0,
        left_x0,
        0.0,
        cfg.UPPER_C_DEPTH_Y,
        cfg.UPPER_C_LEFT_BOTTOM_Z,
        cfg.ROOM_HEIGHT_Z,
    )
    door_trim_notch = _box_from_bounds(
        -cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_FRAME_PROTRUSION + cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_TRIM_OFFSET_Y,
        cfg.UPPER_C_DEPTH_Y + cfg.CLEARANCE_TOLERANCE,
        cfg.UPPER_C_LEFT_BOTTOM_Z - cfg.CLEARANCE_TOLERANCE,
        cfg.DOOR_HEIGHT_Z + cfg.DOOR_FRAME_WIDTH + cfg.CLEARANCE_TOLERANCE,
    )
    left_filler = left_filler_raw.cut(door_trim_notch)
    asm.add(
        left_filler, name="upper_c_wall_d_scribe", color=_color(cfg.COLOR_BAMBOO_FRONT)
    )

    right_filler = _box_from_bounds(
        right_x1,
        cfg.ROOM_LENGTH_X,
        0.0,
        cfg.UPPER_C_DEPTH_Y,
        cfg.UPPER_C_RIGHT_BOTTOM_Z,
        cfg.ROOM_HEIGHT_Z,
    )
    asm.add(
        right_filler, name="upper_c_wall_a_scribe", color=_color(cfg.COLOR_BAMBOO_FRONT)
    )

    # 3. Continuous 110 mm static ceiling valance with flush matte-black exhaust vent grille
    vent_cx = cfg.VENT_C_OFFSET_FROM_WALL_D_X + 0.5 * cfg.VENT_GRILLE_WIDTH_X
    grille_x0 = vent_cx - 0.5 * cfg.VENT_FRONT_GRILLE_WIDTH_X
    grille_x1 = vent_cx + 0.5 * cfg.VENT_FRONT_GRILLE_WIDTH_X
    grille_cz = valance_z0 + 0.5 * cfg.CABINET_TOP_VALANCE_HEIGHT_Z
    grille_z0 = grille_cz - 0.5 * cfg.VENT_FRONT_GRILLE_HEIGHT_Z
    grille_z1 = grille_cz + 0.5 * cfg.VENT_FRONT_GRILLE_HEIGHT_Z

    valance_raw = _box_from_bounds(
        left_x0,
        right_x1,
        y_carcass_front,
        cfg.UPPER_C_DEPTH_Y,
        valance_z0,
        cfg.ROOM_HEIGHT_Z,
    )
    grille_cutout = _box_from_bounds(
        grille_x0,
        grille_x1,
        y_carcass_front - cfg.CLEARANCE_TOLERANCE,
        cfg.UPPER_C_DEPTH_Y + cfg.CLEARANCE_TOLERANCE,
        grille_z0,
        grille_z1,
    )
    valance = valance_raw.cut(grille_cutout)
    asm.add(valance, name="upper_c_top_valance", color=_color(cfg.COLOR_BAMBOO_FRONT))

    # Flush matte-black louvered slot grille on valance + internal duct routing from wall_C_vent
    grille_outer = _box_from_bounds(
        grille_x0,
        grille_x1,
        y_carcass_front,
        cfg.UPPER_C_DEPTH_Y + cfg.VENT_FRONT_GRILLE_PROTRUSION,
        grille_z0,
        grille_z1,
    )
    grille_inner = _box_from_bounds(
        grille_x0 + 8.0,
        grille_x1 - 8.0,
        y_carcass_front - cfg.CLEARANCE_TOLERANCE,
        cfg.UPPER_C_DEPTH_Y + cfg.VENT_FRONT_GRILLE_PROTRUSION + cfg.CLEARANCE_TOLERANCE,
        grille_z0 + 8.0,
        grille_z1 - 8.0,
    )
    grille_frame = grille_outer.cut(grille_inner)
    for slat_i in range(1, 4):
        sz = grille_z0 + slat_i * (cfg.VENT_FRONT_GRILLE_HEIGHT_Z / 4.0)
        slat = _box_from_bounds(
            grille_x0 + 6.0,
            grille_x1 - 6.0,
            cfg.UPPER_C_DEPTH_Y - 6.0,
            cfg.UPPER_C_DEPTH_Y + cfg.VENT_FRONT_GRILLE_PROTRUSION,
            sz - 2.0,
            sz + 2.0,
        )
        grille_frame = grille_frame.union(slat)
    asm.add(
        grille_frame,
        name="upper_c_vent_grille_black",
        color=_color(cfg.COLOR_BLACK_METAL),
    )

    # Internal flat duct rising from Wall C exhaust vent to the valance grille
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
        y_carcass_front,
        grille_z0,
        grille_z1,
    )
    asm.add(
        duct_riser.union(duct_horiz),
        name="upper_c_exhaust_duct",
        color=_color(cfg.COLOR_DUCT),
    )

    # 4. Hinged bamboo doors + matte-black vertical handles (2 left over basin, 2 right)
    door_z_top = cfg.CABINET_DOOR_TOP_Z

    # Left pair (over doorway + basin)
    left_mid = 0.5 * (left_x0 + left_x1)
    left_doors = (
        ("upper_c_door_L1", left_x0 + 0.5 * gap, left_mid - 0.5 * gap, True),
        ("upper_c_door_L2", left_mid + 0.5 * gap, left_x1 - 0.5 * gap, False),
    )
    for d_name, dx0, dx1, handle_on_right in left_doors:
        door = _box_from_bounds(
            dx0, dx1, y_carcass_front, cfg.UPPER_C_DEPTH_Y, cfg.UPPER_C_LEFT_BOTTOM_Z, door_z_top
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
            cfg.UPPER_C_DEPTH_Y,
            cfg.UPPER_C_DEPTH_Y + cfg.HANDLE_PROTRUSION,
            hz0,
            hz0 + cfg.HANDLE_LENGTH_Z,
        )
        asm.add(handle, name=f"{d_name}_handle", color=_color(cfg.COLOR_BLACK_METAL))

    # Right pair (dropped to z = 1500 mm beside toilet)
    right_mid = 0.5 * (right_x0 + right_x1)
    right_doors = (
        ("upper_c_door_R1", right_x0 + 0.5 * gap, right_mid - 0.5 * gap, True),
        ("upper_c_door_R2", right_mid + 0.5 * gap, right_x1 - 0.5 * gap, False),
    )
    for d_name, dx0, dx1, handle_on_right in right_doors:
        door = _box_from_bounds(
            dx0, dx1, y_carcass_front, cfg.UPPER_C_DEPTH_Y, cfg.UPPER_C_RIGHT_BOTTOM_Z, door_z_top
        )
        asm.add(door, name=d_name, color=_color(cfg.COLOR_BAMBOO_FRONT))
        hx_center = (
            dx1 - cfg.HANDLE_EDGE_OFFSET
            if handle_on_right
            else dx0 + cfg.HANDLE_EDGE_OFFSET
        )
        hz0 = cfg.UPPER_C_RIGHT_BOTTOM_Z + cfg.HANDLE_BASE_OFFSET_Z
        handle = _box_from_bounds(
            hx_center - 0.5 * cfg.HANDLE_WIDTH,
            hx_center + 0.5 * cfg.HANDLE_WIDTH,
            cfg.UPPER_C_DEPTH_Y,
            cfg.UPPER_C_DEPTH_Y + cfg.HANDLE_PROTRUSION,
            hz0,
            hz0 + cfg.HANDLE_LENGTH_Z,
        )
        asm.add(handle, name=f"{d_name}_handle", color=_color(cfg.COLOR_BLACK_METAL))

    # 5. Recessed under-cabinet LED channels above mirror (both left & right sections)
    _add_led_channel_along_x(
        asm,
        "upper_c_led_left",
        left_x0 + 10.0,
        left_x1 - 15.0,
        cfg.UPPER_C_DEPTH_Y,
        cfg.UPPER_C_LEFT_BOTTOM_Z,
    )
    _add_led_channel_along_x(
        asm,
        "upper_c_led_right",
        right_x0 + 15.0,
        right_x1 - 10.0,
        cfg.UPPER_C_DEPTH_Y,
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

    # Local helper to orient cat parts at (CAT_CENTER_X, CAT_CENTER_Y) facing -Y + CAT_YAW_DEG
    def _place(shape: cq.Workplane) -> cq.Workplane:
        return shape.rotate((0, 0, 0), (0, 0, 1), cfg.CAT_YAW_DEG).translate(
            (cfg.CAT_CENTER_X, cfg.CAT_CENTER_Y, z_mat_top)
        )

    # Cozy folded mat on top of the washing machine
    mat_sketch = cq.Sketch().rect(cfg.CAT_MAT_WIDTH_X, cfg.CAT_MAT_DEPTH_Y).vertices().fillet(25.0)
    mat = (
        cq.Workplane("XY")
        .placeSketch(mat_sketch)
        .extrude(cfg.CAT_MAT_THICKNESS_Z)
        .rotate((0, 0, 0), (0, 0, 1), cfg.CAT_YAW_DEG)
        .translate((cfg.CAT_CENTER_X, cfg.CAT_CENTER_Y, z_base))
    )
    cat_asm.add(mat, name="cat_blanket_mat", color=_color(cfg.COLOR_CAT_MAT))

    # Plump loafing body (rounded capsule extruded & topped with smooth dome, facing -Y)
    body_r = 0.5 * cfg.CAT_BODY_WIDTH
    body_straight = max(10.0, cfg.CAT_BODY_LENGTH - cfg.CAT_BODY_WIDTH)
    body_sketch = (
        cq.Sketch()
        .rect(cfg.CAT_BODY_WIDTH, cfg.CAT_BODY_LENGTH)
        .vertices()
        .fillet(body_r - 2.0)
    )
    lower_body = (
        cq.Workplane("XY")
        .placeSketch(body_sketch)
        .extrude(0.55 * cfg.CAT_BODY_HEIGHT)
    )
    # Soft rounded upper back (horizontal cylinder + end spheres along Y)
    spine_z = 0.50 * cfg.CAT_BODY_HEIGHT
    spine_r = 0.48 * cfg.CAT_BODY_WIDTH
    spine_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-0.5 * body_straight)
        .center(0.0, spine_z)
        .circle(spine_r)
        .extrude(body_straight)
    )
    front_chest = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, -0.5 * body_straight, spine_z))
        .sphere(spine_r)
    )
    rear_haunch = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.5 * body_straight, spine_z))
        .sphere(spine_r)
    )
    # Clip bottom cleanly flat at z = 0 so the loaf rests squarely on the mat
    clip_box = _box_from_bounds(-300.0, 300.0, -300.0, 300.0, 0.0, 300.0)
    body = lower_body.union(spine_cyl).union(front_chest).union(rear_haunch).intersect(clip_box)

    # Round head nestled at front-top (-Y)
    head_y = -0.5 * cfg.CAT_BODY_LENGTH + 18.0
    head_z = cfg.CAT_BODY_HEIGHT + 18.0
    head = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, head_y, head_z))
        .sphere(cfg.CAT_HEAD_RADIUS)
    )

    # Two cute pointed ears on top of head
    ear_base_z = head_z + 0.62 * cfg.CAT_HEAD_RADIUS
    ears = None
    for side in (-1.0, 1.0):
        ear = (
            cq.Workplane("XY")
            .circle(cfg.CAT_EAR_BASE_RADIUS)
            .workplane(offset=cfg.CAT_EAR_HEIGHT)
            .circle(2.5)
            .loft()
            .rotate((0, 0, 0), (0, 1, 0), side * 16.0)
            .translate((side * 27.0, head_y + 4.0, ear_base_z))
        )
        ears = ear if ears is None else ears.union(ear)

    # Two tiny tucked front paws peeking out beneath chest
    paws = None
    for side in (-1.0, 1.0):
        paw = (
            cq.Workplane("XY")
            .transformed(offset=(side * 30.0, -0.5 * cfg.CAT_BODY_LENGTH - 8.0, 16.0))
            .sphere(19.0)
            .intersect(clip_box)
        )
        paws = paw if paws is None else paws.union(paw)

    # Curled tail wrapping snugly around the right (+X) flank
    tail_r = cfg.CAT_TAIL_RADIUS
    tail_pts = [
        (0.0, 0.5 * cfg.CAT_BODY_LENGTH - 10.0),
        (body_r + 14.0, 0.42 * cfg.CAT_BODY_LENGTH),
        (body_r + 16.0, 0.0),
        (body_r + 6.0, -0.35 * cfg.CAT_BODY_LENGTH),
    ]
    tail_path = cq.Workplane("XY").workplane(offset=tail_r).spline(tail_pts)
    tail_section = (
        cq.Workplane("YZ")
        .workplane(offset=tail_pts[0][0])
        .center(tail_pts[0][1], tail_r)
        .circle(tail_r)
    )
    tail = tail_section.sweep(tail_path)
    tail_tip = (
        cq.Workplane("XY")
        .transformed(offset=(tail_pts[-1][0], tail_pts[-1][1], tail_r))
        .sphere(tail_r)
    )

    cat_fur = body.union(head).union(ears).union(paws).union(tail).union(tail_tip)
    cat_asm.add(_place(cat_fur), name="cat_body", color=_color(cfg.COLOR_CAT_FUR))

    # Eyes & tiny pink nose facing -Y
    eye_y = head_y - cfg.CAT_HEAD_RADIUS * math.cos(math.radians(22.0))
    eye_z = head_z + 8.0
    eyes = None
    for side in (-1.0, 1.0):
        eye = (
            cq.Workplane("XY")
            .transformed(offset=(side * 19.0, eye_y, eye_z))
            .sphere(6.0)
        )
        eyes = eye if eyes is None else eyes.union(eye)
    cat_asm.add(_place(eyes), name="cat_eyes", color=_color(cfg.COLOR_BLACK_METAL))

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
