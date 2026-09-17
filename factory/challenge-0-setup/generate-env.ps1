[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ResourceGroup,
    [string]$SubscriptionId,
    [string]$FoundryResourceName,
    [string]$ProjectName = 'factory-project',
    [string]$ModelDeploymentName,
    [string]$AppInsightsName,
    [string]$OutputPath = (Join-Path (Split-Path $PSScriptRoot -Parent) '.env'),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$OutputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
if ((Test-Path -LiteralPath $OutputPath) -and -not $Force) {
    throw "File already exists: $OutputPath. Use -Force to replace it, including any custom settings."
}
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI is required. Install it and sign in before running this script.'
}

function Invoke-AzureJson {
    param([string[]]$Arguments)

    $cliArguments = $Arguments + @('--only-show-errors', '--output', 'json')
    if ($SubscriptionId) {
        $cliArguments += @('--subscription', $SubscriptionId)
    }
    $json = & az @cliArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI failed: az $($Arguments -join ' '). No environment file was written."
    }
    try {
        $result = ConvertFrom-Json -InputObject ($json -join "`n") -ErrorAction Stop
    }
    catch {
        throw 'Azure CLI returned invalid JSON. No environment file was written.'
    }
    if ($null -eq $result) {
        throw 'Azure CLI returned no data. No environment file was written.'
    }
    return $result
}

function Select-NamedResource {
    param([object[]]$Resources, [string]$RequestedName, [string]$ParameterName)

    $candidates = @($Resources)
    if ($RequestedName) {
        $candidates = @($Resources | Where-Object { $_.name -eq $RequestedName })
    }
    if ($candidates.Count -ne 1) {
        $available = ($Resources | ForEach-Object { $_.name }) -join ', '
        throw "Expected one resource for -$ParameterName; found $($candidates.Count). Available names: $available. Specify -$ParameterName explicitly when needed."
    }
    return $candidates[0]
}

$subscription = Invoke-AzureJson @('account', 'show')
if ([string]::IsNullOrWhiteSpace($subscription.id)) {
    throw 'No subscription ID returned. Sign in to Azure CLI and select a subscription.'
}
$SubscriptionId = $subscription.id

$accounts = @(Invoke-AzureJson @('cognitiveservices', 'account', 'list', '--resource-group', $ResourceGroup))
$foundry = Select-NamedResource -Resources @($accounts | Where-Object { $_.kind -eq 'AIServices' }) `
    -RequestedName $FoundryResourceName -ParameterName 'FoundryResourceName'
if ($foundry.properties.provisioningState -ne 'Succeeded') {
    throw 'The Foundry account has not successfully provisioned.'
}

$project = Invoke-AzureJson @(
    'cognitiveservices', 'account', 'project', 'show', '--resource-group', $ResourceGroup,
    '--name', $foundry.name, '--project-name', $ProjectName
)
$keys = Invoke-AzureJson @(
    'cognitiveservices', 'account', 'keys', 'list', '--resource-group', $ResourceGroup,
    '--name', $foundry.name
)
$deployments = @(Invoke-AzureJson @(
    'cognitiveservices', 'account', 'deployment', 'list', '--resource-group', $ResourceGroup,
    '--name', $foundry.name
))
$model = Select-NamedResource -Resources $deployments `
    -RequestedName $ModelDeploymentName -ParameterName 'ModelDeploymentName'
if ($model.properties.provisioningState -ne 'Succeeded') {
    throw 'The model deployment has not successfully provisioned.'
}

$components = @(Invoke-AzureJson @(
    'resource', 'list', '--resource-group', $ResourceGroup, '--resource-type', 'Microsoft.Insights/components'
))
$component = Select-NamedResource -Resources $components `
    -RequestedName $AppInsightsName -ParameterName 'AppInsightsName'
$insights = Invoke-AzureJson @(
    'resource', 'show', '--resource-group', $ResourceGroup, '--name', $component.name,
    '--resource-type', 'Microsoft.Insights/components', '--api-version', '2020-02-02'
)

$settings = [ordered]@{
    AZURE_SUBSCRIPTION_ID = $SubscriptionId
    RESOURCE_GROUP = $ResourceGroup
    FOUNDRY_RESOURCE_NAME = $foundry.name
    PROJECT_NAME = $ProjectName
    FOUNDRY_ENDPOINT = $foundry.properties.endpoint
    PROJECT_CONNECTION_STRING = $project.properties.endpoints.'AI Foundry API'
    MODEL_DEPLOYMENT_NAME = $model.name
    API_KEY = $keys.key1
    APPLICATIONINSIGHTS_CONNECTION_STRING = $insights.properties.ConnectionString
    APPINSIGHTS_INSTRUMENTATION_KEY = $insights.properties.InstrumentationKey
    AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING = 'true'
    OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT = 'true'
}
$lines = @(
    foreach ($setting in $settings.GetEnumerator()) {
        $value = [string]$setting.Value
        if ([string]::IsNullOrWhiteSpace($value) -or $value -match '[\r\n]') {
            throw "Missing or invalid value for $($setting.Key). No environment file was written."
        }
        $escapedValue = $value.Replace('\', '\\').Replace('"', '\"')
        '{0}="{1}"' -f $setting.Key, $escapedValue
    }
)

$fileMode = if ($Force) { [System.IO.FileMode]::Create } else { [System.IO.FileMode]::CreateNew }
$stream = [System.IO.File]::Open($OutputPath, $fileMode, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
try {
    $writer = [System.IO.StreamWriter]::new($stream, [System.Text.UTF8Encoding]::new($false))
    try {
        foreach ($line in $lines) {
            $writer.WriteLine($line)
        }
    }
    finally {
        $writer.Dispose()
    }
}
finally {
    $stream.Dispose()
}
Write-Host "Environment file written to: $OutputPath"