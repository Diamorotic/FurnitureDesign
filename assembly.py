"""Combined bathroom CAD scene, dimensional/clearance assertions, and 3D viewer update."""

import cadquery as cq

import config as cfg
from room_shell import build_room_shell
from vanity import build_vanity


def run_clearance_assertions() -> None:
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

    toilet_front_x = cfg.ROOM_LENGTH_X - cfg.CISTERN_DEPTH_X - cfg.TOILET_PROJECTION_X
    print(
        f"[OK] Room shell verified: {cfg.ROOM_LENGTH_X:.0f} x {cfg.ROOM_DEPTH_Y:.0f} "
        f"x {cfg.ROOM_HEIGHT_Z:.0f} mm"
    )
    print(
        f"[INFO] Wall C clear depth before door trim: {cfg.DOOR_TRIM_OFFSET_Y:.0f} mm "
        f"(clear door hole at y = {cfg.DOOR_OFFSET_Y:.0f}..{door_end_y:.0f} mm)"
    )
    print(
        f"[INFO] Distance from Wall D (x = 0) to toilet front tip: {toilet_front_x:.0f} mm; "
        f"to cistern ledge: {cfg.ROOM_LENGTH_X - cfg.CISTERN_DEPTH_X:.0f} mm"
    )


def build_scene() -> cq.Assembly:
    """Build the complete bathroom CAD assembly."""
    scene = cq.Assembly(name="bathroom")
    scene.add(build_room_shell(), name="room_shell")

    vanity_asm = build_vanity()
    if vanity_asm is not None:
        scene.add(vanity_asm, name="vanity")

    return scene


run_clearance_assertions()
model = build_scene()

from ocp_viewer import show; show(model)
