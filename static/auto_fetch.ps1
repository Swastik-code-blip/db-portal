# DB Portal - Auto Fetch & Save Hardware Info (PowerShell)
# Run: Right-click -> Run with PowerShell

$PORTAL_URL = "http://127.0.0.1:8000"

Write-Host "="*55 -ForegroundColor Cyan
Write-Host "  DB PORTAL - AUTO HARDWARE FETCHER (PowerShell)" -ForegroundColor Cyan
Write-Host "="*55 -ForegroundColor Cyan

# Fetch hardware info
$cpu        = (Get-WmiObject Win32_Processor).Name
$cores      = (Get-WmiObject Win32_Processor).NumberOfCores
$ram_bytes  = (Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory
$ram_gb     = [math]::Round($ram_bytes / 1GB, 1)
$serial     = (Get-WmiObject Win32_BIOS).SerialNumber
$os         = (Get-WmiObject Win32_OperatingSystem).Caption
$os_ver     = (Get-WmiObject Win32_OperatingSystem).Version
$gpu        = (Get-WmiObject Win32_VideoController).Name
$disk       = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$disk_gb    = [math]::Round($disk.Size / 1GB, 0)
$free_gb    = [math]::Round($disk.FreeSpace / 1GB, 1)
$board      = (Get-WmiObject Win32_BaseBoard).Product
$computer   = $env:COMPUTERNAME
$bios       = (Get-WmiObject Win32_BIOS).SMBIOSBIOSVersion
$mac        = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).MacAddress
$ip         = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object -First 1).IPAddress

Write-Host "`n  Computer : $computer"
Write-Host "  OS       : $os"
Write-Host "  CPU      : $cpu ($cores cores)"
Write-Host "  RAM      : $ram_gb GB"
Write-Host "  Disk C:  : $disk_gb GB (Free: $free_gb GB)"
Write-Host "  GPU      : $gpu"
Write-Host "  Serial   : $serial"
Write-Host "  MAC      : $mac"
Write-Host "  IP       : $ip"
Write-Host "="*55

Write-Host "`nENTER PORTAL LOGIN DETAILS:" -ForegroundColor Yellow
$username = Read-Host "  Username"
$password = Read-Host "  Password" -AsSecureString
$password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
$hw_id    = Read-Host "  Hardware ID (press Enter for '$computer')"
if (-not $hw_id) { $hw_id = $computer }
$location = Read-Host "  Location (e.g. Head Office)"
$hw_type  = Read-Host "  Type [Desktop]"
if (-not $hw_type) { $hw_type = "Desktop" }
$brand    = Read-Host "  Brand (e.g. Dell, HP)"
if (-not $brand) { $brand = "Unknown" }
$model    = Read-Host "  Model (press Enter for '$computer')"
if (-not $model) { $model = $computer }

Write-Host "`n  Sending to portal..." -ForegroundColor Cyan

$body = @{
    username = $username
    password = $password
    hardware = @{
        hw_id         = $hw_id
        hardware_type = $hw_type
        brand         = $brand
        model_name    = $model
        serial_number = if ($serial) { $serial } else { "$hw_id-SN" }
        location      = $location
        specifications = "$cpu, $ram_gb GB RAM, $disk_gb GB Storage"
        notes         = "Auto-fetched via PowerShell on $(Get-Date -Format 'yyyy-MM-dd') from $computer"
        properties    = @{
            "Computer Name"    = $computer
            "Operating System" = $os
            "OS Version"       = $os_ver
            "CPU"              = $cpu
            "CPU Cores"        = "$cores"
            "RAM"              = "$ram_gb GB"
            "Storage (C:)"     = "$disk_gb GB"
            "Free Space (C:)"  = "$free_gb GB"
            "GPU"              = $gpu
            "Serial Number"    = $serial
            "MAC Address"      = $mac
            "IP Address"       = $ip
            "Motherboard"      = $board
            "BIOS Version"     = $bios
        }
    }
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$PORTAL_URL/api/auto-fetch/" -Method POST -Body $body -ContentType "application/json"
    if ($response.success) {
        Write-Host "`n  SUCCESS! $($response.message)" -ForegroundColor Green
        Write-Host "  Hardware ID : $($response.hw_id)" -ForegroundColor Green
        Write-Host "  Action      : $($response.action.ToUpper())" -ForegroundColor Green
        Write-Host "`n  View at: $PORTAL_URL/hardware/" -ForegroundColor Cyan
    } else {
        Write-Host "`n  ERROR: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "`n  CANNOT CONNECT: $_" -ForegroundColor Red
    Write-Host "  Make sure portal is running at $PORTAL_URL" -ForegroundColor Yellow
}

Write-Host "`n" + "="*55
Read-Host "Press Enter to exit"
