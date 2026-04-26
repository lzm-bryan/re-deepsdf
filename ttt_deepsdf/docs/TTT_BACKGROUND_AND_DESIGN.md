# TTT Background And Design

## 1. What TTT means here

`TTT` here means `Test-Time Training` or `Test-Time Adaptation`: the model is
allowed to update a small set of parameters at inference time using the current
test sample itself.

Useful references:

- Test-Time Training with Self-Supervision for Generalization under
  Distribution Shifts
  - https://arxiv.org/abs/1909.13231
- Learning to (Learn at Test Time): RNNs with Expressive Hidden States
  - https://arxiv.org/abs/2407.04620

## 2. Why TTT is a good fit for DeepSDF

DeepSDF already performs a test-time optimization step in `reconstruct.py`:

- the decoder is fixed
- a shape-specific latent code is optimized for the current test instance

That means the project already contains a natural entry point for a TTT-style
idea.

## 3. Why plain latent optimization is not enough as an innovation point

If we only say "DeepSDF uses test-time latent optimization", that is true but
not novel for this homework extension.

To turn it into a clearer innovation point, we introduce an additional
adaptation module:

- `TTT Adapter`

This creates a new algorithmic comparison:

1. `test_mean`
   No per-instance adaptation. Use the mean latent code.
2. `test_opt`
   Optimize only the latent code.
3. `test_ttt_adapter`
   Optimize the latent code plus a tiny residual adapter at test time.

## 4. Proposed TTT adapter

The decoder remains frozen.

The test-time module is a tiny residual MLP:

- input:
  - `xyz` coordinates
  - base decoder SDF prediction
- output:
  - a residual correction term

Final prediction:

```text
sdf_final = sdf_decoder + sdf_adapter
```

This is intentionally small so that:

- the base pretrained decoder remains the main representation
- the TTT component is lightweight and explainable
- the comparison with plain latent optimization stays fair

## 5. Why this design is practical

This design avoids a large retraining project.

It works with the current completed airplane checkpoint:

- existing decoder checkpoint
- existing train/test splits
- existing SDF sampling format

So the innovation can be evaluated as a controlled extension rather than a full
new pipeline.

## 6. What should be measured

Primary quantitative comparison:

- baseline `test_mean` MAE
- baseline `test_opt` MAE
- new `test_ttt_adapter` MAE

Secondary observations:

- adaptation stability
- runtime cost per test shape
- whether TTT gains are consistent across many test instances or only a few

## 7. Risks

- The adapter may overfit if it is too large.
- If the adapter is too weak, it may not outperform latent-only optimization.
- If evaluation uses the exact same points for adaptation and scoring, the gain
  may be optimistic.

Recommended mitigation:

- keep adapter very small
- use regularization
- optionally separate adaptation points and evaluation points later

## 8. Practical claim for the homework

A reasonable homework claim is:

"We extend DeepSDF with an explicit test-time training module. Instead of
optimizing only the latent code, we also optimize a tiny residual adapter for
each test shape. This gives a more explicit TTT formulation and can be compared
directly against the original DeepSDF latent-optimization baseline."





