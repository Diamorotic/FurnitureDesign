\# Workspace Rules: Bathroom CAD



\## Environment \& Execution

\- Always run Python scripts and package commands via `pixi run` (e.g., `pixi run python assembly.py`). Never invoke global `python` or `pip`.

\- To add Conda packages, use `pixi add <pkg>`. To add PyPI packages, use `pixi add --pypi <pkg>`.



\## CAD \& Architecture Conventions

\- Use `cadquery` for parametric 3D geometry and `ocp\_viewer` (`from ocp\_viewer import show`) for 3D previews.

\- Always end `assembly.py` with `from ocp\_viewer import show; show(model)` so the 3D viewer updates automatically on every run.

\- Never start `python -m ocp\_viewer` inside agent commands; assume the standalone viewer server is already running on port 3939.

\- All dimensions, coordinates, and tolerances must be in \*\*millimeters (mm)\*\* as top-level constants in `config.py`.

\- Keep modules separated: `config.py` (room bounds \& plumbing rough-ins), `room\_shell.py` (walls/floor/openings), furniture modules (e.g., `vanity.py`), and `assembly.py` (combined scene + clearance assertions).

