#!/usr/bin/env python3
from pathlib import Path

src = Path("external_artifacts/remote_deepsdf_setup/DeepSDF/train_deep_sdf.py")
text = src.read_text(encoding="utf-8")

insert = r'''

def curriculum_linear(epoch, num_epochs, start, end):
    if num_epochs <= 1:
        return float(end)
    progress = max(0.0, min(1.0, float(epoch - 1) / float(num_epochs - 1)))
    return float(start) + progress * (float(end) - float(start))
'''
text = text.replace(
    "\n\ndef main_function(experiment_directory, continue_from, batch_split):",
    insert + "\n\ndef main_function(experiment_directory, continue_from, batch_split):",
)

text = text.replace(
    "    enforce_minmax = True\n\n    do_code_regularization",
    '''    enforce_minmax = True

    curriculum_specs = get_spec_with_default(specs, "CurriculumFullish", {})
    curriculum_enabled = bool(curriculum_specs.get("Enabled", False))
    curriculum_eps_start = float(curriculum_specs.get("EpsilonStart", 0.01))
    curriculum_eps_end = float(curriculum_specs.get("EpsilonEnd", 0.001))
    curriculum_hard_start = float(curriculum_specs.get("HardWeightStart", 1.0))
    curriculum_hard_end = float(curriculum_specs.get("HardWeightEnd", 2.5))
    curriculum_semi_start = float(curriculum_specs.get("SemiHardWeightStart", 1.0))
    curriculum_semi_end = float(curriculum_specs.get("SemiHardWeightEnd", 1.5))
    curriculum_easy_start = float(curriculum_specs.get("EasyWeightStart", 1.0))
    curriculum_easy_end = float(curriculum_specs.get("EasyWeightEnd", 0.8))
    curriculum_near_surface = float(curriculum_specs.get("NearSurfaceBand", 0.02))
    if curriculum_enabled:
        logging.info(
            "CurriculumDeepSDF-fullish enabled: epsilon {}->{}, hard {}->{}, semi {}->{}, easy {}->{}, near_surface={}".format(
                curriculum_eps_start,
                curriculum_eps_end,
                curriculum_hard_start,
                curriculum_hard_end,
                curriculum_semi_start,
                curriculum_semi_end,
                curriculum_easy_start,
                curriculum_easy_end,
                curriculum_near_surface,
            )
        )

    do_code_regularization''',
)

text = text.replace(
    '        logging.info("epoch {}...".format(epoch))\n\n        decoder.train()',
    '''        logging.info("epoch {}...".format(epoch))
        curriculum_epsilon = curriculum_linear(epoch, num_epochs, curriculum_eps_start, curriculum_eps_end) if curriculum_enabled else 0.0
        curriculum_hard_weight = curriculum_linear(epoch, num_epochs, curriculum_hard_start, curriculum_hard_end) if curriculum_enabled else 1.0
        curriculum_semi_weight = curriculum_linear(epoch, num_epochs, curriculum_semi_start, curriculum_semi_end) if curriculum_enabled else 1.0
        curriculum_easy_weight = curriculum_linear(epoch, num_epochs, curriculum_easy_start, curriculum_easy_end) if curriculum_enabled else 1.0
        if curriculum_enabled:
            logging.info(
                "curriculum fullish epsilon {:.5f}, weights hard/semi/easy {:.3f}/{:.3f}/{:.3f}".format(
                    curriculum_epsilon,
                    curriculum_hard_weight,
                    curriculum_semi_weight,
                    curriculum_easy_weight,
                )
            )

        decoder.train()''',
)

old = "                chunk_loss = loss_l1(pred_sdf, sdf_gt[i]) / num_sdf_samples"
old_cuda = "                chunk_loss = loss_l1(pred_sdf, sdf_gt[i].cuda()) / num_sdf_samples"
new = r'''                if curriculum_enabled:
                    target_sdf = sdf_gt[i].to(pred_sdf.device)
                    abs_error = torch.abs(pred_sdf - target_sdf)
                    epsilon_loss = torch.clamp(abs_error - curriculum_epsilon, min=0.0)

                    pred_detached = pred_sdf.detach()
                    target_detached = target_sdf.detach()
                    hard_mask = (pred_detached * target_detached) < 0
                    near_mask = torch.abs(target_detached) <= curriculum_near_surface
                    semi_mask = (~hard_mask) & near_mask
                    easy_mask = (~hard_mask) & (~near_mask)

                    weights = torch.ones_like(epsilon_loss) * curriculum_easy_weight
                    weights = torch.where(semi_mask, torch.ones_like(weights) * curriculum_semi_weight, weights)
                    weights = torch.where(hard_mask, torch.ones_like(weights) * curriculum_hard_weight, weights)
                    weights = weights / torch.clamp(torch.mean(weights), min=1e-8)
                    chunk_loss = torch.sum(epsilon_loss * weights) / num_sdf_samples
                else:
                    target_sdf = sdf_gt[i].to(pred_sdf.device)
                    chunk_loss = loss_l1(pred_sdf, target_sdf) / num_sdf_samples'''
if old in text:
    text = text.replace(old, new)
elif old_cuda in text:
    text = text.replace(old_cuda, new)
else:
    raise SystemExit("Expected DeepSDF loss line not found; refusing to generate patched trainer.")

Path("external_artifacts/baselines/curriculum_deepsdf_fullish_2026-04-26/scripts/train_deep_sdf_curriculum_fullish.generated.py").write_text(text, encoding="utf-8")

