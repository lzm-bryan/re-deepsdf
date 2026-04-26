param(
    [string]$BaselineRoot = 'external_artifacts/baselines/sota_baselines_2026-04-25',
    [switch]$CloneRepos
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $BaselineRoot | Out-Null
foreach ($name in @('docs','envs','scripts','repos','data_manifests','runs','logs')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $BaselineRoot $name) | Out-Null
}

$repos = @(
    @{ Name='convolutional_occupancy_networks'; Url='https://github.com/autonomousvision/convolutional_occupancy_networks.git' },
    @{ Name='occupancy_networks'; Url='https://github.com/autonomousvision/occupancy_networks.git' },
    @{ Name='nksr'; Url='https://github.com/nv-tlabs/nksr.git' },
    @{ Name='POCO'; Url='https://github.com/valeoai/POCO.git' }
)

if ($CloneRepos) {
    foreach ($repo in $repos) {
        $dst = Join-Path (Join-Path $BaselineRoot 'repos') $repo.Name
        if (Test-Path -LiteralPath (Join-Path $dst '.git')) {
            Write-Output "repo_exists $($repo.Name) $dst"
        } else {
            git clone --depth 1 $repo.Url $dst
        }
    }
} else {
    Write-Output 'repo_clone_skipped'
}

$status = [ordered]@{
    updated_utc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    baseline_root = $BaselineRoot
    clone_repos = [bool]$CloneRepos
    repos = @{}
}
foreach ($repo in $repos) {
    $dst = Join-Path (Join-Path $BaselineRoot 'repos') $repo.Name
    $status.repos[$repo.Name] = [ordered]@{
        path = $dst
        present = (Test-Path -LiteralPath $dst)
    }
}
$status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $BaselineRoot 'deploy_status.local.json') -Encoding UTF8
Write-Output "prepared=$BaselineRoot"


