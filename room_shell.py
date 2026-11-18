"""Parametric 3D geometry for the existing bathroom shell, openings, and fixed fixtures."""

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


def build_walls_and_floor() -> cq.Assembly:
    """Build floor, semi-transparent walls (A, B, C, D with doorway), pipe cover, door, and ceiling."""
    envelope = cq.Assembly(name="envelope")

    wt = cfg.WALL_TILE_THICKNESS
    x_ext_min = -wt
    x_ext_max = cfg.ROOM_LENGTH_X + wt
    y_ext_min = -wt
    y_ext_max = cfg.ROOM_DEPTH_Y + wt

    # Finished floor tile layer (top surface at z = 0)
    floor = _box_from_bounds(
        x_ext_min, x_ext_max, y_ext_min, y_ext_max, -cfg.FLOOR_TILE_THICKNESS, 0.0
    )
    envelope.add(floor, name="floor", color=_color(cfg.COLOR_FLOOR))

    # Wall A (+X, toilet & shower back wall)
    wall_a = _box_from_bounds(
        cfg.ROOM_LENGTH_X,
        x_ext_max,
        0.0,
        cfg.ROOM_DEPTH_Y,
        0.0,
        cfg.ROOM_HEIGHT_Z,
    )
    envelope.add(wall_a, name="wall_A", color=_color(cfg.COLOR_WALL))

    # Wall B (+Y, washing machine & shower side wall)
    wall_b = _box_from_bounds(
        x_ext_min,
        x_ext_max,
        cfg.ROOM_DEPTH_Y,
        y_ext_max,
        0.0,
        cfg.ROOM_HEIGHT_Z,
    )
    envelope.add(wall_b, name="wall_B", color=_color(cfg.COLOR_WALL))

    # Wall C (-Y, power outlets & sink rough-ins wall)
    wall_c = _box_from_bounds(
        x_ext_min,
        x_ext_max,
        y_ext_min,
        0.0,
        0.0,
        cfg.ROOM_HEIGHT_Z,
    )
    envelope.add(wall_c, name="wall_C", color=_color(cfg.COLOR_WALL))

    # Wall D (-X, entrance door wall with 702 x 2010 mm clear hole cutout)
    door_y0 = cfg.DOOR_OFFSET_Y
    door_y1 = cfg.DOOR_OFFSET_Y + cfg.DOOR_WIDTH_Y
    wall_d_solid = _box_from_bounds(
        x_ext_min, 0.0, 0.0, cfg.ROOM_DEPTH_Y, 0.0, cfg.ROOM_HEIGHT_Z
    )
    door_cutout = _box_from_bounds(
        x_ext_min - cfg.CLEARANCE_TOLERANCE,
        cfg.CLEARANCE_TOLERANCE,
        door_y0,
        door_y1,
        0.0,
        cfg.DOOR_HEIGHT_Z,
    )
    wall_d = wall_d_solid.cut(door_cutout)
    envelope.add(wall_d, name="wall_D", color=_color(cfg.COLOR_WALL))

    # Full-height plasterboard heating-pipe cover in D-B corner (173 x 550 mm)
    pipe_cover = _box_from_bounds(
        0.0,
        cfg.PIPE_COVER_WIDTH_X,
        cfg.ROOM_DEPTH_Y - cfg.PIPE_COVER_DEPTH_Y,
        cfg.ROOM_DEPTH_Y,
        0.0,
        cfg.PIPE_COVER_HEIGHT_Z,
    )
    envelope.add(pipe_cover, name="corner_D_B_pipe_cover", color=_color(cfg.COLOR_WALL))

    # Entrance door frame (60 mm architrave starting at y = 200 mm) & outward-opening door leaf
    frame_outer = _box_from_bounds(
        x_ext_min - cfg.DOOR_FRAME_PROTRUSION,
        cfg.DOOR_FRAME_PROTRUSION,
        cfg.DOOR_TRIM_OFFSET_Y,
        door_y1 + cfg.DOOR_FRAME_WIDTH,
        0.0,
        cfg.DOOR_HEIGHT_Z + cfg.DOOR_FRAME_WIDTH,
    )
    frame_inner = _box_from_bounds(
        x_ext_min - 2.0 * cfg.DOOR_FRAME_PROTRUSION,
        2.0 * cfg.DOOR_FRAME_PROTRUSION,
        door_y0,
        door_y1,
        0.0,
        cfg.DOOR_HEIGHT_Z,
    )
    door_frame = frame_outer.cut(frame_inner)
    envelope.add(door_frame, name="door_frame", color=_color(cfg.COLOR_DOOR_WOOD))

    # Hinged on the Wall C side (y = door_y0), swinging outward into -X
    hinge_x = x_ext_min
    hinge_y = door_y0
    door_leaf = _box_from_bounds(
        hinge_x - cfg.DOOR_LEAF_THICKNESS,
        hinge_x,
        door_y0,
        door_y1,
        0.0,
        cfg.DOOR_HEIGHT_Z,
    ).rotate(
        (hinge_x, hinge_y, 0.0),
        (hinge_x, hinge_y, 1.0),
        cfg.DOOR_OPEN_ANGLE_DEG,
    )
    envelope.add(door_leaf, name="door_leaf", color=_color(cfg.COLOR_DOOR_WOOD))

    # Suspended plasterboard ceiling plane (semi-transparent)
    ceiling = _box_from_bounds(
        0.0,
        cfg.ROOM_LENGTH_X,
        0.0,
        cfg.ROOM_DEPTH_Y,
        cfg.ROOM_HEIGHT_Z,
        cfg.ROOM_HEIGHT_Z + cfg.CEILING_BOARD_THICKNESS,
    )
    envelope.add(ceiling, name="ceiling", color=_color(cfg.COLOR_CEILING))

    return envelope


def build_washing_machine() -> cq.Assembly:
    """Build existing front-load washing machine (back to Wall B, door facing -Y)."""
    wm = cq.Assembly(name="washing_machine")

    extra_margin_x = 0.5 * (cfg.WM_ENVELOPE_WIDTH_X - cfg.WM_BODY_WIDTH_X)
    wm_x0 = cfg.WM_START_X + extra_margin_x
    wm_x1 = wm_x0 + cfg.WM_BODY_WIDTH_X
    wm_y1 = cfg.ROOM_DEPTH_Y - cfg.WM_BACK_GAP_Y
    wm_y0 = cfg.ROOM_DEPTH_Y - cfg.WM_FRONT_FROM_WALL_B

    pad = _box_from_bounds(wm_x0, wm_x1, wm_y0, wm_y1, 0.0, cfg.WM_PAD_HEIGHT_Z)
    wm.add(pad, name="vibration_pad", color=_color(cfg.COLOR_BLACK_METAL))

    body = _box_from_bounds(
        wm_x0, wm_x1, wm_y0, wm_y1, cfg.WM_PAD_HEIGHT_Z, cfg.WM_TOTAL_HEIGHT_Z
    )
    wm.add(body, name="washer_cabinet", color=_color(cfg.COLOR_WASHER_BODY))

    door_cx = 0.5 * (wm_x0 + wm_x1)
    porthole = (
        cq.Workplane("XZ")
        .workplane(offset=-wm_y0)
        .center(door_cx, cfg.WM_DOOR_CENTER_Z)
        .circle(0.5 * cfg.WM_DOOR_DIAMETER)
        .extrude(cfg.WM_DOOR_PROTRUSION_Y)
    )
    wm.add(porthole, name="washer_door", color=_color(cfg.COLOR_WASHER_DOOR))

    return wm


def build_toilet_and_cistern() -> cq.Assembly:
    """Build concealed cistern tiled ledge (stops at shower), flush plate, and wall-hung toilet."""
    wc = cq.Assembly(name="toilet_and_cistern")

    cistern_x0 = cfg.ROOM_LENGTH_X - cfg.CISTERN_DEPTH_X
    cistern_y0 = cfg.CISTERN_GAP_FROM_WALL_C
    cistern_y1 = cfg.CISTERN_GAP_FROM_WALL_C + cfg.CISTERN_WIDTH_Y

    cistern_box = _box_from_bounds(
        cistern_x0, cfg.ROOM_LENGTH_X, cistern_y0, cistern_y1, 0.0, cfg.CISTERN_HEIGHT_Z
    )
    wc.add(cistern_box, name="cistern_ledge", color=_color(cfg.COLOR_CISTERN))

    # Flush plate on front of cistern boxing
    fp_y0 = cfg.CISTERN_GAP_FROM_WALL_C + cfg.FLUSH_PLATE_OFFSET_FROM_RIGHT_Y
    fp_y1 = fp_y0 + cfg.FLUSH_PLATE_WIDTH_Y
    fp_z1 = cfg.CISTERN_HEIGHT_Z - cfg.FLUSH_PLATE_TOP_MARGIN_Z
    fp_z0 = fp_z1 - cfg.FLUSH_PLATE_HEIGHT_Z
    flush_plate = _box_from_bounds(
        cistern_x0 - cfg.FLUSH_PLATE_PROTRUSION_X,
        cistern_x0,
        fp_y0,
        fp_y1,
        fp_z0,
        fp_z1,
    )
    wc.add(flush_plate, name="flush_plate", color=_color(cfg.COLOR_CHROME))

    # D-shaped wall-hung toilet bowl & closed lid
    radius = 0.5 * cfg.TOILET_WIDTH_Y
    bowl_front_x = cistern_x0 - cfg.TOILET_PROJECTION_X
    arc_cx = bowl_front_x + radius

    bowl_rect = _box_from_bounds(
        arc_cx,
        cistern_x0,
        cfg.TOILET_CENTER_Y - radius,
        cfg.TOILET_CENTER_Y + radius,
        cfg.TOILET_BOTTOM_Z,
        cfg.TOILET_BOTTOM_Z + cfg.TOILET_BOWL_HEIGHT_Z,
    )
    bowl_front_cyl = (
        cq.Workplane("XY")
        .workplane(offset=cfg.TOILET_BOTTOM_Z)
        .center(arc_cx, cfg.TOILET_CENTER_Y)
        .circle(radius)
        .extrude(cfg.TOILET_BOWL_HEIGHT_Z)
    )
    toilet_bowl = bowl_rect.union(bowl_front_cyl)
    wc.add(toilet_bowl, name="toilet_bowl", color=_color(cfg.COLOR_CERAMIC))

    seat_z0 = cfg.TOILET_BOTTOM_Z + cfg.TOILET_BOWL_HEIGHT_Z
    seat_rect = _box_from_bounds(
        arc_cx,
        cistern_x0,
        cfg.TOILET_CENTER_Y - radius,
        cfg.TOILET_CENTER_Y + radius,
        seat_z0,
        seat_z0 + cfg.TOILET_SEAT_HEIGHT_Z,
    )
    seat_front_cyl = (
        cq.Workplane("XY")
        .workplane(offset=seat_z0)
        .center(arc_cx, cfg.TOILET_CENTER_Y)
        .circle(radius)
        .extrude(cfg.TOILET_SEAT_HEIGHT_Z)
    )
    toilet_lid = seat_rect.union(seat_front_cyl)
    wc.add(toilet_lid, name="toilet_seat_lid", color=_color(cfg.COLOR_CERAMIC))

    return wc


def build_shower_enclosure() -> cq.Assembly:
    """Build walk-in glass shower enclosure, black profiles, and floor drain."""
    shower = cq.Assembly(name="shower_enclosure")

    glass_t = cfg.SHOWER_GLASS_THICKNESS
    prof = cfg.SHOWER_PROFILE_SIZE

    # Side glass panel along x = SHOWER_START_X (next to washing machine)
    side_glass = _box_from_bounds(
        cfg.SHOWER_START_X,
        cfg.SHOWER_START_X + glass_t,
        cfg.SHOWER_FRONT_Y,
        cfg.ROOM_DEPTH_Y,
        0.0,
        cfg.SHOWER_GLASS_HEIGHT_Z,
    )
    shower.add(
        side_glass, name="shower_side_glass", color=_color(cfg.COLOR_SHOWER_GLASS)
    )

    # Front glass panel along y = SHOWER_FRONT_Y (full rectangular height up to 2033 mm)
    front_glass = _box_from_bounds(
        cfg.SHOWER_START_X,
        cfg.ROOM_LENGTH_X,
        cfg.SHOWER_FRONT_Y,
        cfg.SHOWER_FRONT_Y + glass_t,
        0.0,
        cfg.SHOWER_GLASS_HEIGHT_Z,
    )
    shower.add(
        front_glass, name="shower_front_glass", color=_color(cfg.COLOR_SHOWER_GLASS)
    )

    # Matte-black vertical corner & wall mounting profiles
    corner_post = _box_from_bounds(
        cfg.SHOWER_START_X,
        cfg.SHOWER_START_X + prof,
        cfg.SHOWER_FRONT_Y,
        cfg.SHOWER_FRONT_Y + prof,
        0.0,
        cfg.SHOWER_GLASS_HEIGHT_Z,
    )
    wall_b_post = _box_from_bounds(
        cfg.SHOWER_START_X,
        cfg.SHOWER_START_X + prof,
        cfg.ROOM_DEPTH_Y - prof,
        cfg.ROOM_DEPTH_Y,
        0.0,
        cfg.SHOWER_GLASS_HEIGHT_Z,
    )
    wall_a_post = _box_from_bounds(
        cfg.ROOM_LENGTH_X - prof,
        cfg.ROOM_LENGTH_X,
        cfg.SHOWER_FRONT_Y,
        cfg.SHOWER_FRONT_Y + prof,
        0.0,
        cfg.SHOWER_GLASS_HEIGHT_Z,
    )
    profiles = corner_post.union(wall_b_post).union(wall_a_post)
    shower.add(
        profiles, name="shower_black_profiles", color=_color(cfg.COLOR_BLACK_METAL)
    )

    # Floor drain grate inside shower
    drain = _box_from_bounds(
        cfg.SHOWER_DRAIN_CENTER_X - 0.5 * cfg.SHOWER_DRAIN_SIZE_X,
        cfg.SHOWER_DRAIN_CENTER_X + 0.5 * cfg.SHOWER_DRAIN_SIZE_X,
        cfg.SHOWER_DRAIN_CENTER_Y - 0.5 * cfg.SHOWER_DRAIN_SIZE_Y,
        cfg.SHOWER_DRAIN_CENTER_Y + 0.5 * cfg.SHOWER_DRAIN_SIZE_Y,
        0.0,
        cfg.SHOWER_DRAIN_THICKNESS,
    )
    shower.add(drain, name="shower_floor_drain", color=_color(cfg.COLOR_CHROME))

    return shower


def build_wall_installations_and_lamps() -> cq.Assembly:
    """Build Wall B & C power outlets, sink rough-ins, ventilation grilles, and ceiling lamps."""
    inst = cq.Assembly(name="installations")

    # 3-gang power outlet panel on Wall C (y = 0)
    outlet_c = _box_from_bounds(
        cfg.OUTLET_C_START_X,
        cfg.OUTLET_C_START_X + cfg.OUTLET_C_WIDTH_X,
        0.0,
        cfg.OUTLET_C_DEPTH_Y,
        cfg.OUTLET_C_BOTTOM_Z,
        cfg.OUTLET_C_BOTTOM_Z + cfg.OUTLET_C_HEIGHT_Z,
    )
    inst.add(outlet_c, name="wall_C_power_outlets", color=_color(cfg.COLOR_BLACK_METAL))

    # 2-gang power outlet panel on Wall B above washing machine (y = ROOM_DEPTH_Y)
    outlet_b_x0 = cfg.PIPE_COVER_WIDTH_X + cfg.OUTLET_B_OFFSET_FROM_PIPE_COVER_X
    outlet_b_z1 = cfg.ROOM_HEIGHT_Z - cfg.OUTLET_B_TOP_FROM_CEILING_Z
    outlet_b = _box_from_bounds(
        outlet_b_x0,
        outlet_b_x0 + cfg.OUTLET_B_WIDTH_X,
        cfg.ROOM_DEPTH_Y - cfg.OUTLET_B_DEPTH_Y,
        cfg.ROOM_DEPTH_Y,
        outlet_b_z1 - cfg.OUTLET_B_HEIGHT_Z,
        outlet_b_z1,
    )
    inst.add(outlet_b, name="wall_B_power_outlets", color=_color(cfg.COLOR_BLACK_METAL))

    # Sink hot & cold water outlets (TopView.jpg rectangular valves on Wall C)
    hot_valve = _box_from_bounds(
        cfg.SINK_WATER_HOT_X - 0.5 * cfg.SINK_VALVE_SIZE_X,
        cfg.SINK_WATER_HOT_X + 0.5 * cfg.SINK_VALVE_SIZE_X,
        0.0,
        cfg.SINK_VALVE_PROTRUSION_Y,
        cfg.SINK_WATER_Z - 0.5 * cfg.SINK_VALVE_SIZE_Z,
        cfg.SINK_WATER_Z + 0.5 * cfg.SINK_VALVE_SIZE_Z,
    )
    inst.add(hot_valve, name="sink_hot_water_valve", color=_color(cfg.COLOR_HOT_WATER))

    cold_valve = _box_from_bounds(
        cfg.SINK_WATER_COLD_X - 0.5 * cfg.SINK_VALVE_SIZE_X,
        cfg.SINK_WATER_COLD_X + 0.5 * cfg.SINK_VALVE_SIZE_X,
        0.0,
        cfg.SINK_VALVE_PROTRUSION_Y,
        cfg.SINK_WATER_Z - 0.5 * cfg.SINK_VALVE_SIZE_Z,
        cfg.SINK_WATER_Z + 0.5 * cfg.SINK_VALVE_SIZE_Z,
    )
    inst.add(
        cold_valve, name="sink_cold_water_valve", color=_color(cfg.COLOR_COLD_WATER)
    )

    # Sink waste pipe stub on Wall C
    drain_stub = (
        cq.Workplane("XZ")
        .center(cfg.SINK_DRAIN_X, cfg.SINK_DRAIN_Z)
        .circle(0.5 * cfg.SINK_DRAIN_DIAMETER)
        .extrude(-cfg.SINK_DRAIN_PROTRUSION_Y)
    )
    inst.add(drain_stub, name="sink_drain_stub", color=_color(cfg.COLOR_DRAIN_PIPE))

    # Under-counter LED electrical cable stub in A-C corner (~300 mm above floor)
    led_cable = (
        cq.Workplane("XZ")
        .center(
            cfg.ROOM_LENGTH_X - cfg.LED_CABLE_OFFSET_FROM_WALL_A_X,
            cfg.LED_CABLE_HEIGHT_Z,
        )
        .circle(0.5 * cfg.LED_CABLE_DIAMETER)
        .extrude(-cfg.LED_CABLE_PROTRUSION_Y)
    )
    inst.add(
        led_cable,
        name="ac_corner_led_cable",
        color=_color(cfg.COLOR_ELECTRICAL_CABLE),
    )

    # Wall C ventilation grille near ceiling (161 x 151 mm)
    vent_top_z = cfg.ROOM_HEIGHT_Z - cfg.VENT_TOP_MARGIN_Z
    vent_bottom_z = vent_top_z - cfg.VENT_GRILLE_HEIGHT_Z
    vent_c = _box_from_bounds(
        cfg.VENT_C_OFFSET_FROM_WALL_D_X,
        cfg.VENT_C_OFFSET_FROM_WALL_D_X + cfg.VENT_GRILLE_WIDTH_X,
        0.0,
        cfg.VENT_PROTRUSION,
        vent_bottom_z,
        vent_top_z,
    )
    inst.add(vent_c, name="wall_C_vent", color=_color(cfg.COLOR_VENT))

    # Wall B ventilation grille inside shower (~250 mm from Wall A, same height as Wall C vent)
    vent_b_x1 = cfg.ROOM_LENGTH_X - cfg.VENT_B_OFFSET_FROM_WALL_A_X
    vent_b = _box_from_bounds(
        vent_b_x1 - cfg.VENT_B_WIDTH_X,
        vent_b_x1,
        cfg.ROOM_DEPTH_Y - cfg.VENT_PROTRUSION,
        cfg.ROOM_DEPTH_Y,
        vent_bottom_z,
        vent_top_z,
    )
    inst.add(vent_b, name="wall_B_shower_vent", color=_color(cfg.COLOR_VENT))

    # 3 surface-mounted cylindrical ceiling lamps
    lamp_z0 = cfg.ROOM_HEIGHT_Z - cfg.LAMP_HEIGHT_Z
    for idx, (cx, cy) in enumerate(cfg.LAMP_CENTERS_XY, start=1):
        lamp = (
            cq.Workplane("XY")
            .workplane(offset=lamp_z0)
            .center(cx, cy)
            .circle(0.5 * cfg.LAMP_DIAMETER)
            .extrude(cfg.LAMP_HEIGHT_Z)
        )
        inst.add(
            lamp,
            name=f"ceiling_lamp_{idx}",
            color=_color(cfg.COLOR_BLACK_METAL),
        )

    return inst


def build_room_shell() -> cq.Assembly:
    """Assemble the complete existing bathroom shell and fixed installations."""
    room = cq.Assembly(name="room_shell")
    room.add(build_walls_and_floor(), name="envelope")
    room.add(build_washing_machine(), name="washing_machine")
    room.add(build_toilet_and_cistern(), name="toilet_and_cistern")
    room.add(build_shower_enclosure(), name="shower_enclosure")
    room.add(build_wall_installations_and_lamps(), name="installations")
    return room
