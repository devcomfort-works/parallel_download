"""
Example: Preview download requests using download_dry with tabulate.

This example demonstrates how to use the download_dry method to preview
download requests and display the results in a formatted table using tabulate.

Before running this example:
    pip install tabulate

Usage:
    python download_dry_preview.py
"""

import asyncio
from pathlib import Path
from tabulate import tabulate

from parallel_download import Downloader, DownloadRequest


async def preview_downloads_with_table():
    """
    Preview download requests and display results in a formatted table.

    This function demonstrates:
    - Creating download requests with various URLs and filenames
    - Using download_dry to validate requests without downloading
    - Displaying results in a clean, tabular format
    - Filtering valid and invalid requests
    """
    # Initialize downloader
    downloader = Downloader(
        out_dir=Path("./downloads"),
        timeout="BALANCED",
        max_concurrent=5,
    )

    # Define download requests
    # Mix of valid and invalid requests for demonstration
    requests = [
        DownloadRequest(url="https://example.com/document.pdf", filename="document.pdf"),
        DownloadRequest(url="https://example.com/data.csv", filename="data.csv"),
        DownloadRequest(
            url="https://httpbin.org/bytes/1024", filename="sample_1kb.bin"
        ),
        DownloadRequest(url="https://example.com/report.xlsx", filename="report.xlsx"),
        # Invalid cases
        DownloadRequest(
            url="https://example.com/file.zip", filename="invalid/path/file.zip"
        ),
        DownloadRequest(url="https://example.com/archive.tar", filename="bad\\file.tar"),
    ]

    print("\n" + "=" * 80)
    print("DOWNLOAD REQUEST PREVIEW".center(80))
    print("=" * 80 + "\n")

    # Preview requests
    previews = await downloader.download_dry(requests)

    # Prepare data for table
    table_data = []
    for idx, preview in enumerate(previews, 1):
        status_icon = "✓" if preview.status == "valid" else "✗"
        reason = preview.reason if preview.reason else "-"
        table_data.append(
            [
                idx,
                status_icon,
                preview.filename,
                preview.status.upper(),
                reason,
            ]
        )

    # Display main results table
    headers = ["#", "Status", "Filename", "Validation", "Error/Notes"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Summary statistics
    print("\n" + "-" * 80)
    valid_count = sum(1 for p in previews if p.status == "valid")
    invalid_count = sum(1 for p in previews if p.status == "invalid")

    summary_data = [
        ["Total Requests", len(previews)],
        ["Valid Requests", valid_count],
        ["Invalid Requests", invalid_count],
        ["Validation Rate", f"{(valid_count / len(previews) * 100):.1f}%"],
    ]

    print("\nSUMMARY:")
    print(tabulate(summary_data, headers=["Metric", "Count"], tablefmt="simple"))
    print("-" * 80 + "\n")

    # Display valid requests in detail
    valid_previews = [p for p in previews if p.status == "valid"]
    if valid_previews:
        print("✓ VALID REQUESTS (Ready for download):\n")
        valid_data = [
            [idx + 1, preview.filename, preview.url]
            for idx, preview in enumerate(valid_previews)
        ]
        print(tabulate(valid_data, headers=["#", "Filename", "URL"], tablefmt="grid"))

    # Display invalid requests in detail
    invalid_previews = [p for p in previews if p.status == "invalid"]
    if invalid_previews:
        print("\n✗ INVALID REQUESTS (Cannot be downloaded):\n")
        invalid_data = [
            [idx + 1, preview.filename, preview.reason]
            for idx, preview in enumerate(invalid_previews)
        ]
        print(
            tabulate(
                invalid_data, headers=["#", "Filename", "Error"], tablefmt="grid"
            )
        )

    print()


async def preview_with_batch_size():
    """
    Preview multiple batches of download requests.

    This function demonstrates handling large numbers of requests
    by processing them in batches and displaying results per batch.
    """
    downloader = Downloader(out_dir=Path("./downloads"))

    # Generate test data: 3 batches with different characteristics
    batches = [
        {
            "name": "Batch 1: Small Files",
            "requests": [
                DownloadRequest(
                    url="https://httpbin.org/bytes/1024", filename=f"small_{i}.bin"
                )
                for i in range(3)
            ],
        },
        {
            "name": "Batch 2: Mixed Valid/Invalid",
            "requests": [
                DownloadRequest(url="https://example.com/valid.pdf", filename="valid.pdf"),
                DownloadRequest(
                    url="https://example.com/invalid.zip", filename="bad/invalid.zip"
                ),
                DownloadRequest(url="https://example.com/ok.csv", filename="ok.csv"),
            ],
        },
        {
            "name": "Batch 3: API Endpoints",
            "requests": [
                DownloadRequest(
                    url="https://api.example.com/data?format=json", filename="api_data.json"
                ),
                DownloadRequest(
                    url="https://api.example.com/export?token=abc123",
                    filename="export.csv",
                ),
            ],
        },
    ]

    print("\n" + "=" * 80)
    print("BATCH PREVIEW REPORT".center(80))
    print("=" * 80 + "\n")

    # Process each batch
    batch_summary = []
    for batch_idx, batch in enumerate(batches, 1):
        print(f"\n{batch['name']}")
        print("-" * 80)

        previews = await downloader.download_dry(batch["requests"])

        # Prepare batch data
        batch_data = []
        for preview in previews:
            status_icon = "✓" if preview.status == "valid" else "✗"
            batch_data.append(
                [
                    status_icon,
                    preview.filename,
                    preview.status.upper(),
                    preview.reason if preview.reason else "-",
                ]
            )

        print(tabulate(batch_data, headers=["Status", "Filename", "Validation", "Notes"]))

        # Batch statistics
        valid = sum(1 for p in previews if p.status == "valid")
        invalid = sum(1 for p in previews if p.status == "invalid")
        batch_summary.append([batch['name'], len(previews), valid, invalid])

    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL BATCH SUMMARY")
    print("=" * 80 + "\n")
    print(
        tabulate(
            batch_summary,
            headers=["Batch", "Total", "Valid", "Invalid"],
            tablefmt="grid",
        )
    )
    print()


async def preview_with_filtering():
    """
    Preview requests and filter results based on validation status.

    This function demonstrates:
    - Creating requests from a list of URLs
    - Using download_dry to validate
    - Filtering and displaying specific results
    - Using filtered results for subsequent operations
    """
    downloader = Downloader(out_dir=Path("./downloads"))

    # List of URLs to validate
    urls_and_filenames = [
        ("https://example.com/report.pdf", "report.pdf"),
        ("https://example.com/data.xlsx", "data.xlsx"),
        ("https://example.com/config", "config"),  # No extension
        ("https://example.com/archive.tar.gz", "archive.tar.gz"),
        ("https://example.com/backup", "backup/file"),  # Invalid path
        ("https://api.example.com/download?id=123", "api_download.bin"),
    ]

    requests = [
        DownloadRequest(url=url, filename=filename)
        for url, filename in urls_and_filenames
    ]

    print("\n" + "=" * 80)
    print("REQUEST VALIDATION WITH FILTERING".center(80))
    print("=" * 80 + "\n")

    # Preview all requests
    previews = await downloader.download_dry(requests)

    # Filter valid and invalid
    valid_previews = [p for p in previews if p.status == "valid"]
    invalid_previews = [p for p in previews if p.status == "invalid"]

    # Display comprehensive report
    print("\n1. ALL REQUESTS")
    print("-" * 80)
    all_data = [
        [
            preview.filename,
            preview.status.upper(),
            preview.reason if preview.reason else "-",
        ]
        for preview in previews
    ]
    print(tabulate(all_data, headers=["Filename", "Status", "Reason"], tablefmt="simple"))

    # Valid requests only
    if valid_previews:
        print("\n2. VALID REQUESTS (Can be downloaded)")
        print("-" * 80)
        valid_data = [
            [preview.filename, preview.url] for preview in valid_previews
        ]
        print(
            tabulate(
                valid_data, headers=["Filename", "URL"], tablefmt="grid"
            )
        )

    # Invalid requests only
    if invalid_previews:
        print("\n3. INVALID REQUESTS (Need manual action)")
        print("-" * 80)
        invalid_data = [
            [preview.filename, preview.reason] for preview in invalid_previews
        ]
        print(
            tabulate(
                invalid_data, headers=["Filename", "Reason"], tablefmt="grid"
            )
        )

    # Summary with percentages
    print("\n4. STATISTICS")
    print("-" * 80)
    stats = [
        ["Total", len(previews)],
        ["Valid", f"{len(valid_previews)} ({len(valid_previews)/len(previews)*100:.1f}%)"],
        [
            "Invalid",
            f"{len(invalid_previews)} ({len(invalid_previews)/len(previews)*100:.1f}%)",
        ],
    ]
    print(tabulate(stats, headers=["Metric", "Value"], tablefmt="simple"))
    print()


async def main():
    """Run all preview examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "PARALLEL DOWNLOAD - DRY RUN PREVIEW EXAMPLES".center(78) + "║")
    print("╚" + "=" * 78 + "╝")

    # Example 1: Basic preview with table
    await preview_downloads_with_table()

    # Example 2: Batch preview
    await preview_with_batch_size()

    # Example 3: Filtering preview
    await preview_with_filtering()

    print("\n" + "=" * 80)
    print("All examples completed!".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

