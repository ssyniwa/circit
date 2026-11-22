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
        "strategy": "重装甲・正面突破型（軍備生産を最優先し、前衛重視で敵駐留地へ積極侵攻）",
        "desc": "荒れ地に君臨する魔導帝国。古龍の魔力を動力源とし、重装甲機による正面突破を得意とする。",
    },
    "サイバー科学国家システムズ": {
        "id": "systems",
        "terrain": "科学都市",
        "core": "プラズマ核融合炉",
        "color": "#2980b9",
        "emoji": "⚡",
        "home": (0, 7),
        "strategy": "経済重視・電撃拡張型（産業投資を最優先し、高速機で無人・中立領地を急速拡大）",
        "desc": "高度に発達した科学都市国家。圧倒的な経済力と高速機動戦術で版図を広げる。",
    },
    "水上自然都市融合国家オアシス": {
        "id": "oasis",
        "terrain": "水上自然都市",
        "core": "エーテルタービン",
        "color": "#27ae60",
        "emoji": "🌿",
        "home": (7, 0),
        "strategy": "バランス・領域防衛型（産業と軍備を均等に育て、得意地形と防衛線を堅実に維持）",
        "desc": "自然と調和する水上都市国家。環境エーテルを利用した安定した戦線維持に長ける。",
    },
    "月面開拓国家ムーンライト": {
        "id": "moonlight",
        "terrain": "月面都市",
        "core": "ゼロ・ポイント機関",
        "color": "#8e44ad",
        "emoji": "🌙",
        "home": (7, 7),
        "strategy": "少数精鋭・長距離砲撃型（高コスト精鋭機を後衛主体で編成し、高火力砲撃で敵軍を粉砕）",
        "desc": "月面クレーターに築かれた開拓国家。未知の真空エネルギー機関による高火力砲撃戦を繰り広げる。",
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
        "trait": "重装甲バリア（防御力+20・前衛配置で戦力ボーナス）",
        "desc": "圧倒的な防御力と安定した進軍を誇る重機甲。",
    },
    "超高速ホバリングバイク": {
        "id": "hover",
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "cost": 110,
        "trait": "高速強襲（機動力+25・先制攻撃ボーナス）",
        "desc": "電撃的な領地制圧に特化した反重力ビークル。",
    },
    "全地形万能バギー": {
        "id": "buggy",
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "cost": 100,
        "trait": "全地形適応（どの地形でも地形適正ボーナス+20）",
        "desc": "荒れ地から水上まであらゆる地形に対応するバランス型フレーム。",
    },
    "ステルス・ウィング": {
        "id": "wing",
        "speed": 90,
        "accel": 65,
        "handling": 60,
        "cost": 130,
        "trait": "光学迷彩（後衛配置で攻撃力+25・奇襲効果）",
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
    "エーテル・バルカン砲": {
        "id": "vulcan",
        "attack": 60,
        "bonus_accel": 5,
        "cost": 40,
        "style": "高速3連バースト射撃（安定した手数で前衛・後衛問わず活躍）",
    },
    "プラズマ・キャノン": {
        "id": "cannon",
        "attack": 90,
        "bonus_accel": -5,
        "cost": 70,
        "style": "超長射程レーザー砲撃（後衛配置時に火力+30の狙撃ボーナス）",
    },
    "近接ブレードポッド": {
        "id": "blade",
        "attack": 75,
        "bonus_accel": 15,
        "cost": 55,
        "style": "超高速斬撃突撃（前衛配置時に火力+30・敵陣へ切り込む）",
    },
    "武装なし（軽量化）": {
        "id": "none",
        "attack": 0,
        "bonus_accel": 25,
        "cost": 0,
        "style": "超軽量体当たりタックル（機動力+30で部隊全体の速度底上げ）",
    },
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

    if c["id"] == "heavy":
        defense += 20
    elif c["id"] == "hover":
        speed += 25
    if w["id"] == "none":
        speed += 30

    cost = c["cost"] + co["cost"] + a["cost"] + w["cost"]
    power = attack + defense + (speed // 2)
    return {
        "chassis": chassis_name,
        "chassis_id": c["id"],
        "chassis_trait": c["trait"],
        "core": core_name,
        "core_id": co["id"],
        "armor": armor_name,
        "armor_id": a["id"],
        "weapon": weapon_name,
        "weapon_id": w["id"],
        "weapon_style": w["style"],
        "speed": speed,
        "accel": accel,
        "defense": defense,
        "attack": attack,
        "power": power,
        "cost": cost,
    }


def calc_unit_effective_power(unit, terrain, nation_terrain):
    p = unit["power"]
    slot = unit.get("slot", "前衛・上")
    is_front = slot.startswith("前衛")
    is_rear = slot.startswith("後衛")

    if unit["chassis_id"] == "heavy" and is_front:
        p += 20
    elif unit["chassis_id"] == "wing" and is_rear:
        p += 25
    elif unit["chassis_id"] == "buggy":
        p += 20

    if unit["weapon_id"] == "cannon" and is_rear:
        p += 30
    elif unit["weapon_id"] == "blade" and is_front:
        p += 30
    elif unit["weapon_id"] == "vulcan":
        p += 10

    if terrain == nation_terrain and unit["chassis_id"] != "buggy":
        p += 25

    return p


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


def create_mass_unit(nation_name, corp_idx, slot_idx):
    """初期配備用の武装無し量産型機体を生成"""
    core_name = NATIONS[nation_name]["core"]
    m = calc_machine_stats(
        "全地形万能バギー", core_name, "標準耐熱コーティング", "武装なし（軽量化）"
    )
    m["uid"] = f"{NATIONS[nation_name]['id']}_c{corp_idx+1}_s{slot_idx+1}"
    m["name"] = f"量産型{corp_idx+1}-{slot_idx+1}(無装)"
    m["slot"] = FORMATION_SLOTS[slot_idx]
    m["is_mass"] = True
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

    funds = {n: 600 for n in NATIONS}
    industry_lv = {n: 1 for n in NATIONS}

    # 全国家・全4部隊に6機ずつの武装無し量産型機体を初期配備し、格納庫リストは空で開始
    hangar = {n: [] for n in NATIONS}
    corps = {}
    for n_name, info in NATIONS.items():
        hr, hc = info["home"]
        corps[n_name] = [
            {
                "id": f"第{i+1}部隊",
                "pos": (hr, hc),
                "units": [create_mass_unit(n_name, i, s_i) for s_i in range(6)],
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
        "=== ワールドマップを生成しました（全4部隊に6機の量産型機体を配備済み） ==="
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


def get_garrison_corps(r, c, owner_nation):
    if not owner_nation:
        return []
    return [
        cp
        for cp in st.session_state.corps[owner_nation]
        if cp["pos"] == (r, c) and len(cp["units"]) > 0
    ]


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


# =========================================================
# 他国（AI）のフェーズ別戦略行動
# =========================================================
def run_ai_phase1_economy():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        inc = get_income(nat)
        add_funds(nat, inc)
        lv = st.session_state.industry_lv[nat]
        cost = lv * 150

        if nat == "サイバー科学国家システムズ":
            should_upgrade = st.session_state.funds[nat] >= cost and lv < 10
        elif nat == "魔導技術国家メイズ":
            should_upgrade = st.session_state.funds[nat] >= cost + 300 and lv < 6
        elif nat == "水上自然都市融合国家オアシス":
            should_upgrade = st.session_state.funds[nat] >= cost + 150 and lv < 8
        else:
            should_upgrade = st.session_state.funds[nat] >= cost + 250 and lv < 8

        if should_upgrade:
            add_funds(nat, -cost)
            st.session_state.industry_lv[nat] += 1
            st.session_state.logs.insert(
                0, f"{info['emoji']} 【AI:{nat}】産業を Lv.{lv+1} に強化。"
            )


def run_ai_phase2_production():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        core_name = info["core"]

        if nat == "魔導技術国家メイズ":
            chassis_choice = random.choice(["重装甲魔導アーマー", "全地形万能バギー"])
            armor_choice = random.choice(["重チタン・ハードプレート", "魔力収束シールド発生器"])
            weapon_choice = random.choice(["近接ブレードポッド", "エーテル・バルカン砲"])
            max_builds = 2
        elif nat == "サイバー科学国家システムズ":
            chassis_choice = random.choice(["超高速ホバリングバイク", "ステルス・ウィング"])
            armor_choice = "標準耐熱コーティング"
            weapon_choice = "エーテル・バルカン砲"
            max_builds = 2
        elif nat == "水上自然都市融合国家オアシス":
            chassis_choice = random.choice(["全地形万能バギー", "重装甲魔導アーマー"])
            armor_choice = "魔力収束シールド発生器"
            weapon_choice = random.choice(["エーテル・バルカン砲", "プラズマ・キャノン"])
            max_builds = 1
        else:
            chassis_choice = random.choice(["ステルス・ウィング", "超高速ホバリングバイク"])
            armor_choice = "魔力収束シールド発生器"
            weapon_choice = "プラズマ・キャノン"
            max_builds = 1

        for _ in range(max_builds):
            unit = calc_machine_stats(
                chassis_choice, core_name, armor_choice, weapon_choice
            )
            if st.session_state.funds[nat] >= unit["cost"]:
                add_funds(nat, -unit["cost"])
                unit["uid"] = (
                    f"{info['id']}_t{st.session_state.turn}_{random.randint(1000,9999)}"
                )
                unit["name"] = f"{chassis_choice[:4]}改"
                unit["slot"] = FORMATION_SLOTS[0]
                unit["is_mass"] = False
                st.session_state.hangar[nat].append(unit)
                st.session_state.logs.insert(
                    0,
                    f"{info['emoji']} 【AI:{nat}】格納庫に新鋭機「{unit['name']}({weapon_choice[:4]})」を生産。",
                )


def run_ai_phase3_formation():
    p_nat = st.session_state.player_nation
    for nat, info in NATIONS.items():
        if nat == p_nat:
            continue
        hangar_units = st.session_state.hangar[nat]
        if not hangar_units:
            continue

        # 格納庫にある新鋭機と既存部隊の量産機を交換
        for cp in st.session_state.corps[nat]:
            if not hangar_units:
                break
            for u_i, cur_u in enumerate(cp["units"]):
                if not hangar_units:
                    break
                if cur_u.get("is_mass", False):
                    new_u = hangar_units.pop(0)
                    new_u["slot"] = cur_u.get("slot", FORMATION_SLOTS[u_i % 6])
                    cp["units"][u_i] = new_u
                    hangar_units.append(cur_u)


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

            for _step in range(2):
                adj = get_adjacent_cells(r, c)
                non_own = [
                    pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] != nat
                ]
                friendly = [
                    pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] == nat
                ]
                if non_own or not friendly:
                    break
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
            candidates = [
                pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] != nat
            ]
            if not candidates or cp["invaded_this_turn"]:
                continue

            def score_target(pos):
                tr, tc = pos
                owner = st.session_state.owner_grid[tr][tc]
                terrain = st.session_state.terrain_grid[tr][tc]
                garrison = get_garrison_corps(tr, tc, owner)
                is_empty = owner is None or len(garrison) == 0

                score = 0
                if is_empty:
                    score += 50
                if terrain == info["terrain"]:
                    score += 25

                if nat == "魔導技術国家メイズ" and not is_empty:
                    score += 45
                elif nat == "サイバー科学国家システムズ" and is_empty:
                    score += 60
                elif nat == "水上自然都市融合国家オアシス" and terrain == "水上自然都市":
                    score += 70
                elif nat == "月面開拓国家ムーンライト":
                    my_pow = sum(
                        calc_unit_effective_power(u, terrain, info["terrain"])
                        for u in cp["units"]
                    )
                    if my_pow >= 450 and not is_empty:
                        score += 55
                return score + random.randint(0, 15)

            tr, tc = max(candidates, key=score_target)
            defender = st.session_state.owner_grid[tr][tc]
            terrain = st.session_state.terrain_grid[tr][tc]
            garrison_list = get_garrison_corps(tr, tc, defender)
            cp["invaded_this_turn"] = True

            if defender is None or len(garrison_list) == 0:
                st.session_state.owner_grid[tr][tc] = nat
                cp["pos"] = (tr, tc)
                label = "中立地域" if defender is None else f"{defender}の無人領地"
                ai_logs.append(
                    f"{info['emoji']} 【AI:{nat}】{cp['id']} が ({tr+1},{tc+1})[{terrain}] の{label}を戦闘なしで占領！"
                )
            else:
                atk_power = sum(
                    calc_unit_effective_power(u, terrain, info["terrain"])
                    for u in cp["units"]
                )
                def_info = NATIONS[defender]
                def_units = [u for g_cp in garrison_list for u in g_cp["units"]]
                def_power = sum(
                    calc_unit_effective_power(u, terrain, def_info["terrain"])
                    for u in def_units
                )
                if atk_power >= def_power:
                    st.session_state.owner_grid[tr][tc] = nat
                    cp["pos"] = (tr, tc)
                    for g_cp in garrison_list:
                        g_cp["pos"] = def_info["home"]
                        g_cp["units"] = g_cp["units"][:1]
                    ai_logs.append(
                        f"{info['emoji']} 【AI:{nat}】{cp['id']} が ({tr+1},{tc+1})[{terrain}] で {defender} 駐留部隊を撃破し占領！"
                    )
                else:
                    cp["pos"] = info["home"]
                    cp["units"] = cp["units"][:1]
                    ai_logs.append(
                        f"{info['emoji']} 【AI:{nat}】{cp['id']} が ({tr+1},{tc+1}) の {defender} 防衛部隊に敗北し本拠地へ撤退。"
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
    st.write("4つの国家の基本情報・固有動力コア・AI戦略傾向を確認し、運営する国家を選択してください。")

    cols = st.columns(2)
    for idx, (n_name, info) in enumerate(NATIONS.items()):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {info['emoji']} {n_name}")
                st.write(
                    f"**拠点地形:** {info['terrain']}（本拠地: {info['home'][0]+1}, {info['home'][1]+1}）"
                )
                st.write(f"**固有動力コア:** {info['core']}")
                st.write(f"**国家戦略:** {info['strategy']}")
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
        "担当国家の産業を活性化し、毎ターンの獲得資金を増やしましょう。他3国もそれぞれの国家戦略に沿って経済運営を行います。"
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
        f"生産した機体は**格納庫リスト**に保管され、フェーズ3で部隊の機体と入れ替えることができます。動力コアは **{p_nat}** 固有の「**{locked_core}**」に限定されています。"
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        sel_chassis = st.selectbox("① フレーム・ボディ", list(CHASSIS_OPTIONS.keys()))
        st.caption(f"🔹 フレーム特性: {CHASSIS_OPTIONS[sel_chassis]['trait']}")
        sel_core = st.selectbox(
            "② 動力機関（コア・国家限定）", [locked_core], disabled=True
        )
    with col_p2:
        sel_armor = st.selectbox("③ 装甲・防御システム", list(ARMOR_OPTIONS.keys()))
        sel_weapon = st.selectbox("④ 主武装・アタッチメント", list(WEAPON_OPTIONS.keys()))
        st.caption(f"🔸 武器攻撃特徴: {WEAPON_OPTIONS[sel_weapon]['style']}")

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
        m2.metric("基礎攻撃力", stats["attack"])
        m3.metric("基礎防御力", stats["defense"])
        m4.metric("基礎総合戦力", stats["power"])
        st.info(
            f"**固有特性サマリー:**\n- {stats['chassis_trait']}\n- {stats['weapon_style']}"
        )
        st.code(
            f"image/chassis_{stats['chassis_id']}_core_{stats['core_id']}_armor_{stats['armor_id']}_weapon_{stats['weapon_id']}.png",
            language="text",
        )
        can_afford = st.session_state.funds[p_nat] >= stats["cost"]
        if st.button(
            "🛠️ この機体を生産して格納庫へ入れる", type="primary", disabled=not can_afford
        ):
            add_funds(p_nat, -stats["cost"])
            new_u = dict(stats)
            new_u["uid"] = f"p_t{st.session_state.turn}_{random.randint(1000,9999)}"
            new_u["name"] = unit_name
            new_u["slot"] = FORMATION_SLOTS[0]
            new_u["is_mass"] = False
            st.session_state.hangar[p_nat].append(new_u)
            st.session_state.logs.insert(
                0, f"🛠️ 【自国】魔道機甲「{unit_name}」を生産し格納庫へ入れました。"
            )
            st.rerun()

    st.markdown("---")
    st.markdown(f"#### 📦 格納庫リスト（現在 {len(st.session_state.hangar[p_nat])} 機）")
    if st.session_state.hangar[p_nat]:
        for hu in st.session_state.hangar[p_nat]:
            st.write(
                f"- **{hu['name']}**（戦力:{hu['power']} / {hu['chassis']} / {hu['weapon']}）"
            )
    else:
        st.caption("現在格納庫に機体はありません。")

    st.markdown("---")
    if st.button("➡️ フェーズ3（部隊編成・配置）へ進む", type="primary"):
        run_ai_phase2_production()
        st.session_state.phase = 3
        st.rerun()


# =========================================================
# フェーズ3：部隊編成フェーズ（開閉式・格納庫リストとの交換形態）
# =========================================================
elif st.session_state.phase == 3:
    p_nat = st.session_state.player_nation
    p_info = NATIONS[p_nat]
    st.subheader("フェーズ3：部隊編成・戦闘配置フェーズ")
    st.write(
        "初期状態では全国家・全4部隊に**6機の武装無し量産型機体**が配備されています。各部隊ウィンドウを開き、**格納庫リスト**から選択した機体と入れ替え・配置変更を行ってください。"
    )

    user_corps = st.session_state.corps[p_nat]
    hangar_list = st.session_state.hangar[p_nat]

    st.info(
        f"📦 **格納庫リストの待機機体数:** {len(hangar_list)} 機（各部隊6機・全24枠編成）"
    )

    for idx, cp in enumerate(user_corps):
        with st.expander(
            f"🛡️ {cp['id']}（配置:{len(cp['units'])}/6機 / 位置:({cp['pos'][0]+1},{cp['pos'][1]+1})）",
            expanded=(idx == 0),
        ):
            slot_map = {u.get("slot"): u for u in cp["units"]}
            f_col_rear, f_col_front = st.columns(2)
            with f_col_rear:
                st.caption("【後衛ライン】（砲撃・ステルス向き）")
                for s_name in ["後衛・上", "後衛・中", "後衛・下"]:
                    occupant = slot_map.get(s_name)
                    if occupant:
                        eff_p = calc_unit_effective_power(
                            occupant, p_info["terrain"], p_info["terrain"]
                        )
                        st.success(
                            f"**{s_name}**: 🤖 {occupant['name']} (実戦力:{eff_p} / {occupant['weapon'][:4]})"
                        )
                    else:
                        st.markdown(f"- *{s_name}*: （空き）")
            with f_col_front:
                st.caption("【前衛ライン】（近接・重装甲向き）")
                for s_name in ["前衛・上", "前衛・中", "前衛・下"]:
                    occupant = slot_map.get(s_name)
                    if occupant:
                        eff_p = calc_unit_effective_power(
                            occupant, p_info["terrain"], p_info["terrain"]
                        )
                        st.warning(
                            f"**{s_name}**: 🤖 {occupant['name']} (実戦力:{eff_p} / {occupant['weapon'][:4]})"
                        )
                    else:
                        st.markdown(f"- *{s_name}*: （空き）")

            st.markdown("---")
            st.markdown("#### 🤖 部隊機体一覧・格納庫リストとの交換")
            for u_i, u in enumerate(cp["units"]):
                u_img_path, _ = resolve_machine_image(
                    u["chassis_id"], u["core_id"], u["armor_id"], u["weapon_id"]
                )
                uc0, uc1, uc2, uc3 = st.columns([1.1, 2.6, 2.0, 2.3])
                with uc0:
                    if u_img_path:
                        st.image(u_img_path, use_container_width=True)
                    else:
                        st.caption("画像なし")
                uc1.write(
                    f"🤖 **{u['name']}**\n\n基礎戦力:{u['power']} / {u['chassis']} / {u['weapon']}"
                )
                cur_slot = u.get("slot", FORMATION_SLOTS[0])
                if cur_slot not in FORMATION_SLOTS:
                    cur_slot = FORMATION_SLOTS[0]
                new_slot = uc2.selectbox(
                    "配置ポジション",
                    FORMATION_SLOTS,
                    index=FORMATION_SLOTS.index(cur_slot),
                    key=f"slot_{idx}_{u['uid']}_{u_i}",
                )
                u["slot"] = new_slot

                with uc3:
                    if hangar_list:
                        swap_map = {
                            f"{hu['name']} (戦力:{hu['power']} / {hu['weapon'][:4]})": h_idx
                            for h_idx, hu in enumerate(hangar_list)
                        }
                        swap_label = st.selectbox(
                            "格納庫から交換する機体",
                            list(swap_map.keys()),
                            key=f"swap_sel_{idx}_{u['uid']}_{u_i}",
                        )
                        if st.button(
                            "🔄 この機体と交換",
                            key=f"swap_btn_{idx}_{u['uid']}_{u_i}",
                            use_container_width=True,
                        ):
                            h_idx = swap_map[swap_label]
                            incoming_u = hangar_list.pop(h_idx)
                            incoming_u["slot"] = u["slot"]
                            outgoing_u = cp["units"][u_i]
                            cp["units"][u_i] = incoming_u
                            hangar_list.append(outgoing_u)
                            st.session_state.logs.insert(
                                0,
                                f"🔄 【自国】{cp['id']} の「{outgoing_u['name']}」を格納庫の「{incoming_u['name']}」と交換しました。",
                            )
                            st.rerun()
                    else:
                        st.caption("格納庫に交換可能な機体がありません（フェーズ2で生産可能）。")

    st.markdown("---")
    if st.button("➡️ フェーズ4（侵攻・移動）へ進む", type="primary"):
        run_ai_phase3_formation()
        st.session_state.phase = 4
        st.session_state.battle_data = None
        st.rerun()


# =========================================================
# フェーズ4：侵攻フェーズ（開閉式部隊ウィンドウ・自領移動無制限・侵攻1回）
# =========================================================
elif st.session_state.phase == 4:
    p_nat = st.session_state.player_nation
    p_info = NATIONS[p_nat]
    st.subheader("フェーズ4：侵攻・移動フェーズ")
    st.write(
        "各部隊ウィンドウを開いて行動を指示してください。自国領地内の移動は何度でも可能、侵攻・占領は**各部隊1ターン1回まで**です。**中立地域および防衛部隊のいない敵国領地は戦闘なしで無血占領**できます。"
    )

    user_corps = st.session_state.corps[p_nat]
    if "active_corp_idx" not in st.session_state:
        st.session_state.active_corp_idx = 0

    highlight_coord = user_corps[st.session_state.active_corp_idx]["pos"]

    top_map_col, top_corps_col = st.columns([1.35, 1.15])
    with top_map_col:
        st.markdown("### 🗺️ 現在の戦略マップ（自軍・敵軍部隊位置）")
        st.markdown(
            render_map_html(highlight_pos=highlight_coord), unsafe_allow_html=True
        )
        st.caption(
            f"黄枠: 選択中部隊（{user_corps[st.session_state.active_corp_idx]['id']}）の位置 / ★隊1〜4: 自軍部隊 / 🔥⚡🌿🌙隊1〜4: 他国部隊"
        )

    with top_corps_col:
        st.markdown("### 🛡️ 各部隊の作戦ウィンドウ（開閉式）")
        for idx, cp in enumerate(user_corps):
            cur_r, cur_c = cp["pos"]
            inv_status = "侵攻済" if cp.get("invaded_this_turn") else "侵攻可"
            with st.expander(
                f"{cp['id']}｜位置:({cur_r+1},{cur_c+1})｜{len(cp['units'])}/6機｜{inv_status}",
                expanded=(idx == st.session_state.active_corp_idx),
            ):
                if st.button(
                    "📍 マップでこの部隊の位置をハイライト",
                    key=f"hl_{idx}",
                ):
                    st.session_state.active_corp_idx = idx
                    st.rerun()

                adj = get_adjacent_cells(cur_r, cur_c)
                friendly_adj = [
                    pos for pos in adj if st.session_state.owner_grid[pos[0]][pos[1]] == p_nat
                ]
                unoccupied_hostile_adj = []
                garrisoned_enemy_adj = []
                for pos in adj:
                    owner = st.session_state.owner_grid[pos[0]][pos[1]]
                    if owner == p_nat:
                        continue
                    if owner is None or len(get_garrison_corps(pos[0], pos[1], owner)) == 0:
                        unoccupied_hostile_adj.append(pos)
                    else:
                        garrisoned_enemy_adj.append(pos)

                # 自領内移動（何度でも可能）
                if friendly_adj:
                    move_target = st.selectbox(
                        "自国領地内の移動先",
                        friendly_adj,
                        format_func=lambda p: f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}]",
                        key=f"move_sel_{idx}",
                    )
                    if st.button(
                        "🧭 この自国領地へ移動",
                        key=f"move_btn_{idx}",
                        use_container_width=True,
                    ):
                        cp["pos"] = move_target
                        st.session_state.active_corp_idx = idx
                        st.session_state.logs.insert(
                            0,
                            f"🧭 【自国】{cp['id']} が ({move_target[0]+1},{move_target[1]+1}) へ移動しました。",
                        )
                        st.rerun()
                else:
                    st.caption("隣接する自国領地はありません。")

                # 侵攻・占領（各部隊ターン1回）
                if cp.get("invaded_this_turn"):
                    st.warning("🔒 今ターンの侵攻・占領は完了済みです。")
                else:
                    if unoccupied_hostile_adj and cp["units"]:
                        neu_target = st.selectbox(
                            "無血占領先（中立・無人敵領地）",
                            unoccupied_hostile_adj,
                            format_func=lambda p: (
                                f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}] - "
                                f"{(st.session_state.owner_grid[p[0]][p[1]] + '（無人領地）') if st.session_state.owner_grid[p[0]][p[1]] else '中立地域'}"
                            ),
                            key=f"neu_sel_{idx}",
                        )
                        if st.button(
                            "🏳️ 戦闘なしで占領",
                            key=f"neu_btn_{idx}",
                            use_container_width=True,
                        ):
                            nr, nc = neu_target
                            prev_owner = st.session_state.owner_grid[nr][nc]
                            t_name = st.session_state.terrain_grid[nr][nc]
                            st.session_state.owner_grid[nr][nc] = p_nat
                            cp["pos"] = (nr, nc)
                            cp["invaded_this_turn"] = True
                            st.session_state.active_corp_idx = idx
                            target_desc = (
                                f"{prev_owner}の無人領地"
                                if prev_owner
                                else "中立地域"
                            )
                            st.session_state.logs.insert(
                                0,
                                f"🏳️ 【自国】{cp['id']} が ({nr+1},{nc+1})[{t_name}] の{target_desc}を戦闘なしで占領しました！",
                            )
                            st.rerun()

                    if garrisoned_enemy_adj and cp["units"]:
                        inv_target = st.selectbox(
                            "侵攻先（敵部隊駐留領地）",
                            garrisoned_enemy_adj,
                            format_func=lambda p: (
                                f"({p[0]+1},{p[1]+1}) [{st.session_state.terrain_grid[p[0]][p[1]]}] - "
                                f"{st.session_state.owner_grid[p[0]][p[1]]}"
                            ),
                            key=f"inv_sel_{idx}",
                        )
                        if st.button(
                            "⚔️ 侵攻開始（自動戦闘）",
                            key=f"inv_btn_{idx}",
                            type="primary",
                            use_container_width=True,
                        ):
                            tr, tc = inv_target
                            defender = st.session_state.owner_grid[tr][tc]
                            def_info = NATIONS[defender]
                            terrain = st.session_state.terrain_grid[tr][tc]

                            atk_power = sum(
                                calc_unit_effective_power(u, terrain, p_info["terrain"])
                                for u in cp["units"]
                            )
                            garrison_list = get_garrison_corps(tr, tc, defender)
                            def_units = [
                                u for g_cp in garrison_list for u in g_cp["units"]
                            ]
                            def_power = sum(
                                calc_unit_effective_power(u, terrain, def_info["terrain"])
                                for u in def_units
                            )
                            won = atk_power >= def_power
                            cp["invaded_this_turn"] = True
                            st.session_state.active_corp_idx = idx

                            unit_visuals = []
                            for u in cp["units"]:
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
                                        "chassis_id": u["chassis_id"],
                                        "weapon_id": u["weapon_id"],
                                        "img_uri": image_to_data_uri(u_img_path),
                                    }
                                )

                            enemy_visuals = []
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
                                        "slot": du.get(
                                            "slot",
                                            FORMATION_SLOTS[idx_d % len(FORMATION_SLOTS)],
                                        ),
                                        "chassis_id": du["chassis_id"],
                                        "weapon_id": du["weapon_id"],
                                        "img_uri": image_to_data_uri(d_path),
                                    }
                                )

                            if won:
                                st.session_state.owner_grid[tr][tc] = p_nat
                                cp["pos"] = (tr, tc)
                                for g_cp in garrison_list:
                                    g_cp["pos"] = def_info["home"]
                                    g_cp["units"] = g_cp["units"][:1]
                                res_msg = f"🏆 【自国】{cp['id']} が ({tr+1},{tc+1})[{terrain}] で {defender} 駐留部隊を撃破し占領！"
                            else:
                                cp["pos"] = p_info["home"]
                                cp["units"] = cp["units"][:1]
                                res_msg = f"💥 【自国】{cp['id']} が ({tr+1},{tc+1}) の {defender} 防衛部隊に敗北し本拠地へ撤退しました。"

                            st.session_state.logs.insert(0, res_msg)
                            st.session_state.battle_data = {
                                "player_name": p_nat,
                                "player_color": p_info["color"],
                                "enemy_name": defender,
                                "enemy_color": def_info["color"],
                                "atk_power": atk_power,
                                "def_power": def_power,
                                "won": won,
                                "player_units": unit_visuals,
                                "enemy_units": enemy_visuals,
                                "target_label": f"({tr+1},{tc+1}) {terrain}",
                            }
                            st.rerun()

    # 大きめサイズの戦闘画面（機体・武器種ごとの固有攻撃アニメーション）
    if st.session_state.battle_data:
        b_json = json.dumps(st.session_state.battle_data)
        st.markdown("### 💥 戦闘シミュレーション（機体特性・武器別攻撃エフェクト）")
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

  function drawWeaponAttack(weaponId, startX, startY, targetX, targetY, progress, isPlayer) {{
    if (weaponId === 'cannon') {{
      ctx.save();
      ctx.strokeStyle = isPlayer ? '#00f5d4' : '#ff4d6d';
      ctx.lineWidth = 8 * (1 - progress * 0.4);
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(startX + (targetX - startX) * Math.min(progress * 1.4, 1), targetY);
      ctx.stroke();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5;
      ctx.stroke();
      ctx.restore();
    }} else if (weaponId === 'blade') {{
      const slashX = startX + (targetX - startX) * progress;
      ctx.save();
      ctx.strokeStyle = isPlayer ? '#f72585' : '#ff9e00';
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.arc(slashX, startY, 26, -Math.PI * 0.4, Math.PI * 0.4);
      ctx.stroke();
      ctx.restore();
    }} else if (weaponId === 'none') {{
      const shockX = startX + (targetX - startX) * progress;
      ctx.save();
      ctx.strokeStyle = '#a8dadc';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(shockX, startY, 14 + progress * 12, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }} else {{
      for (let k = 0; k < 3; k++) {{
        const pSub = Math.max(0, Math.min(1, progress * 1.3 - k * 0.12));
        const bx = startX + (targetX - startX) * pSub;
        const by = startY + (k - 1) * 7;
        ctx.fillStyle = isPlayer ? '#ffd166' : '#ff6b6b';
        ctx.beginPath();
        ctx.arc(bx, by, 5.5, 0, Math.PI * 2);
        ctx.fill();
      }}
    }}
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

    const moveProgress = Math.min(frame / 42, 1);

    b.player_units.forEach((u, i) => {{
      const isRear = u.slot.startsWith('後衛');
      const baseX = isRear ? 35 : 145;
      let speedMult = 1.0;
      if (u.chassis_id === 'hover') speedMult = 1.35;
      if (u.chassis_id === 'heavy') speedMult = 0.8;
      const advance = (isRear ? 75 : 145) * speedMult;

      let attackSurge = 0;
      if (frame >= 42 && frame <= 78) {{
        const phaseSin = Math.sin(((frame - 42) / 36) * Math.PI);
        attackSurge = (u.weapon_id === 'blade' || u.weapon_id === 'none') ? phaseSin * 260 : phaseSin * 30;
      }}
      const retreat = (!b.won && frame > 78) ? Math.min((frame - 78) * 5, 170) : 0;
      const x = baseX + advance * moveProgress + attackSurge - retreat;
      const y = getRowY(u.slot, i);

      const img = pImages[i];
      if (img && img.complete && img.naturalWidth > 0) {{
        ctx.drawImage(img, x, y, 84, 64);
      }} else {{
        ctx.fillStyle = b.player_color;
        ctx.fillRect(x, y, 84, 64);
      }}

      if (u.chassis_id === 'heavy') {{
        ctx.strokeStyle = 'rgba(255, 215, 0, 0.55)';
        ctx.lineWidth = 3;
        ctx.strokeRect(x - 4, y - 4, 92, 72);
      }}

      if (frame >= 42 && frame <= 85) {{
        const bp = (frame - 42) / 43;
        drawWeaponAttack(u.weapon_id, x + 84, y + 32, 680, y + 32, bp, true);
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
      const destroyed = b.won && frame > 74;

      if (!destroyed) {{
        const eImg = eImages[i];
        if (eImg && eImg.complete && eImg.naturalWidth > 0) {{
          ctx.drawImage(eImg, x, y, 84, 64);
        }} else {{
          ctx.fillStyle = b.enemy_color;
          ctx.fillRect(x, y, 84, 64);
        }}

        if (frame >= 48 && frame <= 85) {{
          const ebp = (frame - 48) / 37;
          drawWeaponAttack(eu.weapon_id || 'vulcan', x, y + 32, 240, y + 32, ebp, false);
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

    if (frame >= 55 && frame <= 88) {{
      ctx.fillStyle = b.won ? 'rgba(241, 196, 15, 0.7)' : 'rgba(231, 76, 60, 0.7)';
      ctx.beginPath();
      ctx.arc(b.won ? 700 : 260, 230, 28 + ((frame - 55) % 16), 0, Math.PI * 2);
      ctx.fill();
    }}

    if (frame < 98) {{
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
