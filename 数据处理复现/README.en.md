# Data Processing Archive

[中文](README.md) | [English](README.en.md)

This directory preserves historical notes for DeepSDF data preprocessing. It is
not the main reproduction entry point. For the base airplane experiment, start
from the repository root `README.en.md`; for TTT/LoRA experiments, start from
`ttt_deepsdf/README.md`.

## When To Use This Directory

Use this material when you need to:

- Understand how raw ShapeNet meshes can be converted into DeepSDF SDF samples.
- Reproduce preprocessing on a CPU-only or headless Linux server.
- Trace the external articles and dataset notes used during the project.
- Inspect archived web pages when the original references are unavailable.

Most users do not need this directory for normal inference, visualization, or
training with the prepared data artifacts.

## Files

| File | Purpose |
| --- | --- |
| `DeepSDF_CPU_服务器复现全流程.md` | General CPU-only server reproduction guide for DeepSDF preprocessing. Sensitive machine-specific details have been replaced with placeholders. |
| `数据集.txt` | Link to the archived dataset artifact used during this project. |
| `weixinhum-149218796-link.txt` | Original external article URL. Prefer this over mirrored HTML when possible. |
| `weixinhum-149218796-mirror.html` | Local mirror of the external article. It may contain encoding issues from the original fetch process. |
| `qq_38677322-110957634-0411185841185_0zaxv2h5.s0f.html` | Offline webpage backup retained for provenance. |

## Recommended Reading Order

1. Read `DeepSDF_CPU_服务器复现全流程.md` for the preprocessing workflow.
2. Use `weixinhum-149218796-link.txt` to verify the external reference.
3. Open the HTML backups only when offline access is needed.
4. If a mirrored page displays garbled text, treat the original URL as the
   authoritative reference.

## Privacy Note

The reproduction guide intentionally avoids publishing real IP addresses,
private key paths, usernames, or machine-specific absolute paths. Replace the
placeholders with values from your own environment when running the commands.
