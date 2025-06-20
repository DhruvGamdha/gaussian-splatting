# ==============================================================================
# Data Transfer Script - Windows to Nova
# ==============================================================================
# This script handles secure file transfers from local Windows machine to Nova server
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
$ProjectSubPath = "2025_jan_14\customFrames\vid_2\4_cubemap_combined\ver1"
$ProjectName = "2025_jan_14"  # For general project transfers

# Constructed paths
$RemoteDataPath = "$RemoteBasePath/data"
$LocalDataPath = "$LocalBasePath\data"

# Specific transfer paths
$LocalSourcePath = "$LocalDataPath\$ProjectSubPath"
$RemoteDestPath = "$RemoteDataPath/$($ProjectSubPath -replace '\\', '/')"

# Transfer Functions
# ==============================================================================

function Transfer-LocalToRemote {
    param(
        [string]$LocalPath = $LocalSourcePath,
        [string]$RemotePath = $RemoteDestPath
    )
    
    Write-Host "Transferring from Local to Remote..." -ForegroundColor Green
    Write-Host "Source: $LocalPath" -ForegroundColor Yellow
    Write-Host "Destination: $RemoteServer`:$RemotePath" -ForegroundColor Yellow
    
    # Check if local source exists
    if (!(Test-Path $LocalPath)) {
        Write-Host "Error: Local source path does not exist: $LocalPath" -ForegroundColor Red
        return
    }
    
    $command = "scp -r `"$LocalPath`" $RemoteServer`:$RemotePath"
    Write-Host "Command: $command" -ForegroundColor Cyan
    
    # Execute the transfer
    Invoke-Expression $command
}

function Transfer-ProjectToRemote {
    param(
        [string]$LocalPath = "$LocalDataPath\$ProjectName\",
        [string]$RemotePath = "$RemoteDataPath"
    )
    
    Write-Host "Transferring entire project from Local to Remote..." -ForegroundColor Green
    Write-Host "Source: $LocalPath" -ForegroundColor Yellow
    Write-Host "Destination: $RemoteServer`:$RemotePath" -ForegroundColor Yellow
    
    # Check if local source exists
    if (!(Test-Path $LocalPath)) {
        Write-Host "Error: Local project path does not exist: $LocalPath" -ForegroundColor Red
        return
    }
    
    $command = "scp -r `"$LocalPath`" $RemoteServer`:$RemotePath"
    Write-Host "Command: $command" -ForegroundColor Cyan
    
    # Uncomment the line below to execute the transfer
    # Invoke-Expression $command
}

function Show-TransferPaths {
    Write-Host "`nPath Configuration:" -ForegroundColor Blue
    Write-Host "Local Base: $LocalBasePath" -ForegroundColor White
    Write-Host "Remote Base: $RemoteBasePath" -ForegroundColor White
    Write-Host "`nSpecific Transfer:" -ForegroundColor Blue
    Write-Host "Local Source: $LocalSourcePath" -ForegroundColor White
    Write-Host "Remote Destination: $RemoteDestPath" -ForegroundColor White
    Write-Host "`nProject Transfer:" -ForegroundColor Blue
    Write-Host "Local Project: $LocalDataPath\$ProjectName\" -ForegroundColor White
    Write-Host "Remote Data Dir: $RemoteDataPath" -ForegroundColor White
}

# Main Execution
# ==============================================================================

Write-Host "=== Windows to Nova Transfer Script ===" -ForegroundColor Blue
Write-Host "Remote Server: $RemoteServer" -ForegroundColor White
Write-Host "Project: $ProjectName" -ForegroundColor White
Write-Host ""

# Choose transfer type
$choice = Read-Host "Choose transfer type: (1) Specific files/folders, (2) Entire project, (3) Show paths only [1/2/3]"

switch ($choice) {
    "1" {
        Transfer-LocalToRemote
    }
    "2" {
        Transfer-ProjectToRemote
    }
    "3" {
        Show-TransferPaths
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

# Legacy commands (commented for reference)
# ==============================================================================
# Transfer specific directory from Local to Remote
# scp -r D:\ResearchDataCodes\Dhruv\Projects\others\gaussian_splatting\data\2025_jan_14\customFrames\vid_2\4_cubemap_combined\ver1 dgamdha@nova.its.iastate.edu:/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data/2025_jan_14/customFrames/vid_2/4_cubemap_combined/ver1

# Transfer entire project from Local to Remote
# scp -r D:\ResearchDataCodes\Dhruv\Projects\others\gaussian_splatting\data\2025_jan_14\ dgamdha@nova.its.iastate.edu:/work/mech-ai-scratch/dgamdha/projects/sdat/code/gaussian-splatting/data