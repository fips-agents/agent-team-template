"""Role specification parsing."""

from pathlib import Path
from typing import Any

import yaml


def parse_role_spec(file_path: Path) -> dict[str, Any]:
    """Parse a role specification file with YAML frontmatter.

    Returns dict with 'frontmatter', 'content', and 'source_file' keys.

    Raises:
        ValueError: If the file has invalid frontmatter format.
    """
    with open(file_path) as f:
        content = f.read()

    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError(
            f"Invalid role spec format in {file_path}: missing frontmatter delimiters"
        )

    frontmatter = yaml.safe_load(parts[1])
    if not frontmatter:
        raise ValueError(f"Empty frontmatter in {file_path}")

    body = "---".join(parts[2:]).strip()

    return {
        "frontmatter": frontmatter,
        "content": body,
        "source_file": file_path.name,
    }
