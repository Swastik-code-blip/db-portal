# DB Portal - Auto Fetch & Save Hardware Info (PowerShell)
# Run: Right-click -> Run with PowerShell

$PORTAL_URL = "https://web-production-d8992.up.railway.app"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  DB PORTAL - AUTO HARDWARE FETCHER (PowerShell)" -ForegroundColor Cyan
Write-Host "  Fetching system info automatically..." -ForegroundColor Gray
Write-Host "====================================================" -ForegroundColor Cyan

# Auto fetch everything
$cpu       = (Get-WmiObject Win32_Processor).Name
$cores     = (Get-WmiObject Win32_Processor).NumberOfCores
$ram_bytes = (Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory
$ram_gb    = [math]::Round($ram_bytes / 1GB, 1)
$serial    = (Get-WmiObject Win32_BIOS).SerialNumber
$os        = (Get-WmiObject Win32_OperatingSystem).Caption
$os_ver    = (Get-WmiObject Win32_OperatingSystem).Version
$gpu       = (Get-WmiObject Win32_VideoController | Select-Object -First 1).Name
$disk      = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$disk_gb   = [math]::Round($disk.Size / 1GB, 0)
$free_gb   = [math]::Round($disk.FreeSpace / 1GB, 1)
$board     = (Get-WmiObject Win32_BaseBoard).Product
$bios      = (Get-WmiObject Win32_BIOS).SMBIOSBIOSVersion
$computer  = $env:COMPUTERNAME
$brand_raw = (Get-WmiObject Win32_ComputerSystem).Manufacturer
$model_raw = (Get-WmiObject Win32_ComputerSystem).Model
$arch      = $env:PROCESSOR_ARCHITECTURE

# Clean up brand
$brand = $brand_raw
if (-not $brand -or $brand -eq "System manufacturer" -or $brand -eq "To Be Filled By O.E.M.") {
    $brand = (Get-WmiObject Win32_BaseBoard).Manufacturer
}
if (-not $brand -or $brand -eq "To Be Filled By O.E.M.") { $brand = "Assembled" }

# Clean up model
$model = $model_raw
if (-not $model -or $model -eq "System Product Name" -or $model -eq "To Be Filled By O.E.M.") {
    $model = $computer
}

# Detect hardware type from chassis
$hw_type = "Desktop"
try {
    $chassis = (Get-WmiObject Win32_SystemEnclosure).ChassisTypes
    if ($chassis -match "8|9|10|11|12|14|18|21") { $hw_type = "Laptop" }
    elseif ($chassis -match "17|23") { $hw_type = "Server" }
} catch {}

# MAC and IP
try {
    $mac = (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).MacAddress
    $ip  = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object -First 1).IPAddress
} catch {
    $mac = "N/A"; $ip = "N/A"
}

# Print auto-detected info
Write-Host "`n  AUTO-DETECTED:" -ForegroundColor Yellow
Write-Host "  Computer Name : $computer"
Write-Host "  Hardware Type : $hw_type"
Write-Host "  Brand         : $brand"
Write-Host "  Model         : $model"
Write-Host "  OS            : $os"
Write-Host "  CPU           : $cpu ($cores cores)"
Write-Host "  RAM           : $ram_gb GB"
Write-Host "  Storage C:    : $disk_gb GB (Free: $free_gb GB)"
Write-Host "  GPU           : $gpu"
Write-Host "  Serial No     : $serial"
Write-Host "  MAC Address   : $mac"
Write-Host "  IP Address    : $ip"
Write-Host "====================================================" -ForegroundColor Cyan

# Ask user for required info
Write-Host "`n  PLEASE FILL IN:" -ForegroundColor Yellow

$username = Read-Host "  Portal Username"
$pwd_sec  = Read-Host "  Portal Password" -AsSecureString
$password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pwd_sec))

$hw_id_suggest = $computer.ToUpper()
$hw_id_input   = Read-Host "  Hardware ID [$hw_id_suggest] (press Enter to use)"
$hw_id         = if ($hw_id_input) { $hw_id_input } else { $hw_id_suggest }

$location = ""
while (-not $location) {
    $location = Read-Host "  Location (e.g. Head Office, Bhopal)"
    if (-not $location) { Write-Host "  Location is required!" -ForegroundColor Red }
}

# Price — always ask
$price_input = Read-Host "  Purchase Price in Rs (e.g. 45000) press Enter to skip"
$price = if ($price_input) { $price_input } else { "0" }

# Purchase date
$date_input = Read-Host "  Purchase Date (YYYY-MM-DD) press Enter for today"
$purchase_date = if ($date_input) { $date_input } else { (Get-Date -Format "yyyy-MM-dd") }

# If serial not found, ask
if (-not $serial -or $serial -eq "N/A" -or $serial -eq "To Be Filled By O.E.M.") {
    $serial = Read-Host "  Serial Number (could not auto-detect, please enter)"
    if (-not $serial) { $serial = "$hw_id-SN" }
}

# Confirm type and brand
$type_input = Read-Host "  Hardware Type detected as '$hw_type' - press Enter to keep or type new"
if ($type_input) { $hw_type = $type_input }

$brand_input = Read-Host "  Brand detected as '$brand' - press Enter to keep or type new"
if ($brand_input) { $brand = $brand_input }

Write-Host "`n  Sending to portal..." -ForegroundColor Cyan

$body = @{
    username = $username
    password = $password
    hardware = @{
        hw_id          = $hw_id
        hardware_type  = $hw_type
        brand          = $brand
        model_name     = $model
        serial_number  = $serial
        location       = $location
        price          = $price
        purchase_date  = $purchase_date
        specifications = "$cpu, $ram_gb GB RAM, $disk_gb GB Storage"
        notes          = "Auto-fetched via PowerShell on $(Get-Date -Format 'yyyy-MM-dd') from $computer"
        properties     = @{
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
            "Architecture"     = $arch
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

Write-Host "`n====================================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
