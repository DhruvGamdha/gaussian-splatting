# ==============================================================================
# Data Transfer Script - Nova to Windows
# ==============================================================================
# This script handles secure file transfers between Nova server and local Windows machine
# using SCP (Secure Copy Protocol)

# Configuration Variables
# ==============================================================================

# Remote server details
$RemoteUser = "dgamdha"
$RemoteHost = "nova.its.iastate.edu"
$RemoteServer = "$RemoteUser@$RemoteHost"

# Base paths
$RemoteBasePath = "/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting"
$LocalBasePath = "D:\ResearchDataCodes\Dhruv\Projects\others\gaussian_splatting"

# Project-specific paths (modify as needed for different projects)
$ProjectSubPath = "2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver1"
$ProjectName = "2025_jan_14"  # For general project transfers

# Constructed paths
$RemoteDataPath = "$RemoteBasePath/data"
$LocalDataPath = "$LocalBasePath\data"

# Specific transfer paths
$RemoteSubPath = "$RemoteDataPath/$ProjectSubPath"
$LocalSubPath = "$LocalDataPath\$($ProjectSubPath -replace '/', '\')"

# Transfer Functions
# ==============================================================================

function Transfer-LocalToRemote {
    param(
        [string]$LocalPath = "$LocalDataPath\$ProjectName\",
        [string]$RemotePath = "$RemoteDataPath"
    )
    
    Write-Host "Transferring from Local to Remote..." -ForegroundColor Green
    Write-Host "Source: $LocalPath" -ForegroundColor Yellow
    Write-Host "Destination: $RemoteServer`:$RemotePath" -ForegroundColor Yellow
    
    $command = "scp -r `"$LocalPath`" $RemoteServer`:$RemotePath"
    Write-Host "Command: $command" -ForegroundColor Cyan
    
    # Uncomment the line below to execute the transfer
    # Invoke-Expression $command
}

function Transfer-RemoteToLocal {
    param(
        [string]$RemotePath = $RemoteSubPath,
        [string]$LocalPath = $LocalSubPath
    )
    
    Write-Host "Transferring from Remote to Local..." -ForegroundColor Green
    Write-Host "Source: $RemoteServer`:$RemotePath" -ForegroundColor Yellow
    Write-Host "Destination: $LocalPath" -ForegroundColor Yellow
    
    # Ensure local directory exists
    $localDir = Split-Path $LocalPath -Parent
    if (!(Test-Path $localDir)) {
        Write-Host "Creating local directory: $localDir" -ForegroundColor Magenta
        New-Item -ItemType Directory -Path $localDir -Force | Out-Null
    }
    
    $command = "scp -r $RemoteServer`:$RemotePath `"$LocalPath`""
    Write-Host "Command: $command" -ForegroundColor Cyan
    
    # Execute the transfer
    Invoke-Expression $command
}

# Main Execution
# ==============================================================================

Write-Host "=== Data Transfer Script ===" -ForegroundColor Blue
Write-Host "Remote Server: $RemoteServer" -ForegroundColor White
Write-Host "Project: $ProjectName" -ForegroundColor White
Write-Host ""

# Choose transfer direction
$choice = Read-Host "Choose transfer direction: (1) Local to Remote, (2) Remote to Local, (3) Show paths only [1/2/3]"

switch ($choice) {
    "1" {
        Transfer-LocalToRemote
    }
    "2" {
        Transfer-RemoteToLocal
    }
    "3" {
        Write-Host "`nPath Configuration:" -ForegroundColor Blue
        Write-Host "Remote Base: $RemoteBasePath" -ForegroundColor White
        Write-Host "Local Base: $LocalBasePath" -ForegroundColor White
        Write-Host "Current Remote Path: $RemoteSubPath" -ForegroundColor White
        Write-Host "Current Local Path: $LocalSubPath" -ForegroundColor White
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

# Legacy commands (commented for reference)
# ==============================================================================
# Transfer Directory from Local to Remote
# scp -r D:\\ResearchDataCodes\\Dhruv\\Projects\\others\\gaussian_splatting\\data\\2025_jan_14\ dgamdha@nova.its.iastate.edu:/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data

# Transfer Directory from Remote to Local  
# scp -r dgamdha@nova.its.iastate.edu:/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/rawFrames/4_cubemap_combined/ver1 D:\ResearchDataCodes\Dhruv\Projects\others\gaussian_splatting\data\2025_jan_14\customFrames\vid_2\4_cubemap_combined\ver1