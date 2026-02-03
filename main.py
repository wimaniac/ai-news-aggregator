from app.runner import run_scrapers

def main(hours: int = 24):
    result = run_scrapers(hours=hours)
    print(f"Đã cào thành công {len(result['youtube'])} YouTube videos")
    print(f"Đã cào thành công {len(result['news'])} bài báo.")
if __name__ == "__main__":
    main(hours=100)