import csv


def save_history_to_csv(filename, history):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "download_mbps", "upload_mbps", "ping_ms", "server"])
        for h in history:
            w.writerow([
                h["timestamp"],
                f"{h['download']:.4f}",
                f"{h['upload']:.4f}",
                h["ping"],
                h["server"]
            ])
