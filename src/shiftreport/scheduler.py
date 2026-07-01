"""Programacion desatendida en Windows via schtasks.

Registra una tarea DIARIA que ejecuta el reporte a una hora fija, aunque la
app este cerrada. La tarea solo se crea cuando se invoca explicitamente
(--install-schedule); nunca de forma automatica.
"""
from __future__ import annotations

import subprocess

TASK_PREFIX = "ShiftReport_"


def strip_schedule_flags(argv: list[str]) -> list[str]:
    """Quita del argv los flags de programacion (y sus valores)."""
    out: list[str] = []
    skip = False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a in ("--install-schedule", "--schedule-name"):
            skip = True  # tiene valor a continuacion
            continue
        if a == "--uninstall-schedule":
            continue
        out.append(a)
    return out


def build_run_command(argv: list[str], python_exe: str, frozen: bool) -> str:
    """Construye el comando que la tarea ejecutara a diario."""
    clean = strip_schedule_flags(argv)
    if frozen:
        base = [python_exe]          # es el .exe empaquetado
    else:
        base = [python_exe, "-m", "shiftreport"]
    parts = base + clean
    return " ".join(f'"{p}"' if (" " in p and not p.startswith('"')) else p for p in parts)


def build_create_args(task_name: str, time_hhmm: str, run_command: str) -> list[str]:
    return ["schtasks", "/Create", "/SC", "DAILY", "/TN", task_name,
            "/ST", time_hhmm, "/TR", run_command, "/F"]


def install_daily(run_command: str, time_hhmm: str, name: str = "default") -> str:
    task = f"{TASK_PREFIX}{name}"
    args = build_create_args(task, time_hhmm, run_command)
    subprocess.run(args, check=True, capture_output=True, text=True)
    return task


def uninstall(name: str = "default") -> str:
    task = f"{TASK_PREFIX}{name}"
    subprocess.run(["schtasks", "/Delete", "/TN", task, "/F"],
                   check=True, capture_output=True, text=True)
    return task
