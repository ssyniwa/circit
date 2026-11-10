import glob
import json
import os
import streamlit as st

st.set_page_config(
    page_title="エーテルサーキット：魔導機甲カスタムファクトリー",
    page_icon="🛠️",
    layout="wide",
)

# 1. パーツデータベースの拡張（4つのスロット）
CHASSIS_OPTIONS = {
    "重装甲魔導アーマー": {
        "speed": 60,
        "accel": 50,
        "handling": 80,
        "desc": "圧倒的な防御力と安定したコーナーリングを誇る重機甲。",
        "img": "heavy_armor.png",
    },
    "超高速ホバリングバイク": {
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "desc": "直線の爆発的な加速と最高速に特化した反重力ビークル。",
        "img": "hover_bike.png",
    },
    "全地形万能バギー": {
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "desc": "あらゆる路面状況に対応するバランス型フレーム。",
        "img": "all_terrain_buggy.png",
    },
    "ステルス・ウィング": {
        "speed": 90,
        "accel": 65,
        "handling": 60,
        "desc": "空力特性を極限まで高めた超軽量滑空フレーム。",
        "img": "stealth_wing.png",
    },
}

CORE_OPTIONS = {
    "古龍の魔結晶": {
        "power": 90,
        "boost": 70,
        "desc": "莫大な魔力を供給するが、熱暴走のリスクがある。",
        "img": "dragon_core.png",
    },
    "プラズマ核融合炉": {
        "power": 80,
        "boost": 90,
        "desc": "安定した高出力を発揮し、瞬間ブースト性能に優れる。",
        "img": "plasma_core.png",
    },
    "エーテルタービン": {
        "power": 70,
        "boost": 80,
        "desc": "環境エネルギーを効率よく変換するエコ＆高レスポンス炉。",
        "img": "ether_turbine.png",
    },
    "ゼロ・ポイント機関": {
        "power": 100,
        "boost": 100,
        "desc": "次元の真空から無限のエネルギーを引き出すオーパーツ機関。",
        "img": "zero_point_core.png",
    },
}

ARMOR_OPTIONS = {
    "標準耐熱コーティング": {
        "defense": 20,
        "weight": -5,
        "img": "armor_standard.png",
    },
    "魔力収束シールド発生器": {
        "defense": 45,
        "weight": -15,
        "img": "armor_shield.png",
    },
    "重チタン・ハードプレート": {
        "defense": 70,
        "weight": 20,
        "img": "armor_titanium.png",
    },
}

WEAPON_OPTIONS = {
    "エーテル・バルカン砲": {
        "attack": 60,
        "bonus_accel": 5,
        "img": "weapon_vulcan.png",
    },
    "プラズマ・キャノン": {
        "attack": 90,
        "bonus_accel": -5,
        "img": "weapon_cannon.png",
    },
    "近接ブレードポッド": {
        "attack": 75,
        "bonus_accel": 15,
        "img": "weapon_blade.png",
    },
    "武装なし（軽量化）": {
        "attack": 0,
        "bonus_accel": 25,
        "img": "weapon_none.png",
    },
}

st.title("🛠️ 魔導機甲・カスタムファクトリー ＆ サーキット")
st.markdown(
    "豊富なパーツを自由に組み合わせて自分だけの機体を構築し、imageディレクトリ内のビジュアルを確認しながらサーキット出走テストを行おう！"
)

# 2. カスタマイズUI（4カラム）
st.subheader("🔧 マシンパーツ・アッセンブル")

col1, col2 = st.columns(2)
with col1:
    selected_chassis = st.selectbox(
        "① フレーム・ボディ", list(CHASSIS_OPTIONS.keys())
    )
    selected_core = st.selectbox("② 動力機関（コア）", list(CORE_OPTIONS.keys()))
with col2:
    selected_armor = st.selectbox("③ 装甲・防御システム", list(ARMOR_OPTIONS.keys()))
    selected_weapon = st.selectbox("④ 主武装・アタッチメント", list(WEAPON_OPTIONS.keys()))

chassis_data = CHASSIS_OPTIONS[selected_chassis]
core_data = CORE_OPTIONS[selected_core]
armor_data = ARMOR_OPTIONS[selected_armor]
weapon_data = WEAPON_OPTIONS[selected_weapon]

# 3. スペック合算計算
total_speed = (
    chassis_data["speed"]
    + core_data["power"] // 2
    - max(0, armor_data["weight"])
)
total_accel = (
    chassis_data["accel"]
    + core_data["boost"] // 2
    + weapon_data["bonus_accel"]
)
total_handling = chassis_data["handling"]
total_defense = armor_data["defense"]
total_attack = weapon_data["attack"]

st.markdown("---")

# 4. ビジュアル表示セクション（imageディレクトリ連携）
st.subheader("🖼️ マシン・ビジュアル確認")

# imageディレクトリ内の画像ファイルを検索するヘルパー関数
def find_image_path(preferred_filename):
    target_path = os.path.join("image", preferred_filename)
    if os.path.exists(target_path):
        return target_path
    
    # 見つからない場合のフォールバック（imageディレクトリ内の適当な画像を探す）
    image_files = glob.glob("image/*.png") + glob.glob("image/*.jpg")
    if image_files:
        return image_files[0]
    return None

# ボディまたはパーツに紐づく画像パスを取得
image_file_name = chassis_data["img"]
resolved_image_path = find_image_path(image_file_name)

vcol1, vcol2 = st.columns([1, 2])
with vcol1:
    if resolved_image_path and os.path.exists(resolved_image_path):
        st.image(
            resolved_image_path,
            caption=f"機体コンセプト: {selected_chassis}",
            use_container_width=True,
        )
    else:
        st.warning(
            f"⚠️ 'image/{image_file_name}' が見つかりませんでした。\n\n`image` ディレクトリに該当画像ファイルを配置してください。"
        )

with vcol2:
    st.markdown("### 📊 総合スペック評価")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("最高速度 (SPEED)", f"{total_speed} km/h")
    sc2.metric("加速力 (ACCEL)", f"{total_accel} pts")
    sc3.metric("操舵性 (HANDLING)", f"{total_handling} pts")

    sc4, sc5 = st.columns(2)
    sc4.metric("防御力 (DEFENSE)", f"{total_defense} pts")
    sc5.metric("攻撃力 (ATTACK)", f"{total_attack} pts")

    st.info(
        f"**構成サマリー**: {selected_chassis} ＋ {selected_core} ＋ {selected_armor} ＋ {selected_weapon}"
    )

machine_config = {
    "name": f"{selected_chassis}",
    "speed": total_speed,
    "accel": total_accel,
    "handling": total_handling,
}
config_json = json.dumps(machine_config)

st.markdown("---")

# 5. サーキット走行シミュレーション
st.subheader("🏁 リアルタイム・サーキットシミュレーション")

simulation_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    background-color: #0e1117;
    color: #ffffff;
    font-family: sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  canvas {{
    background: #1a1c23;
    border: 2px solid #30363d;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  }}
  .controls {{
    margin-top: 15px;
    display: flex;
    gap: 10px;
  }}
  button {{
    background-color: #238636;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
  }}
  button:hover {{ background-color: #2ea043; }}
  button.brake {{ background-color: #da3633; }}
  button.brake:hover {{ background-color: #f85149; }}
  .hud {{
    display: flex;
    gap: 20px;
    margin-bottom: 10px;
    font-size: 14px;
    font-family: monospace;
  }}
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

  let isRunning = false;
  let startTime = 0;
  let elapsedTime = 0;
  let currentSpeed = 0;
  let distance = 0;
  let throttle = false;

  const trackCenterX = 350;
  const trackCenterY = 200;
  const trackRadiusX = 250;
  const trackRadiusY = 130;

  function startRace() {{
    isRunning = true;
    startTime = performance.now();
    distance = 0;
    currentSpeed = 0;
  }}

  function accelerate(val) {{
    throttle = val;
  }}

  function update() {{
    if (isRunning) {{
      const maxSpd = config.speed;
      const accelRate = config.accel * 0.05;

      if (throttle) {{
        currentSpeed += accelRate;
        if (currentSpeed > maxSpd) currentSpeed = maxSpd;
      }} else {{
        currentSpeed -= 1.5;
        if (currentSpeed < 0) currentSpeed = 0;
      }}

      distance += currentSpeed * 0.002;
      elapsedTime = ((performance.now() - startTime) / 1000).toFixed(2);
      document.getElementById('m-time').innerText = elapsedTime + 's';
      document.getElementById('m-spd').innerText = Math.floor(currentSpeed);
    }}
  }}

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX, trackRadiusY, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 60;
    ctx.stroke();

    ctx.beginPath();
    ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX - 30, trackRadiusY - 30, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#21262d';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX + 30, trackRadiusY + 30, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#21262d';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.strokeStyle = '#f0f6fc';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(trackCenterX, trackCenterY - trackRadiusY - 30);
    ctx.lineTo(trackCenterX, trackCenterY - trackRadiusY + 30);
    ctx.stroke();

    const angle = (distance * 0.5) % (Math.PI * 2);
    const carX = trackCenterX + Math.cos(angle - Math.PI / 2) * trackRadiusX;
    const carY = trackCenterY + Math.sin(angle - Math.PI / 2) * trackRadiusY;

    ctx.save();
    ctx.translate(carX, carY);
    ctx.rotate(angle);

    ctx.fillStyle = '#58a6ff';
    ctx.fillRect(-12, -6, 24, 12);
    ctx.fillStyle = '#7ee787';
    ctx.fillRect(-4, -4, 8, 8);
    
    if (throttle && isRunning) {{
      ctx.fillStyle = '#f85149';
      ctx.beginPath();
      ctx.moveTo(-12, -4);
      ctx.lineTo(-22, 0);
      ctx.lineTo(-12, 4);
      ctx.fill();
    }}
    ctx.restore();
  }}

  function loop() {{
    update();
    draw();
    requestAnimationFrame(loop);
  }}

  loop();
</script>

</body>
</html>
"""

st.components.v1.html(simulation_html, height=480)

<FollowUp label="パーツの組み合わせに応じたカスタム画像をGeminiの画像生成APIやファイル名規則で動的に切り替える仕組みを追加したいですか？" query="パーツの組み合わせ名（例：フレーム＋コア＋武装）の文字列からファイル名を動的に生成し、imageディレクトリ内の対応画像を完璧に一致させて表示する仕組みを教えて。" />
