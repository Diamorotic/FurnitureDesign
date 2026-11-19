"""Combined bathroom CAD scene, dimensional/clearance assertions, and 3D viewer update."""

import math

import cadquery as cq

import config as cfg
from room_shell import build_room_shell
from vanity import build_vanity


def run_room_shell_assertions() -> None:
    """Validate blueprint dimension chains and baseline room clearances."""
    # 1. Wall B X-chain: pipe cover (173) + washer zone (633) + shower width (834 at ceiling) == 1640
    wall_b_sum = cfg.PIPE_COVER_WIDTH_X + cfg.WM_ENVELOPE_WIDTH_X + cfg.SHOWER_WIDTH_X
    assert abs(wall_b_sum - cfg.ROOM_LENGTH_X) <= cfg.CLEARANCE_TOLERANCE, (
        f"Wall B X-chain mismatch: {wall_b_sum} mm vs ROOM_LENGTH_X={cfg.ROOM_LENGTH_X} mm"
    )

    # 2. Wall A Y-chain: niche (288) + cistern (735) + shower depth (685) == 1708 (~1710)
    wall_a_sum = cfg.CISTERN_GAP_FROM_WALL_C + cfg.CISTERN_WIDTH_Y + cfg.SHOWER_DEPTH_Y
    assert abs(wall_a_sum - cfg.ROOM_DEPTH_Y) <= cfg.CLEARANCE_TOLERANCE, (
        f"Wall A Y-chain mismatch: {wall_a_sum} mm vs ROOM_DEPTH_Y={cfg.ROOM_DEPTH_Y} mm"
    )

    # 3. Wall D doorway fits inside Wall D length and leaves room before corner pipe cover
    door_end_y = cfg.DOOR_OFFSET_Y + cfg.DOOR_WIDTH_Y
    pipe_cover_start_y = cfg.ROOM_DEPTH_Y - cfg.PIPE_COVER_DEPTH_Y
    assert door_end_y <= pipe_cover_start_y, (
        f"Door opening (y_end={door_end_y} mm) overlaps pipe cover (y_start={pipe_cover_start_y} mm)"
    )

    # 4. Wall B sockets sit cleanly above washing machine and between pipe cover & shower
    outlet_b_x0 = cfg.PIPE_COVER_WIDTH_X + cfg.OUTLET_B_OFFSET_FROM_PIPE_COVER_X
    outlet_b_x1 = outlet_b_x0 + cfg.OUTLET_B_WIDTH_X
    outlet_b_z0 = (
        cfg.ROOM_HEIGHT_Z - cfg.OUTLET_B_TOP_FROM_CEILING_Z - cfg.OUTLET_B_HEIGHT_Z
    )
    assert outlet_b_x1 < cfg.SHOWER_START_X, (
        f"Wall B sockets (x1={outlet_b_x1} mm) overlap shower glass (x={cfg.SHOWER_START_X} mm)"
    )
    assert outlet_b_z0 > cfg.WM_TOTAL_HEIGHT_Z, (
        f"Wall B sockets (z0={outlet_b_z0} mm) overlap washing machine ({cfg.WM_TOTAL_HEIGHT_Z} mm)"
    )

    # 5. Cistern vertical chain: toilet lid stays below flush plate
    toilet_top_z = (
        cfg.TOILET_BOTTOM_Z + cfg.TOILET_BOWL_HEIGHT_Z + cfg.TOILET_SEAT_HEIGHT_Z
    )
    flush_bottom_z = (
        cfg.CISTERN_HEIGHT_Z - cfg.FLUSH_PLATE_TOP_MARGIN_Z - cfg.FLUSH_PLATE_HEIGHT_Z
    )
    assert toilet_top_z < flush_bottom_z, (
        f"Toilet lid top ({toilet_top_z} mm) overlaps flush plate ({flush_bottom_z} mm)"
    )

    # 6. Center walkway clearance between washing machine front porthole and Wall C
    washer_front_most_y = (
        cfg.ROOM_DEPTH_Y - cfg.WM_FRONT_FROM_WALL_B - cfg.WM_DOOR_PROTRUSION_Y
    )
    assert washer_front_most_y >= cfg.MIN_WALKWAY_CLEARANCE, (
        f"Insufficient walkway width in front of washer: {washer_front_most_y} mm"
    )

    print(
        f"[OK] Room shell verified: {cfg.ROOM_LENGTH_X:.0f} x {cfg.ROOM_DEPTH_Y:.0f} "
        f"x {cfg.ROOM_HEIGHT_Z:.0f} mm"
    )


def run_furniture_assertions() -> None:
    """Validate clearances, ergonomics, and ceiling-lamp non-collision for all furniture."""
    if not cfg.ENABLE_VANITY:
        return

    lamp_bottom_z = cfg.ROOM_HEIGHT_Z - cfg.LAMP_HEIGHT_Z  # 2291.0 mm

    # 1. Counter depth clears Wall D door frame trim
    assert cfg.COUNTER_DEPTH_Y <= cfg.DOOR_TRIM_OFFSET_Y, (
        f"Counter depth ({cfg.COUNTER_DEPTH_Y} mm) exceeds Wall D door trim ({cfg.DOOR_TRIM_OFFSET_Y} mm)"
    )

    # 2. Semi-recessed basin clears Wall C outlets (X), toilet front (X), and leaves standing space to washer (Y)
    basin_x0 = cfg.BASIN_CENTER_X - 0.5 * cfg.BASIN_WIDTH_X
    basin_x1 = cfg.BASIN_CENTER_X + 0.5 * cfg.BASIN_WIDTH_X
    outlet_c_x1 = cfg.OUTLET_C_START_X + cfg.OUTLET_C_WIDTH_X
    toilet_front_x = cfg.ROOM_LENGTH_X - cfg.CISTERN_DEPTH_X - cfg.TOILET_PROJECTION_X
    washer_front_y = (
        cfg.ROOM_DEPTH_Y - cfg.WM_FRONT_FROM_WALL_B - cfg.WM_DOOR_PROTRUSION_Y
    )
    basin_standing_space_y = washer_front_y - cfg.BASIN_DEPTH_Y

    assert basin_x0 > outlet_c_x1, (
        f"Basin left edge ({basin_x0} mm) overlaps Wall C outlets (x1={outlet_c_x1} mm)"
    )
    assert basin_x1 < toilet_front_x, (
        f"Basin right edge ({basin_x1} mm) overlaps toilet nose (x={toilet_front_x} mm)"
    )
    assert basin_standing_space_y >= cfg.MIN_BASIN_WALKWAY_CLEARANCE, (
        f"Basin-to-washer standing clearance too tight: {basin_standing_space_y:.0f} mm"
    )

    # 3. Wall C upper cabinets clear clear doorway opening, toilet cabinet, basin step, and ceiling lamps
    assert cfg.UPPER_C_DEPTH_Y < cfg.DOOR_OFFSET_Y, (
        f"Wall C upper cabinets ({cfg.UPPER_C_DEPTH_Y} mm) intrude into clear doorway ({cfg.DOOR_OFFSET_Y} mm)"
    )
    assert cfg.UPPER_C_DEPTH_Y < cfg.TOILET_CAB_Y0, (
        f"Wall C upper cabinets ({cfg.UPPER_C_DEPTH_Y} mm) collide with toilet cabinet (y={cfg.TOILET_CAB_Y0} mm)"
    )
    assert cfg.UPPER_C_STEP_X > basin_x1, (
        f"Wall C upper cabinet step ({cfg.UPPER_C_STEP_X} mm) overhangs basin right edge ({basin_x1} mm)"
    )
    lamp_door_clearance_z = lamp_bottom_z - cfg.CABINET_DOOR_TOP_Z
    assert lamp_door_clearance_z >= cfg.MIN_LAMP_DOOR_CLEARANCE, (
        f"Cabinet doors too close to ceiling lamp bottom: {lamp_door_clearance_z:.1f} mm"
    )

    # 4. Wall A toilet cabinet double doors clear Lamp 3 in full swing arc too
    toilet_door_width = 0.5 * (cfg.TOILET_CAB_Y1 - cfg.TOILET_CAB_Y0)
    cistern_front_x = cfg.ROOM_LENGTH_X - cfg.TOILET_CAB_DEPTH_X
    lamp3_x_near = cfg.LAMP_3_CENTER_X + 0.5 * cfg.LAMP_DIAMETER
    lamp3_y_near = cfg.LAMP_3_NEAR_Y
    lamp3_dist = math.hypot(cistern_front_x - lamp3_x_near, lamp3_y_near - cfg.TOILET_CAB_Y0)
    assert toilet_door_width < lamp3_dist, (
        f"Toilet cabinet door ({toilet_door_width:.1f} mm) hits Lamp 3 ({lamp3_dist:.1f} mm)"
    )

    # 5. Wall B washer cabinet clears 2-gang sockets, shower glass, cat headroom, and Lamp 1
    outlet_b_top_z = cfg.ROOM_HEIGHT_Z - cfg.OUTLET_B_TOP_FROM_CEILING_Z
    cat_headroom_z = cfg.WASHER_CAB_BOTTOM_Z - cfg.WM_TOTAL_HEIGHT_Z
    washer_door_width = 0.5 * (cfg.WASHER_CAB_X1 - cfg.WASHER_CAB_X0)
    washer_cab_front_y = cfg.ROOM_DEPTH_Y - cfg.WASHER_CAB_DEPTH_Y
    lamp1_y_far = cfg.LAMP_1_NEAR_Y + cfg.LAMP_DIAMETER

    assert cfg.WASHER_CAB_BOTTOM_Z > outlet_b_top_z + 50.0, (
        f"Washer cabinet ({cfg.WASHER_CAB_BOTTOM_Z} mm) too close to Wall B sockets ({outlet_b_top_z} mm)"
    )
    assert cfg.WASHER_CAB_X1 < cfg.SHOWER_START_X, (
        f"Washer cabinet (x1={cfg.WASHER_CAB_X1} mm) touches shower glass ({cfg.SHOWER_START_X} mm)"
    )
    assert cat_headroom_z >= cfg.MIN_CAT_HEADROOM_Z, (
        f"Cat headroom over washer too low: {cat_headroom_z:.0f} mm"
    )
    assert washer_door_width < (washer_cab_front_y - lamp1_y_far), (
        f"Washer cabinet door ({washer_door_width:.1f} mm) hits Lamp 1"
    )

    print(
        f"[OK] Furniture vision verified | Basin walkway: {basin_standing_space_y:.0f} mm | "
        f"Lamp-to-door Z clearance: {lamp_door_clearance_z:.0f} mm | "
        f"Toilet-to-Wall C corner reveal: {cfg.TOILET_CAB_Y0 - cfg.UPPER_C_DEPTH_Y:.0f} mm | "
        f"Cat headroom: {cat_headroom_z:.0f} mm"
    )


def build_scene() -> cq.Assembly:
    """Build the complete bathroom CAD assembly."""
    scene = cq.Assembly(name="bathroom")
    scene.add(build_room_shell(), name="room_shell")

    vanity_asm = build_vanity()
    if vanity_asm is not None:
        scene.add(vanity_asm, name="vanity")

    return scene


run_room_shell_assertions()
run_furniture_assertions()
model = build_scene()

from ocp_viewer import show; show(model)
