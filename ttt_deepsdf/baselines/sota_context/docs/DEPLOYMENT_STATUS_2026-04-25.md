# Baseline Deployment Status

Updated: 2026-04-25, Asia/Singapore.

## Locations

- Local: `external_artifacts/baselines/sota_baselines_2026-04-25`
- Server 30622: `external_artifacts/baselines/sota_baselines_2026-04-25`
- Server 30446: `external_artifacts/baselines/sota_baselines_2026-04-25`

## Code Repositories

All four baseline repositories are staged locally and on both servers.

| Repo | Source | Commit |
| --- | --- | --- |
| `convolutional_occupancy_networks` | `https://github.com/autonomousvision/convolutional_occupancy_networks.git` | `838bea5` |
| `occupancy_networks` | `https://github.com/autonomousvision/occupancy_networks.git` | `406f794` |
| `nksr` | `https://github.com/nv-tlabs/nksr.git` | `14d7567` |
| `POCO` | `https://github.com/valeoai/POCO.git` | `7f85ace` |

Notes:

- Initial direct GitHub clone attempts from the servers were unstable.
- Retried with safer Git settings: HTTP/1.1, shallow clone, blob filtering,
  timeout/retry logic, and proxy fallbacks.
- Final successful clones on both servers came through direct GitHub after the
  safer settings were applied, so no SFTP repo copy is needed for normal use.
- Earlier incomplete server-side clone folders were preserved as
  `*.incomplete.<timestamp>` inside the baseline `repos` directory.

## Data Manifests

The manifest generator now points to actual `SurfaceSamples` paths.

| Class | Official test count | Found surface PLY files |
| --- | ---: | ---: |
| airplane | 456 | 456 |
| chair | 832 | 832 |
| lamp | 213 | 213 |

Manifest files:

- `data_manifests/airplane_official_full_test_inputs.csv`
- `data_manifests/chair_official_full_test_inputs.csv`
- `data_manifests/lamp_official_full_test_inputs.csv`
- `data_manifests/manifest.json`

## Environment Status

Conda environment YAMLs are prepared but not installed yet:

- `envs/convonet_environment.yml`
- `envs/nksr_environment.yml`
- `envs/poco_environment.yml`

No new GPU experiments were started during staging. The active full-Chamfer
queue should finish before any new baseline smoke test is launched unless the
user explicitly assigns an idle server.

## Recommended Next Actions

When a server becomes idle:

1. Run internal DeepSDF controls first:
   - latent-only high-iteration baseline;
   - latent-only best-of-2;
   - last-layer TTT.
2. Install one external baseline environment at a time, starting with ConvONet
   or NKSR.
3. Use lamp for the first external smoke test because it is the smallest class.
4. Evaluate all generated meshes with the existing local/DeepSDF Chamfer
   evaluator to keep the metric scale consistent.




