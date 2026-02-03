import asyncio
import time
from pathlib import Path
from shutil import rmtree

from parallel_download.downloader import Downloader
from parallel_download.models import DownloadRequest


async def run_test(name: str, max_concurrent: int, urls: list[str], output_dir: Path):
    print(f"\n🧪 {name} 테스트 시작 (동시성: {max_concurrent})...")

    # 디렉토리 초기화 (테스트 공정성을 위해 삭제 후 재생성)
    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    downloader = Downloader(out_dir=output_dir, timeout=60, max_concurrent=max_concurrent)

    # 중복 파일명 방지를 위해 파일명 지정 (file_01.ext)
    requests = []
    for i, url in enumerate(urls):
        # 간단한 확장자 추출 (실제로는 더 복잡할 수 있음)
        ext = url.split(".")[-1]
        if len(ext) > 4 or "/" in ext:
            ext = "download"
        filename = f"file_{i:02d}.{ext}"
        requests.append(DownloadRequest(url=url, filename=filename))

    start_time = time.perf_counter()
    results = await downloader.download(requests)
    end_time = time.perf_counter()

    duration = end_time - start_time
    success_count = sum(1 for r in results if r.status == "success")

    print(f"✅ 완료: {success_count}/{len(requests)} 파일")
    print(f"⏱️ 소요 시간: {duration:.4f} 초")

    # 경로 정리를 위해 다운로드된 파일 목록 반환 (선택 사항)
    return duration


async def main():
    # 테스트용 URL 목록 (가벼운 파일들 위주로 구성)
    base_urls = [
        "https://raw.githubusercontent.com/devcomfort/parallel_download/main/README.md",
        "https://raw.githubusercontent.com/devcomfort/parallel_download/main/LICENSE",
        "https://www.python.org/static/img/python-logo.png",
        "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
        "https://raw.githubusercontent.com/devcomfort/parallel_download/main/pyproject.toml",
    ]

    # 파일 개수를 늘려 동시성 효과를 확인 (총 10개)
    urls = base_urls * 2

    base_dir = Path("./example_downloads")

    print(f"📥 총 {len(urls)}개의 파일을 다운로드하여 성능 비교를 시작합니다.")
    print(f"📂 기본 저장 경로: {base_dir.absolute()}")

    # 1. 순차 다운로드 테스트 (동시성 1)
    seq_time = await run_test(
        "순차 다운로드 (Sequential)",
        max_concurrent=1,
        urls=urls,
        output_dir=base_dir / "sequential",
    )

    # 2. 병렬 다운로드 테스트 (동시성 5)
    print("\n--------------------------------------------------")
    print("잠시 대기 후 병렬 다운로드 시작...")
    await asyncio.sleep(1)  # 네트워크/리소스 정리 대기

    par_time = await run_test(
        "병렬 다운로드 (Parallel)",
        max_concurrent=5,
        urls=urls,
        output_dir=base_dir / "parallel",
    )

    print("\n📊 성능 비교 결과:")
    print("=" * 30)
    print(f"🐢 순차 다운로드: {seq_time:.4f}s")
    print(f"🐇 병렬 다운로드: {par_time:.4f}s")

    if par_time < seq_time:
        speedup = seq_time / par_time
        print(f"🚀 병렬 처리가 약 {speedup:.2f}배 더 빠릅니다!")
    else:
        print("ℹ️ 파일 크기가 작거나 네트워크 지연이 적어 차이가 미미할 수 있습니다.")


if __name__ == "__main__":
    asyncio.run(main())
