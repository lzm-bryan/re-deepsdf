#!/usr/bin/env python3
"""Generate new planes from random latent codes using trained DeepSDF decoder"""

import torch
import numpy as np
import trimesh
import os
import sys

# Add DeepSDF to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source_code', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source_code', 'src', 'networks'))

from networks.deep_sdf_decoder import Decoder

def load_decoder(checkpoint_path, specs_path):
    """Load the trained decoder"""
    import json

    with open(specs_path, 'r') as f:
        specs = json.load(f)

    # Get network specs
    dims = specs['NetworkSpecs']['dims']
    dropout = tuple(specs['NetworkSpecs']['dropout']) if specs['NetworkSpecs']['dropout'] else ()
    dropout_prob = specs['NetworkSpecs'].get('dropout_prob', 0.2)
    norm_layers = tuple(specs['NetworkSpecs']['norm_layers']) if specs['NetworkSpecs']['norm_layers'] else ()
    latent_in = tuple(specs['NetworkSpecs']['latent_in']) if specs['NetworkSpecs']['latent_in'] else ()
    code_length = specs['CodeLength']
    weight_norm = specs['NetworkSpecs'].get('weight_norm', True)

    # Create decoder
    decoder = Decoder(
        latent_size=code_length,
        dims=dims,
        dropout=dropout,
        dropout_prob=dropout_prob,
        norm_layers=norm_layers,
        latent_in=latent_in,
        weight_norm=weight_norm
    )

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu')

    # Handle different checkpoint formats and DataParallel "module." prefix
    if 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint

    # Remove "module." prefix if present (DataParallel)
    new_state_dict = {}
    for k, v in state_dict.items():
        if k.startswith('module.'):
            new_state_dict[k[7:]] = v
        else:
            new_state_dict[k] = v

    decoder.load_state_dict(new_state_dict)
    decoder.eval()
    return decoder, code_length

def load_latent_stats(latent_path):
    """Load statistics from trained latent codes"""
    checkpoint = torch.load(latent_path, map_location='cpu')
    latent_codes = checkpoint['latent_codes']
    codes = torch.stack([latent_codes['weight'][i] for i in range(latent_codes['weight'].shape[0])])
    mean = codes.mean(dim=0)
    std = codes.std(dim=0)
    return mean, std

def sample_random_latent(code_length, stat=None):
    """Sample a random latent code from learned distribution"""
    if stat is not None:
        mean = stat[0].detach().cpu().numpy()
        std = stat[1].detach().cpu().numpy()
        latent = torch.from_numpy(np.random.normal(mean, std)).float().unsqueeze(0)
    else:
        latent = torch.randn(1, code_length) * 0.5
    return latent

def decode_mesh(decoder, latent, N=128, max_batch=2**18, range_min=-1.0, range_max=1.0):
    """Generate mesh from latent code using marching cubes"""
    from skimage import measure

    # Create grid
    x = np.linspace(range_min, range_max, N)
    y = np.linspace(range_min, range_max, N)
    z = np.linspace(range_min, range_max, N)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    coords = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)

    # Expand latent to match grid size
    latent_expanded = latent.expand(coords.shape[0], -1)

    # Combine latent and coordinates
    inputs = torch.cat([latent_expanded, torch.from_numpy(coords).float()], dim=1)

    # Batch prediction
    sdf_values = []
    for i in range(0, len(inputs), max_batch):
        batch = inputs[i:i+max_batch]
        with torch.no_grad():
            pred = decoder(batch)
        sdf_values.append(pred.cpu().numpy())

    sdf_values = np.concatenate(sdf_values, axis=0)
    sdf_grid = sdf_values.reshape(N, N, N)

    # Apply marching cubes - find a level within the data range
    level = 0.0
    sdf_min, sdf_max = sdf_grid.min(), sdf_grid.max()
    if sdf_min > 0:
        level = sdf_min + 0.01
    elif sdf_max < 0:
        level = sdf_max - 0.01

    try:
        spacing = ((range_max - range_min) / N, (range_max - range_min) / N, (range_max - range_min) / N)
        verts, faces, normals, values = measure.marching_cubes(
            sdf_grid, level=level, spacing=spacing
        )
        verts = verts + range_min

        mesh = trimesh.Trimesh(vertices=verts, faces=faces)
        return mesh
    except (ValueError, RuntimeError) as e:
        print(f"Marching cubes failed: {e}, sdf range: [{sdf_min:.4f}, {sdf_max:.4f}]")
        return None

def generate_new_planes(n=5, output_dir="generated_planes"):
    """Generate n new planes"""
    os.makedirs(output_dir, exist_ok=True)

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    decoder_path = os.path.join(base_dir, '..', 'models', 'ModelParameters', '600.pth')
    specs_path = os.path.join(base_dir, '..', 'configs', 'specs.json')
    latent_path = os.path.join(base_dir, '..', 'models', 'LatentCodes', '600.pth')

    # Load decoder
    print("Loading decoder...")
    decoder, code_length = load_decoder(decoder_path, specs_path)
    print(f"Decoder loaded. Code length: {code_length}")

    # Load latent stats
    print("Loading latent code statistics...")
    latent_mean, latent_std = load_latent_stats(latent_path)
    print(f"Latent stats: mean={latent_mean.mean():.6f}, std={latent_std.mean():.6f}")
    stat = (latent_mean, latent_std)

    # Generate random planes
    for i in range(n):
        print(f"Generating plane {i+1}/{n}...")

        latent = sample_random_latent(code_length, stat=stat)
        mesh = decode_mesh(decoder, latent)

        if mesh is not None:
            output_path = os.path.join(output_dir, f"generated_plane_{i+1:03d}.ply")
            mesh.export(output_path)
            print(f"  Saved: {output_path}")
            print(f"  Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
        else:
            print(f"  Failed to generate plane {i+1}")

    print(f"\nDone! Generated {n} new planes in {output_dir}/")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate new planes from random latent codes")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of planes to generate")
    parser.add_argument("-o", "--output", type=str, default="generated_planes",
                        help="Output directory")
    args = parser.parse_args()

    generate_new_planes(n=args.num, output_dir=args.output)
