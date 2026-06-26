# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Minimal CLI for operational tasks (run outside the web process)."""

import sys


def migrate() -> None:
    """Run Alembic migrations to the latest revision."""
    from alembic.config import Config

    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    print("Migrations complete.")


def main() -> None:
    commands = {"migrate": migrate}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(f"Usage: python -m app.cli <command>\nCommands: {', '.join(commands)}")
        sys.exit(1)
    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
