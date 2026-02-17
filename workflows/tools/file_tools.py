"""File utilities for safely reading files by pattern."""

from crewai.tools import tool
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)


@tool("Read Files By Pattern")
def read_files_by_pattern(directory: str, pattern: str,
                          base_dir: str = ".") -> str:
    """Read all files matching a glob pattern within a safe base directory.

    Args:
        directory: The directory to search in (relative to base_dir).
        pattern: The glob pattern to match (e.g. "*.yaml", "**/*.py").
        base_dir: The root directory to restrict access to.

    Returns:
        The concatenated contents of all matching files.
    """
    base = Path(base_dir).resolve()

    search_dir = (base / directory).resolve()

    if not search_dir.is_relative_to(base):

        logging.error(f"Directory '{directory}' is outside base '{base_dir}'.")

        return ""

    if not search_dir.is_dir():

        logging.error(f"Directory '{search_dir}' does not exist.")

        return ""

    results = []

    for file_path in sorted(search_dir.glob(pattern)):

        resolved = file_path.resolve()

        if not resolved.is_relative_to(base):

            logging.warning(f"Skipping '{file_path}' (outside base directory).")

            continue

        if not resolved.is_file():

            continue

        try:
            content = resolved.read_text(encoding="utf-8")

            results.append(f"--- {resolved.relative_to(base)} ---\n{content}")

        except Exception as e:

            logging.error(f"Error reading '{resolved}': {e}")

    logging.info(f"Read {len(results)} file(s) matching '{pattern}' in '{search_dir}'.")

    return "\n\n".join(results)


@tool("Read File By Name")
def read_file_by_name(file_name: str, base_dir: str = ".") -> str:
    """Read a single file by name within a safe base directory.

    Args:
        file_name: The file path to read (relative to base_dir).
        base_dir: The root directory to restrict access to.

    Returns:
        The contents of the file, or an empty string on error.
    """
    base = Path(base_dir).resolve()

    file_path = (base / file_name).resolve()

    if not file_path.is_relative_to(base):

        logging.error(f"File '{file_name}' is outside base '{base_dir}'.")

        return ""

    if not file_path.is_file():

        logging.error(f"File '{file_path}' does not exist.")

        return ""

    try:
        content = file_path.read_text(encoding="utf-8")

        logging.info(f"Read file '{file_path.relative_to(base)}'.")

        return content

    except Exception as e:

        logging.error(f"Error reading '{file_path}': {e}")

        return ""
