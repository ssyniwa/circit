import base64
import glob
import json
import os
import random
import streamlit as st

st.set_page_config(
    page_title="エーテル・ウォー：4大国魔導機甲戦記",
    page_icon="⚔️",
    layout="wide",
)

# 1. 国家データベース
NATIONS = {
    "魔導技術国家メイズ": {
        "id": "maze",
        "terrain": "荒れ地",
        "core": "古龍の魔結晶",
        "color": "#c0392b",
        "emoji": "🔥",
        "home": (0, 0),
        "desc": "荒れ地に君臨する魔導帝国。古龍の魔力を動力源とする。",
    },
    "サイバー科学国家システムズ": {
        "id": "systems",
        "terrain": "科学都市",
        "core": "プラズマ核融合炉",
        "color": "#2980b9",
        "emoji": "⚡",
        "home": (0, 7),
        "desc": "高度に発達した科学都市国家。プラズマ技術による高出力戦術を得意とする。",
    },
    "水上自然都市融合国家オアシス": {
        "id": "oasis",
        "terrain": "水上自然都市",
        "core": "エーテルタービン",
        "color": "#27ae60",
        "emoji": "🌿",
        "home": (7, 0),
        "desc": "自然と調和する水上都市国家。環境エーテルを利用した機動戦に長ける。",
    },
    "月面開拓国家ムーンライト": {
        "id": "moonlight",
        "terrain": "月面都市",
        "core": "ゼロ・ポイント機関",
        "color": "#8e44ad",
        "emoji": "🌙",
        "home": (7, 7),
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
        "cost": 120,
        "desc": "圧倒的な防御力と安定した進軍を誇る重機甲。",
    },
    "超高速ホバリングバイク": {
        "id": "hover",
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "cost": 110,
        "desc": "電撃的な領地制圧に特化した反重力ビークル。",
    },
    "全地形万能バギー": {
        "id": "buggy",
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "cost": 100,
        "desc": "荒れ地から水上まであらゆる地形に対応するバランス型フレーム。",
    },
    "ステルス・ウィング": {
        "id": "wing",
        "speed": 90,
        "accel": 65,
        "handling": 60,
        "cost": 130,
        "desc": "敵防衛網を突破する超軽量滑空フレーム。",
    },
}

CORE_OPTIONS = {
    "古龍の魔結晶": {
        "id": "dragon",
        "power": 90,
        "boost": 70,
        "cost": 80,
        "desc": "【メイズ専用】莫大な魔力を供給する古代竜の結晶炉。",
    },
    "プラズマ核融合炉": {
        "id": "plasma",
        "power": 80,
        "boost": 90,
        "cost": 80,
        "desc": "【システムズ専用】安定した高出力を発揮する最新鋭核融合炉。",
    },
    "エーテルタービン": {
        "id": "ether",
        "power": 70,
        "boost": 80,
        "cost": 70,
        "desc": "【オアシス専用】大気と水の魔力を高効率で変換する環境機関。",
    },
    "ゼロ・ポイント機関": {
        "id": "zero",
        "power": 100,
        "boost": 100,
        "cost": 100,
        "desc": "【ムーンライト専用】次元の真空から無限エネルギーを引き出すオーパーツ。",
    },
}

ARMOR_OPTIONS = {
    "標準耐熱コーティング": {"id": "standard", "defense": 20, "weight": -5, "cost": 30},
    "魔力収束シールド発生器": {"id": "shield", "defense": 45, "weight": -15, "cost": 60},
    "重チタン・ハードプレート": {"id": "titanium", "defense": 70, "weight": 20, "cost": 75},
}

WEAPON_OPTIONS = {
    "エーテル・バルカン砲": {"id": "vulcan", "attack": 60, "bonus_accel": 5, "cost": 40},
    "プラズマ・キャノン": {"id": "cannon", "attack": 90, "bonus_accel": -5, "cost": 70},
    "近接ブレードポッド": {"id": "blade", "attack": 75, "bonus_accel": 15, "cost": 55},
    "武装なし（軽量化）": {"id": "none", "attack": 0, "bonus_accel": 25, "cost": 0},
}

FORMATION_SLOTS = [
    "前衛・上",
    "前衛・中",
    "前衛・下",
    "後衛・上",
    "後衛・中",
    "後衛・下",
]


def calc_machine_stats(chassis_name, core_name, armor_name, weapon_name):
    c = CHASSIS_OPTIONS[chassis_name]
    co = CORE_OPTIONS[core_name]
    a = ARMOR_OPTIONS[armor_name]
    w = WEAPON_OPTIONS[weapon_name]
    speed = c["speed"] + co["power"] // 2 - max(0, a["weight"])
    accel = c["accel"] + co["boost"] // 2 + w["bonus_accel"]
    defense = a["defense"] + c["handling"] // 2
    attack = w["attack"] + co["power"] // 2
    cost = c["cost"] + co["cost"] + a["cost"] + w["cost"]
    power = attack + defense + (speed // 2)
    return {
        "chassis": chassis_name,
        "chassis_id": c["id"],
        "core": core_name,
        "core_id": co["id"],
        "armor": armor_name,
        "armor_id": a["id"],
        "weapon": weapon_name,
        "weapon_id": w["id"],
        "speed": speed,
        "accel": accel,
        "defense": defense,
        "attack": attack,
        "power": power,
        "cost": cost,
    }


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
            return path, "フォールバック表示（フレーム標準画像）"

    any_images = (
        glob.glob("image/*.png") + glob.glob("image/*.jpg") + glob.glob("image/*.webp")
    )
    if any_images:
        return any_images[0], "プレースホルダー表示（image内の代替画像）"
    return None, "画像なし"


def image_to_data_uri(img_path):
    if not img_path or not os.path.exists(img_path):
        return None
    ext = os.path.splitext(img_path)[1].lower()
    mime = (
        "image/png"
        if ext == ".png"
        else ("image/jpeg" if ext in [".jpg", ".jpeg"] else "image/webp")
    )
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def create_default_unit(nation_name, uid_suffix, slot_idx=0):
    core_name = NATIONS[nation_name]["core"]
    m = calc_machine_stats(
        "全地形万能バギー", core_name, "標準耐熱コーティング", "エーテル・バルカン砲"
    )
    m["uid"] = f"{NATIONS[nation_name]['id']}_{uid_suffix}"
    m["name"] = f"量産機#{uid_suffix}"
    m["slot"] = FORMATION_SLOTS[slot_idx % len(FORMATION_SLOTS)]
    return m


def init_world(player_nation=None):
    terrain_grid = []
    owner_grid = []
    for r in range(8):
        t_row, o_row = [], []
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

    for n_name, info in NATIONS.items():
        hr, hc = info["home"]
        owner_grid[hr][hc] = n_name

    funds = {n: 500 for n in NATIONS}
    industry_lv = {n: 1 for n in NATIONS}

    hangar = {}
    corps = {}
    for n_name, info in NATIONS.items():
        hr, hc = info["home"]
        nat_units = [create_default_unit(n_name, f"init_{i+1}", i) for i in range(6)]
        hangar[n_name] = nat_units
        corps[n_name] = [
            {
                "id": f"第{i+1}部隊",
                "pos": (hr, hc),
                "units": [nat_units[i]],
                "invaded_this_turn": False,
            }
            for i in range(4)
        ]

    st.session_state.player_nation = player_nation
    st.session_state.phase = 0 if player_nation is None else 1
    st.session_state.turn = 1
    st.session_state.terrain_grid = terrain_grid
    st.session_state.owner_grid = owner_grid
    st.session_state.funds = funds
    st.session_state.industry_lv = industry_lv
    st.session_state.hangar = hangar
    st.session_state.corps = corps
    st.session_state.battle_data = None
    st.session_state.logs = [
        "=== ワールドマップを生成しました（全64領地） ==="
    ]


if "phase" not in st.session_state:
    init_world(None)


def get_income(nation_name):
    owned_count = sum(
        1
        for r in range(8)
        for c in range(8)
        if st.session_state.owner_grid[r][c] == nation_name
    )
    lv = st.session_state.industry_lv.get(nation_name, 1)
    return 100 + (lv * 60) + (owned_count * 25)


def add_funds(nation_name, amount):
    updated = dict(st.session_state.funds)
    updated[nation_name] = updated.get(nation_name, 0) + amount
    st.session_state.funds = updated


def get_adjacent_cells(r, c):
    res = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            res.append((nr, nc))
    return res


def render_map_html(highlight_pos=None):
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
    p_nat = st.session_state.player_nation
    rows_html = []
    for r in range(8):
        cells = []
        for c in range(8):
            owner = st.session_state.owner_grid[r][c]
            terrain = st.session_state.terrain_grid[r][c]
            t_icon = terrain_icons[terrain]
            t_label = terrain_short[terrain]

            player_badges = []
            enemy_badges = []
            for n_name, info in NATIONS.items():
                for idx, cp in enumerate(st.session_state.corps[n_name]):
                    if cp["pos"] == (r, c) and cp["units"]:
                        if n_name == p_nat:
                            player_badges.append(f"★隊{idx+1}")
                        else:
                            enemy_badges.append(f"{info['emoji']}隊{idx+1}")

            if owner:
                bg_color = NATIONS[owner]["color"]
                o_icon = NATIONS[owner]["emoji"]
                is_player = owner == p_nat
                border_style = "2px solid #ffffff" if is_player else "1px solid #1f242d"
                owner_tag = "★自国" if is_player else owner[:2]
            else:
                bg_color = "#262c36"
                o_icon = "🏳️"
                border_style = "1px solid #1f242d"
                owner_tag = "中立"

            if highlight_pos == (r, c):
                border_style = "3px solid #f1c40f"

            p_str = (
                f'<span style="color:#ffeaa7;font-weight:bold;">{" ".join(player_badges)}</span>'
                if player_badges
                else ""
            )
            e_str = (
                f'<span style="color:#ffcccc;">{" ".join(enemy_badges)}</span>'
                if enemy_badges
                else ""
            )
            badges_line = f"{p_str} {e_str}".strip()
            if not badges_line:
                badges_line = "&nbsp;"

            cell_html = (
                f'<td style="background-color:{bg_color};border:{border_style};'
                f'padding:4px 2px;color:#ffffff;border-radius:6px;width:12.5%;vertical-align:middle;">'
                f'<div style="font-size:14px;line-height:1.2;">{o_icon} <span style="font-size:10px;">{owner_tag}</span></div>'
                f'<div style="font-size:10px;line-height:1.2;opacity:0.95;">{t_icon}{t_label} ({r+1},{c+1})</div>'
                f'<div style="font-size:9px;line-height:1.2;">{badges_line}</div>'
                f"</td>"
            )
            cells.append(cell_html)
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<table style="width:100%;border-collapse:separate;border-spacing:3px;text-align:center;">'
        + "".join(rows_html)
        + "</table>"
    )


# --- 他国（AI）のフェーズ別戦略行動 ---
def run_ai_phase1_economy():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        inc = get_income(nat)
        add_funds(nat, inc)
        lv = st.session_state.industry_lv[nat]
        cost = lv * 150
        # 資金が潤沢なら産業投資を優先
        if st.session_state.funds[nat] >= cost + 120 and lv < 8:
            add_funds(nat, -cost)
            st.session_state.industry_lv[nat] += 1
            st.session_state.logs.insert(
                0, f"{info['emoji']} 【AI:{nat}】産業を Lv.{lv+1} に強化（収入+{inc}G）。"
            )


def run_ai_phase2_production():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        core_name = info["core"]
        # 領地や地形に合わせた機体選定
        if info["terrain"] == "荒れ地":
            chassis_choice = "重装甲魔導アーマー"
        elif info["terrain"] == "科学都市":
            chassis_choice = "超高速ホバリングバイク"
        elif info["terrain"] == "水上自然都市":
            chassis_choice = "全地形万能バギー"
        else:
            chassis_choice = "ステルス・ウィング"

        armor_choice = random.choice(list(ARMOR_OPTIONS.keys()))
        weapon_choice = random.choice(list(WEAPON_OPTIONS.keys()))
        unit = calc_machine_stats(chassis_choice, core_name, armor_choice, weapon_choice)
        if st.session_state.funds[nat] >= unit["cost"]:
            add_funds(nat, -unit["cost"])
            unit["uid"] = (
                f"{info['id']}_t{st.session_state.turn}_{random.randint(1000,9999)}"
            )
            unit["name"] = f"{chassis_choice[:4]}機"
            unit["slot"] = FORMATION_SLOTS[0]
            st.session_state.hangar[nat].append(unit)
            st.session_state.logs.insert(
                0, f"{info['emoji']} 【AI:{nat}】新鋭機「{unit['name']}」を生産。"
            )


def run_ai_phase3_formation():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        assigned = {u["uid"] for cp in st.session_state.corps[nat] for u in cp["units"]}
        standby = [u for u in st.session_state.hangar[nat] if u["uid"] not in assigned]
        for cp in st.session_state.corps[nat]:
            while len(cp["units"]) < 3 and standby:
                u = standby.pop(0)
                used_slots = {item.get("slot") for item in cp["units"]}
                free_slots = [s for s in FORMATION_SLOTS if s not in used_slots]
                u["slot"] = free_slots[0] if free_slots else FORMATION_SLOTS[0]
                cp["units"].append(u)
            # スロット位置を戦力に合わせて整理（高火力は後衛・前衛へ適切配置）
            for idx_u, u in enumerate(cp["units"]):
                u["slot"] = FORMATION_SLOTS[idx_u % len(FORMATION_SLOTS)]


def run_ai_phase4_movement_and_invasion():
    p_nat = st.session_state.player_nation
    ai_logs = []
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        for cp in st.session_state.corps[nat]:
            cp["invaded_this_turn"] = False
            if not cp["units"]:
                continue
            r, c = cp["pos"]
            if st.session_state.owner_grid[r][c] != nat:
                cp["pos"] = info["home"]
                r, c = cp["pos"]

            # 1. 自領内移動で前線へ近づく戦略判断
            adj = get_adjacent_cells(r, c)
            enemy_or_neutral = [
                pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] != nat
            ]
            friendly = [
                pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] == nat
            ]

            if not enemy_or_neutral and friendly:
                # 隣接に敵/中立がない場合、自領内で最も敵/中立に近いマスへ移動
                best_move = max(
                    friendly,
                    key=lambda p: len(
                        [
                            q
                            for q in get_adjacent_cells(p[0], p[1])
                            if st.session_state.owner_grid[q[0]][q[1]] != nat
                        ]
                    ),
                )
                cp["pos"] = best_move
                r, c = cp["pos"]
                adj = get_adjacent_cells(r, c)
                enemy_or_neutral = [
                    pos
                    for pos in adj
                    if st.session_state.owner_grid[pos[0]][pos[1]] != nat
                ]

            # 2. 各部隊ターン1回限りの侵攻・中立占領
            if enemy_or_neutral and not cp["invaded_this_turn"]:
                # 中立領地を最優先、次に得意地形を優先
                neutral_targets = [
                    pos for pos in enemy_or_neutral if st.session_state.owner_grid[pos[0]][pos[1]] is None
                ]
                if neutral_targets:
                    tr, tc = neutral_targets[0]
                    terrain = st.session_state.terrain_grid[tr][tc]
                    st.session_state.owner_grid[tr][tc] = nat
                    cp["pos"] = (tr, tc)
                    cp["invaded_this_turn"] = True
                    ai_logs.append(
                        f"{info['emoji']} 【AI:{nat}】{cp['id']} が中立領地 ({tr+1},{tc+1})[{terrain}] を無血占領！"
                    )
                else:
                    tr, tc = max(
                        enemy_or_neutral,
                        key=lambda p: 1
                        if st.session_state.terrain_grid[p[0]][p[1]] == info["terrain"]
                        else 0,
                    )
                    defender = st.session_state.owner_grid[tr][tc]
                    terrain = st.session_state.terrain_grid[tr][tc]
                    atk_power = sum(u["power"] for u in cp["units"]) + (
                        30 if terrain == info["terrain"] else 0
                    )
                    def_power = (
                        sum(u["power"] for u in st.session_state.corps[defender][0]["units"])
                        + 50
                    )
                    cp["invaded_this_turn"] = True
                    if atk_power >= def_power:
                        st.session_state.owner_grid[tr][tc] = nat
                        cp["pos"] = (tr, tc)
                        ai_logs.append(
                            f"{info['emoji']} 【AI:{nat}】{cp['id']} が ({tr+1},{tc+1})[{terrain}] の {defender} を撃破し占領！"
                        )
                    else:
                        cp["pos"] = info["home"]
                        cp["units"] = cp["units"][:1]
                        ai_logs.append(
                            f"{info['emoji']} 【AI:{nat}】{cp['id']} が ({tr+1},{tc+1}) の侵攻に失敗し本拠地へ撤退。"
                        )

    st.session_state.logs = ai_logs + st.session_state.logs


# --- ヘッダー＆全領地支配チェック ---
st.title("⚔️ エーテル・ウォー：4大国魔導機甲戦記")

if st.session_state.player_nation:
    p_nat = st.session_state.player_nation
    p_info = NATIONS[p_nat]
    owned_total = sum(
        1
        for r in range(8)
        for c in range(8)
        if st.session_state.owner_grid[r][c] == p_nat
    )
    if owned_total == 64:
        st.balloons()
        st.success(
            f"🏆 祝・全64領地完全支配！ 第 {st.session_state.turn} ターンにて **{p_nat}** が世界を統一しました！"
        )
        if st.button("最初から新しく始める"):
            init_world(None)
            st.rerun()
        st.stop()

    current_funds = st.session_state.funds.get(p_nat, 0)
    current_inc = get_income(p_nat)
    h1, h2, h3, h4, h5 = st.columns(5)
    h1.metric("担当国家", f"{p_info['emoji']} {p_nat}")
    h2.metric(
        "現在ターン / フェーズ", f"第{st.session_state.turn}T / Ph.{st.session_state.phase}"
    )
    h3.metric("所持資金", f"{current_funds} G")
    h4.metric("毎ターン収入予測", f"+{current_inc} G")
    h5.metric("支配領地", f"{owned_total} / 64")
    st.markdown("---")


# =========================================================
# フェーズ0：国家選択
# =========================================================
if st.session_state.phase == 0:
    st.subheader("フェーズ0：担当国家の選択")
    st.write("4つの国家の基本情報と固有動力コアを確認し、運営する国家を選択してください。")

    cols = st.columns(2)
    for idx, (n_name, info) in enumerate(NATIONS.items()):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {info['emoji']} {n_name}")
                st.write(
                    f"**拠点地形:** {info['terrain']}（本拠地: {info['home'][0]+1}, {info['home'][1]+1}）"
                )
                st.write(f"**固有動力コア:** {info['core']}")
                st.write(info["desc"])
                if st.button(
                    f"{n_name} で開始する", key=f"select_{info['id']}", type="primary"
                ):
                    init_world(n_name)
                    st.session_state.logs.insert(0, f"▶ {n_name} を担当国家として選択しました。")
                    st.rerun()


# =========================================================
# フェーズ1：資金調達フェーズ
# =========================================================
elif st.session_state.phase == 1:
    p_nat = st.session_state.player_nation
    st.subheader("フェーズ1：資金調達フェーズ")
    st.write(
        "担当国家の産業を活性化し、毎ターンの獲得資金を増やしましょう。他国も同時に経済・産業フェーズを実行します。"
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        lv = st.session_state.industry_lv[p_nat]
        upgrade_cost = lv * 150
        st.metric("現在の産業レベル", f"Lv.{lv}")
        st.write(f"産業強化コスト: **{upgrade_cost} G**（毎ターン収入 +60 G）")
        if st.button(
            "🏭 産業を活性化する（レベルアップ）",
            disabled=st.session_state.funds[p_nat] < upgrade_cost,
        ):
            add_funds(p_nat, -upgrade_cost)
            st.session_state.industry_lv[p_nat] += 1
            st.session_state.logs.insert(
                0, f"🏭 【自国】産業レベルが Lv.{lv+1} に上昇しました！"
            )
            st.rerun()

    with c2:
        st.markdown(render_map_html(), unsafe_allow_html=True)

    st.markdown("---")
    if st.button("➡️ フェーズ2（魔道機甲生産）へ進む", type="primary"):
        run_ai_phase1_economy()
        st.session_state.phase = 2
        st.rerun()


# =========================================================
# フェーズ2：魔道機甲生産フェーズ
# =========================================================
elif st.session_state.phase == 2:
    p_nat = st.session_state.player_nation
    p_info = NATIONS[p_nat]
    locked_core = p_info["core"]

    st.subheader("フェーズ2：魔道機甲生産フェーズ")
    st.write(
        f"資金を使って魔道機甲を生産します。動力コアは **{p_nat}** 固有の「**{locked_core}**」に限定されています。"
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sel_chassis = st.selectbox("① フレーム・ボディ", list(CHASSIS_OPTIONS.keys()))
        sel_core = st.selectbox(
            "② 動力機関（コア・国家限定）", [locked_core], disabled=True
        )
    with col_p2:
        sel_armor = st.selectbox("③ 装甲・防御システム", list(ARMOR_OPTIONS.keys()))
        sel_weapon = st.selectbox("④ 主武装・アタッチメント", list(WEAPON_OPTIONS.keys()))

    unit_name = st.text_input(
        "機体名称", value=f"{sel_chassis[:4]}-{random.randint(10,99)}"
    )
    stats = calc_machine_stats(sel_chassis, sel_core, sel_armor, sel_weapon)
    img_path, img_status = resolve_machine_image(
        stats["chassis_id"], stats["core_id"], stats["armor_id"], stats["weapon_id"]
    )

    v1, v2 = st.columns([1, 2])
    with v1:
        if img_path:
            st.image(
                img_path, caption=f"{unit_name} [{img_status}]", use_container_width=True
            )
        else:
            st.warning("`image` フォルダに画像が見つかりません。")
    with v2:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("生産コスト", f"{stats['cost']} G")
        m2.metric("攻撃力", stats["attack"])
        m3.metric("防御力", stats["defense"])
        m4.metric("総合戦闘力", stats["power"])
        st.code(
            f"image/chassis_{stats['chassis_id']}_core_{stats['core_id']}_armor_{stats['armor_id']}_weapon_{stats['weapon_id']}.png",
            language="text",
        )
        can_afford = st.session_state.funds[p_nat] >= stats["cost"]
        if st.button(
            "🛠️ この機体を生産する", type="primary", disabled=not can_afford
        ):
            add_funds(p_nat, -stats["cost"])
            new_u = dict(stats)
            new_u["uid"] = f"p_t{st.session_state.turn}_{random.randint(1000,9999)}"
            new_u["name"] = unit_name
            new_u["slot"] = FORMATION_SLOTS[0]
            st.session_state.hangar[p_nat].append(new_u)
            st.session_state.logs.insert(
                0, f"🛠️ 【自国】魔道機甲「{unit_name}」を生産しました。"
            )
            st.rerun()

    st.write(f"**現在の格納庫総保有数:** {len(st.session_state.hangar[p_nat])} 機")
    st.markdown("---")
    if st.button("➡️ フェーズ3（部隊編成・配置）へ進む", type="primary"):
        run_ai_phase2_production()
        st.session_state.phase = 3
        st.rerun()


# =========================================================
# フェーズ3：部隊編成フェーズ（前衛3＋後衛3の計6機配置＆格納庫移動）
# =========================================================
elif st.session_state.phase == 3:
    p_nat = st.session_state.player_nation
    st.subheader("フェーズ3：部隊編成・戦闘配置フェーズ")
    st.write(
        "4つの部隊にそれぞれ最大 **6機**（前衛3か所・後衛3か所）まで魔道機甲を編成できます。不要になった機体は「格納庫へ移動」ボタンで待機状態に戻せます。"
    )

    user_corps = st.session_state.corps[p_nat]
    hangar_list = st.session_state.hangar[p_nat]

    assigned_uids = {u["uid"] for cp in user_corps for u in cp["units"]}
    standby_units = [u for u in hangar_list if u["uid"] not in assigned_uids]

    st.info(
        f"📦 **格納庫の待機機体数:** {len(standby_units)} 機（全保有数: {len(hangar_list)} 機）"
    )

    corp_tabs = st.tabs(
        [
            f"{cp['id']}（{len(cp['units'])}/6機・位置:{cp['pos'][0]+1},{cp['pos'][1]+1}）"
            for cp in user_corps
        ]
    )
    for idx, tab in enumerate(corp_tabs):
        cp = user_corps[idx]
        with tab:
            slot_map = {u.get("slot"): u for u in cp["units"]}
            st.markdown("#### 📐 現在の陣形配置（最大6機）")
            f_col_rear, f_col_front = st.columns(2)
            with f_col_rear:
                st.caption("【後衛ライン】")
                for s_name in ["後衛・上", "後衛・中", "後衛・下"]:
                    occupant = slot_map.get(s_name)
                    if occupant:
                        st.success(
                            f"**{s_name}**: 🤖 {occupant['name']} (戦力:{occupant['power']})"
                        )
                    else:
                        st.markdown(f"- *{s_name}*: （空き）")
            with f_col_front:
                st.caption("【前衛ライン】")
                for s_name in ["前衛・上", "前衛・中", "前衛・下"]:
                    occupant = slot_map.get(s_name)
                    if occupant:
                        st.warning(
                            f"**{s_name}**: 🤖 {occupant['name']} (戦力:{occupant['power']})"
                        )
                    else:
                        st.markdown(f"- *{s_name}*: （空き）")

            st.markdown("---")
            st.markdown(f"#### 🤖 配備中の機体管理（{len(cp['units'])} / 6 機）")
            if not cp["units"]:
                st.write("この部隊には現在機体が配備されていません。")

            for u_i, u in enumerate(cp["units"]):
                u_img_path, _ = resolve_machine_image(
                    u["chassis_id"], u["core_id"], u["armor_id"], u["weapon_id"]
                )
                uc0, uc1, uc2, uc3 = st.columns([1.1, 3, 2, 1.4])
                with uc0:
                    if u_img_path:
                        st.image(u_img_path, use_container_width=True)
                    else:
                        st.caption("画像なし")
                uc1.write(
                    f"🤖 **{u['name']}**\n\n戦力:{u['power']} / {u['chassis']} / {u['weapon']}"
                )
                cur_slot = u.get("slot", FORMATION_SLOTS[0])
                if cur_slot not in FORMATION_SLOTS:
                    cur_slot = FORMATION_SLOTS[0]
                new_slot = uc2.selectbox(
                    "配置ポジション",
                    FORMATION_SLOTS,
                    index=FORMATION_SLOTS.index(cur_slot),
                    key=f"slot_{idx}_{u['uid']}",
                )
                u["slot"] = new_slot
                if uc3.button("📦 格納庫へ移動", key=f"rem_{idx}_{u['uid']}"):
                    removed_u = cp["units"].pop(u_i)
                    st.session_state.logs.insert(
                        0,
                        f"📦 【自国】「{removed_u['name']}」を {cp['id']} から格納庫へ移動しました。",
                    )
                    st.rerun()

            if len(cp["units"]) < 6 and standby_units:
                st.markdown("---")
                st.markdown("#### ➕ 格納庫から部隊へ配備")
                add_map = {
                    f"{u['name']}（戦力:{u['power']} / {u['chassis']}）": u
                    for u in standby_units
                }
                pick_label = st.selectbox(
                    "格納庫の待機機体を選択", list(add_map.keys()), key=f"add_sel_{idx}"
                )
                picked_u = add_map[pick_label]
                p_img_path, _ = resolve_machine_image(
                    picked_u["chassis_id"],
                    picked_u["core_id"],
                    picked_u["armor_id"],
                    picked_u["weapon_id"],
                )
                ac1, ac2 = st.columns([1, 4])
                with ac1:
                    if p_img_path:
                        st.image(p_img_path, use_container_width=True)
                with ac2:
                    used_slots = {u.get("slot") for u in cp["units"]}
                    free_slots = [s for s in FORMATION_SLOTS if s not in used_slots]
                    target_slot = st.selectbox(
                        "配備先ポジション",
                        free_slots if free_slots else FORMATION_SLOTS,
                        key=f"add_slot_{idx}",
                    )
                    if st.button("部隊へ配備する", key=f"add_btn_{idx}", type="primary"):
                        picked_u["slot"] = target_slot
                        cp["units"].append(picked_u)
                        st.rerun()

    st.markdown("---")
    if st.button("➡️ フェーズ4（侵攻・移動）へ進む", type="primary"):
        run_ai_phase3_formation()
        st.session_state.phase = 4
        st.session_state.battle_data = None
        st.rerun()


# =========================================================
# フェーズ4：侵攻フェーズ（自領内移動無制限・侵攻各部隊1回・中立無血占領）
# =========================================================
elif st.session_state.phase == 4:
    p_nat = st.session_state.player_nation
    p_info = NATIONS[p_nat]
    st.subheader("フェーズ4：侵攻・移動フェーズ")
    st.write(
        "自国領地内の移動は何度でも可能ですが、**侵攻・占領は各部隊1ターンにつき1回まで**です。**中立地域は戦闘なしでそのまま占領**できます。"
    )

    user_corps = st.session_state.corps[p_nat]
    c_idx = st.selectbox(
        "行動させる部隊を選択",
        range(4),
        format_func=lambda i: (
            f"{user_corps[i]['id']}（現在地:{user_corps[i]['pos'][0]+1},{user_corps[i]['pos'][1]+1} / "
            f"機体:{len(user_corps[i]['units'])}/6 / "
            f"今ターン侵攻:{'済' if user_corps[i].get('invaded_this_turn') else '未'}）"
        ),
    )
    active_corp = user_corps[c_idx]
    cur_r, cur_c = active_corp["pos"]
    adj = get_adjacent_cells(cur_r, cur_c)

    friendly_adj = [
        pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] == p_nat
    ]
    neutral_adj = [
        pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] is None
    ]
    enemy_adj = [
        pos
        for pos in adj
        if st.session_state.owner_grid[pos[0]][pos[1]] not in (None, p_nat)
    ]

    top_map_col, top_cmd_col = st.columns([1.4, 1])
    with top_map_col:
        st.markdown("### 🗺️ 現在の戦略マップ（自軍・敵軍部隊位置）")
        st.markdown(
            render_map_html(highlight_pos=(cur_r, cur_c)), unsafe_allow_html=True
        )
        st.caption(
            f"黄枠: {active_corp['id']} の現在地 ({cur_r+1}, {cur_c+1}) / ★隊1〜4: 自軍部隊 / 🔥⚡🌿🌙隊1〜4: 他国部隊"
        )

    with top_cmd_col:
        st.markdown("### 🧭 自領内移動（何度でも可能）")
        if friendly_adj:
            move_target = st.selectbox(
                "移動先（自国領地）",
                friendly_adj,
                format_func=lambda p: f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}]",
                key="move_sel",
            )
            if st.button("この自国領地へ移動する", use_container_width=True):
                active_corp["pos"] = move_target
                st.session_state.logs.insert(
                    0,
                    f"🧭 【自国】{active_corp['id']} が ({move_target[0]+1},{move_target[1]+1}) へ移動しました。",
                )
                st.rerun()
        else:
            st.info("隣接する自国領地がありません。")

        st.markdown("---")
        already_invaded = bool(active_corp.get("invaded_this_turn"))
        if already_invaded:
            st.warning(
                f"🔒 {active_corp['id']} は今ターンの侵攻・占領をすでに実行済みです（自領内移動は可能）。"
            )
        else:
            st.markdown("### 🏳️ 中立地域の無血占領（各部隊ターン1回）")
            if neutral_adj and active_corp["units"]:
                neu_target = st.selectbox(
                    "占領する隣接中立地域",
                    neutral_adj,
                    format_func=lambda p: f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}]",
                    key="neu_sel",
                )
                if st.button("🏳️ 戦闘なしで中立地域を占領する", use_container_width=True):
                    nr, nc = neu_target
                    t_name = st.session_state.terrain_grid[nr][nc]
                    st.session_state.owner_grid[nr][nc] = p_nat
                    active_corp["pos"] = (nr, nc)
                    active_corp["invaded_this_turn"] = True
                    st.session_state.logs.insert(
                        0,
                        f"🏳️ 【自国】{active_corp['id']} が中立地域 ({nr+1},{nc+1})[{t_name}] を無血占領しました！",
                    )
                    st.rerun()
            else:
                st.caption("隣接する中立地域がないか、機体が未配備です。")

            st.markdown("### ⚔️ 敵国領地への侵攻（各部隊ターン1回・自動戦闘）")
            if enemy_adj and active_corp["units"]:
                inv_target = st.selectbox(
                    "侵攻先（敵国領地）",
                    enemy_adj,
                    format_func=lambda p: f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}] - {st.session_state.owner_grid[p[0]][p[1]]}",
                    key="inv_sel",
                )
                if st.button(
                    "⚔️ 敵国領地へ侵攻（自動戦闘を実行）",
                    type="primary",
                    use_container_width=True,
                ):
                    tr, tc = inv_target
                    defender = st.session_state.owner_grid[tr][tc]
                    terrain = st.session_state.terrain_grid[tr][tc]
                    atk_power = sum(u["power"] for u in active_corp["units"]) + (
                        30 if terrain == p_info["terrain"] else 0
                    )
                    def_power = (
                        sum(
                            u["power"]
                            for u in st.session_state.corps[defender][0]["units"]
                        )
                        + 50
                    )
                    won = atk_power >= def_power
                    active_corp["invaded_this_turn"] = True

                    unit_visuals = []
                    for u in active_corp["units"]:
                        u_img_path, _ = resolve_machine_image(
                            u["chassis_id"],
                            u["core_id"],
                            u["armor_id"],
                            u["weapon_id"],
                        )
                        unit_visuals.append(
                            {
                                "name": u["name"],
                                "slot": u.get("slot", "前衛・上"),
                                "img_uri": image_to_data_uri(u_img_path),
                            }
                        )

                    enemy_visuals = []
                    def_corps = st.session_state.corps[defender]
                    def_units = def_corps[0]["units"] if def_corps else []
                    for idx_d, du in enumerate(def_units[:6]):
                        d_path, _ = resolve_machine_image(
                            du["chassis_id"],
                            du["core_id"],
                            du["armor_id"],
                            du["weapon_id"],
                        )
                        enemy_visuals.append(
                            {
                                "name": du["name"],
                                "slot": FORMATION_SLOTS[idx_d % len(FORMATION_SLOTS)],
                                "img_uri": image_to_data_uri(d_path),
                            }
                        )
                    if not enemy_visuals:
                        for idx_d in range(3):
                            enemy_visuals.append(
                                {
                                    "name": f"{defender[:4]}防衛機",
                                    "slot": FORMATION_SLOTS[idx_d],
                                    "img_uri": None,
                                }
                            )

                    if won:
                        st.session_state.owner_grid[tr][tc] = p_nat
                        active_corp["pos"] = (tr, tc)
                        res_msg = f"🏆 【自国】{active_corp['id']} が ({tr+1},{tc+1})[{terrain}] の {defender} を撃破し領地を奪取！"
                    else:
                        active_corp["pos"] = p_info["home"]
                        active_corp["units"] = active_corp["units"][:1]
                        res_msg = f"💥 【自国】{active_corp['id']} が ({tr+1},{tc+1}) の侵攻に敗北し、本拠地へ撤退しました。"

                    st.session_state.logs.insert(0, res_msg)
                    st.session_state.battle_data = {
                        "player_name": p_nat,
                        "player_color": p_info["color"],
                        "enemy_name": defender,
                        "enemy_color": NATIONS[defender]["color"],
                        "atk_power": atk_power,
                        "def_power": def_power,
                        "won": won,
                        "player_units": unit_visuals,
                        "enemy_units": enemy_visuals,
                        "target_label": f"({tr+1},{tc+1}) {terrain}",
                    }
                    st.rerun()
            else:
                st.caption("隣接する敵国領地がないか、機体が未配備です。")

    # 大きめサイズの戦闘画面（920x460）
    if st.session_state.battle_data:
        b_json = json.dumps(st.session_state.battle_data)
        st.markdown("### 💥 戦闘シミュレーション（6機陣形・機体画像自動戦闘）")
        battle_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ background: #0e1117; color: #fff; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; }}
  canvas {{ background: #161b22; border: 2px solid #30363d; border-radius: 10px; max-width: 100%; }}
  .banner {{ margin-top: 10px; font-size: 17px; font-weight: bold; }}
</style>
</head>
<body>
<canvas id="battleCanvas" width="920" height="460"></canvas>
<div id="resultBanner" class="banner">戦闘アニメーション再生中...</div>
<script>
  const b = {b_json};
  const canvas = document.getElementById('battleCanvas');
  const ctx = canvas.getContext('2d');
  let frame = 0;

  const pImages = b.player_units.map(u => {{
    if (!u.img_uri) return null;
    const img = new Image();
    img.src = u.img_uri;
    return img;
  }});

  const eImages = b.enemy_units.map(u => {{
    if (!u.img_uri) return null;
    const img = new Image();
    img.src = u.img_uri;
    return img;
  }});

  function getRowY(slot, fallbackIdx) {{
    if (slot.includes('上')) return 55;
    if (slot.includes('中')) return 195;
    if (slot.includes('下')) return 335;
    return 55 + (fallbackIdx % 3) * 140;
  }}

  function drawBattle() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#21262d';
    ctx.lineWidth = 1;
    for (let gx = 80; gx < 920; gx += 80) {{
      ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, 460); ctx.stroke();
    }}

    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 8]);
    ctx.beginPath(); ctx.moveTo(460, 20); ctx.lineTo(460, 440); ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#8b949e';
    ctx.font = 'bold 13px sans-serif';
    ctx.fillText('【自軍】' + b.player_name, 30, 26);
    ctx.fillText('【敵軍】' + b.enemy_name, 730, 26);

    const moveProgress = Math.min(frame / 45, 1);

    b.player_units.forEach((u, i) => {{
      const isRear = u.slot.startsWith('後衛');
      const baseX = isRear ? 35 : 145;
      const advance = isRear ? 85 : 155;
      const surge = (frame >= 45 && frame <= 75) ? Math.sin(((frame - 45) / 30) * Math.PI) * 32 : 0;
      const retreat = (!b.won && frame > 75) ? Math.min((frame - 75) * 5, 160) : 0;
      const x = baseX + advance * moveProgress + surge - retreat;
      const y = getRowY(u.slot, i);

      const img = pImages[i];
      if (img && img.complete && img.naturalWidth > 0) {{
        ctx.drawImage(img, x, y, 84, 64);
      }} else {{
        ctx.fillStyle = b.player_color;
        ctx.fillRect(x, y, 84, 64);
      }}

      if (frame >= 45 && frame <= 85) {{
        const bp = (frame - 45) / 40;
        const bx = x + 84 + (680 - (x + 84)) * bp;
        const by = y + 32;
        ctx.fillStyle = '#ffd166';
        ctx.beginPath();
        ctx.arc(bx, by, 7, 0, Math.PI * 2);
        ctx.fill();
      }}

      ctx.strokeStyle = b.player_color;
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x, y, 84, 64);

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 11px sans-serif';
      ctx.fillText(u.name + ' (' + u.slot + ')', x, y - 6);
    }});

    b.enemy_units.forEach((eu, i) => {{
      const isRear = eu.slot.startsWith('後衛');
      const x = isRear ? 785 : 675;
      const y = getRowY(eu.slot, i);
      const destroyed = b.won && frame > 72;

      if (!destroyed) {{
        const eImg = eImages[i];
        if (eImg && eImg.complete && eImg.naturalWidth > 0) {{
          ctx.drawImage(eImg, x, y, 84, 64);
        }} else {{
          ctx.fillStyle = b.enemy_color;
          ctx.fillRect(x, y, 84, 64);
        }}

        if (frame >= 50 && frame <= 85) {{
          const ebp = (frame - 50) / 35;
          const ebx = x - (x - 260) * ebp;
          const eby = y + 32;
          ctx.fillStyle = '#ff6b6b';
          ctx.beginPath();
          ctx.arc(ebx, eby, 6, 0, Math.PI * 2);
          ctx.fill();
        }}

        ctx.strokeStyle = b.enemy_color;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(x, y, 84, 64);
        ctx.fillStyle = '#ffffff';
        ctx.font = '11px sans-serif';
        ctx.fillText(eu.name, x, y - 6);
      }} else {{
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 15px sans-serif';
        ctx.fillText('💥 撃破', x + 14, y + 38);
      }}
    }});

    if (frame >= 55 && frame <= 85) {{
      ctx.fillStyle = b.won ? 'rgba(241, 196, 15, 0.7)' : 'rgba(231, 76, 60, 0.7)';
      ctx.beginPath();
      ctx.arc(b.won ? 700 : 280, 230, 28 + ((frame - 55) % 16), 0, Math.PI * 2);
      ctx.fill();
    }}

    if (frame < 95) {{
      frame++;
      requestAnimationFrame(drawBattle);
    }} else {{
      const el = document.getElementById('resultBanner');
      if (b.won) {{
        el.style.color = '#2ecc71';
        el.innerText = '【勝利】' + b.target_label + ' を制圧！（戦力 ' + b.atk_power + ' vs ' + b.def_power + '）';
      }} else {{
        el.style.color = '#e74c3c';
        el.innerText = '【敗北】' + b.target_label + ' の侵攻に失敗し本拠地へ撤退（戦力 ' + b.atk_power + ' vs ' + b.def_power + '）';
      }}
    }}
  }}
  drawBattle();
</script>
</body>
</html>
"""
        st.components.v1.html(battle_html, height=520)

    st.markdown("---")
    if st.button(
        "➡️ 他国の侵攻フェーズを実行し、フェーズ5（ターン結果・マップ）へ進む",
        type="primary",
    ):
        run_ai_phase4_movement_and_invasion()
        st.session_state.phase = 5
        st.rerun()


# =========================================================
# フェーズ5：ターンの結果をマップ表示
# =========================================================
elif st.session_state.phase == 5:
    st.subheader(f"フェーズ5：第 {st.session_state.turn} ターン結果・ワールドマップ")

    m_col, r_col = st.columns([2, 1])
    with m_col:
        st.markdown(render_map_html(), unsafe_allow_html=True)
        st.caption(
            "※ 左上(1〜4,1〜4): 荒れ地 / 右上(1〜4,5〜8): 科学都市 / 左下(5〜8,1〜4): 水上自然都市 / 右下(5〜8,5〜8): 月面都市 ｜ ★隊:自軍 / 🔥⚡🌿🌙隊:敵軍"
        )
    with r_col:
        st.markdown("### 📜 今ターンの戦況ログ")
        st.text_area(
            "戦況ログ",
            "\n".join(st.session_state.logs[:18]),
            height=380,
            label_visibility="collapsed",
        )

    st.markdown("---")
    if st.button("🔄 次のターン（フェーズ1：資金調達）へ進む", type="primary"):
        p_nat = st.session_state.player_nation
        inc = get_income(p_nat)
        add_funds(p_nat, inc)
        # 自軍各部隊の侵攻回数制限をリセット
        for cp in st.session_state.corps[p_nat]:
            cp["invaded_this_turn"] = False
        st.session_state.turn += 1
        st.session_state.phase = 1
        st.session_state.battle_data = None
        st.session_state.logs.insert(
            0,
            f"=== 第 {st.session_state.turn} ターン開始（自国収入 +{inc} G → 所持 {st.session_state.funds[p_nat]} G・侵攻回数リセット）===",
        )
        st.rerun()
