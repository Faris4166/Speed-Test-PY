import speedtest
from utils.converter import bps_to_mbps


def run_full_test(stop_flag, status_callback):
    st = speedtest.Speedtest()

    status_callback("Finding best server...")
    best = st.get_best_server()
    if stop_flag.is_set():
        return None

    server_name = f"{best['sponsor']} ({best['name']}, {best['country']})"
    ping_val = best.get("latency", 0.0)

    status_callback("Testing download...")
    dl = st.download()
    if stop_flag.is_set():
        return None

    status_callback("Testing upload...")
    up = st.upload()
    if stop_flag.is_set():
        return None

    result = st.results.dict()

    return {
        "server": server_name,
        "download": bps_to_mbps(dl),
        "upload": bps_to_mbps(up),
        "ping": result.get("ping", ping_val)
    }
