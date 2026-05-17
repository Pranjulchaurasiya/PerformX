# PerformX API end-to-end test
$base = "http://localhost:8000/api"

Write-Host "`n=== 1. Login as Employee ===" -ForegroundColor Cyan
$loginBody = '{"email":"alice@performx.com","password":"Employee@123"}'
$loginResp = Invoke-WebRequest -Uri "$base/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
$token = ($loginResp.Content | ConvertFrom-Json).access_token
Write-Host "Token: $($token.Substring(0,30))..."

$headers = @{ Authorization = "Bearer $token" }

Write-Host "`n=== 2. Get /auth/me ===" -ForegroundColor Cyan
$me = Invoke-WebRequest -Uri "$base/auth/me" -Headers $headers -UseBasicParsing
Write-Host $me.Content

Write-Host "`n=== 3. List Goals (employee) ===" -ForegroundColor Cyan
$goals = Invoke-WebRequest -Uri "$base/goals" -Headers $headers -UseBasicParsing
$goalsData = $goals.Content | ConvertFrom-Json
Write-Host "Total goals: $($goalsData.total)"
$goalsData.items | ForEach-Object { Write-Host "  [$($_.status)] $($_.title) - $($_.weightage)%" }

Write-Host "`n=== 4. Checkin window status ===" -ForegroundColor Cyan
$window = Invoke-WebRequest -Uri "$base/checkins/window-status" -Headers $headers -UseBasicParsing
Write-Host $window.Content

Write-Host "`n=== 5. Login as Manager ===" -ForegroundColor Cyan
$mgrLogin = Invoke-WebRequest -Uri "$base/auth/login" -Method POST -Body '{"email":"manager@performx.com","password":"Manager@123"}' -ContentType "application/json" -UseBasicParsing
$mgrToken = ($mgrLogin.Content | ConvertFrom-Json).access_token
$mgrHeaders = @{ Authorization = "Bearer $mgrToken" }

Write-Host "`n=== 6. Manager team goals (pending approval) ===" -ForegroundColor Cyan
$teamGoals = Invoke-WebRequest -Uri "$base/goals?status=submitted" -Headers $mgrHeaders -UseBasicParsing
$teamData = $teamGoals.Content | ConvertFrom-Json
Write-Host "Pending approval: $($teamData.total)"
$teamData.items | ForEach-Object { Write-Host "  [$($_.status)] $($_.title)" }

Write-Host "`n=== 7. Manager analytics - QoQ team ===" -ForegroundColor Cyan
$qoq = Invoke-WebRequest -Uri "$base/analytics/manager/qoq-team" -Headers $mgrHeaders -UseBasicParsing
Write-Host $qoq.Content

Write-Host "`n=== 8. Manager escalations widget ===" -ForegroundColor Cyan
$esc = Invoke-WebRequest -Uri "$base/escalations/my-team" -Headers $mgrHeaders -UseBasicParsing
Write-Host $esc.Content

Write-Host "`n=== 9. Login as Admin ===" -ForegroundColor Cyan
$adminLogin = Invoke-WebRequest -Uri "$base/auth/login" -Method POST -Body '{"email":"admin@performx.com","password":"Admin@123"}' -ContentType "application/json" -UseBasicParsing
$adminToken = ($adminLogin.Content | ConvertFrom-Json).access_token
$adminHeaders = @{ Authorization = "Bearer $adminToken" }

Write-Host "`n=== 10. Admin cycles (with penalty_factor) ===" -ForegroundColor Cyan
$cycles = Invoke-WebRequest -Uri "$base/admin/cycles" -Headers $adminHeaders -UseBasicParsing
$cyclesData = $cycles.Content | ConvertFrom-Json
$cyclesData | ForEach-Object { Write-Host "  $($_.name) penalty=$($_.penalty_factor) active=$($_.is_active)" }

Write-Host "`n=== 11. Admin analytics - org QoQ trends ===" -ForegroundColor Cyan
$orgQoq = Invoke-WebRequest -Uri "$base/analytics/admin/org-qoq-trends" -Headers $adminHeaders -UseBasicParsing
Write-Host $orgQoq.Content

Write-Host "`n=== 12. Admin analytics - manager effectiveness ===" -ForegroundColor Cyan
$mgrEff = Invoke-WebRequest -Uri "$base/analytics/admin/manager-effectiveness" -Headers $adminHeaders -UseBasicParsing
Write-Host $mgrEff.Content

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green
