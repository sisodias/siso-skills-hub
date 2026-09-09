---
name: contabo-vps
description: Connect to, provision and debug a Contabo VPS. Use when SSH to a Contabo box fails with "Permission denied", when a panel password reset appears not to work, or when provisioning a new Contabo server. Encodes the reinstall-is-the-fix rule learned the hard way.
version: 1.0.0
tags: [infrastructure, vps, contabo, ssh]
---

# Contabo VPS

## The one thing that costs hours if you get it wrong

**On Contabo, the root password is set during the *reinstall wizard*. It is never emailed,
and changing it in the panel on a running VPS frequently does not reach the disk.**

If SSH says `Permission denied` and the credentials "should" be right, do not keep trying
passwords. Diagnose with the host key, then reinstall.

## Diagnose before touching anything

```bash
IP=<address>

# 1. Is sshd even up, or are we banned?
nc -vz $IP 22                       # "succeeded" = reachable, NOT fail2ban'd
                                    # refused/timeout = banned or box down

# 2. What auth does the server accept?
ssh -v -o PreferredAuthentications=none root@$IP 2>&1 | grep -i "continue"
# "publickey,password" -> password auth IS enabled; a rejection means wrong credential
# "publickey" only     -> key-only image; NO password will ever work

# 3. Has the box actually rebooted/reinstalled? (the decisive check)
ssh-keyscan -t ed25519 $IP 2>/dev/null | grep ssh-ed25519 | awk '{print $3}'
```

**The host key is the ground truth.** A genuine Contabo password reset reboots the server,
and a reinstall regenerates the host key. If the host key has not changed since your first
contact, nothing the panel claims to have applied has reached the running system — no
number of retries will help.

Compare the full string. Truncating it produces false "CHANGED" readings.

## Decision table

| Symptom | Meaning | Fix |
|---|---|---|
| Port 22 refused/timeout | fail2ban or box down | Wait, or reboot from panel |
| Only `publickey` offered | Key-only image | Reinstall, or add key via panel + reinstall |
| `publickey,password` offered but all passwords fail, host key unchanged | Panel change never applied | **Reinstall** |
| Password works, key does not | Key not on disk | Install it (below) |

Stop after ~3 password attempts. More invites a fail2ban lockout that turns a fixable
problem into a wait.

## The reliable fix: reinstall

Panel → the instance → reinstall → **Ubuntu 24.04** → **set the system password in the
wizard**. That password is the credential; it is not emailed. An SSH-key field is optional
and may not be offered — that is normal, do not block on it.

Reinstall is safe on a fresh box and is usually faster than diagnosing a stuck reset.

Afterwards the host key changes, so clear the stale one or the connection will warn:

```bash
ssh-keygen -R $IP
```

## First contact, then key-only

```bash
PUB=$(cat ~/.ssh/id_ed25519.pub)
sshpass -p "$PW" ssh -o StrictHostKeyChecking=accept-new \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no root@$IP \
  "mkdir -p /root/.ssh && chmod 700 /root/.ssh && \
   grep -qF '$PUB' /root/.ssh/authorized_keys 2>/dev/null || echo '$PUB' >> /root/.ssh/authorized_keys && \
   chmod 600 /root/.ssh/authorized_keys"

# verify the key works BEFORE disabling passwords
ssh -o BatchMode=yes -i ~/.ssh/id_ed25519 root@$IP 'echo ok'
```

Harden only once key auth is proven, and validate the config before reloading so a typo
cannot lock you out:

```bash
printf 'PasswordAuthentication no\nPermitRootLogin prohibit-password\nPubkeyAuthentication yes\n' \
  > /etc/ssh/sshd_config.d/99-siso.conf
sshd -t && systemctl reload ssh
```

## VNC

The panel exposes VNC on a separate host:port. It is a real fallback, but:

- it uses its **own password**, set in the panel — not the root password;
- VNC auth silently truncates the password to **8 characters**;
- it lands at a normal console login, so it still needs working system credentials.

Verify what it wants before assuming it is a way in:

```bash
nc -vz <vnc-host> <vnc-port>     # reachable?
# RFB handshake reports the security type: "None" = open, "VNC Auth" = password required
```

## Running long installs

Do not background an `ssh ... <<EOF` heredoc locally and trust the exit code — the local
process can return 0 while the remote work is still running, and a second `apt-get` then
fails on the dpkg lock. Run it in the foreground with a generous timeout, or poll the lock:

```bash
ssh $HOST 'for i in $(seq 1 60); do
  fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || { echo FREE; break; }; sleep 10; done'
```

Always verify by checking for the installed binaries, never by trusting the exit status.

## Known-good provisioning set (Ubuntu 24.04)

`postgresql-16 redis-server rabbitmq-server nodejs(22.x via NodeSource) caddy`, then
`corepack enable && corepack prepare pnpm@11.3.0 --activate`.

Caddy needs its own apt repository; it is not in Ubuntu's archive.

Firewall: deny incoming, allow 22/80/443 only. Keep databases bound to localhost or a
private network — never expose 5432/6379/5672 publicly.
