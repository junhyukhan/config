Add a new ingress entry to the cloudflared tunnel config at ~/dev/config/cloudflared/.cloudflared/config.yml so that a local service is exposed via the Cloudflare tunnel.

The user will provide:
- $ARGUMENTS: hostname and local service URL in the format `<hostname> <service>`, e.g. `api.jhkn.dev http://localhost:8080`

Steps:
1. Read ~/dev/config/cloudflared/.cloudflared/config.yml
2. Parse the two arguments from $ARGUMENTS (hostname and service URL). If only one argument is given, ask the user for the missing one.
3. Check that the hostname doesn't already exist in the config. If it does, tell the user and stop.
4. Add a new ingress entry ABOVE the catch-all (`- service: http_status:404`), matching the existing formatting style.
5. Show the user the updated config and confirm the entry was added.
6. Restart cloudflared: `sudo systemctl restart cloudflared`
