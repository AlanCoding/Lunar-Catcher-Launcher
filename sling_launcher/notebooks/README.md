`02_orbit_cycle_feasibility.ipynb` is the executed Phase 4 companion, with sourced
orbital constants and explicitly illustrative cycle inputs. It imports reusable
modules and is not a complete or optimized launcher model.

From the repository root, register a project-local kernel once:

    .env/hub/bin/python -m ipykernel install --prefix .env/hub --name hub-study --display-name 'Lunar hub study'

Rebuild and execute:

    JUPYTER_PATH="$PWD/.env/hub/share/jupyter" .env/hub/bin/python sling_launcher/notebooks/build_notebook.py --execute

The full Phase 5 engineering notebook will follow review of the orbital and
mechanical requirements. Exact inputs live in the modules, not duplicated cells.
