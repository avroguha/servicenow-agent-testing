# acctest fixture plugin: local users with their group memberships and admin status, one JSON object per line.
# Deployed to the agent as the custom asset "acctest-scripts"; started by acctest_users.cmd (the check command),
# because a .ps1 cannot be the command itself - cmd/exec resolve .cmd through PATH, PowerShell needs a full path.
$ErrorActionPreference = 'Continue'
"ACCTEST_USERS v1 os=windows host=$env:COMPUTERNAME user=$env:USERNAME"
$membership = @{}
foreach ($g in Get-LocalGroup) {
    try { $members = @(Get-LocalGroupMember -Group $g.Name -ErrorAction Stop) } catch { $members = @() }
    foreach ($m in $members) {
        $n = ($m.Name -split '\\')[-1]
        if (-not $membership.ContainsKey($n)) { $membership[$n] = @() }
        $membership[$n] += $g.Name
    }
}
$count = 0
foreach ($u in Get-LocalUser) {
    $groups = @($membership[$u.Name] | Where-Object { $_ })
    $o = [ordered]@{
        user              = $u.Name
        sid               = $u.SID.Value
        enabled           = [bool]$u.Enabled
        password_required = [bool]$u.PasswordRequired
        last_logon        = if ($u.LastLogon) { $u.LastLogon.ToString('s') } else { $null }
        groups            = $groups
        admin             = [bool]($groups -contains 'Administrators')
    }
    ($o | ConvertTo-Json -Compress -Depth 3)
    $count++
}
"ACCTEST_USERS end count=$count"
exit 0
