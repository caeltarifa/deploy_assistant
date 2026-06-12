# Deploy Assistant

## Start Up

Prereqs:
- Docker and Docker Compose installed
- For visible Playwright Chromium UI on Linux: X11 display access (see notes below)

Start the service (build + run in background):

```bash
docker compose up --build -d
```

Check status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop:

```bash
docker compose down
```

## Scripts

Login (fixed credentials from config):

```bash
python3.10 scripts/login.py fixed
```

Login (custom):

```bash
python3.10 scripts/login.py <url> <username> <password>
```

Create module:

```bash
python3.10 scripts/create_module.py <service_name> <video_url>
```

Start module:

```bash
python3.10 scripts/start_module.py <service_name>
```

Stop module:

```bash
python3.10 scripts/stop_module.py <service_name>
```

List visible services:

```bash
python3.10 scripts/list_services.py
```

## Playwright Chromium UI (Optional)

The app launches Chromium with `headless=False`. To see the test browser window inside the container, you must grant the container access to your display:

```bash
xhost +local:root
```

Make sure `DISPLAY` is set on your host (e.g. `:0`) and then restart the container:

```bash
docker compose restart
```

If you are on Wayland, you may need:

```bash
xhost +SI:localuser:root
```

On macOS/Windows, use an X server (XQuartz/VcXsrv) and set `DISPLAY` accordingly.
