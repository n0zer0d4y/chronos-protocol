from .server import serve


def main():
    """Chronos Protocol - Super-powered time, timezone conversion, and activity logging functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Super-powered time server with activity logging for AI coding agents"
    )
    parser.add_argument("--local-timezone", type=str, help="Override local timezone")
    parser.add_argument("--storage-mode",
                        choices=["centralized", "per-project"],
                        default="centralized",
                        help="Storage strategy: centralized (default) or per-project")
    parser.add_argument("--data-dir", type=str, default="./data",
                        help="Directory for centralized storage (ignored in per-project mode)")
    parser.add_argument("--project-root", type=str, 
                        help="UNIVERSAL: Explicit project root directory (overrides auto-detection for per-project mode)")
    parser.add_argument("--id-format",
                        choices=["short", "uuid", "custom"],
                        default="short",
                        help="ID format: short (22-char ShortUUID), uuid (36-char legacy), custom (configurable)")
    parser.add_argument("--timeout",
                        type=int,
                        default=60,
                        help="Operation timeout in seconds (default: 60)")

    args = parser.parse_args()
    asyncio.run(serve(args.local_timezone, args.data_dir, args.storage_mode, args.project_root, args.id_format, args.timeout))


if __name__ == "__main__":
    main()