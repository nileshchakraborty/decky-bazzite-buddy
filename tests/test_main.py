import subprocess
import unittest
from unittest.mock import patch

import main


def result(returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class ParseWindowsBootTargetTests(unittest.TestCase):
    def test_parses_active_windows_entry(self):
        output = """BootCurrent: 0001
Boot0001* Bazzite
Boot00AF* Windows Boot Manager\tHD(1,GPT,...)
"""

        self.assertEqual(main.parse_windows_boot_target(output), "00AF")

    def test_parses_inactive_windows_entry(self):
        self.assertEqual(
            main.parse_windows_boot_target("Boot00af  Windows Boot Manager\n"),
            "00AF",
        )

    def test_rejects_similar_entry_names(self):
        self.assertIsNone(
            main.parse_windows_boot_target("Boot00AF* Windows Boot Manager Backup\n")
        )

    def test_detection_reports_efibootmgr_failure(self):
        with patch.object(
            main,
            "run_command",
            return_value=result(1, stderr="EFI variables are not supported"),
        ):
            target, error = main.detect_windows_boot_target()

        self.assertIsNone(target)
        self.assertIn("EFI variables are not supported", error)

    def test_clear_boot_next_handles_missing_efibootmgr(self):
        with patch.object(main, "run_command", side_effect=FileNotFoundError):
            self.assertFalse(main.clear_boot_next())


class RebootToWindowsTests(unittest.IsolatedAsyncioTestCase):
    async def test_availability_does_not_expose_boot_number(self):
        plugin = main.Plugin()
        with patch.object(main, "detect_windows_boot_target", return_value=("00AF", None)):
            self.assertEqual(
                await plugin.get_windows_boot_target(), {"available": True}
            )

    async def test_does_not_reboot_when_bootnext_fails(self):
        plugin = main.Plugin()
        with (
            patch.object(main, "detect_windows_boot_target", return_value=("00AF", None)),
            patch.object(
                main,
                "run_command",
                return_value=result(1, stderr="permission denied"),
            ) as run,
        ):
            response = await plugin.reboot_to_windows()

        self.assertFalse(response["ok"])
        self.assertIn("permission denied", response["error"])
        run.assert_called_once_with(["efibootmgr", "-n", "00AF"])

    async def test_clears_bootnext_when_reboot_fails(self):
        plugin = main.Plugin()
        with (
            patch.object(main, "detect_windows_boot_target", return_value=("00AF", None)),
            patch.object(
                main,
                "run_command",
                side_effect=[
                    result(),
                    result(1, stderr="reboot refused"),
                ],
            ) as run,
            patch.object(main, "clear_boot_next", return_value=True) as clear,
        ):
            response = await plugin.reboot_to_windows()

        self.assertFalse(response["ok"])
        self.assertEqual(
            [call.args[0] for call in run.call_args_list],
            [
                ["efibootmgr", "-n", "00AF"],
                ["systemctl", "--no-block", "reboot"],
            ],
        )
        clear.assert_called_once_with()

    async def test_reboots_only_after_setting_bootnext(self):
        plugin = main.Plugin()
        with (
            patch.object(main, "detect_windows_boot_target", return_value=("00AF", None)),
            patch.object(main, "run_command", side_effect=[result(), result()]) as run,
        ):
            response = await plugin.reboot_to_windows()

        self.assertEqual(response, {"ok": True})
        self.assertEqual(
            [call.args[0] for call in run.call_args_list],
            [
                ["efibootmgr", "-n", "00AF"],
                ["systemctl", "--no-block", "reboot"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
