# Local numerical data and reproduction

Generated `.npz` simulation histories are Git-ignored. Existing local arrays remain at their original paths; new clones contain the code, configuration, summary results and publication assets. Run a study's calculation stage before its plotting stage when local arrays are absent. Long dynamic simulations can take substantial time.

[simulation_cache_manifest.json](simulation_cache_manifest.json) records paths, byte sizes and SHA-256 checksums for the 68 arrays retained locally during the history cleanup. Checksums identify those exact saved artifacts; regenerating with different library versions can change numerical output or archive bytes.

## Generation routes

Run Python modules from the repository root using the study's documented environment and parameters. The following entry points write the arrays; the linked study README gives invocation details.

| Study | Generating modules / scripts | Instructions |
|---|---|---|
| Staged spool bank | `sling_launcher.staged_spool_bank.report` | [README](sling_launcher/staged_spool_bank/README.md) |
| Inertial spooled tether | `sling_launcher.spooled_tether_2d.run` (32/64-node and ratio3 cases) | [README](sling_launcher/spooled_tether_2d/README.md) |
| Straw constant-speed dynamics | `sling_launcher.lunar_slider_straw.guide_comparison.constant_speed.simulate` (32/64 nodes) | [README](sling_launcher/lunar_slider_straw/guide_comparison/constant_speed/README.md) |
| Straw scalar/shape screening | `sling_launcher.lunar_slider_straw.screening.scalar` and `.shapes` | [Straw topic](sling_launcher/lunar_slider_straw/README.md) |
| Straw ring reference | `sling_launcher.lunar_slider_straw.reference` | [Ring reference](sling_launcher/lunar_slider_straw/RING_REFERENCE.md) |
| Conveyor steady shapes | `sling_launcher.conveyor_loop.steady.report` and `.ratio_cases` | [README](sling_launcher/conveyor_loop/steady/README.md) |
| Architecture comparison | `sling_launcher.architecture_comparison.compare` and `.shape_comparison` | [README](sling_launcher/architecture_comparison/README.md) |
| Point-mass payout control | `sling_launcher.payout_control.report` | [README](sling_launcher/payout_control/README.md) |
| P1 terrain / tapered tether | `sling_launcher.sag_taper_trade.publication.calculate`, after `fetch_patch` | [Reproduction](sling_launcher/sag_taper_trade/publication/README.md#publication-assets-and-reproduction) |

Some retained arrays represent older parameter cases. Use their associated summary/configuration and historical generator version if exact reconstruction is required. The obsolete `bank_histories.npz` is superseded by the current scheduling outputs.

## Local recovery archives

`.local-backups/` is ignored and remains on the maintainer's computer. It contains full Git database snapshots taken before history cleanup, including historical arrays. These archives are recovery copies and are excluded from pushes. Local arrays can be copied directly from their original paths; historical versions can be extracted from an isolated restoration of a Git snapshot with `git show REV:path > output.npz`. Restore snapshots into a separate temporary repository to preserve the cleaned repository.

Terrain download URLs, ranges and hashes remain in each study's provenance records. The P1 terrain cache has its own [download instructions](sling_launcher/sag_taper_trade/publication/README.md#publication-assets-and-reproduction).
