# Data Processing Archive

[中文](README.md) | [English](README.en.md)

This directory is a **historical archive for data-processing notes and reference links**. It is not the main reproduction entry point.

If you are reading this repository for the first time, start from the root `README.md` or `README.en.md` to reproduce the base DeepSDF airplane experiment. If you are interested in the TTT/LoRA experiments, go directly to `ttt_deepsdf/README.md`. This folder is useful when you need to trace data provenance, inspect older CPU/server processing notes, or recover the external references used during the project.

## When To Read This Folder

- You want to understand the early data-processing and server reproduction workflow.
- You want to find the dataset notes or web references used at that time.
- You want to check whether the saved offline webpage backups are still usable.

For normal model reproduction and result inspection, you usually do not need to read this directory first.

## Files

- `DeepSDF_CPU_服务器复现全流程.md`
  - Notes for reproducing DeepSDF in a CPU environment and on a server.

- `qq_38677322-110957634-0411185841185_0zaxv2h5.s0f.html`
  - A previously saved local webpage backup. Open it in a browser if needed.

- `weixinhum-149218796-mirror.html`
  - A local mirror generated from the target article.
  - Note: because of source-site anti-scraping and transcoding behavior, the mirrored page may contain garbled Chinese text.

- `weixinhum-149218796-link.txt`
  - The original article link. This is the most stable reference and should be kept.

- `数据集.txt`
  - A local text note related to dataset records.

## Recommended Order

1. Read `DeepSDF_CPU_服务器复现全流程.md` when you need the original process notes.
2. Read `weixinhum-149218796-link.txt` when tracing external references.
3. Open `weixinhum-149218796-mirror.html` or the other HTML backup only when you need offline access to the old pages.
4. If an HTML file shows garbled text, treat the original link in the txt file as the reliable source.

## Common Case

- `weixinhum-149218796-mirror.html` still shows garbled Chinese text:
  - This is usually caused by encoding loss during the original fetch/transcoding step, not by the local Markdown file.
  - Keeping `weixinhum-149218796-link.txt` as the stable source is the safest option.
