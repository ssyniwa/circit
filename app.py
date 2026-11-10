import glob
import json
import os
import streamlit as st

st.set_page_config(
    page_title="エーテルサーキット：魔導機甲カスタムファクトリー",
    page_icon="🛠️",
    layout="wide",
)

# 1. パーツデータベース（表示名、内部ID、スペック定義）
CHASSIS_OPTIONS = {
    "重装甲魔導アーマー": {
        "id": "heavy",
        "speed": 60,
        "accel": 50,
        "handling": 80,
        "desc": "圧倒的な防御力と安定したコーナーリングを誇る重機甲。",
    },
    "超高速ホバリングバイク": {
        "id": "hover",
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "desc": "直線の爆発的な加速と最高速に特化した反重力ビークル。",
    },
    "全地形万能バギー": {
        "id": "buggy",
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "desc": "あらゆる路面状況に対応するバランス型フレーム。",
    },
    "ステルス・ウィング": {
        "id": "wing",
        "speed": 90,
        "accel": 65,
        "handling": 60,
        "desc": "空力特性を極限まで高めた超軽量滑空フレーム。",
    },
}

CORE_OPTIONS = {
    "古龍の魔結晶": {
        "id": "dragon",
        "power": 90,
        "boost": 70,
        "desc": "莫大な魔力を供給するが、熱暴走のリスクがある。",
    },
    "プラズマ核融合炉": {
        "id": "plasma",
        "power": 80,
        "boost": 90,
        "desc": "安定した高出力を発揮し、瞬間ブースト性能に優れる。",
    },
    "エーテルタービン": {
        "id": "ether",
        "power": 70,
        "boost": 80,
        "desc": "環境エネルギーを効率よく変換するエコ＆高レスポンス炉。",
    },
    "ゼロ・ポイント機関": {
        "id": "zero",
        "power": 100,
        "boost": 100,
        "desc": "次元の真空から無限のエネルギーを引き出すオーパーツ機関。",
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

st.title("🛠️ 魔導機甲・カスタムファクトリー ＆ サーキット")
st.markdown("4つのパーツを組み合わせて専用のビジュアル画像を動的に読み込みます。")

# 2. UI・選択ボックス
st.subheader("🔧 マシンパーツ・アッセンブル")

col1, col2 = st.columns(2)
with col1:
    selected_chassis = st.selectbox("① フレーム・ボディ", list(CHASSIS_OPTIONS.keys()))
    selected_core = st.selectbox("② 動力機関（コア）", list(CORE_OPTIONS.keys()))
with col2:
    selected_armor = st.selectbox("③ 装甲・防御システム", list(ARMOR_OPTIONS.keys()))
    selected_weapon = st.selectbox("④ 主武装・アタッチメント", list(WEAPON_OPTIONS.keys()))

c_data = CHASSIS_OPTIONS[selected_chassis]
co_data = CORE_OPTIONS[selected_core]
a_data = ARMOR_OPTIONS[selected_armor]
w_data = WEAPON_OPTIONS[selected_weapon]

# 3. スペック計算
total_speed = c_data["speed"] + co_data["power"] // 2 - max(0, a_data["weight"])
total_accel = c_data["accel"] + co_data["boost"] // 2 + w_data["bonus_accel"]
total_handling = c_data["handling"]

st.markdown("---")

# 4. 動的画像検索・表示システム
st.subheader("🖼️ マシン・ビジュアル確認")

def resolve_machine_image(chassis_id, core_id, armor_id, weapon_id):
    """
    1. 完全一致ファイル名 (chassis_X_core_Y_armor_Z_weapon_W.png)
    2. ボディ単体ファイル名 (chassis_X.png)
    3. imageディレクトリ内の任意の画像
    の優先順位で検索してパスを返す
    """
    exts = [".png", ".jpg", ".webp"]
    
    # パターン1: 完全一致
    full_combo_name = f"chassis_{chassis_id}_core_{core_id}_armor_{armor_id}_weapon_{weapon_id}"
    for ext in exts:
        path = os.path.join("image", full_combo_name + ext)
        if os.path.exists(path):
            return path, "完全一致（パーツ組み合わせ専用画像）"
            
    # パターン2: ボディ単体フォールバック
    chassis_only_name = f"chassis_{chassis_id}"
    for ext in exts:
        path = os.path.join("image", chassis_only_name + ext)
        if os.path.exists(path):
            return path, f"フォールバック表示（{selected_chassis} 標準画像）"

    # パターン3: 任意画像フォールバック
    any_images = glob.glob("image/*.png") + glob.glob("image/*.jpg") + glob.glob("image/*.webp")
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
            caption=f"{selected_chassis} [{status_label}]",
            use_container_width=True,
        )
    else:
        st.error("⚠️ `image` ディレクトリに画像ファイルがありません。")

with vcol2:
    st.markdown("### 📊 総合スペック評価")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("最高速度 (SPEED)", f"{total_speed} km/h")
    sc2.metric("加速力 (ACCEL)", f"{total_accel} pts")
    sc3.metric("操舵性 (HANDLING)", f"{total_handling} pts")

    st.code(
        f"期待される画像ファイル名:\nimage/chassis_{c_data['id']}_core_{co_data['id']}_armor_{a_data['id']}_weapon_{w_data['id']}.png",
        language="text",
    )

machine_config = {
    "name": selected_chassis,
    "speed": total_speed,
    "accel": total_accel,
    "handling": total_handling,
}
config_json = json.dumps(machine_config)

st.markdown("---")

# 5. サーキット走行シミュレーション（HTML5 Canvas）
st.subheader("🏁 リアルタイム・サーキットシミュレーション")

simulation_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ background-color: #0e1117; color: #ffffff; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; }}
  canvas {{ background: #1a1c23; border: 2px solid #30363d; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
  .controls {{ margin-top: 15px; display: flex; gap: 10px; }}
  button {{ background-color: #238636; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
  button:hover {{ background-color: #2ea043; }}
  button.brake {{ background-color: #da3633; }}
  button.brake:hover {{ background-color: #f85149; }}
  .hud {{ display: flex; gap: 20px; margin-bottom: 10px; font-size: 14px; font-family: monospace; }}
</style>
</head>
<body>
<div class="hud">
  <div>MACHINE: <span id="m-name" style="color: #58a6ff;">-</span></div>
  <div>LAP TIME: <span id="m-time" style="color: #3fb950;">0.00s</span></div>
  <div>CURRENT SPEED: <span id="m-spd" style="color: #d29922;">0</span> km/h</div>
</div>
<canvas id="simCanvas" width="700" height="400"></canvas>
<div class="controls">
  <button id="btnStart" onclick="startRace()">レーススタート / リセット</button>
  <button onclick="accelerate(true)">▶ アクセル</button>
  <button class="brake" onclick="accelerate(false)">■ ブレーキ</button>
</div>
<script>
  const config = {config_json};
  document.getElementById('m-name').innerText = config.name;
  const canvas = document.getElementById('simCanvas');
  const ctx = canvas.getContext('2d');
  let isRunning = false, startTime = 0, elapsedTime = 0, currentSpeed = 0, distance = 0, throttle = false;
  const trackCenterX = 350, trackCenterY = 200, trackRadiusX = 250, trackRadiusY = 130;

  function startRace() {{ isRunning = true; startTime = performance.now(); distance = 0; currentSpeed = 0; }}
  function accelerate(val) {{ throttle = val; }}
  function update() {{
    if (isRunning) {{
      const maxSpd = config.speed, accelRate = config.accel * 0.05;
      if (throttle) {{ currentSpeed += accelRate; if (currentSpeed > maxSpd) currentSpeed = maxSpd; }}
      else {{ currentSpeed -= 1.5; if (currentSpeed < 0) currentSpeed = 0; }}
      distance += currentSpeed * 0.002;
      elapsedTime = ((performance.now() - startTime) / 1000).toFixed(2);
      document.getElementById('m-time').innerText = elapsedTime + 's';
      document.getElementById('m-spd').innerText = Math.floor(currentSpeed);
    }}
  }}
  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath(); ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX, trackRadiusY, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#30363d'; ctx.lineWidth = 60; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX - 30, trackRadiusY - 30, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#21262d'; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX + 30, trackRadiusY + 30, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#21262d'; ctx.lineWidth = 2; ctx.stroke();
    ctx.strokeStyle = '#f0f6fc'; ctx.lineWidth = 4; ctx.beginPath();
    ctx.moveTo(trackCenterX, trackCenterY - trackRadiusY - 30); ctx.lineTo(trackCenterX, trackCenterY - trackRadiusY + 30); ctx.stroke();
    const angle = (distance * 0.5) % (Math.PI * 2);
    const carX = trackCenterX + Math.cos(angle - Math.PI / 2) * trackRadiusX;
    const carY = trackCenterY + Math.sin(angle - Math.PI / 2) * trackRadiusY;
    ctx.save(); ctx.translate(carX, carY); ctx.rotate(angle);
    ctx.fillStyle = '#58a6ff'; ctx.fillRect(-12, -6, 24, 12);
    ctx.fillStyle = '#7ee787'; ctx.fillRect(-4, -4, 8, 8);
    if (throttle && isRunning) {{
      ctx.fillStyle = '#f85149'; ctx.beginPath(); ctx.moveTo(-12, -4); ctx.lineTo(-22, 0); ctx.lineTo(-12, 4); ctx.fill();
    }}
    ctx.restore();
  }}
  function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
  loop();
</script>
</body>
</html>
"""

st.components.v1.html(simulation_html, height=480)
