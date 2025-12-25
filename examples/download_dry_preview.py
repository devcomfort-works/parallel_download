"""
Example: Preview download requests using download_dry with tabulate.

Demonstrates when to use download_dry() to validate filenames before downloading:
1. Auto extraction - URL has clear filename, no explicit specification needed
2. Must specify - URL ambiguous, explicit filename required
3. Error detection - dry_run catches invalid filenames early

Before running:
    pip install tabulate
"""

import asyncio
from pathlib import Path
from tabulate import tabulate

from parallel_download import Downloader, DownloadRequest


async def auto_extraction_scenario():
    """
    Scenario 1: Auto Extraction Works

    When URL clearly contains filename, download_dry confirms it extracts correctly.
    No need to explicitly specify filename.
    """
    print("\n" + "=" * 80)
    print("SCENARIO 1: AUTO EXTRACTION - URL clearly contains filename".center(80))
    print("=" * 80)
    print("Decision: No explicit filename needed, URL is clear enough\n")

    downloader = Downloader(out_dir=Path("./downloads"))

    # URLs where filename is obvious from URL path
    requests = [
        DownloadRequest(url="https://example.com/documents/report.pdf"),
        DownloadRequest(url="https://example.com/images/logo.png"),
        DownloadRequest(url="https://cdn.example.com/data/dataset.csv"),
        DownloadRequest(url="https://github.com/repo/releases/v1.0.tar.gz"),
        DownloadRequest(url="https://example.com/download/file.zip?token=abc123"),
        DownloadRequest(url="https://api.example.com/exports/users.json"),
    ]

    previews = await downloader.download_dry(requests)

    table_data = [
        [
            req.url,
            p.filename,
            p.status.upper(),
            p.reason if p.status == "invalid" else "-",
        ]
        for req, p in zip(requests, previews)
    ]

    print(
        tabulate(
            table_data,
            headers=["URL", "Extracted Filename", "Status", "Error"],
            tablefmt="grid",
        )
    )
    print()


async def must_specify_scenario():
    """
    Scenario 2: Must Specify Filename

    When URL is ambiguous/unclear, dry_run reveals you MUST explicitly specify filename.
    This is where dry_run adds value - catches problem early.
    """
    print("=" * 80)
    print(
        "SCENARIO 2: MUST SPECIFY - URL ambiguous, filename extraction fails".center(80)
    )
    print("=" * 80)
    print("Decision: Must explicitly specify filename, URL alone insufficient\n")

    downloader = Downloader(out_dir=Path("./downloads"))

    # Ambiguous URLs requiring explicit filename
    ambiguous_urls = [
        ("https://example.com", "No path information"),
        ("https://example.com/api/v1/download", "No file extension"),
        ("https://example.com/files/", "Directory path, not file"),
        ("https://api.example.com/data?id=123", "Only query parameters"),
    ]

    print("Without explicit filename (dry_run catches these):\n")

    requests = [
        DownloadRequest(url=url, filename="temp.bin") for url, _ in ambiguous_urls
    ]
    previews = await downloader.download_dry(requests)

    error_data = [
        [url, desc, p.status.upper(), p.reason if p.status == "invalid" else "-"]
        for (url, desc), p in zip(ambiguous_urls, previews)
    ]

    print(
        tabulate(
            error_data, headers=["URL", "Type", "Status", "Error"], tablefmt="grid"
        )
    )

    print("\nSolution - Provide explicit filename:\n")

    requests_fixed = [
        DownloadRequest(url="https://example.com", filename="index.html"),
        DownloadRequest(url="https://example.com/api/v1/download", filename="data.bin"),
        DownloadRequest(url="https://example.com/files/", filename="archive.zip"),
        DownloadRequest(
            url="https://api.example.com/data?id=123", filename="export.json"
        ),
    ]

    previews_fixed = await downloader.download_dry(requests_fixed)

    fixed_data = [
        [
            req.url,
            p.filename,
            p.status.upper(),
            p.reason if p.status == "invalid" else "-",
        ]
        for req, p in zip(requests_fixed, previews_fixed)
    ]

    print(
        tabulate(
            fixed_data,
            headers=["URL", "Specified Filename", "Status", "Error"],
            tablefmt="grid",
        )
    )
    print()


async def validation_errors_scenario():
    """
    Scenario 3: Validation Errors

    dry_run detects invalid filenames (path separators) BEFORE download.
    This prevents runtime failures.
    """
    print("=" * 80)
    print("SCENARIO 3: VALIDATION - dry_run detects invalid filenames early".center(80))
    print("=" * 80)
    print("Decision: Fix filename issues before actual download\n")

    downloader = Downloader(out_dir=Path("./downloads"))

    print("Invalid filenames (will fail):\n")

    invalid_requests = [
        DownloadRequest(url="https://example.com/file.zip", filename="docs/file.zip"),
        DownloadRequest(
            url="https://example.com/data.csv", filename="data\\backup\\file.csv"
        ),
        DownloadRequest(
            url="https://example.com/image.png", filename="imgs/subfolder/image.png"
        ),
    ]

    invalid_previews = await downloader.download_dry(invalid_requests)

    invalid_data = [
        [
            req.url,
            p.filename,
            p.status.upper(),
            p.reason if p.status == "invalid" else "-",
        ]
        for req, p in zip(invalid_requests, invalid_previews)
    ]

    print(
        tabulate(
            invalid_data,
            headers=["URL", "Invalid Filename", "Status", "Error"],
            tablefmt="grid",
        )
    )

    print("\nFixed filenames (all valid):\n")

    valid_requests = [
        DownloadRequest(url="https://example.com/file.zip", filename="file.zip"),
        DownloadRequest(url="https://example.com/data.csv", filename="data_backup.csv"),
        DownloadRequest(url="https://example.com/image.png", filename="image.png"),
    ]

    valid_previews = await downloader.download_dry(valid_requests)

    valid_data = [
        [
            req.url,
            p.filename,
            p.status.upper(),
            p.reason if p.status == "invalid" else "-",
        ]
        for req, p in zip(valid_requests, valid_previews)
    ]

    print(
        tabulate(
            valid_data,
            headers=["URL", "Valid Filename", "Status", "Error"],
            tablefmt="grid",
        )
    )
    print()


async def special_characters_scenario():
    """
    Scenario 4: Special Characters Support

    dry_run shows which special characters are supported in filenames.
    """
    print("=" * 80)
    print("SCENARIO 4: SPECIAL CHARACTERS - What filename patterns work".center(80))
    print("=" * 80)
    print("Decision: Use supported characters in filenames\n")

    downloader = Downloader(out_dir=Path("./downloads"))

    special_char_files = [
        "report_2024-01-15.pdf",
        "file(v2.1).zip",
        "data@backup.csv",
        "document_final[APPROVED].xlsx",
        "archive~old.tar.gz",
        "日本語ファイル.txt",
        "файл_документ.docx",
        "中文_数据.json",
    ]

    requests = [
        DownloadRequest(url="https://example.com/download", filename=name)
        for name in special_char_files
    ]

    previews = await downloader.download_dry(requests)

    char_data = [
        [req.url, name, p.status.upper(), p.reason if p.status == "invalid" else "-"]
        for req, name, p in zip(requests, special_char_files, previews)
    ]

    print(
        tabulate(
            char_data,
            headers=["URL", "Filename Pattern", "Status", "Error"],
            tablefmt="grid",
        )
    )
    print()


async def batch_validation_scenario():
    """
    Scenario 5: Batch Validation

    dry_run on multiple requests shows which ones will fail before real download.
    Useful for filtering valid requests from mixed list.
    """
    print("=" * 80)
    print("SCENARIO 5: BATCH VALIDATION - Check multiple requests at once".center(80))
    print("=" * 80)
    print("Decision: Pre-validate batch before actual download\n")

    downloader = Downloader(out_dir=Path("./downloads"))

    # Mixed batch: some valid, some invalid
    mixed_requests = [
        DownloadRequest(url="https://example.com/doc1.pdf", filename="document1.pdf"),
        DownloadRequest(
            url="https://example.com/data", filename="data/file.csv"
        ),  # Invalid
        DownloadRequest(url="https://example.com/img.png", filename="image.png"),
        DownloadRequest(
            url="https://example.com/arch", filename="archive\\backup.zip"
        ),  # Invalid
        DownloadRequest(
            url="https://example.com/file.xlsx", filename="spreadsheet.xlsx"
        ),
    ]

    previews = await downloader.download_dry(mixed_requests)

    valid_count = sum(1 for p in previews if p.status == "valid")
    invalid_count = sum(1 for p in previews if p.status == "invalid")

    batch_data = []
    for req, preview in zip(mixed_requests, previews):
        status_icon = "✓" if preview.status == "valid" else "✗"
        batch_data.append(
            [
                req.url,
                status_icon,
                preview.filename,
                preview.status.upper(),
                preview.reason if preview.reason else "-",
            ]
        )

    print(
        tabulate(
            batch_data,
            headers=["URL", "✓/✗", "Filename", "Status", "Error/Note"],
            tablefmt="grid",
        )
    )

    print(f"\nSummary: {valid_count} valid, {invalid_count} invalid")
    print(f"Ready to download: {valid_count} files\n")


async def main():
    """Run all scenarios."""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + "PARALLEL DOWNLOAD - DRY_RUN DECISION SCENARIOS".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print("\nWhen to use download_dry():")
    print("• Validate filenames BEFORE actual download")
    print("• Decide if explicit filename specification needed")
    print("• Catch invalid patterns early")

    await auto_extraction_scenario()
    await must_specify_scenario()
    await validation_errors_scenario()
    await special_characters_scenario()
    await batch_validation_scenario()

    print("=" * 80)
    print("All scenarios demonstrated!".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
