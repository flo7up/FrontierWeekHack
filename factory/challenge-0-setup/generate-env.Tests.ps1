$ErrorActionPreference = 'Stop'
$testState = @{ Scenario = 'success'; Calls = [System.Collections.Generic.List[object]]::new() }
$generator = Join-Path $PSScriptRoot 'generate-env.ps1'
$tempDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
$null = New-Item -ItemType Directory -Path $tempDirectory
$outputPath = Join-Path $tempDirectory '.env'

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        throw $Message
    }
}

function Assert-Fails {
    param([scriptblock]$Action, [string]$MessagePattern)
    try {
        & $Action
    }
    catch {
        Assert-True ($_.Exception.Message -like $MessagePattern) "Unexpected failure: $($_.Exception.Message)"
        return
    }
    throw "Expected failure matching: $MessagePattern"
}

function az {
    $testState.Calls.Add(@($args))
    Set-Variable -Name LASTEXITCODE -Value 0 -Scope 1
    if ($testState.Scenario -eq 'cli-failure') {
        Set-Variable -Name LASTEXITCODE -Value 1 -Scope 1
        return '{}'
    }
    if ($testState.Scenario -eq 'invalid-json') {
        return 'not-json'
    }
    $command = $args -join ' '
    switch -Wildcard ($command) {
        'account show *' {
            $result = @{ id = 'resolved-subscription' }
        }
        'cognitiveservices account list *' {
            $result = @(@{
                name = 'existing-foundry'; kind = 'AIServices'
                properties = @{ provisioningState = 'Succeeded'; endpoint = 'https://existing-foundry.cognitiveservices.azure.com/' }
            })
            if ($testState.Scenario -eq 'no-foundry') { $result = @() }
            if ($testState.Scenario -eq 'failed-foundry') { $result[0].properties.provisioningState = 'Failed' }
            if ($testState.Scenario -in @('multiple-foundry', 'multiple-all')) {
                $result += @{ name = 'other-foundry'; kind = 'AIServices' }
            }
        }
        'cognitiveservices account project show *' {
            $endpoint = 'https://existing-foundry.services.ai.azure.com/api/projects/factory-project'
            if ($testState.Scenario -eq 'missing-endpoint') { $endpoint = $null }
            $result = @{ properties = @{ endpoints = @{ 'AI Foundry API' = $endpoint } } }
        }
        'cognitiveservices account deployment list *' {
            $result = @(@{ name = 'custom-model'; properties = @{ provisioningState = 'Succeeded' } })
            if ($testState.Scenario -eq 'failed-model') { $result[0].properties.provisioningState = 'Failed' }
            if ($testState.Scenario -in @('multiple-models', 'multiple-all')) {
                $result += @{ name = 'other-model'; properties = @{ provisioningState = 'Succeeded' } }
            }
        }
        'resource list *' {
            $result = @(@{ name = 'existing-insights' })
            if ($testState.Scenario -in @('multiple-insights', 'multiple-all')) {
                $result += @{ name = 'other-insights' }
            }
        }
        'resource show *' {
            $result = @{ properties = @{ ConnectionString = 'InstrumentationKey=test-key;IngestionEndpoint=https://example.test/'; InstrumentationKey = 'test-key' } }
            if ($testState.Scenario -eq 'missing-insights') { $result.properties.ConnectionString = $null }
        }
        default { throw "Unexpected Azure command: $command" }
    }
    ConvertTo-Json -InputObject $result -Depth 8 -Compress
}

try {
    $parameters = @{ ResourceGroup = 'existing-rg'; SubscriptionId = 'requested-subscription'; OutputPath = $outputPath }
    $messages = @(& $generator @parameters 6>&1)
    $expected = @(
        'AZURE_SUBSCRIPTION_ID="resolved-subscription"'
        'RESOURCE_GROUP="existing-rg"'
        'FOUNDRY_RESOURCE_NAME="existing-foundry"'
        'PROJECT_NAME="factory-project"'
        'FOUNDRY_ENDPOINT="https://existing-foundry.cognitiveservices.azure.com/"'
        'PROJECT_CONNECTION_STRING="https://existing-foundry.services.ai.azure.com/api/projects/factory-project"'
        'MODEL_DEPLOYMENT_NAME="custom-model"'
        'APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=test-key;IngestionEndpoint=https://example.test/"'
        'APPINSIGHTS_INSTRUMENTATION_KEY="test-key"'
        'AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING="true"'
        'OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="true"'
    )
    $actual = [System.IO.File]::ReadAllLines($outputPath)
    Assert-True (@(Compare-Object $expected $actual).Count -eq 0) 'Generated settings do not match the deployment contract.'
    Assert-True ([System.IO.File]::ReadAllBytes($outputPath)[0] -eq 65) 'Output must be UTF-8 without a BOM.'
    Assert-True (($messages -join "`n") -notmatch 'test-key') 'Connection details leaked to output.'
    Assert-True (($testState.Calls[0] -join ' ') -like '*--subscription requested-subscription*') 'Explicit subscription was not used.'
    foreach ($call in ($testState.Calls | Select-Object -Skip 1)) {
        Assert-True (($call -join ' ') -like '*--subscription resolved-subscription*') 'A resource read was not scoped to the resolved subscription.'
    }
    Write-Host 'PASS: complete configuration, discovered model name, subscription scoping, encoding, no secret output'

    $before = [System.IO.File]::ReadAllText($outputPath)
    $callCount = $testState.Calls.Count
    Assert-Fails { & $generator @parameters } '*File already exists*'
    Assert-True ($testState.Calls.Count -eq $callCount) 'Existing file should be rejected before Azure calls.'
    Assert-True ([System.IO.File]::ReadAllText($outputPath) -eq $before) 'Existing configuration was changed.'
    Write-Host 'PASS: existing file protected by default'

    $failureCases = @(
        @{ Scenario = 'cli-failure'; Message = '*Azure CLI failed*' }
        @{ Scenario = 'invalid-json'; Message = '*invalid JSON*' }
        @{ Scenario = 'no-foundry'; Message = '*Azure CLI returned no data*' }
        @{ Scenario = 'failed-foundry'; Message = '*Foundry account has not successfully provisioned*' }
        @{ Scenario = 'multiple-foundry'; Message = '*FoundryResourceName*' }
        @{ Scenario = 'multiple-models'; Message = '*ModelDeploymentName*' }
        @{ Scenario = 'multiple-insights'; Message = '*AppInsightsName*' }
        @{ Scenario = 'failed-model'; Message = '*model deployment has not successfully provisioned*' }
        @{ Scenario = 'missing-endpoint'; Message = '*PROJECT_CONNECTION_STRING*' }
        @{ Scenario = 'missing-insights'; Message = '*APPLICATIONINSIGHTS_CONNECTION_STRING*' }
    )
    foreach ($failureCase in $failureCases) {
        $testState.Scenario = $failureCase.Scenario
        Assert-Fails { & $generator @parameters -Force } $failureCase.Message
        Assert-True ([System.IO.File]::ReadAllText($outputPath) -eq $before) "Configuration changed on $($failureCase.Scenario)."
        Write-Host "PASS: $($failureCase.Scenario) leaves existing configuration untouched"
    }

    $testState.Scenario = 'multiple-all'
    & $generator @parameters -Force -FoundryResourceName 'existing-foundry' `
        -ModelDeploymentName 'custom-model' -AppInsightsName 'existing-insights'
    Assert-True ([System.IO.File]::ReadAllText($outputPath) -eq $before) 'Explicit resource selectors did not recover the same configuration.'
    Write-Host 'PASS: explicit selectors resolve ambiguity and Force permits replacement'

    $testState.Scenario = 'success'
    $temporarySetup = Join-Path $tempDirectory 'factory/challenge-0-setup'
    $null = New-Item -ItemType Directory -Path $temporarySetup -Force
    $temporaryGenerator = Join-Path $temporarySetup 'generate-env.ps1'
    Copy-Item -LiteralPath $generator -Destination $temporaryGenerator
    & $temporaryGenerator -ResourceGroup 'existing-rg'
    $defaultOutput = Join-Path (Split-Path $temporarySetup -Parent) '.env'
    Assert-True (Test-Path -LiteralPath $defaultOutput) 'Default output must be in the scenario folder, independent of the working directory.'
    Write-Host 'PASS: default output path and current-subscription fallback'
}
finally {
    Remove-Item -LiteralPath $tempDirectory -Recurse -Force
}