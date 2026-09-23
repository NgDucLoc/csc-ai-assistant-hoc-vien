#!/usr/bin/env bash
# Nhánh cứu hộ — công cụ 5 phút, không phải công cụ qua đêm.
#
# Sáu session ghép thành ba ngày. Giữa buổi sáng và buổi chiều chỉ có giờ nghỉ
# trưa, nên nhóm tụt lại phải bắt kịp trong vài phút chứ không phải sau một đêm.
#
# Lệnh này:
#   - chạy dưới 2 phút, hoạt động OFFLINE từ git bundle nếu không có mạng
#   - đồng bộ src/, data/ và .cache/ từ solution/session-N
#   - KHÔNG đụng vào docs/ — canvas, blueprint và ADR là deliverable của nhóm,
#     ghi đè lên chúng là xóa mất điểm của học viên
#   - in ra bản khác biệt để nhóm biết mình vừa nhận cái gì, thay vì nhận một
#     hộp đen rồi không giải thích được ở phần phản biện Session 6
#
# Dùng:  ./scripts/rescue.sh 3
#        ./scripts/rescue.sh 3 --dry-run
#        ./scripts/rescue.sh 3 --bundle /Volumes/USB/csc.bundle

set -euo pipefail

SESSION="${1:-}"
shift || true

DRY_RUN=0
BUNDLE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --bundle)  BUNDLE="$2"; shift 2 ;;
    *) echo "Tham số không hiểu: $1" >&2; exit 2 ;;
  esac
done

if [[ ! "$SESSION" =~ ^[1-6]$ ]]; then
  cat >&2 <<'USAGE'
Dùng: ./scripts/rescue.sh <1..6> [--dry-run] [--bundle ĐƯỜNG_DẪN]

  <N>        Số buổi vừa kết thúc. Nhánh solution/session-N là trạng thái repo
             ĐÚNG SAU khi kết thúc buổi đó.
  --dry-run  Chỉ in ra sẽ thay đổi những gì, không ghi đè.
  --bundle   Dùng git bundle offline trên USB khi mạng lớp học không dùng được.
USAGE
  exit 2
fi

cd "$(dirname "$0")/.."
BRANCH="solution/session-${SESSION}"
SYNC_PATHS=(src data .cache tests scripts eval promptfooconfig.yaml pyproject.toml)

echo "═══ CỨU HỘ · ${BRANCH} ═══"

# --- 1. Bảo vệ công việc của nhóm trước khi làm gì khác ---------------------
if [[ -n "$(git status --porcelain)" ]]; then
  STASH="rescue-$(date +%H%M%S)"
  echo "▸ Cất tạm thay đổi chưa commit vào stash '${STASH}' (lấy lại: git stash pop)"
  [[ $DRY_RUN -eq 0 ]] && git stash push -u -m "$STASH" >/dev/null
fi

# --- 2. Lấy nhánh cứu hộ, ưu tiên bundle offline ---------------------------
if [[ -n "$BUNDLE" ]]; then
  echo "▸ Nạp từ bundle offline: ${BUNDLE}"
  [[ -f "$BUNDLE" ]] || { echo "  KHÔNG tìm thấy bundle. Hỏi giảng viên USB cứu hộ." >&2; exit 1; }
  [[ $DRY_RUN -eq 0 ]] && git fetch "$BUNDLE" "+refs/heads/${BRANCH}:refs/remotes/rescue/${BRANCH}"
  SOURCE="refs/remotes/rescue/${BRANCH}"
else
  echo "▸ Lấy ${BRANCH} từ origin"
  if ! git fetch --quiet origin "${BRANCH}:refs/remotes/origin/${BRANCH}" 2>/dev/null; then
    echo "  Không lấy được từ mạng. Hỏi giảng viên USB cứu hộ rồi chạy lại với:"
    echo "      ./scripts/rescue.sh ${SESSION} --bundle /Volumes/USB/csc.bundle"
    exit 1
  fi
  SOURCE="refs/remotes/origin/${BRANCH}"
fi

# --- 3. In bản khác biệt trước khi ghi đè -----------------------------------
echo
echo "▸ Những tệp sẽ được thay thế:"
git diff --stat "HEAD..${SOURCE}" -- "${SYNC_PATHS[@]}" || true
echo
echo "▸ docs/ KHÔNG bị đụng tới. Canvas, blueprint và ADR của nhóm giữ nguyên."

if [[ $DRY_RUN -eq 1 ]]; then
  echo
  echo "(--dry-run: chưa ghi gì cả)"
  exit 0
fi

# --- 4. Đồng bộ ------------------------------------------------------------
echo
for path in "${SYNC_PATHS[@]}"; do
  if git cat-file -e "${SOURCE}:${path}" 2>/dev/null; then
    git checkout "${SOURCE}" -- "${path}"
    echo "  đồng bộ  ${path}"
  fi
done

# --- 5. Xác nhận trạng thái -------------------------------------------------
echo
echo "▸ Kiểm tra nhanh sau cứu hộ:"
if python3 -c "import sys; sys.path.insert(0,'.'); import src.config" 2>/dev/null; then
  echo "  [PASS]  mã nguồn nạp được"
else
  echo "  [FAIL]  mã nguồn chưa nạp được — chạy 'uv sync' rồi thử lại"
fi

cat <<NEXT

═══ XONG ═══

Bước tiếp theo:
  1. uv run python scripts/checkpoint.py ${SESSION}     xác nhận đã đủ điều kiện
  2. git add -A && git commit -m "[LAB-${SESSION}] Đồng bộ từ nhánh cứu hộ"
  3. Tiếp tục buổi hiện tại từ đây.

Nhóm vẫn phải giải thích được mã nguồn ở phần phản biện Session 6. Dành 5 phút
đọc bản khác biệt ở trên trước khi đi tiếp.
NEXT
