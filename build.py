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
        "id": data.get("id"),
        "name": data.get("name"),
        "group": data.get("group"),
        "rules": [
            {
                "domain_suffix": domains
            }
        ]
    }


# =========================
# 主构建
# =========================
def build(urls):
    result = []

    for url in urls:
        try:
            data = fetch_yaml(url)
            result.append(convert_service(data))
        except Exception as e:
            print(f"[ERROR] {url}: {e}")

    return result


# =========================
# main
# =========================
if __name__ == "__main__":

    urls = [
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/apple_streaming.yml",
        "https://raw.githubusercontent.com/AdguardTeam/HostlistsRegistry/main/services/dropbox.yml",
    ]

    output = build(urls)

    # 创建输出目录
    out_dir = "json"
    os.makedirs(out_dir, exist_ok=True)

    out_file = os.path.join(out_dir, "sing-box.json")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ done -> {out_file}")
