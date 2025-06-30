import re
import requests
import unicodedata
import time
from datetime import datetime

CHANNEL_FILE = "channels.txt"
PRIORITY_FILE = "priority.txt"
LOG_FILE = "log.txt"

URL_SRCS = [
    "https://ott-playlist-worker.prankgokils.workers.dev/",
    "https://raw.githubusercontent.com/H3X0M/gg/refs/heads/main/new_2025.m3u",
    "https://raw.githubusercontent.com/ali-fajar/FORSAT-TV/refs/heads/main/FORSAT%20TV%20NEW%20PRO",
    "https://raw.githubusercontent.com/alkhalifitv/TV/master/playlist",
    "https://raw.githubusercontent.com/ali-fajar/FORSAT-TV/refs/heads/main/IPTV%20FORSAT%20PRO",
    "https://raw.githubusercontent.com/ali-fajar/FORSAT-TV/df22ef82b50540d090ec80e981b4893bb1398a46/iptvforsat",
    "https://github.com/mbahnunung/v3/blob/kn/m3u8/vs1.m3u8",
    "https://raw.githubusercontent.com/mbahnunung/v3/refs/heads/kn/m3u8/z.m3u8",
    "https://raw.githubusercontent.com/riagusmita182/channel/refs/heads/main/new",
    "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25",
    "https://raw.githubusercontent.com/alkhalifitv/TV/refs/heads/master/playlist",
    "https://raw.githubusercontent.com/rgieplaylist/Premium/refs/heads/main/LifeTime",
    "https://raw.githubusercontent.com/hud4156/mytv/refs/heads/main/indovision.m3u",
    "https://raw.githubusercontent.com/rgieplaylist/Premium/refs/heads/main/30JUN2025",
]

def log_error(url, reason):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {url} - GAGAL ({reason})\n")

def download_text(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 503:
            print(f"⚠️ {url} masih memproses, tunggu 10 detik...")
            time.sleep(10)
            return download_text(url)
        else:
            log_error(url, f"Status code {r.status_code}")
            print(f"❌ Lewati: {url} — Status code {r.status_code}")
            return None
    except Exception as e:
        log_error(url, str(e))
        print(f"❌ Lewati: {url} — {e}")
        return None

def normalize_name(name):
    name = re.sub(r'\(.*?\)', '', name)
    name = unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode()
    name = name.lower().replace('hd','').replace('fhd','').replace('v+','').replace('r+','').replace('+','')
    name = re.sub(r'\W+', '', name)
    return name.strip()

def extract_field(pattern, text):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ''

def split_entries(text):
    pattern = (
        r'((?:#.*\n)*'
        r'#EXTINF[^\n]*\n'
        r'(?:#.*\n)*'
        r'https?:\/\/[^\s]+?\.(?:mpd|m3u8)(?:\?[^\s]+)?)'
    )
    return re.findall(pattern, text)

def is_valid_channel_name(name):
    bad_keywords = ['like gecko', 'chrome', 'android', 'dalvik', 'safari', 'applewebkit', 'linux', 'mobile']
    lower = name.lower()
    return all(bad not in lower for bad in bad_keywords) and len(name) > 2

def parse_channel_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    channel_order = []
    channel_meta = {}
    current_group = ""

    for line in lines:
        line = line.strip()
        if line.startswith("====="):
            grp_match = re.search(r'group-title="([^"]+)"', line)
            if grp_match:
                current_group = grp_match.group(1)
            continue
        if line.startswith("Name="):
            name_match = re.search(r'Name="([^"]+)"', line)
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            if name_match:
                display_name = name_match.group(1).strip()
                norm = normalize_name(display_name)
                channel_order.append(norm)
                channel_meta[norm] = {
                    "display_name": display_name,
                    "group-title": current_group,
                    "tvg-logo": logo_match.group(1) if logo_match else None
                }
    return channel_order, channel_meta

def parse_priority_file(path):
    priomap = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    ch, dom = map(str.strip, line.strip().split("=", 1))
                    norm = normalize_name(ch)
                    priomap[norm] = dom
    except FileNotFoundError:
        print(f"⚠️ File {path} tidak ditemukan. Prioritas domain dilewati.")
    return priomap

# --- Main Script ---

print("➡️ Membaca channel.txt...")
channel_order, channel_meta = parse_channel_file(CHANNEL_FILE)

print("➡️ Membaca priority.txt...")
priority_map = parse_priority_file(PRIORITY_FILE)

print("➡️ Mengunduh semua sumber playlist...")
src_texts = []
for u in URL_SRCS:
    print(f"🔗 Mengunduh: {u}")
    content = download_text(u)
    if content:
        src_texts.append(content)

src_dict = {}
unmatched_channels = set()

for txt in src_texts:
    for entry in split_entries(txt):
        name = extract_field(r',([^\n]+)', entry)
        if not name or not is_valid_channel_name(name):
            continue
        norm = normalize_name(name)
        src_dict.setdefault(norm, []).append((entry, name))

print("➡️ Menyusun playlist akhir ...")
out = ["#EXTM3U\n\n"]
used_streams = set()

for norm in channel_order:
    if norm not in src_dict:
        unmatched_channels.add(channel_meta[norm]["display_name"])
        continue

    # Urutkan berdasarkan prioritas
    preferred_domain = priority_map.get(norm, "terabit.web.id")
    def domain_priority(block_entry):
        block, _ = block_entry
        url = next((line for line in block.strip().splitlines() if line.startswith("http")), "")
        return 0 if preferred_domain in url else 1

    src_dict[norm] = sorted(src_dict[norm], key=domain_priority)

    meta = channel_meta.get(norm, {})
    final_name = meta.get("display_name", "")
    group_title = meta.get("group-title", "")
    logo = meta.get("tvg-logo")

    for block, original_name in src_dict[norm]:
        lines = block.strip().splitlines()
        stream_url = next((line for line in lines if line.startswith("http")), None)
        license_key = next((line for line in lines if "#KODIPROP:inputstream.adaptive.license_key" in line), "")

        if not stream_url:
            continue

        uniq_id = f"{stream_url.strip()}|{license_key.strip()}"
        if uniq_id in used_streams:
            continue
        used_streams.add(uniq_id)

        new_block = []
        for line in lines:
            if line.startswith("#EXTINF"):
                tvg_id = final_name.replace(" ", "") + ".id"
                extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{group_title}"'
                if logo:
                    extinf += f' tvg-logo="{logo}"'
                extinf += f',{final_name}'
                new_block.append(extinf)
            else:
                new_block.append(line)

        out.append("\n".join(new_block) + "\n\n")

with open("oantek.m3u", "w", encoding="utf-8") as f:
    f.writelines(out)

if unmatched_channels:
    with open("tidakcocok.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(unmatched_channels)))
    print(f"⚠️ {len(unmatched_channels)} channel tidak ditemukan. Lihat tidakcocok.txt")

print("✅ Playlist selesai dibuat — file oantek.m3u berhasil dibuat.")
