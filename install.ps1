# Chronos Protocol MCP Server Installation Script
# This script sets up the chronos-protocol MCP server for centralized use across all projects

param(
    [string]$DataDir = "",
    [switch]$SkipInstall = $false
)

Write-Host "🚀 Chronos Protocol MCP Server Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if we're in the correct directory
$currentDir = Get-Location
$expectedPath = "chronos-protocol"
if (-not $currentDir.Path.EndsWith($expectedPath)) {
    Write-Host "❌ Please run this script from the chronos-protocol directory" -ForegroundColor Red
    exit 1
}

# Set default DataDir if not provided - use current directory + chronos-data
if ([string]::IsNullOrEmpty($DataDir)) {
    $DataDir = Join-Path $currentDir.Path "chronos-data"
    Write-Host "📁 Using default data directory: $DataDir" -ForegroundColor Yellow
}

# Step 1: Install Python dependencies
if (-not $SkipInstall) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "pip install failed"
        }
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
        exit 1
    }

    # Step 2: Install package in editable mode
    Write-Host "📦 Installing chronos-protocol package..." -ForegroundColor Yellow
    try {
        pip install -e .
        if ($LASTEXITCODE -ne 0) {
            throw "pip install -e . failed"
        }
        Write-Host "✅ Package installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install package: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Create chronos-data directory
Write-Host "📁 Creating centralized chronos-data directory..." -ForegroundColor Yellow
try {
    $dataPath = $DataDir
    if (-not (Test-Path $dataPath)) {
        New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
        Write-Host "✅ Data directory created: $dataPath" -ForegroundColor Green
    } else {
        Write-Host "✅ Data directory already exists: $dataPath" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to create data directory: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Test server startup
Write-Host "🧪 Testing server startup..." -ForegroundColor Yellow
try {
    $null = python -m chronos_protocol --data-dir "$dataPath" --help 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Server startup test failed"
    }
    Write-Host "✅ Server startup test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Server startup test failed: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Generate MCP configuration
Write-Host "⚙️ Generating MCP configuration..." -ForegroundColor Yellow
$absoluteDataPath = (Get-Item $dataPath).FullName
$mcpConfig = @{
    mcpServers = @{
        "chronos-protocol" = @{
            command = "python"
            args = @("-m", "chronos_protocol", "--data-dir", $absoluteDataPath)
        }
    }
} | ConvertTo-Json -Depth 3

Write-Host "📋 MCP Configuration for Cursor:" -ForegroundColor Cyan
Write-Host $mcpConfig -ForegroundColor White

# Save configuration to file
$configPath = "mcp-config.json"
$mcpConfig | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "✅ MCP configuration saved to: $configPath" -ForegroundColor Green

# Step 6: Validate installation
Write-Host "✅ Validating installation..." -ForegroundColor Yellow

# Check if package is importable
try {
    python -c "import chronos_protocol; print('✅ Package import successful')"
    if ($LASTEXITCODE -ne 0) {
        throw "Package import failed"
    }
} catch {
    Write-Host "❌ Package import test failed: $_" -ForegroundColor Red
    exit 1
}

# Check data directory permissions
try {
    $testFile = Join-Path $absoluteDataPath "test_write.tmp"
    "test" | Out-File -FilePath $testFile -Encoding UTF8
    if (Test-Path $testFile) {
        Remove-Item $testFile -Force
        Write-Host "✅ Data directory write permissions verified" -ForegroundColor Green
    } else {
        throw "Test file was not created"
    }
} catch {
    Write-Host "❌ Data directory write test failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy the MCP configuration above to your Cursor settings" -ForegroundColor White
Write-Host "2. Restart Cursor to reload MCP settings" -ForegroundColor White
Write-Host "3. Check 'MCP & Integrations' settings - you should see 9 chronos-protocol tools" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Configuration Details:" -ForegroundColor Cyan
Write-Host "- Data Directory: $absoluteDataPath" -ForegroundColor White
Write-Host "- All activity logs will be centralized in this location" -ForegroundColor White
Write-Host "- Accessible from any project directory" -ForegroundColor White
Write-Host ""
Write-Host "🛠️ Troubleshooting:" -ForegroundColor Cyan
Write-Host "- If tools don't appear, check Cursor's MCP logs" -ForegroundColor White
Write-Host "- Ensure Python is in your PATH" -ForegroundColor White
Write-Host "- Verify the data directory path is correct" -ForegroundColor White
Write-Host ""
Write-Host "Configuration file saved as: $configPath" -ForegroundColor Yellow
