import requests
import yaml
import json
import re
import os

# =========================
# 提取 domain（无损）
# =========================
def extract_domain(rule: str):
    if not rule:
        return None

    match = re.match(r"\|\|([^\/\^\s]+)", rule)
    if match:
        return match.group(1).strip()

    return None


# =========================
# 下载 YAML
# =========================
def fetch_yaml(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return yaml.safe_load(r.text)


# =========================
# 转换 service
# =========================
def convert_service(data):
    domains = []
    seen = set()

    for r in data.get("rules", []):
        domain = extract_domain(r)
        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

    return {
        "version": 4,
        "rules": [
            {
                "domain_suffix": domains
            }
        ]
    }


# =========================
# URL → 文件名
# =========================
def get_filename(url):
    return url.split("/")[-1].replace(".yml", ".json")


# =========================
# 主函数
# =========================
if __name__ == "__main__":

    urls = [
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/apple_streaming.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/dropbox.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bluesky.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/chatgpt.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/youtube.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/bilibili.yml",
    ]

    out_dir = "json"
    os.makedirs(out_dir, exist_ok=True)

    for url in urls:
        try:
            data = fetch_yaml(url)
            output = convert_service(data)

            filename = get_filename(url)
            out_path = os.path.join(out_dir, filename)

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"✅ generated -> {out_path}")

        except Exception as e:
            print(f"❌ error {url}: {e}")
