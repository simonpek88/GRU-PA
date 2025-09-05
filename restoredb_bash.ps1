param(
    [Parameter(Mandatory=$true)]
    [string]$BackupTimestamp
)

# 检查MySQL备份文件是否存在
$backupFile = "MySQL_Backup\GRU-PA-MySQL_Backup_$BackupTimestamp.sql"

if (-not (Test-Path $backupFile)) {
    Write-Error "备份文件不存在: $backupFile"
    exit 1
}

# 读取MySQL配置
$mysqlConfig = Get-Content ".mysql.cnf" | Out-String
# 初始化变量（使用[ref]确保变量被识别为已使用）
$mysqlUser = [ref]""
$mysqlPassword = [ref]""
$mysqlPort = [ref]""

# 解析配置文件
$mysqlConfig -split "`n" | ForEach-Object {
    $line = $_.Trim()
    if ($line -match "^user\s*=\s*(.+)$") {
        $mysqlUser.Value = $matches[1]
    }
    elseif ($line -match "^password\s*=\s*(.+)$") {
        $mysqlPassword.Value = $matches[1]
    }
    elseif ($line -match "^port\s*=\s*(.+)$") {
        $mysqlPort.Value = $matches[1]
    }
}

# 构建MySQL命令并执行
$mysqlArgs = @(
    "--user=$($mysqlUser.Value)"
    "--password=$($mysqlPassword.Value)"
    "--port=$($mysqlPort.Value)"
    "gru-pa"
)

# 执行MySQL命令
Get-Content $backupFile | & mysql @mysqlArgs

Write-Host "数据库恢复完成: $backupFile"
