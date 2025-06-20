# ==============================================================================
# Windows Run Scripts - Gaussian Splatting
# ==============================================================================
# Simple PowerShell script to run Python scripts with configurable paths

# Configuration Variables
# ==============================================================================

# Base paths
$BasePath = "C:\Users\dgamdha\work\Projects\others\gaussian_splatting"
$DataPath = "$BasePath\data"
$AccessoriesPath = "$BasePath\code_gaussian-splatting\accessories"

# Project configuration (modify as needed)
$ProjectPath = "onedrive_2023_12_13\type1"  # Adjust this path for your project structure
$InputFolder = "original"
$OutputFolder = "cubemap_combined\ver1"

# Script parameters
$ConfigFile = "$AccessoriesPath\win_combcube_multi_interme_config.txt"
$EquirectDir = "$DataPath\$ProjectPath\$InputFolder"
$OutDir = "$DataPath\$ProjectPath\$OutputFolder"
$StartIdx = 0
$EndIdx = 14
$NumIntermediate = 3
$VFov = 90
$OutSize = 512

# Script Execution
# ==============================================================================

Write-Host "=== Running Cubemap Multiple Intermediates ===" -ForegroundColor Green
Write-Host "Config: $ConfigFile" -ForegroundColor Yellow
Write-Host "Input: $EquirectDir" -ForegroundColor Yellow
Write-Host "Output: $OutDir" -ForegroundColor Yellow
Write-Host ""

# Create output directory if it doesn't exist
if (!(Test-Path $OutDir)) {
    Write-Host "Creating output directory..." -ForegroundColor Magenta
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}

# Run the Python script
python combinecubemap_multiple_intermediates.py `
    --config "$ConfigFile" `
    --equirect_dir "$EquirectDir" `
    --start_idx $StartIdx `
    --end_idx $EndIdx `
    --num_intermediate $NumIntermediate `
    --vfov $VFov `
    --out_size $OutSize `
    --out_dir "$OutDir"

Write-Host "Script execution completed!" -ForegroundColor Green

# Additional Scripts (uncomment to use)
# ==============================================================================

# Alternative script with different parameters
<#
python combinecubemap_multiple.py `
    --config "$AccessoriesPath\combcube_multi_config.txt" `
    --start_idx 20 `
    --end_idx 100 `
    --out_dir "$DataPath\2025_jan_14\customFrames\vid_2\rawFrames\4_cubemap_combined\ver4"
#>

