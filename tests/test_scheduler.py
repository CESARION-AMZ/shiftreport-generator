from shiftreport.scheduler import (
    build_create_args,
    build_run_command,
    strip_schedule_flags,
)


def test_strip_schedule_flags():
    argv = ["data.csv", "-g", "area", "--install-schedule", "14:30", "--schedule-name", "turno"]
    assert strip_schedule_flags(argv) == ["data.csv", "-g", "area"]


def test_strip_uninstall_flag():
    assert strip_schedule_flags(["data.csv", "--uninstall-schedule"]) == ["data.csv"]


def test_build_run_command_module():
    cmd = build_run_command(["data.csv", "-g", "area", "--install-schedule", "14:30"],
                            "C:/py/python.exe", frozen=False)
    assert "-m" in cmd and "shiftreport" in cmd
    assert "data.csv" in cmd
    assert "--install-schedule" not in cmd


def test_build_run_command_frozen():
    cmd = build_run_command(["data.csv"], "C:/app/ShiftReport.exe", frozen=True)
    assert "shiftreport" not in cmd.split("data.csv")[0].replace("ShiftReport.exe", "")
    assert "data.csv" in cmd


def test_build_create_args_shape():
    args = build_create_args("ShiftReport_x", "14:30", "run me")
    assert args[0] == "schtasks" and "/Create" in args and "/SC" in args
    assert "DAILY" in args and "14:30" in args
