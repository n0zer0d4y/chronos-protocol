"""Storage configuration and data directory resolution.

This module provides functionality for resolving data storage directories
based on different storage modes (centralized vs per-project) and handles
project root detection with multiple fallback strategies.
"""

from __future__ import annotations
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class StorageMode:
    """Constants and validation for storage modes."""
    
    CENTRALIZED = "centralized"
    PER_PROJECT = "per-project"
    
    @classmethod
    def validate(cls, mode: str) -> str:
        """Validate and normalize storage mode.
        
        Args:
            mode: Storage mode string to validate
            
        Returns:
            Normalized storage mode string
            
        Raises:
            ValueError: If storage mode is invalid
            
        Examples:
            >>> StorageMode.validate("centralized")
            'centralized'
            >>> StorageMode.validate("PER_PROJECT") 
            'per-project'
            >>> StorageMode.validate("per_project")
            'per-project'
        """
        if not isinstance(mode, str):
            raise ValueError(f"Storage mode must be a string, got {type(mode).__name__}")
        
        # Normalize: lowercase, replace underscores with hyphens
        normalized = mode.lower().replace("_", "-")
        
        if normalized not in [cls.CENTRALIZED, cls.PER_PROJECT]:
            raise ValueError(
                f"Invalid storage_mode: '{mode}'. "
                f"Must be '{cls.CENTRALIZED}' or '{cls.PER_PROJECT}'"
            )
        
        return normalized


def detect_project_root(explicit_root: Optional[str] = None) -> Path:
    """Detect project root directory using multiple strategies.
    
    Uses priority-based detection:
    1. Explicit --project-root argument
    2. MCP_PROJECT_ROOT environment variable
    3. PROJECT_ROOT environment variable
    4. Current working directory (fallback)
    
    Args:
        explicit_root: Explicit project root path (highest priority)
        
    Returns:
        Resolved absolute path to project root directory
        
    Raises:
        FileNotFoundError: If explicit_root doesn't exist
        ValueError: If explicit_root is not a directory
        
    Examples:
        >>> detect_project_root("/path/to/project")
        Path('/path/to/project')
        >>> detect_project_root()  # Uses environment variables or CWD
        Path('/current/working/directory')
    """
    
    # Priority 1: Explicit argument (highest priority)
    if explicit_root:
        root = Path(explicit_root).resolve()
        if not root.exists():
            raise FileNotFoundError(f"Specified project_root does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Specified project_root is not a directory: {root}")
        logger.info(f"Using explicit project root: {root}")
        return root
    
    # Priority 2: MCP_PROJECT_ROOT environment variable
    env_root = os.getenv("MCP_PROJECT_ROOT")
    if env_root:
        root = Path(env_root).resolve()
        if root.exists() and root.is_dir():
            logger.info(f"Using MCP_PROJECT_ROOT environment variable: {root}")
            return root
        logger.warning(f"MCP_PROJECT_ROOT exists but invalid: {env_root}")
    
    # Priority 3: PROJECT_ROOT environment variable
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        root = Path(env_root).resolve()
        if root.exists() and root.is_dir():
            logger.info(f"Using PROJECT_ROOT environment variable: {root}")
            return root
        logger.warning(f"PROJECT_ROOT exists but invalid: {env_root}")
    
    # Priority 4: Current working directory (fallback)
    cwd = Path.cwd()
    logger.info(f"Using current working directory as project root: {cwd}")
    return cwd


def resolve_data_dir(
    storage_mode: str = "centralized",
    project_root: Optional[str] = None,
    data_dir: str = "./chronos-data"
) -> Path:
    """Resolve actual data directory based on storage configuration.
    
    Args:
        storage_mode: Storage mode ("centralized" or "per-project")
        project_root: Explicit project root (for per-project mode)
        data_dir: Default data directory (for centralized mode)
        
    Returns:
        Resolved absolute path to data directory
        
    Raises:
        ValueError: If storage_mode is invalid
        FileNotFoundError: If project_root doesn't exist (per-project mode)
        
    Examples:
        >>> resolve_data_dir("centralized", data_dir="./my-data")
        Path('/current/directory/my-data')
        >>> resolve_data_dir("per-project", project_root="/workspace")
        Path('/workspace/chronos-data')
    """
    
    # Validate and normalize storage mode
    mode = StorageMode.validate(storage_mode)
    
    if mode == StorageMode.PER_PROJECT:
        # Per-project mode: use project root + chronos-data subdirectory
        project_path = detect_project_root(project_root)
        resolved_dir = project_path / "chronos-data"
        logger.info(f"Per-project storage: {resolved_dir}")
        
    elif mode == StorageMode.CENTRALIZED:
        # Centralized mode: use explicit data_dir or environment variable
        env_data_dir = os.getenv("MCP_DATA_DIR")
        if env_data_dir:
            resolved_dir = Path(env_data_dir).resolve()
            logger.info(f"Using MCP_DATA_DIR environment variable: {resolved_dir}")
        else:
            resolved_dir = Path(data_dir).resolve()
            logger.info(f"Centralized storage: {resolved_dir}")
    
    return resolved_dir


def validate_and_create_data_dir(data_dir: Path) -> None:
    """Validate data directory and create if needed.
    
    Ensures the data directory exists, is writable, and accessible.
    Creates parent directories as needed.
    
    Args:
        data_dir: Path to data directory to validate/create
        
    Raises:
        PermissionError: If no write permission to data directory
        OSError: If failed to create/access data directory
        
    Examples:
        >>> validate_and_create_data_dir(Path("/path/to/chronos-data"))
        # Creates directory and tests write permissions
    """
    
    try:
        # Create directory if it doesn't exist (including parents)
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Data directory ready: {data_dir}")
        
        # Test write permissions
        test_file = data_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        logger.info("✅ Data directory write permissions verified")
        
    except PermissionError as e:
        raise PermissionError(
            f"No write permission to data directory: {data_dir}. "
            f"Check file permissions and try again."
        ) from e
    except OSError as e:
        raise OSError(
            f"Failed to create/access data directory: {data_dir}. "
            f"Check path validity and permissions."
        ) from e
