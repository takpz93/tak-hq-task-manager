"""
タスク管理 Webアプリ
起動: streamlit run app.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))
os.environ.setdefault("GOOGLE_CREDENTIALS", str(DIR / "credentials.json"))
os.environ.setdefault("GOOGLE_TOKEN",       str(DIR / "token.json"))

TZ      = ZoneInfo("Asia/Tokyo")
DAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]

# ── 優先度 ────────────────────────────────────────────────────────
PRIORITY = {
    "S": {"label": "S｜緊急 × 重要",     "color": "#E53935", "rank": 4},
    "A": {"label": "A｜緊急 × 低重要",   "color": "#FB8C00", "rank": 3},
    "B": {"label": "B｜低緊急 × 重要",   "color": "#1E88E5", "rank": 2},
    "C": {"label": "C｜低緊急 × 低重要", "color": "#43A047", "rank": 1},
}
PRIORITY_KEYS = list(PRIORITY.keys())

# ── 動画制作 管理表 ──────────────────────────────────────────────
# 既定のスプレッドシートID（環境変数 VIDEO_SHEET_ID / st.secrets で上書き可）
DEFAULT_VIDEO_SHEET_ID = "1jwJZt8fqMjErtnFrTjKk9kBnBNe0n0m76HqbpvS5LTU"

def video_sheet_id() -> str:
    """設定済みのスプレッドシートIDを返す（secrets > 環境変数 > 既定）。"""
    try:
        sid = st.secrets.get("video_sheet_id")  # type: ignore[attr-defined]
        if sid:
            return str(sid)
    except Exception:
        pass
    return os.environ.get("VIDEO_SHEET_ID", DEFAULT_VIDEO_SHEET_ID)

# ── ページ設定 ────────────────────────────────────────────────────
st.set_page_config(page_title="タスク管理", page_icon="📋",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .stApp, body { background:#FDFBF5 !important; }
  section[data-testid="stSidebar"] > div { background:#F5F2EA !important; }
  .main .block-container { background:#FDFBF5; padding-top:1rem; }
  html,body,[class*="css"] { font-family:'Helvetica Neue',Arial,sans-serif; }
  h1,h2,h3 { color:#2d2d2d !important; }

  .card {
    background:#fff; border:1px solid #e8e4db;
    border-radius:12px; padding:16px 20px; margin:8px 0;
  }
  .card-title { font-size:1rem; font-weight:600; color:#2d2d2d; margin-bottom:4px; }
  .card-sub   { font-size:0.82rem; color:#8a7f72; }

  .badge {
    display:inline-block; border-radius:6px; padding:2px 9px;
    font-size:0.78rem; font-weight:700; color:#fff; margin-right:6px;
  }
  .sec-lbl {
    font-size:0.7rem; font-weight:700; color:#8a7f72;
    text-transform:uppercase; letter-spacing:.1em; margin:12px 0 6px;
  }
  .alert-warn {
    background:#fff8e1; border-left:4px solid #f9a825;
    border-radius:8px; padding:10px 14px; font-size:0.88rem; color:#5d4037;
    margin:8px 0;
  }
  .alert-ok {
    background:#e8f5e9; border-left:4px solid #43a047;
    border-radius:8px; padding:10px 14px; font-size:0.88rem; color:#1b5e20;
    margin:8px 0;
  }
  .stButton > button { border-radius:8px !important; font-weight:500 !important; }
  iframe { border-radius:10px; }
</style>
""", unsafe_allow_html=True)


# ── サービス ──────────────────────────────────────────────────────
@st.cache_resource
def get_cal():
    from secretary import calendar_ops
    return calendar_ops

@st.cache_resource
def get_tsk():
    from secretary import tasks_ops
    return tasks_ops


# ── メタデータ ────────────────────────────────────────────────────
APP_KEY = "task_manager_v2"

def is_app_task(ev: dict) -> bool:
    try:
        return json.loads(ev.get("description", "")).get("app") == APP_KEY
    except Exception:
        return False

def get_meta(ev: dict) -> dict:
    try:
        return json.loads(ev.get("description", ""))
    except Exception:
        return {}

def task_color(priority: str) -> str:
    return PRIORITY.get(priority, PRIORITY["C"])["color"]


# ── スロット検索 ──────────────────────────────────────────────────
def _get_task_busy_ranges() -> list[tuple]:
    """Google Tasks に登録済みのスケジュール済み時間帯を取得（busy 計算用）"""
    tsk = get_tsk()
    busy = []
    try:
        raw = tsk.list_all_tasks()
    except Exception:
        return busy
    for t in raw:
        try:
            meta = json.loads(t.get("notes", "{}"))
        except Exception:
            continue
        if meta.get("app") != APP_KEY:
            continue
        s_str = meta.get("scheduled_start", "")
        e_str = meta.get("scheduled_end", "")
        if s_str and e_str:
            try:
                busy.append((
                    datetime.fromisoformat(s_str).astimezone(TZ),
                    datetime.fromisoformat(e_str).astimezone(TZ),
                ))
            except Exception:
                pass
    return busy


def find_free_slots(duration_min: int, start_from: date,
                    deadline: "date | datetime", n: int = 3) -> list[datetime]:
    from secretary.calendar_ops import list_events_range, utc_z
    WORK_START, WORK_END, STEP = 6, 23, 30

    start_dt = max(
        datetime.now(TZ).replace(second=0, microsecond=0) + timedelta(minutes=STEP),
        datetime(start_from.year, start_from.month, start_from.day, WORK_START, 0, tzinfo=TZ),
    )
    if isinstance(deadline, datetime):
        end_dt = deadline if deadline.tzinfo else deadline.replace(tzinfo=TZ)
    else:
        end_dt = datetime(deadline.year, deadline.month, deadline.day, WORK_END, 0, tzinfo=TZ)

    # Google Calendar の既存予定
    busy_raw = list_events_range(
        time_min=utc_z(start_dt), time_max=utc_z(end_dt), max_results=500)
    busy = []
    for ev in busy_raw:
        s = ev.get("start", {}).get("dateTime")
        e = ev.get("end",   {}).get("dateTime")
        if s and e:
            busy.append((
                datetime.fromisoformat(s).astimezone(TZ),
                datetime.fromisoformat(e).astimezone(TZ),
            ))
    # Google Tasks のスケジュール済み時間帯も busy に追加
    busy.extend(_get_task_busy_ranges())

    cur = start_dt
    if cur.minute % STEP:
        cur += timedelta(minutes=STEP - cur.minute % STEP)
    cur = cur.replace(second=0, microsecond=0)

    slots = []
    while cur + timedelta(minutes=duration_min) <= end_dt and len(slots) < n:
        if cur.hour < WORK_START:
            cur = cur.replace(hour=WORK_START, minute=0); continue
        if cur.hour >= WORK_END:
            cur = (cur + timedelta(days=1)).replace(hour=WORK_START, minute=0); continue
        slot_end = cur + timedelta(minutes=duration_min)
        if not any(s < slot_end and e > cur for s, e in busy):
            slots.append(cur)
            cur = slot_end
        else:
            cur += timedelta(minutes=STEP)
    return slots


def find_lower_priority_tasks(my_priority: str, deadline: date) -> list[dict]:
    """Google Tasks から自分より低い優先度のタスクを期限前から探す"""
    tsk     = get_tsk()
    my_rank = PRIORITY[my_priority]["rank"]
    result  = []
    try:
        raw = tsk.list_all_tasks()
    except Exception:
        return result
    for t in raw:
        try:
            meta = json.loads(t.get("notes", "{}"))
        except Exception:
            continue
        if meta.get("app") != APP_KEY:
            continue
        p = meta.get("priority", "C")
        if PRIORITY.get(p, PRIORITY["C"])["rank"] >= my_rank:
            continue
        s_str = meta.get("scheduled_start", "")
        if not s_str:
            continue
        try:
            sched_dt = datetime.fromisoformat(s_str).astimezone(TZ)
        except Exception:
            continue
        if sched_dt.date() > deadline:
            continue
        result.append({
            "ev_id":    t["id"],
            "title":    meta.get("title", t.get("title", "")),
            "priority": p,
            "start":    s_str,
            "duration": meta.get("duration_minutes", 60),
            "due_date": meta.get("due_date", ""),
        })
    return result


# ── タスク登録 ────────────────────────────────────────────────────
def register_task(title: str, priority: str, due_date: date,
                  due_allday: bool, due_time_str: str,
                  duration: int, slot: datetime,
                  memo: str = "") -> dict:
    """
    Google Calendar 予定（時刻ブロック）+ Google Tasks（チェックリスト）の両方に登録。
    Google Tasks API は時刻指定不可のため、カレンダー予定で時刻を管理する。
    """
    cal     = get_cal()
    tsk     = get_tsk()
    summary = f"[{priority}] {title}"
    slot_end = slot + timedelta(minutes=duration)
    meta_dict = {
        "app":              APP_KEY,
        "title":            title,
        "priority":         priority,
        "due_date":         due_date.isoformat(),
        "due_allday":       due_allday,
        "due_time":         due_time_str,
        "duration_minutes": duration,
        "memo":             memo,
        "scheduled_start":  slot.isoformat(),
        "scheduled_end":    slot_end.isoformat(),
    }
    # Google Tasks のみに登録
    due_str = slot.astimezone(timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")
    return tsk.add_task(title,
                        notes=json.dumps(meta_dict, ensure_ascii=False),
                        due=due_str)


# ── イベント取得 ──────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_events() -> list[dict]:
    """Google Calendar の全予定を取得（アプリタスク含む）"""
    cal = get_cal()
    try:
        return cal.list_events(days=90, days_past=7, max_results=500)
    except Exception:
        return []


def load_cal_events():
    return [ev for ev in load_events() if not is_app_task(ev)]


@st.cache_data(ttl=60)
def load_app_tasks() -> list[dict]:
    """Google Tasks API からアプリタスクを統一形式で返す"""
    tsk = get_tsk()
    try:
        raw = tsk.list_all_tasks()
    except Exception:
        return []
    result = []
    for t in raw:
        try:
            meta = json.loads(t.get("notes", "{}"))
        except Exception:
            meta = {}
        if meta.get("app") != APP_KEY:
            continue
        s_str = meta.get("scheduled_start", "")
        e_str = meta.get("scheduled_end",   "")
        try:
            sched_dt = datetime.fromisoformat(s_str).astimezone(TZ) if s_str else None
        except Exception:
            sched_dt = None
        due_raw = meta.get("due_date", "")
        try:
            due_d = date.fromisoformat(due_raw)
        except Exception:
            due_d = None
        result.append({
            "_id":      t["id"],
            "_task_id": t["id"],
            "_status":  t.get("status", "needsAction"),
            "title":    meta.get("title", t.get("title", "")),
            "priority": meta.get("priority", "C"),
            "due_date": due_d,
            "due_allday":    meta.get("due_allday", True),
            "due_time":      meta.get("due_time", ""),
            "duration":      meta.get("duration_minutes", 60),
            "memo":          meta.get("memo", ""),
            "sched_dt":      sched_dt,
            "sched_end_str": e_str,
        })
    return result


# ── サイドバー ────────────────────────────────────────────────────
with st.sidebar:
    now = datetime.now(TZ)
    st.markdown(
        f'<div style="text-align:center;padding:10px 0 4px">'
        f'<div style="font-size:.7rem;color:#8a7f72;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:.1em">{DAYS_JA[now.weekday()]}</div>'
        f'<div style="width:42px;height:42px;background:#1E88E5;border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;margin:4px auto;'
        f'font-size:1.4rem;font-weight:500;color:white">{now.day}</div>'
        f'<div style="font-size:.76rem;color:#8a7f72;margin-top:2px">'
        f'{now.strftime("%Y年%m月")}</div></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<div class="sec-lbl">＋ タスクを追加</div>', unsafe_allow_html=True)
    with st.form("task_form", clear_on_submit=True):
        f_title    = st.text_input("タスク名", placeholder="例：企画書を作る",
                                   label_visibility="collapsed")
        f_priority = st.selectbox("優先度",
                                  options=PRIORITY_KEYS,
                                  format_func=lambda k: PRIORITY[k]["label"])
        f_due      = st.date_input("期日", value=date.today() + timedelta(days=3),
                                   min_value=date.today())
        f_allday   = st.radio("期日タイプ", ["終日", "時間指定"], horizontal=True)
        f_due_time = st.time_input("期日時刻",
                                   value=datetime.strptime("18:00", "%H:%M").time())
        f_duration = st.number_input("かかる時間（分）", 15, 480, 60, 15)
        f_memo     = st.text_area("メモ（任意）", placeholder="補足・参考リンクなど",
                                  height=80)
        f_submit   = st.form_submit_button("🔍 最適スロットを提案",
                                           type="primary", use_container_width=True)

    if f_submit:
        if not f_title:
            st.error("タスク名を入力してください")
        else:
            boundary = (datetime.combine(f_due, f_due_time).replace(tzinfo=TZ)
                        if f_allday == "時間指定" else f_due)
            with st.spinner("カレンダーを確認中..."):
                slots = find_free_slots(int(f_duration), date.today(), boundary, n=3)
            if slots:
                st.session_state["proposal"] = {
                    "mode":        "new",
                    "title":       f_title,
                    "priority":    f_priority,
                    "due_date":    f_due,
                    "due_allday":  f_allday == "終日",
                    "due_time":    f_due_time.strftime("%H:%M"),
                    "duration":    int(f_duration),
                    "memo":        f_memo,
                    "slots":       slots,
                }
                st.rerun()
            else:
                # 空きなし → 低優先度タスクとの入れ替え候補を探す
                swaps = find_lower_priority_tasks(f_priority, f_due)
                st.session_state["swap_search"] = {
                    "title":    f_title,
                    "priority": f_priority,
                    "due_date": f_due,
                    "due_allday": f_allday == "終日",
                    "due_time": f_due_time.strftime("%H:%M"),
                    "duration": int(f_duration),
                    "memo":     f_memo,
                    "swaps":    swaps,
                }
                st.rerun()

    st.divider()
    # 優先度凡例
    st.markdown('<div class="sec-lbl">優先度</div>', unsafe_allow_html=True)
    for k, v in PRIORITY.items():
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'margin:3px 0;font-size:0.82rem">'
            f'<span style="width:14px;height:14px;border-radius:3px;'
            f'background:{v["color"]};flex-shrink:0"></span>'
            f'{v["label"]}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    if st.button("🔄 更新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ── メインエリア ──────────────────────────────────────────────────
from streamlit_calendar import calendar as st_calendar

events_raw    = load_events()        # 全カレンダー予定（busy 計算用）
app_tasks_raw = load_app_tasks()     # アプリタスク（Google Tasks API）
task_lookup   = {t["_id"]: t for t in app_tasks_raw}
ev_lookup     = {ev.get("id", ""): ev for ev in events_raw}
cal_events_raw = [ev for ev in events_raw if not is_app_task(ev)]

# ── スロット提案 ──────────────────────────────────────────────────
if "proposal" in st.session_state:
    prop  = st.session_state["proposal"]
    p_cfg = PRIORITY[prop["priority"]]
    badge = (f'<span class="badge" style="background:{p_cfg["color"]}">'
             f'{prop["priority"]}</span>')
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">{badge}{prop["title"]}</div>'
        f'<div class="card-sub">期日 {prop["due_date"]} ／ 所要 {prop["duration"]}分</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**最適な時間スロットを選んでください**")

    cols    = st.columns(len(prop["slots"]))
    chosen  = None
    for i, (col, slot) in enumerate(zip(cols, prop["slots"])):
        end = slot + timedelta(minutes=prop["duration"])
        lbl = (f"{DAYS_JA[slot.weekday()]}曜  "
               f"{slot.strftime('%-m/%-d')}  "
               f"{slot.strftime('%H:%M')}〜{end.strftime('%H:%M')}")
        with col:
            if st.button(lbl, key=f"slot_{i}", use_container_width=True,
                         type="primary" if i == 0 else "secondary"):
                chosen = slot

    if chosen:
        end_s = (chosen + timedelta(minutes=prop["duration"])).strftime("%H:%M")
        with st.spinner("登録中..."):
            if prop.get("mode") == "reschedule" and prop.get("ev_id"):
                # 既存タスクの scheduled_start/end を更新
                tsk_id = prop["ev_id"]
                task   = get_tsk().get_task(tsk_id)
                ne     = chosen + timedelta(minutes=prop["duration"])
                try:
                    meta = json.loads(task.get("notes", "{}"))
                except Exception:
                    meta = {}
                meta["scheduled_start"] = chosen.isoformat()
                meta["scheduled_end"]   = ne.isoformat()
                new_due = chosen.astimezone(timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")
                get_tsk().update_task(tsk_id,
                                      notes=json.dumps(meta, ensure_ascii=False),
                                      due=new_due)
            else:
                register_task(
                    prop["title"], prop["priority"],
                    prop["due_date"], prop["due_allday"], prop["due_time"],
                    prop["duration"], chosen,
                    memo=prop.get("memo", ""),
                )
        del st.session_state["proposal"]
        st.cache_data.clear()
        st.success(f"✅ {chosen.strftime('%-m月%-d日(%a) %H:%M')}〜{end_s} に登録しました！")
        st.rerun()

    if st.button("キャンセル", key="cancel_prop"):
        del st.session_state["proposal"]
        st.rerun()

    st.divider()


# ── 入れ替え提案 ──────────────────────────────────────────────────
if "swap_search" in st.session_state and "proposal" not in st.session_state:
    ss   = st.session_state["swap_search"]
    p_cfg = PRIORITY[ss["priority"]]
    badge = (f'<span class="badge" style="background:{p_cfg["color"]}">'
             f'{ss["priority"]}</span>')
    st.markdown(
        f'<div class="alert-warn">'
        f'⚠️ {badge}<b>{ss["title"]}</b> の期日 {ss["due_date"]} までに空き時間が見つかりませんでした。<br>'
        f'優先度が低いタスクと入れ替えることで時間を確保できます。'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not ss["swaps"]:
        st.info("入れ替え候補のタスクが見つかりませんでした。期日を延ばすか所要時間を短縮してください。")
        if st.button("閉じる", key="close_swap"):
            del st.session_state["swap_search"]
            st.rerun()
    else:
        st.markdown("**入れ替え候補**（優先度の低いタスク）")
        selected = []
        for sw in ss["swaps"]:
            try:
                s_label = datetime.fromisoformat(sw["start"]).astimezone(TZ).strftime("%-m/%-d %H:%M")
            except Exception:
                s_label = "未定"
            p_sw  = sw["priority"]
            badge_sw = (f'<span class="badge" style="background:'
                        f'{PRIORITY[p_sw]["color"]};font-size:0.7rem">{p_sw}</span>')
            if st.checkbox(
                f"{sw['title']}　{s_label}　({sw['duration']}分)",
                key=f"sw_{sw['ev_id']}",
            ):
                selected.append(sw)

        sc1, sc2 = st.columns(2)
        with sc1:
            if selected and st.button("🔄 入れ替えを実行", type="primary", use_container_width=True):
                # 選択タスクを別スロットに移動し、空いたスロットに新タスクを入れる
                with st.spinner("再スケジュール中..."):
                    reschedule_results = []
                    for sw in selected:
                        sw_dl   = (date.fromisoformat(sw["due_date"])
                                   if sw["due_date"] else date.today() + timedelta(days=14))
                        sw_slots = find_free_slots(
                            sw["duration"],
                            date.today() + timedelta(days=1),
                            sw_dl, n=1,
                        )
                        reschedule_results.append({**sw, "new_slot": sw_slots[0] if sw_slots else None})

                    # 新タスクのスロットを再検索
                    new_boundary = (datetime.combine(ss["due_date"],
                                    datetime.strptime(ss["due_time"], "%H:%M").time()).replace(tzinfo=TZ)
                                    if not ss["due_allday"] else ss["due_date"])
                    new_slots = find_free_slots(ss["duration"], date.today(), new_boundary, n=3)

                st.session_state["swap_confirm"] = {
                    "new_task":   ss,
                    "new_slots":  new_slots,
                    "reschedule": reschedule_results,
                }
                del st.session_state["swap_search"]
                st.rerun()
        with sc2:
            if st.button("キャンセル", use_container_width=True, key="cancel_swap"):
                del st.session_state["swap_search"]
                st.rerun()

    st.divider()


# ── 入れ替え確認 ──────────────────────────────────────────────────
if "swap_confirm" in st.session_state and "proposal" not in st.session_state:
    sc_data = st.session_state["swap_confirm"]

    st.markdown("### 🔄 入れ替え計画")

    # 移動するタスクの新スロット
    for r in sc_data["reschedule"]:
        if r["new_slot"]:
            ns  = r["new_slot"]
            end = ns + timedelta(minutes=r["duration"])
            st.markdown(
                f'<div class="alert-ok">'
                f'<b>{r["title"]}</b> [{r["priority"]}]　→　'
                f'{ns.strftime("%-m/%-d(%a) %H:%M")}〜{end.strftime("%H:%M")} に移動</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="alert-warn"><b>{r["title"]}</b>：移動先が見つかりません</div>',
                unsafe_allow_html=True,
            )

    # 新タスクのスロット選択
    nt = sc_data["new_task"]
    if sc_data["new_slots"]:
        st.markdown(f'**「{nt["title"]}」の新しいスロットを選んでください**')
        cols   = st.columns(len(sc_data["new_slots"]))
        chosen = None
        for i, (col, slot) in enumerate(zip(cols, sc_data["new_slots"])):
            end = slot + timedelta(minutes=nt["duration"])
            lbl = (f"{DAYS_JA[slot.weekday()]}曜  {slot.strftime('%-m/%-d')}  "
                   f"{slot.strftime('%H:%M')}〜{end.strftime('%H:%M')}")
            with col:
                if st.button(lbl, key=f"sc_slot_{i}", use_container_width=True,
                             type="primary" if i == 0 else "secondary"):
                    chosen = slot

        if chosen:
            with st.spinner("タスクを更新中..."):
                tsk = get_tsk()
                # 既存タスクの時刻を更新
                for r in sc_data["reschedule"]:
                    if r["new_slot"]:
                        task = tsk.get_task(r["ev_id"])
                        ns   = r["new_slot"]
                        ne   = ns + timedelta(minutes=r["duration"])
                        try:
                            meta = json.loads(task.get("notes", "{}"))
                        except Exception:
                            meta = {}
                        meta["scheduled_start"] = ns.isoformat()
                        meta["scheduled_end"]   = ne.isoformat()
                        new_due = ns.astimezone(timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")
                        tsk.update_task(r["ev_id"],
                                        notes=json.dumps(meta, ensure_ascii=False),
                                        due=new_due)
                # 新タスクを登録
                register_task(nt["title"], nt["priority"],
                              nt["due_date"], nt["due_allday"], nt["due_time"],
                              nt["duration"], chosen,
                              memo=nt.get("memo", ""))
            del st.session_state["swap_confirm"]
            st.cache_data.clear()
            end_s = (chosen + timedelta(minutes=nt["duration"])).strftime("%H:%M")
            st.success(f"✅ 入れ替え完了！「{nt['title']}」を "
                       f"{chosen.strftime('%-m月%-d日 %H:%M')}〜{end_s} に登録しました。")
            st.rerun()
    else:
        st.warning("入れ替え後も新タスクの空きが見つかりませんでした。期日を再確認してください。")

    if st.button("キャンセル", key="cancel_sc"):
        del st.session_state["swap_confirm"]
        st.rerun()

    st.divider()


# ── タスククリック：日付変更 ──────────────────────────────────────
if "reschedule_task" in st.session_state and "proposal" not in st.session_state:
    rt    = st.session_state["reschedule_task"]
    p_cfg = PRIORITY.get(rt["priority"], PRIORITY["C"])
    badge = (f'<span class="badge" style="background:{p_cfg["color"]}">'
             f'{rt["priority"]}</span>')
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">{badge}{rt["title"]}</div>'
        f'<div class="card-sub">現在: {rt["current_start"]}　期日: {rt["due_date"]}　所要: {rt["duration"]}分</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**日付変更** — 新しい日程を設定してください")
    with st.form("reschedule_form"):
        rt_due     = st.date_input("新しい期日", value=date.today() + timedelta(days=3),
                                    min_value=date.today())
        rt_allday  = st.radio("期日タイプ", ["終日", "時間指定"], horizontal=True)
        rt_time    = st.time_input("期日時刻", value=datetime.strptime("18:00", "%H:%M").time())
        rt_submit  = st.form_submit_button("🔍 新しいスロットを提案", type="primary",
                                           use_container_width=True)
        rt_cancel  = st.form_submit_button("キャンセル", use_container_width=True)

    if rt_submit:
        boundary = (datetime.combine(rt_due, rt_time).replace(tzinfo=TZ)
                    if rt_allday == "時間指定" else rt_due)
        with st.spinner("空き時間を検索中..."):
            slots = find_free_slots(rt["duration"], date.today(), boundary, n=3)
        if slots:
            st.session_state["proposal"] = {
                "mode":            "reschedule",
                "ev_id":           rt["ev_id"],
                "title":           rt["title"],
                "priority":        rt["priority"],
                "due_date":        rt_due,
                "due_allday":      rt_allday == "終日",
                "due_time":        rt_time.strftime("%H:%M"),
                "duration":        rt["duration"],
                "slots":           slots,
            }
            del st.session_state["reschedule_task"]
            st.rerun()
        else:
            swaps = find_lower_priority_tasks(rt["priority"], rt_due)
            st.session_state["swap_search"] = {
                "title":    rt["title"],
                "priority": rt["priority"],
                "due_date": rt_due,
                "due_allday": rt_allday == "終日",
                "due_time": rt_time.strftime("%H:%M"),
                "duration": rt["duration"],
                "swaps":    swaps,
            }
            del st.session_state["reschedule_task"]
            st.rerun()

    if rt_cancel:
        del st.session_state["reschedule_task"]
        st.rerun()

    st.divider()


# ── 削除確認 ──────────────────────────────────────────────────────
if "delete_ev_id" in st.session_state:
    title_del = st.session_state.get("delete_ev_title", "このタスク")
    st.markdown(
        f'<div class="alert-warn">⚠️ 「{title_del}」を削除しますか？</div>',
        unsafe_allow_html=True,
    )
    dd1, dd2 = st.columns(2)
    with dd1:
        if st.button("🗑️ 削除する", type="primary", use_container_width=True, key="do_del"):
            del_id = st.session_state["delete_ev_id"]
            get_tsk().delete_task(del_id)
            del st.session_state["delete_ev_id"]
            st.session_state.pop("delete_ev_title", None)
            st.cache_data.clear()
            st.success("削除しました")
            st.rerun()
    with dd2:
        if st.button("キャンセル", use_container_width=True, key="cancel_del"):
            del st.session_state["delete_ev_id"]
            st.session_state.pop("delete_ev_title", None)
            st.rerun()
    st.divider()


# ── タブ ──────────────────────────────────────────────────────────
tab_cal, tab_tasks, tab_video = st.tabs(
    ["📅 カレンダー", "📋 タスク一覧", "🎬 動画制作"]
)

# ════════════════════════════════════════════════════════════════
# タブ①：カレンダー
# ════════════════════════════════════════════════════════════════
with tab_cal:
    view_mode = st.radio("表示", ["月", "週", "日"], horizontal=True,
                         label_visibility="collapsed")
    view_map  = {"月": "dayGridMonth", "週": "timeGridWeek", "日": "timeGridDay"}

    cal_events = []

    # 通常カレンダー予定
    for ev in cal_events_raw:
        s_str = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date") or ""
        e_str = ev.get("end",   {}).get("dateTime") or ev.get("end",   {}).get("date") or ""
        title = ev.get("summary", "(無題)")
        cal_events.append({
            "id": ev.get("id", ""),
            "title": title, "start": s_str, "end": e_str,
            "backgroundColor": "#616161", "borderColor": "#616161",
            "display": "block",
        })

    # アプリタスク（Google Tasks → カレンダーに表示）
    for t in app_tasks_raw:
        if t["_status"] == "completed":
            continue
        if not t["sched_dt"]:
            continue
        sd    = t["sched_dt"]
        ed_str = t["sched_end_str"] or (sd + timedelta(minutes=t["duration"])).isoformat()
        color  = task_color(t["priority"])
        disp   = f'[{t["priority"]}] {t["title"]}'
        if t["memo"]:
            short = t["memo"][:18] + "…" if len(t["memo"]) > 18 else t["memo"]
            disp  = f'{disp}  📝{short}'
        cal_events.append({
            "id": t["_id"],
            "title": disp, "start": sd.isoformat(), "end": ed_str,
            "backgroundColor": color, "borderColor": color,
            "display": "block",
        })

    cal_result = st_calendar(
        events=cal_events,
        options={
            "initialView":    view_map[view_mode],
            "locale":         "ja",
            "firstDay":       1,
            "headerToolbar":  {"left": "prev,next today", "center": "title", "right": ""},
            "buttonText":     {"today": "今日"},
            "height":         660,
            "slotMinTime":    "04:00:00",
            "slotMaxTime":    "24:00:00",
            "nowIndicator":   True,
            "selectable":     True,
            "eventDisplay":   "block",
            "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
            "slotLabelFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        },
        custom_css="""
            .fc { background:#FDFBF5; }
            .fc-event { border-radius:5px; font-size:0.8em; cursor:pointer; }
            .fc-toolbar-title { font-size:1.05em !important; font-weight:600; }
            .fc-today { background:#fef9ec !important; }
            .fc-col-header-cell { font-size:0.8em; color:#8a7f72; }
            .fc-button { border-radius:6px !important; font-size:0.82em !important; }
        """,
        key=f"cal_{view_mode}",
    )

    # ── コールバック ──────────────────────────────────────────────
    if cal_result and cal_result.get("callback"):
        cb = cal_result["callback"]

        if cb == "eventClick":
            ev_id = cal_result.get("eventClick", {}).get("event", {}).get("id", "")
            t = task_lookup.get(ev_id)
            if t:
                s_label = (t["sched_dt"].strftime("%-m/%-d %H:%M")
                           if t["sched_dt"] else "未定")
                st.session_state["reschedule_task"] = {
                    "ev_id":         ev_id,
                    "title":         t["title"],
                    "priority":      t["priority"],
                    "due_date":      t["due_date"].isoformat() if t["due_date"] else "",
                    "duration":      t["duration"],
                    "current_start": s_label,
                }
                st.rerun()

        elif cb in ("dateClick", "select"):
            date_str = (cal_result.get("dateClick") or cal_result.get("select") or {}).get("dateStr", "")
            if date_str:
                try:
                    qdt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(TZ)
                except Exception:
                    qdt = datetime.now(TZ).replace(minute=0, second=0)
                st.session_state["quick_dt"] = qdt
                st.rerun()

    # ── カレンダークリックで新規追加 ──────────────────────────────
    if "quick_dt" in st.session_state and "proposal" not in st.session_state:
        qdt = st.session_state["quick_dt"]
        st.markdown(f"### ＋ {qdt.strftime('%-m月%-d日(%a) %H:%M')} にタスクを追加")
        with st.form("quick_form", clear_on_submit=True):
            q_title    = st.text_input("タスク名", placeholder="例：MTG準備")
            q_priority = st.selectbox("優先度", PRIORITY_KEYS,
                                      format_func=lambda k: PRIORITY[k]["label"])
            q_due      = st.date_input("期日", value=qdt.date())
            q_allday   = st.radio("期日タイプ", ["終日", "時間指定"], horizontal=True)
            q_due_time = st.time_input("期日時刻", value=qdt.time())
            q_duration = st.number_input("かかる時間（分）", 15, 480, 60, 15)
            q_memo     = st.text_area("メモ（任意）", placeholder="補足・参考リンクなど",
                                      height=80)
            qc1, qc2   = st.columns(2)
            with qc1: q_submit = st.form_submit_button("🔍 スロット提案", type="primary",
                                                        use_container_width=True)
            with qc2: q_cancel = st.form_submit_button("キャンセル", use_container_width=True)

        if q_submit and q_title:
            boundary = (datetime.combine(q_due, q_due_time).replace(tzinfo=TZ)
                        if q_allday == "時間指定" else q_due)
            with st.spinner("空き時間を検索中..."):
                slots = find_free_slots(int(q_duration), date.today(), boundary, n=3)
            if slots:
                st.session_state["proposal"] = {
                    "mode":      "new",
                    "title":     q_title,
                    "priority":  q_priority,
                    "due_date":  q_due,
                    "due_allday": q_allday == "終日",
                    "due_time":  q_due_time.strftime("%H:%M"),
                    "duration":  int(q_duration),
                    "memo":      q_memo,
                    "slots":     slots,
                }
            else:
                swaps = find_lower_priority_tasks(q_priority, q_due)
                st.session_state["swap_search"] = {
                    "title":    q_title,
                    "priority": q_priority,
                    "due_date": q_due,
                    "due_allday": q_allday == "終日",
                    "due_time": q_due_time.strftime("%H:%M"),
                    "duration": int(q_duration),
                    "memo":     q_memo,
                    "swaps":    swaps,
                }
            del st.session_state["quick_dt"]
            st.rerun()
        if q_cancel:
            del st.session_state["quick_dt"]
            st.rerun()


# ════════════════════════════════════════════════════════════════
# タブ②：タスク一覧
# ════════════════════════════════════════════════════════════════
with tab_tasks:
    _today = date.today()

    # ── アプリ管理タスク（Google Tasks から） ──────────────────────
    # app_tasks_raw はページ上部で load_app_tasks() 済み
    # タスク一覧用に "ev_id" キーを _id に統一
    app_tasks = [
        {**t, "ev_id": t["_id"]}
        for t in app_tasks_raw
    ]

    # ── フィルター & ソート ───────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        f_status = st.radio("状態", ["すべて", "未来", "期限切れ"],
                            horizontal=True, key="tl_status")
    with fc2:
        f_prio = st.multiselect(
            "優先度", PRIORITY_KEYS,
            default=PRIORITY_KEYS,
            format_func=lambda k: PRIORITY[k]["label"],
            key="tl_prio",
        )
    with fc3:
        f_sort = st.radio("並び替え", ["優先度順", "期日順", "スケジュール順"],
                          horizontal=True, key="tl_sort")

    # フィルタリング
    filtered = []
    for t in app_tasks:
        if t["priority"] not in f_prio:
            continue
        if f_status == "未来":
            if t["due_date"] and t["due_date"] < _today:
                continue
        elif f_status == "期限切れ":
            if not (t["due_date"] and t["due_date"] < _today):
                continue
        filtered.append(t)

    # ソート
    def _sort_key(t: dict):
        p_rank   = -PRIORITY.get(t["priority"], PRIORITY["C"])["rank"]   # 高優先度が上
        due_ord  = t["due_date"].toordinal() if t["due_date"] else 99999
        sched_ts = t["sched_dt"].timestamp() if t["sched_dt"] else 1e18
        if f_sort == "優先度順":
            return (p_rank, due_ord, sched_ts)
        elif f_sort == "期日順":
            return (due_ord, p_rank, sched_ts)
        else:  # スケジュール順
            return (sched_ts, p_rank, due_ord)

    filtered.sort(key=_sort_key)

    # ── 集計バッジ ────────────────────────────────────────────────
    n_overdue = sum(1 for t in filtered if t["due_date"] and t["due_date"] < _today)
    n_total   = len(filtered)
    st.markdown(
        f'<div style="display:flex;gap:10px;margin:8px 0 14px">'
        f'<span style="background:#e8f5e9;color:#1b5e20;border-radius:6px;'
        f'padding:3px 12px;font-size:0.82rem;font-weight:600">'
        f'合計 {n_total} 件</span>'
        + (f'<span style="background:#ffebee;color:#b71c1c;border-radius:6px;'
           f'padding:3px 12px;font-size:0.82rem;font-weight:600">'
           f'⚠️ 期限切れ {n_overdue} 件</span>' if n_overdue else "")
        + f'</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.info("該当するタスクがありません。")
    else:
        # ── タスクカード ──────────────────────────────────────────
        for t in filtered:
            p_cfg  = PRIORITY.get(t["priority"], PRIORITY["C"])
            color  = p_cfg["color"]
            is_ov  = t["due_date"] and t["due_date"] < _today
            border = "#ef9a9a" if is_ov else "#e8e4db"

            # 期日表示
            if t["due_date"]:
                due_label = t["due_date"].strftime("%-m月%-d日")
                if not t["due_allday"] and t["due_time"]:
                    due_label += f" {t['due_time']}"
                days_left = (t["due_date"] - _today).days
                if is_ov:
                    due_chip = (f'<span style="color:#c62828;font-weight:700">'
                                f'⚠️ {due_label}（{abs(days_left)}日超過）</span>')
                elif days_left == 0:
                    due_chip = f'<span style="color:#e65100;font-weight:700">今日 {due_label}</span>'
                elif days_left <= 3:
                    due_chip = f'<span style="color:#f57c00;font-weight:600">📌 {due_label}（あと{days_left}日）</span>'
                else:
                    due_chip = f'<span style="color:#5d4037">{due_label}（あと{days_left}日）</span>'
            else:
                due_chip = '<span style="color:#aaa">期日未設定</span>'

            # スケジュール時刻
            if t["sched_dt"]:
                sd = t["sched_dt"]
                ed = sd + timedelta(minutes=t["duration"])
                sched_label = (f'{DAYS_JA[sd.weekday()]}曜 '
                               f'{sd.strftime("%-m/%-d %H:%M")}〜{ed.strftime("%H:%M")} '
                               f'（{t["duration"]}分）')
            else:
                sched_label = "スケジュール未設定"

            memo_html = ""
            if t.get("memo"):
                escaped_memo = t["memo"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                memo_html = (f'<div class="card-sub" style="margin-top:5px;'
                             f'background:#f9f6ef;border-radius:6px;padding:5px 8px;'
                             f'white-space:pre-wrap">📝 {escaped_memo}</div>')

            st.markdown(
                f'<div class="card" style="border-color:{border};'
                f'{"background:#fff8f8;" if is_ov else ""}">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span class="badge" style="background:{color}">{t["priority"]}</span>'
                f'<span class="card-title" style="margin:0">{t["title"]}</span>'
                f'</div>'
                f'<div class="card-sub">期日：{due_chip}</div>'
                f'<div class="card-sub" style="margin-top:2px">📅 {sched_label}</div>'
                f'{memo_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # アクションボタン
            btn_cols = st.columns([1, 1, 3])
            with btn_cols[0]:
                if st.button("📅 日付変更", key=f"tl_rs_{t['ev_id']}", use_container_width=True):
                    s_label = (t["sched_dt"].strftime("%-m/%-d %H:%M")
                               if t["sched_dt"] else "未定")
                    st.session_state["reschedule_task"] = {
                        "ev_id":         t["ev_id"],
                        "title":         t["title"],
                        "priority":      t["priority"],
                        "due_date":      t["due_date"].isoformat() if t["due_date"] else "",
                        "duration":      t["duration"],
                        "current_start": s_label,
                    }
                    st.rerun()
            with btn_cols[1]:
                if st.button("🗑️ 削除", key=f"tl_del_{t['ev_id']}", use_container_width=True):
                    st.session_state["delete_ev_id"]    = t["ev_id"]
                    st.session_state["delete_ev_title"] = t["title"]
                    st.rerun()


# ════════════════════════════════════════════════════════════════
# タブ③：動画制作 管理表
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=120, show_spinner=False)
def _load_video(sheet_id: str, nonce: int):
    """スプレッドシートを読み込み（120秒キャッシュ / 更新ボタンで nonce 変更）。"""
    from secretary import sheets_ops
    return sheets_ops.load_video_records(sheet_id)


def _alert_text(rec, today) -> str:
    """締切までの残り日数を短いテキストに（期限切れ/本日/あとN日）。"""
    if rec.deadline_date is None:
        return ""
    days = (rec.deadline_date - today).days
    if days < 0:
        return f"⚠️ {-days}日超過"
    if days == 0:
        return "🔥 本日締切"
    if days <= 7:
        return f"あと{days}日"
    return ""


with tab_video:
    sheet_id = video_sheet_id()

    head_l, head_r = st.columns([4, 1])
    with head_l:
        st.markdown("### 🎬 動画制作 管理表")
    with head_r:
        if st.button("🔄 更新", use_container_width=True, key="video_refresh"):
            st.session_state["video_nonce"] = st.session_state.get("video_nonce", 0) + 1
            st.rerun()

    with st.expander("⚙️ 接続するスプレッドシート", expanded=False):
        st.caption("シートのURL内の長いID部分。空欄で既定値を使用します。")
        sid_in = st.text_input("スプレッドシートID", value=sheet_id,
                               label_visibility="collapsed")
        if sid_in.strip():
            sheet_id = sid_in.strip()
        st.caption("※ 初回はスプレッドシート読み取りの再認証が必要です "
                   "（token.json を削除して再起動）。")

    nonce = st.session_state.get("video_nonce", 0)
    try:
        records = _load_video(sheet_id, nonce)
    except Exception as e:
        st.error("スプレッドシートを読み込めませんでした。")
        msg = str(e)
        if "insufficient" in msg.lower() or "scope" in msg.lower() or "403" in msg:
            st.warning("スプレッドシート読み取りの権限が不足しています。"
                       "`token.json` を削除してアプリを再起動し、再認証してください。")
        st.caption(f"詳細: {msg}")
        st.stop()

    today = datetime.now(TZ).date()

    if not records:
        st.info("制作リストを検出できませんでした。シートの先頭にヘッダ"
                "（投稿／担当／クライアント／企画／待ち状態 …）がある表を読み込みます。")
        st.stop()

    # ── 絞り込み ───────────────────────────────────────────────────
    clients = sorted({r.client for r in records if r.client})
    assignees = sorted({r.assignee for r in records if r.assignee})
    fc1, fc2, fc3 = st.columns([1.2, 1.2, 1])
    with fc1:
        sel_clients = st.multiselect("クライアント", clients, key="vf_client")
    with fc2:
        sel_assignees = st.multiselect("担当", assignees, key="vf_assignee")
    with fc3:
        view = st.radio("表示", ["進行中のみ", "すべて"], horizontal=True, key="vf_view")
    kw = st.text_input("企画で検索", placeholder="キーワード", key="vf_kw").strip()

    def _match(r) -> bool:
        if view == "進行中のみ" and not r.is_active:
            return False
        if sel_clients and r.client not in sel_clients:
            return False
        if sel_assignees and r.assignee not in sel_assignees:
            return False
        if kw and kw.lower() not in (r.title or "").lower():
            return False
        return True

    rows_rec = [r for r in records if _match(r)]

    # 進行中の期限切れ→締切順→ステージ序盤順、その後に完了・ボツ
    FAR = date(2099, 12, 31)

    def _sort_key(r):
        return (
            0 if r.is_active else 1,                                     # 進行中を上に
            0 if (r.deadline_date and r.deadline_date < today) else 1,  # 期限切れ最優先
            r.deadline_date or FAR,                                      # 締切が近い順
            r.stage_index if r.stage_index >= 0 else 99,                # 序盤ステージ順
        )

    rows_rec.sort(key=_sort_key)

    overdue_n = sum(1 for r in rows_rec if r.is_active and r.deadline_date
                    and r.deadline_date < today)
    active_n = sum(1 for r in rows_rec if r.is_active)
    st.caption(f"表示 {len(rows_rec)} 件　｜　進行中 {active_n} 件　｜　"
               f"⚠️ 期限切れ {overdue_n} 件")

    # ── 管理表 ─────────────────────────────────────────────────────
    def _status(r):
        if r.is_done:
            return "✅ 済"
        if r.is_killed:
            return "✖ ボツ"
        return "🟢 進行中"

    import pandas as pd

    df = pd.DataFrame([{
        "状態": _status(r),
        "アラート": _alert_text(r, today),
        "締切": r.deadline_date,
        "クライアント": r.client,
        "企画": r.title,
        "ステージ": r.stage_raw,
        "担当": r.assignee or "—",
        "No.": r.no,
        "投稿日": r.post_date,
        "元素材": r.source_url if r.source_url.startswith("http") else None,
        "共有": r.share_url if r.share_url.startswith("http") else None,
    } for r in rows_rec])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=620,
        column_config={
            "状態":   st.column_config.TextColumn("状態", width="small"),
            "アラート": st.column_config.TextColumn("アラート", width="small"),
            "締切":   st.column_config.DateColumn("締切", format="M/D", width="small"),
            "企画":   st.column_config.TextColumn("企画", width="large"),
            "No.":    st.column_config.TextColumn("No.", width="small"),
            "元素材": st.column_config.LinkColumn("元素材", display_text="開く",
                                                  width="small"),
            "共有":   st.column_config.LinkColumn("共有", display_text="開く",
                                                  width="small"),
        },
    )
    st.caption("列見出しをクリックすると並べ替えできます。"
               "元のスプレッドシートは変更しません（読み取り専用）。")
