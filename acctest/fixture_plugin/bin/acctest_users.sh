#!/bin/sh
# acctest fixture plugin: local users with their groups and admin status, one JSON object per line.
# Deployed to the agent as the custom asset "acctest-scripts" and run by the custom check "acctest-users-linux".
# Needs nothing but /etc/passwd, /etc/group and awk (mawk/gawk/busybox); never elevates.
echo "ACCTEST_USERS v1 os=linux host=$(hostname) user=$(id -un)"
awk -F: '
BEGIN {
  while ((getline l < "/etc/group") > 0) {
    split(l, gf, ":"); gid2name[gf[3]] = gf[1]
    n = split(gf[4], mem, ","); for (i = 1; i <= n; i++) if (mem[i] != "") extra[mem[i]] = extra[mem[i]] "," gf[1]
  }
  close("/etc/group")
}
function esc(s) { gsub(/\\/, "\\\\", s); gsub(/"/, "\\\"", s); return s }
{
  glist = gid2name[$4]; if ($1 in extra) glist = glist extra[$1]
  n = split(glist, arr, ","); out = ""; admin = ($3 == 0) ? "true" : "false"
  for (i = 1; i <= n; i++) {
    if (arr[i] == "") continue
    out = out (out == "" ? "" : ",") "\"" esc(arr[i]) "\""
    if (arr[i] == "sudo" || arr[i] == "wheel" || arr[i] == "admin" || arr[i] == "root") admin = "true"
  }
  printf "{\"user\":\"%s\",\"uid\":%s,\"gid\":%s,\"home\":\"%s\",\"shell\":\"%s\",\"groups\":[%s],\"admin\":%s}\n", esc($1), $3, $4, esc($6), esc($7), out, admin
}' /etc/passwd
echo "ACCTEST_USERS end count=$(grep -c . /etc/passwd)"
exit 0
