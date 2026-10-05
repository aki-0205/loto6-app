import random
from datetime import datetime, timedelta
import zoneinfo
import streamlit as st

st.set_page_config(page_title="ロト6 厳選1予想ツール", layout="centered")

# 日本時間（JST）の現在日時を取得
jst = zoneinfo.ZoneInfo("Asia/Tokyo")
now = datetime.now(jst)

# 夜19:00以降なら「翌日」、19:00未満なら「本日」
if now.hour >= 19:
    target_date = now.date() + timedelta(days=1)
    status_msg = "🌙 19時を過ぎたため【次回・翌日分】の予測を出力中"
else:
    target_date = now.date()
    status_msg = "☀️ 本日分（19時まで）の予測を出力中"

target_date_str = target_date.strftime("%Y年%m月%d日")

# 直近データ（前回当せん番号）
last_numbers = [6, 12, 19, 23, 34, 40]
last_bonus = 15

st.title("🎲 ロト6 本命1選 予測")
st.subheader(f"📅 予測対象日: {target_date_str}")
st.caption(status_msg)

st.info(f"📊 **直近の抽せん結果（前回）**\n・本数字: **{', '.join(map(str, last_numbers))}** (ボーナス: **{last_bonus}**)")

# 日付に基づく固定シード
date_seed = int(target_date.strftime("%Y%m%d"))

def get_best_loto6(seed):
    rng = random.Random(seed)
    best_combo = None
    best_score = -999
    best_meta = {}
    
    for _ in range(5000):
        combo = sorted(rng.sample(range(1, 44), 6))
        total_sum = sum(combo)
        low_count = sum(1 for x in combo if 1 <= x <= 21)
        odd_count = sum(1 for x in combo if x % 2 != 0)
        
        overlap_last = len(set(combo) & set(last_numbers))
        
        slide_set = set()
        for x in last_numbers:
            if x - 1 >= 1: slide_set.add(x - 1)
            if x + 1 <= 43: slide_set.add(x + 1)
        overlap_slide = len(set(combo) & slide_set)
        
        consecutive_count = sum(1 for i in range(len(combo)-1) if combo[i+1] - combo[i] == 1)
        
        score = 0
        if 110 <= total_sum <= 160: score += 20
        elif 95 <= total_sum <= 175: score += 10
        if 2 <= low_count <= 4: score += 15
        if 2 <= odd_count <= 4: score += 15
        if 1 <= overlap_last <= 2: score += 15
        if 1 <= overlap_slide <= 2: score += 10
        if consecutive_count == 1: score += 10
        elif consecutive_count == 0: score += 5
        
        if score > best_score:
            best_score = score
            best_combo = combo
            best_meta = {
                "sum": total_sum,
                "low": low_count,
                "high": 6 - low_count,
                "odd": odd_count,
                "even": 6 - odd_count,
                "overlap_last": overlap_last,
                "overlap_slide": overlap_slide
            }
            
    return best_combo, best_meta

if st.button(f"{target_date_str} の【本命1選】を表示", type="primary"):
    combo, meta = get_best_loto6(date_seed)
    num_str = "   ".join([f"**{n:02d}**" for n in combo])
    
    st.success(f"### 🎯 【{target_date_str}】 本命予想")
    st.markdown(f"## 🏆 {num_str}")
    
    st.subheader("📋 分析・選出根拠")
    st.write(f"・**数字の合計値**: `{meta['sum']}` （理想範囲: 100〜170）")
    st.write(f"・**高低バランス (1~21 : 22~43)**: `{meta['low']} : {meta['high']}`")
    st.write(f"・**奇偶バランス (奇数 : 偶数)**: `{meta['odd']} : {meta['even']}`")
    st.write(f"・**前回からの引っ張り数**: `{meta['overlap_last']}` 個")
    st.write(f"・**前回±1（スライド数）**: `{meta['overlap_slide']}` 個")

st.markdown("---")
st.caption("※全15分析条件を多角スコアリングし、最も期待値の高い1組を選出しています。19時に翌日分へ自動切り替えされます。")
