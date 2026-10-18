
import os
import subprocess
import platform

from fastmcp import FastMCP

mcp = FastMCP("LiLi MCP Shell")


def execute(command, cwd=None, env=None):
    system = platform.system()

    if system == "Windows":
        shell = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            command
        ]
    else:
        shell = [
            "/bin/bash",
            "-c",
            command
        ]

    environment = os.environ.copy()

    if env:
        environment.update(env)

    result = subprocess.run(
        shell,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        errors="replace"
    )

    return {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


@mcp.tool
def run_shell(
    command: str,
    cwd: str | None = None,
    env: dict[str, str] | None = None
) -> dict:
    """
    Execute a shell command on the host computer.

    Uses Bash on Linux and PowerShell on Windows.
    Supports arbitrary commands, arguments,
    shell operators, pipelines and redirection.

    Commands run with the permissions of the
    operating-system user running this server.
    """
    return execute(command, cwd, env)


@mcp.tool
def run_pipeline(
    commands: list[str],
    stop_on_error: bool = False
) -> list[dict]:
    """
    Execute multiple commands sequentially.
    Each command runs in a separate shell.
    """
    results = []

    for command in commands:
        result = execute(command)
        results.append(result)

        if stop_on_error and result["exit_code"] != 0:
            break

    return results


@mcp.tool
def get_system_info() -> dict:
    """Return host operating-system information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "working_directory": os.getcwd()
    }


if __name__ == "__main__":
    transport = os.getenv(
        "LILI_MCP_TRANSPORT", "stdio"
    )

    if transport == "http":
        mcp.run(
            transport="http",
            host="127.0.0.1",
            port=9010
        )
    else:
        mcp.run(transport="stdio")
