#!/bin/bash
# Ping IndexNow (Bing, Yandex, Seznam, Naver…) with every URL in the live sitemap.
# Run AFTER a deploy is live:  bash ~/Desktop/vow-seo-build/indexnow.sh
# Optional: pass specific URLs instead, e.g. bash indexnow.sh https://vow.byarnav.com/changelog/
set -euo pipefail
HOST="vow.byarnav.com"
KEY="873d39409550ed61a39ebe5852a229ae"

# 1. The key file must be live first, or IndexNow rejects the request (403).
code=$(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/$KEY.txt")
if [ "$code" != "200" ]; then echo "Key file not live yet (HTTP $code). Deploy first."; exit 1; fi

# 2. URL list: arguments, or every <loc> in the live sitemap.
if [ "$#" -gt 0 ]; then
  URLS=$(printf '%s\n' "$@")
else
  URLS=$(curl -s "https://$HOST/sitemap.xml" | sed -n 's|.*<loc>\(.*\)</loc>.*|\1|p')
fi
LIST=$(printf '%s\n' "$URLS" | sed 's/.*/"&"/' | paste -sd, -)

echo "Submitting:"; printf '  %s\n' $URLS
curl -s -o /dev/null -w "IndexNow response: HTTP %{http_code}\n" \
  -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY.txt\",\"urlList\":[$LIST]}"
echo "200 or 202 = accepted. 403 = key file not found. 422 = URL/host mismatch."
