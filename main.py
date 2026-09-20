import re
import subprocess
from collections.abc import Sequence


COMMAND_TIMEOUT_SECONDS = 10
WINDOWS_BOOT_ENTRY = re.compile(
    r"^Boot([0-9A-Fa-f]{4})\*?\s+Windows Boot Manager(?:\t.*)?\s*$"
)


def parse_windows_boot_target(output: str) -> str | None:
    """Return the exact EFI boot number for Windows Boot Manager, if present."""
    for line in output.splitlines():
        match = WINDOWS_BOOT_ENTRY.match(line)
        if match:
            return match.group(1).upper()
    return None


def run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )


def command_error(result: subprocess.CompletedProcess[str], fallback: str) -> str:
    detail = result.stderr.strip()
    return f"{fallback}: {detail}" if detail else fallback


def detect_windows_boot_target() -> tuple[str | None, str | None]:
    try:
        result = run_command(["efibootmgr"])
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"Unable to inspect EFI boot entries: {error}"

    if result.returncode != 0:
        return None, command_error(result, "Unable to inspect EFI boot entries")

    target = parse_windows_boot_target(result.stdout)
    if target is None:
        return None, "Windows Boot Manager was not found in the EFI boot entries."
    return target, None


def clear_boot_next() -> bool:
    try:
        return run_command(["efibootmgr", "-N"]).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class Plugin:
    # noinspection PyMethodMayBeStatic
    async def get_bazzite_branch(self) -> str | None:
        try:
            file = open("/etc/bazzite/image_branch")
            branch = file.read()
            return branch
        finally:
            return "stable"

    # noinspection PyMethodMayBeStatic
    async def get_windows_boot_target(self) -> dict[str, bool | str]:
        target, error = detect_windows_boot_target()
        if target is None:
            return {"available": False, "error": error or "Unknown error"}
        return {"available": True}

    # noinspection PyMethodMayBeStatic
    async def reboot_to_windows(self) -> dict[str, bool | str]:
        # Re-detect at action time so a stale QAM view can never select an old target.
        target, error = detect_windows_boot_target()
        if target is None:
            return {"ok": False, "error": error or "Unknown error"}

        try:
            boot_next = run_command(["efibootmgr", "-n", target])
        except (OSError, subprocess.SubprocessError) as command_failure:
            return {
                "ok": False,
                "error": f"Unable to set the next boot target: {command_failure}",
            }

        if boot_next.returncode != 0:
            return {
                "ok": False,
                "error": command_error(
                    boot_next, "Unable to set Windows as the next boot target"
                ),
            }

        try:
            reboot = run_command(["systemctl", "--no-block", "reboot"])
        except (OSError, subprocess.SubprocessError) as command_failure:
            # Do not leave a surprising Windows BootNext behind after a failed reboot.
            cleared = clear_boot_next()
            error_message = f"Unable to request a reboot: {command_failure}"
            if not cleared:
                error_message += "; unable to clear the one-time boot target"
            return {
                "ok": False,
                "error": error_message,
            }

        if reboot.returncode != 0:
            cleared = clear_boot_next()
            error_message = command_error(reboot, "Unable to request a reboot")
            if not cleared:
                error_message += "; unable to clear the one-time boot target"
            return {"ok": False, "error": error_message}

        return {"ok": True}
