import glob
import os
import random
import streamlit as st

st.set_page_config(
    page_title="エーテル・ウォー：4大国魔導機甲戦記",
    page_icon="⚔️",
    layout="wide",
)

# 1. 国家データベース（拠点地形、固有コア、カラー設定）
NATIONS = {
    "魔導技術国家メイズ": {
        "id": "maze",
        "terrain": "荒れ地",
        "core": "古龍の魔結晶",
        "color": "#c0392b",
        "emoji": "🔥",
        "desc": "荒れ地に君臨する魔導帝国。古龍の魔力を動力源とする。",
    },
    "サイバー科学国家システムズ": {
        "id": "systems",
        "terrain": "科学都市",
        "core": "プラズマ核融合炉",
        "color": "#2980b9",
        "emoji": "⚡",
        "desc": "高度に発達した科学都市国家。プラズマ技術による高出力戦術を得意とする。",
    },
    "水上自然都市融合国家オアシス": {
        "id": "oasis",
        "terrain": "水上自然都市",
        "core": "エーテルタービン",
        "color": "#27ae60",
        "emoji": "🌿",
        "desc": "自然と調和する水上都市国家。環境エーテルを利用した機動戦に長ける。",
    },
    "月面開拓国家ムーンライト": {
        "id": "moonlight",
        "terrain": "月面都市",
        "core": "ゼロ・ポイント機関",
        "color": "#8e44ad",
        "emoji": "🌙",
        "desc": "月面クレーターに築かれた開拓国家。未知の真空エネルギー機関を操る。",
    },
}

# 2. パーツデータベース
CHASSIS_OPTIONS = {
    "重装甲魔導アーマー": {
        "id": "heavy",
        "speed": 60,
        "accel": 50,
        "handling": 80,
        "desc": "圧倒的な防御力と安定した進軍を誇る重機甲。",
    },
    "超高速ホバリングバイク": {
        "id": "hover",
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "desc": "電撃的な領地制圧に特化した反重力ビークル。",
    },
    "全地形万能バギー": {
        "id": "buggy",
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "desc": "荒れ地から水上まであらゆる地形に対応するバランス型フレーム。",
    },
    "ステルス・ウィング": {
        "id": "wing",
        "speed": 90,
        "accel": 65,
        "handling": 60,
        "desc": "敵防衛網を突破する超軽量滑空フレーム。",
    },
}

CORE_OPTIONS = {
    "古龍の魔結晶": {
        "id": "dragon",
        "power": 90,
        "boost": 70,
        "desc": "【メイズ専用】莫大な魔力を供給する古代竜の結晶炉。",
    },
    "プラズマ核融合炉": {
        "id": "plasma",
        "power": 80,
        "boost": 90,
        "desc": "【システムズ専用】安定した高出力を発揮する最新鋭核融合炉。",
    },
    "エーテルタービン": {
        "id": "ether",
        "power": 70,
        "boost": 80,
        "desc": "【オアシス専用】大気と水の魔力を高効率で変換する環境機関。",
    },
    "ゼロ・ポイント機関": {
        "id": "zero",
        "power": 100,
        "boost": 100,
        "desc": "【ムーンライト専用】次元の真空から無限エネルギーを引き出すオーパーツ。",
    },
}

ARMOR_OPTIONS = {
    "標準耐熱コーティング": {"id": "standard", "defense": 20, "weight": -5},
    "魔力収束シールド発生器": {"id": "shield", "defense": 45, "weight": -15},
    "重チタン・ハードプレート": {"id": "titanium", "defense": 70, "weight": 20},
}

WEAPON_OPTIONS = {
    "エーテル・バルカン砲": {"id": "vulcan", "attack": 60, "bonus_accel": 5},
    "プラズマ・キャノン": {"id": "cannon", "attack": 90, "bonus_accel": -5},
    "近接ブレードポッド": {"id": "blade", "attack": 75, "bonus_accel": 15},
    "武装なし（軽量化）": {"id": "none", "attack": 0, "bonus_accel": 25},
}


def init_game():
    terrain_grid = []
    owner_grid = []
    for r in range(8):
        t_row = []
        o_row = []
        for c in range(8):
            if r < 4 and c < 4:
                t_row.append("荒れ地")
            elif r < 4 and c >= 4:
                t_row.append("科学都市")
            elif r >= 4 and c < 4:
                t_row.append("水上自然都市")
            else:
                t_row.append("月面都市")
            o_row.append(None)
        terrain_grid.append(t_row)
        owner_grid.append(o_row)

    owner_grid[0][0] = "魔導技術国家メイズ"
    owner_grid[0][7] = "サイバー科学国家システムズ"
    owner_grid[7][0] = "水上自然都市融合国家オアシス"
    owner_grid[7][7] = "月面開拓国家ムーンライト"

    st.session_state.terrain_grid = terrain_grid
    st.session_state.owner_grid = owner_grid
    st.session_state.turn = 1
    st.session_state.logs = [
        "=== 世界大戦が開幕しました！主力機体を開発し領地を拡大してください ==="
    ]


if "owner_grid" not in st.session_state:
    init_game()

st.title("⚔️ エーテル・ウォー：4大国魔導機甲戦記")

# 3. 国家選択セクション
st.subheader("🚩 運営国家の選択")
player_nation = st.selectbox(
    "指揮を執る国家を選択してください（他3国はAIが自動運営します）",
    list(NATIONS.keys()),
)
nation_info = NATIONS[player_nation]
st.info(
    f"{nation_info['emoji']} **{player_nation}** ｜ 本拠地形: **{nation_info['terrain']}** ｜ 固有動力コア: **{nation_info['core']}**\n\n{nation_info['desc']}"
)

st.markdown("---")

# 4. マシンパーツ・アッセンブル（カスタムファクトリー）
st.subheader("🔧 主力魔導機甲・開発ファクトリー")

col1, col2 = st.columns(2)
with col1:
    selected_chassis = st.selectbox("① フレーム・ボディ", list(CHASSIS_OPTIONS.keys()))
    locked_core = nation_info["core"]
    selected_core = st.selectbox(
        "② 動力機関（コア） ※国家固有技術のため固定",
        [locked_core],
        disabled=True,
    )
with col2:
    selected_armor = st.selectbox("③ 装甲・防御システム", list(ARMOR_OPTIONS.keys()))
    selected_weapon = st.selectbox("④ 主武装・アタッチメント", list(WEAPON_OPTIONS.keys()))

c_data = CHASSIS_OPTIONS[selected_chassis]
co_data = CORE_OPTIONS[selected_core]
a_data = ARMOR_OPTIONS[selected_armor]
w_data = WEAPON_OPTIONS[selected_weapon]

total_speed = c_data["speed"] + co_data["power"] // 2 - max(0, a_data["weight"])
total_accel = c_data["accel"] + co_data["boost"] // 2 + w_data["bonus_accel"]
total_defense = a_data["defense"] + c_data["handling"] // 2
total_attack = w_data["attack"] + co_data["power"] // 2
combat_power = total_attack + total_defense + (total_speed // 2)


def resolve_machine_image(chassis_id, core_id, armor_id, weapon_id):
    exts = [".png", ".jpg", ".webp"]
    full_combo_name = (
        f"chassis_{chassis_id}_core_{core_id}_armor_{armor_id}_weapon_{weapon_id}"
    )
    for ext in exts:
        path = os.path.join("image", full_combo_name + ext)
        if os.path.exists(path):
            return path, "完全一致（パーツ組み合わせ専用画像）"

    chassis_only_name = f"chassis_{chassis_id}"
    for ext in exts:
        path = os.path.join("image", chassis_only_name + ext)
        if os.path.exists(path):
            return path, f"フォールバック表示（{selected_chassis} 標準画像）"

    any_images = (
        glob.glob("image/*.png") + glob.glob("image/*.jpg") + glob.glob("image/*.webp")
    )
    if any_images:
        return any_images[0], "プレースホルダー表示（`image` 内の代替画像）"
    return None, "画像なし"


image_path, status_label = resolve_machine_image(
    c_data["id"], co_data["id"], a_data["id"], w_data["id"]
)

vcol1, vcol2 = st.columns([1, 2])
with vcol1:
    if image_path:
        st.image(
            image_path,
            caption=f"{player_nation}主力機 [{status_label}]",
            use_container_width=True,
        )
    else:
        st.warning("⚠️ `image` ディレクトリに画像ファイルがありません。")

with vcol2:
    st.markdown("### 📊 開発機体・戦術スペック")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("攻撃力 (ATK)", f"{total_attack}")
    sc2.metric("防御力 (DEF)", f"{total_defense}")
    sc3.metric("機動力 (SPD)", f"{total_speed}")
    sc4.metric("総合戦闘力", f"{combat_power}")

    st.code(
        f"参照画像ファイル名:\nimage/chassis_{c_data['id']}_core_{co_data['id']}_armor_{a_data['id']}_weapon_{w_data['id']}.png",
        language="text",
    )

st.markdown("---")

# 5. 8×8 陣取り戦略シミュレーション
st.subheader(f"🗺️ ワールド戦略マップ（第 {st.session_state.turn} ターン）")

counts = {n: 0 for n in NATIONS}
neutral_count = 0
for r in range(8):
    for c in range(8):
        owner = st.session_state.owner_grid[r][c]
        if owner:
            counts[owner] += 1
        else:
            neutral_count += 1

mcols = st.columns(5)
for idx, (n_name, n_val) in enumerate(NATIONS.items()):
    mcols[idx].metric(f"{n_val['emoji']} {n_name[:6]}..", f"{counts[n_name]} マス")
mcols[4].metric("🏳️ 未開拓・中立", f"{neutral_count} マス")


def get_expandable_cells(nation_name, grid):
    candidates = set()
    for r in range(8):
        for c in range(8):
            if grid[r][c] == nation_name:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc] != nation_name:
                        candidates.add((nr, nc))
    return list(candidates)


def advance_turn(target_cell=None):
    grid = st.session_state.owner_grid
    t_grid = st.session_state.terrain_grid
    turn_logs = []

    if target_cell:
        tr, tc = target_cell
        defender = grid[tr][tc]
        terrain = t_grid[tr][tc]
        atk_power = combat_power + (25 if terrain == nation_info["terrain"] else 0)
        def_power = random.randint(120, 210) if defender else 80

        if atk_power >= def_power or defender is None:
            grid[tr][tc] = player_nation
            target_label = defender if defender else "中立地帯"
            turn_logs.append(
                f"{nation_info['emoji']} 【自軍】({tr+1},{tc+1})[{terrain}] の {target_label} を制圧！(戦力:{atk_power} vs 防衛:{def_power})"
            )
        else:
            turn_logs.append(
                f"🛡️ 【自軍】({tr+1},{tc+1}) の {defender} への侵攻に失敗…(戦力:{atk_power} vs 防衛:{def_power})"
            )

    ai_nations = [n for n in NATIONS.keys() if n != player_nation]
    random.shuffle(ai_nations)

    for ai_nat in ai_nations:
        ai_info = NATIONS[ai_nat]
        candidates = get_expandable_cells(ai_nat, grid)
        if not candidates:
            continue
        neutral_cands = [pos for pos in candidates if grid[pos[0]][pos[1]] is None]
        chosen = random.choice(neutral_cands if neutral_cands else candidates)
        ar, ac = chosen
        defender = grid[ar][ac]
        terrain = t_grid[ar][ac]

        ai_power = random.randint(140, 230) + (25 if terrain == ai_info["terrain"] else 0)
        def_power = (
            (combat_power if defender == player_nation else random.randint(130, 200))
            if defender
            else 70
        )

        if ai_power >= def_power or defender is None:
            grid[ar][ac] = ai_nat
            target_label = defender if defender else "中立地帯"
            turn_logs.append(
                f"{ai_info['emoji']} 【AI:{ai_nat}】が ({ar+1},{ac+1})[{terrain}] の {target_label} を占領！"
            )

    st.session_state.turn += 1
    st.session_state.logs = turn_logs + st.session_state.logs


map_col, ctrl_col = st.columns([2, 1])

with ctrl_col:
    st.markdown("### 🎮 作戦コマンド")
    expandable = get_expandable_cells(player_nation, st.session_state.owner_grid)

    if expandable:
        cell_labels = {
            f"({r+1}行, {c+1}列) - {st.session_state.terrain_grid[r][c]} [{st.session_state.owner_grid[r][c] or '中立'}]": (
                r,
                c,
            )
            for r, c in sorted(expandable)
        }
        selected_target_label = st.selectbox(
            "侵攻・制圧する隣接エリアを選択", list(cell_labels.keys())
        )
        if st.button("⚔️ 出撃してターンを進める", type="primary", use_container_width=True):
            advance_turn(cell_labels[selected_target_label])
            st.rerun()
    else:
        st.success("全領地を制圧、または侵攻可能エリアがありません！")

    if st.button("⏭️ 待機してターンを進める（AI行動）", use_container_width=True):
        advance_turn(None)
        st.rerun()

    if st.button("🔄 マップを初期状態にリセット", use_container_width=True):
        init_game()
        st.rerun()

    st.markdown("### 📜 戦況ログ")
    log_text = "\n".join(st.session_state.logs[:12])
    st.text_area("最新ログ", log_text, height=250, label_visibility="collapsed")

with map_col:
    terrain_icons = {
        "荒れ地": "🏜️",
        "科学都市": "🏙️",
        "水上自然都市": "🌊",
        "月面都市": "🌑",
    }
    terrain_short = {
        "荒れ地": "荒れ地",
        "科学都市": "科学",
        "水上自然都市": "水上",
        "月面都市": "月面",
    }

    # インデントを入れずにHTMLテーブルを構築（コードブロック誤認を防止）
    rows_html = []
    for r in range(8):
        cells = []
        for c in range(8):
            owner = st.session_state.owner_grid[r][c]
            terrain = st.session_state.terrain_grid[r][c]
            t_icon = terrain_icons[terrain]
            t_label = terrain_short[terrain]

            if owner:
                bg_color = NATIONS[owner]["color"]
                o_icon = NATIONS[owner]["emoji"]
                is_player = owner == player_nation
                border_style = "2px solid #ffffff" if is_player else "1px solid #1f242d"
                badge = "★自軍" if is_player else ""
            else:
                bg_color = "#262c36"
                o_icon = "🏳️"
                border_style = "1px solid #1f242d"
                badge = ""

            cell_html = (
                f'<td style="background-color:{bg_color};border:{border_style};'
                f'padding:6px 2px;color:#ffffff;border-radius:6px;width:12.5%;vertical-align:middle;">'
                f'<div style="font-size:16px;line-height:1.2;">{o_icon}</div>'
                f'<div style="font-size:10px;line-height:1.2;opacity:0.95;">{t_icon}{t_label}</div>'
                f'<div style="font-size:9px;line-height:1.2;opacity:0.8;">({r+1},{c+1}) {badge}</div>'
                f"</td>"
            )
            cells.append(cell_html)
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    html_grid = (
        '<table style="width:100%;border-collapse:separate;border-spacing:3px;text-align:center;">'
        + "".join(rows_html)
        + "</table>"
    )
    st.markdown(html_grid, unsafe_allow_html=True)
    st.caption(
        "※ 左上(1〜4,1〜4): 荒れ地 / 右上(1〜4,5〜8): 科学都市 / 左下(5〜8,1〜4): 水上自然都市 / 右下(5〜8,5〜8): 月面都市"
    )
