import json
import streamlit as st

st.set_page_config(
    page_title="エーテルサーキット：魔導機甲グランプリ",
    page_icon="🏎️",
    layout="wide",
)

# カスタカスタムパーツのデータベース
CHASSIS_OPTIONS = {
    "重装甲魔導アーマー": {
        "name": "重装甲魔導アーマー",
        "speed": 60,
        "accel": 50,
        "handling": 80,
        "desc": "圧倒的な防御力と安定したコーナーリングを誇る重機甲。",
    },
    "超高速ホバリングバイク": {
        "name": "超高速ホバリングバイク",
        "speed": 95,
        "accel": 85,
        "handling": 40,
        "desc": "直線の爆発的な加速と最高速に特化した反重力ビークル。",
    },
    "全地形万能バギー": {
        "name": "全地形万能バギー",
        "speed": 75,
        "accel": 70,
        "handling": 75,
        "desc": "あらゆる路面状況に対応するバランス型フレーム。",
    },
}

CORE_OPTIONS = {
    "古龍の魔結晶": {
        "name": "古龍の魔結晶",
        "power": 90,
        "boost": 70,
        "desc": "莫大な魔力を供給するが、熱暴走のリスクがある。",
    },
    "プラズマ核融合炉": {
        "name": "プラズマ核融合炉",
        "power": 80,
        "boost": 90,
        "desc": "安定した高出力を発揮し、瞬間ブースト性能に優れる。",
    },
    "エーテルタービン": {
        "name": "エーテルタービン",
        "power": 70,
        "boost": 80,
        "desc": "環境エネルギーを効率よく変換するエコ＆高レスポンス炉。",
    },
}

BOOSTER_OPTIONS = {
    "イオン噴射スラスター": {
        "name": "イオン噴射スラスター",
        "bonus_speed": 15,
        "bonus_accel": 20,
    },
    "次元跳躍アクセラレーター": {
        "name": "次元跳躍アクセラレーター",
        "bonus_speed": 25,
        "bonus_accel": 10,
    },
    "安定スタビライザー": {
        "name": "安定スタビライザー",
        "bonus_speed": 5,
        "bonus_accel": 15,
    },
}

st.title("🏎️ エーテルサーキット：魔導機甲グランプリ")
st.markdown(
    "異世界の素材やSFテクノロジーを組み合わせてオリジナルの機体をビルドし、ネオン輝くサーキットでの走行シミュレーションに挑もう！"
)

# 1. カスタマイズセクション
st.subheader("🛠️ マシンカスタマイズ工房")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ① フレーム・ボディ")
    selected_chassis_key = st.selectbox(
        "ボディ選択", list(CHASSIS_OPTIONS.keys()), label_visibility="collapsed"
    )
    chassis = CHASSIS_OPTIONS[selected_chassis_key]
    st.info(f"**{chassis['name']}**\n\n{chassis['desc']}")

with col2:
    st.markdown("### ② 動力機関（コア）")
    selected_core_key = st.selectbox(
        "コア選択", list(CORE_OPTIONS.keys()), label_visibility="collapsed"
    )
    core = CORE_OPTIONS[selected_core_key]
    st.success(f"**{core['name']}**\n\n{core['desc']}")

with col3:
    st.markdown("### ③ 補助ブースター")
    selected_booster_key = st.selectbox(
        "ブースター選択", list(BOOSTER_OPTIONS.keys()), label_visibility="collapsed"
    )
    booster = BOOSTER_OPTIONS[selected_booster_key]
    st.warning(f"**{booster['name']}**")

# パラメータ合算計算
total_speed = chassis["speed"] + core["power"] + booster["bonus_speed"]
total_accel = chassis["accel"] + core["boost"] + booster["bonus_accel"]
total_handling = chassis["handling"]

st.markdown("---")

# 2. ステータス表示
st.subheader("📊 マシン性能スペックス")
sc1, sc2, sc3 = st.columns(3)
sc1.metric("最高速度 (MAX SPEED)", f"{total_speed} km/h")
sc2.metric("加速レスポンス (ACCEL)", f"{total_accel} pts")
sc3.metric("操舵安定性 (HANDLING)", f"{total_handling} pts")

# JavaScriptに渡すデータをJSON形式で準備
machine_config = {
    "name": f"{selected_chassis_key} + {selected_core_key}",
    "speed": total_speed,
    "accel": total_accel,
    "handling": total_handling,
}

config_json = json.dumps(machine_config)

st.markdown("---")

# 3. サーキット走行シミュレーション（HTML5 Canvas + JavaScript埋め込み）
st.subheader("🏁 リアルタイム・サーキットシミュレーション")
st.markdown(
    "「レーススタート」を押すと、あなたのマシンがコースに出走します。アクセルやブーストボタンでコントロールを体験しよう！"
)

# HTML/JS コンポーネントの構築
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

  // サーキットの形状定義（オーバルコースの中心座標と半径）
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
        currentSpeed -= 1.5; // 自然減速
        if (currentSpeed < 0) currentSpeed = 0;
      }}

      // 距離と時間の更新
      distance += currentSpeed * 0.002;
      elapsedTime = ((performance.now() - startTime) / 1000).toFixed(2);
      document.getElementById('m-time').innerText = elapsedTime + 's';
      document.getElementById('m-spd').innerText = Math.floor(currentSpeed);
    }}
  }}

  function draw() {{
    // 背景クリア
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. サーキットコースの描画
    ctx.beginPath();
    ctx.ellipse(trackCenterX, trackCenterY, trackRadiusX, trackRadiusY, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 60;
    ctx.stroke();

    // コース内側の白線
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

    // スタート・ゴールライン
    ctx.strokeStyle = '#f0f6fc';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(trackCenterX, trackCenterY - trackRadiusY - 30);
    ctx.lineTo(trackCenterX, trackCenterY - trackRadiusY + 30);
    ctx.stroke();

    // 2. マシンの位置計算（楕円軌道上を移動）
    const angle = (distance * 0.5) % (Math.PI * 2);
    const carX = trackCenterX + Math.cos(angle - Math.PI / 2) * trackRadiusX;
    const carY = trackCenterY + Math.sin(angle - Math.PI / 2) * trackRadiusY;

    // マシン本体の描画
    ctx.save();
    ctx.translate(carX, carY);
    ctx.rotate(angle); // 進行方向に向ける

    // マシンのボディ
    ctx.fillStyle = '#58a6ff';
    ctx.fillRect(-12, -6, 24, 12);
    // コックピット
    ctx.fillStyle = '#7ee787';
    ctx.fillRect(-4, -4, 8, 8);
    // スラスター炎 (アクセル中)
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

# Streamlit上にHTML/JSコンポーネントを描画
st.components.v1.html(simulation_html, height=480)

<FollowUp label="このアプリに「画像生成AI連携機能」を追加して、作成した機体のビジュアルをAIに描かせるコードを組み込みたいですか？" query="魔導機甲のカスタム設定からプロンプトを自動生成し、画像生成AIでビジュアルを出力する機能を追加する方法を教えて。" />
