# Validate Dream Memory Ollama Version
# Run this to verify the setup

Write-Host "=== Dream Memory Ollama Validation ===" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# 1. Syntax check
Write-Host "[1/4] Checking Python syntax..." -ForegroundColor Yellow
try {
    Get-ChildItem -Filter *.py | ForEach-Object { 
        python -m py_compile $_.FullName 
    }
    Write-Host "  PASS: All Python files have valid syntax" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Syntax errors found" -ForegroundColor Red
    $ErrorCount++
}

# 2. Check for forbidden tokens
Write-Host ""
Write-Host "[2/4] Checking for forbidden tokens..." -ForegroundColor Yellow
$Forbidden = @( "OPENAI_API_KEY", "openai", "GEMINI_API_KEY", "google-genai" )
$FoundBad = $false

foreach ($token in $Forbidden) {
    $result = Get-ChildItem -Filter *.py | Select-String -Pattern $token -CaseSensitive:$false -Quiet
    if ($result) {
        Write-Host "  FAIL: Found '$token' in Python files" -ForegroundColor Red
        $FoundBad = $true
        $ErrorCount++
    }
}

# Check requirements.txt
$reqContent = Get-Content requirements.txt -Raw
foreach ($token in $Forbidden) {
    if ($reqContent -match $token) {
        Write-Host "  FAIL: Found '$token' in requirements.txt" -ForegroundColor Red
        $FoundBad = $true
        $ErrorCount++
    }
}

# Check README.md
$readmeContent = Get-Content README.md -Raw
foreach ($token in $Forbidden) {
    if ($readmeContent -match $token) {
        Write-Host "  FAIL: Found '$token' in README.md" -ForegroundColor Red
        $FoundBad = $true
        $ErrorCount++
    }
}

if (-not $FoundBad) {
    Write-Host "  PASS: No forbidden tokens found" -ForegroundColor Green
}

# 3. Check Ollama
Write-Host ""
Write-Host "[3/4] Checking Ollama..." -ForegroundColor Yellow
Write-Host "  Run: ollama list"
Write-Host ""
Write-Host "  Expected: qwen2.5vl:3b should be listed"
Write-Host "  If not found, run: ollama pull qwen2.5vl:3b"
Write-Host ""

# Try to get Ollama status
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  Ollama API: RESPONDING" -ForegroundColor Green
        $models = ($response.Content | ConvertFrom-Json).models
        $hasModel = $false
        foreach ($m in $models) {
            if ($m.name -match "qwen2.5vl") {
                $hasModel = $true
                Write-Host "  Model FOUND: $($m.name)" -ForegroundColor Green
            }
        }
        if (-not $hasModel) {
            Write-Host "  WARNING: qwen2.5vl model not found" -ForegroundColor Yellow
            Write-Host "  Run: ollama pull qwen2.5vl:3b" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  Ollama API: NOT RESPONDING" -ForegroundColor Red
    Write-Host "  Start Ollama: ollama serve" -ForegroundColor Yellow
}

# 4. Summary
Write-Host ""
Write-Host "[4/4] Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Changed files:"
Write-Host "    - config.py (VISION_BACKEND=ollama, no Gemini)"
Write-Host "    - analyzer.py (OllamaAnalyzer only)"
Write-Host "    - capture.py (removed numpy)"
Write-Host "    - request_watcher.py (single-flight logic)"
Write-Host "    - overlay.py (fixed geometry, coordinate mapping)"
Write-Host "    - main.py (fixed imports, F10 logic)"
Write-Host "    - requirements.txt (removed numpy, opencv)"
Write-Host "    - README.md (updated instructions)"
Write-Host ""

if ($ErrorCount -eq 0) {
    Write-Host "  VALIDATION PASSED!" -ForegroundColor Green
} else {
    Write-Host "  VALIDATION FAILED: $ErrorCount errors" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Run Command ===" -ForegroundColor Cyan
Write-Host "python main.py" -ForegroundColor White
Write-Host ""

Write-Host "=== Known Limitations ===" -ForegroundColor Cyan
Write-Host "  - Requires Ollama running locally"
Write-Host "  - Requires qwen2.5vl:3b model installed"
Write-Host "  - Speed depends on CPU/GPU/RAM"
Write-Host "  - Analysis takes 5-15 seconds per frame"
Write-Host ""
