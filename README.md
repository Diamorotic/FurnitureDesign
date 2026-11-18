# Bathroom CAD & Furniture Design

Parametric 3D CAD model and layout for the bathroom project using [CadQuery](https://github.com/CadQuery/cadquery) and [pixi](https://pixi.sh).

## Project Structure

- `config.py`: Room dimensions, plumbing rough-in locations, and tolerances (in mm).
- `room_shell.py`: Parametric walls, floor, door/window openings, and fixtures.
- `vanity.py`: Furniture models (vanity, cabinets, etc.).
- `assembly.py`: Full scene assembly, clearances, and 3D preview triggers.
- `Blueprints/`: Reference photos and 2D sketches.

## Setup & Running

Prerequisites: [Pixi](https://pixi.sh)

```bash
# Run assembly and update the 3D viewer (ocp_viewer)
pixi run python assembly.py
```
