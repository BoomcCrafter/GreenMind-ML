
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
PORT = 8765

COLUMNS = (
    "czas_min", "temp_zadana", "temp_gora", "temp_dol",
    "temp_srednia", "pwm_nadany", "wentylator"
)


def read_results(name):
    path = ROOT / name

    if not path.exists():
        path = ROOT / "wyniki_testow" / name

    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku {name}")

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(COLUMNS) - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"{name}: brakuje kolumn {', '.join(sorted(missing))}"
            )

        data = []

        for line in reader:
            record = {}

            for key, value in line.items():
                if key is None:
                    continue

                try:
                    record[key] = (
                        float(value.replace(",", ".")) if value else None
                    )
                except ValueError:
                    record[key] = None

            if any(record.get(key) is None for key in COLUMNS):
                continue

            record["blad"] = (
                record["temp_zadana"] - record["temp_srednia"]
            )
            data.append(record)

    if not data:
        raise ValueError(f"{name}: brak poprawnych pomiarów")

    start = data[0]["czas_min"]

    for record in data:
        record["t"] = round(record["czas_min"] - start, 6)

    return data


HTML = r'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GreenMind ML</title>
<style>
:root{
  --bg:#07111b;
  --card:#111f2d;
  --line:#284052;
  --text:#edf5f9;
  --muted:#9aafbd;
  --green:#56dfaa;
  --orange:#ffb977;
  --blue:#81baff;
}
*{box-sizing:border-box}
body{
  margin:0;
  background:radial-gradient(ellipse at 15% 0%,#183746,transparent 45%),var(--bg);
  font:15px system-ui,Arial;
  color:var(--text);
}
main{max-width:1350px;margin:auto;padding:24px}
header,.heading,.flex{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:15px;
  flex-wrap:wrap;
}
header{border-bottom:1px solid var(--line);padding-bottom:23px}
h1{font-size:23px;letter-spacing:.2px;margin:0}
h2{font-size:21px;margin:0 0 7px}
h3{font-size:16px;margin:0 0 14px}
p,small,.muted{color:var(--muted)}
small{font-size:12px}
.heading{margin:26px 0 18px}
.tag{
  background:#17372e;
  color:#91f7c8;
  border-radius:40px;
  padding:8px 12px;
  font-size:12px;
  font-weight:650;
}
.modes{display:flex;gap:8px;flex-wrap:wrap}
button,select{
  background:#1b3040;
  color:var(--text);
  border:1px solid #385166;
  border-radius:10px;
  padding:10px 14px;
  font:inherit;
  cursor:pointer;
}
button.active,button.primary{
  background:#17624d;
  border-color:#369d76;
  color:#d9fff0;
}
button:hover{filter:brightness(1.15)}
button:focus-visible,select:focus-visible,input:focus-visible{
  outline:2px solid var(--blue);
}
.grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:12px;
}
.card{
  background:linear-gradient(145deg,#132332,#0e1b28);
  border:1px solid var(--line);
  border-radius:17px;
  padding:18px;
  min-width:0;
}
.metric small{display:block}
.metric strong{
  display:block;
  font-size:27px;
  margin:7px 0;
  font-variant-numeric:tabular-nums;
}
.layout{
  display:grid;
  grid-template-columns:minmax(0,1fr) 260px;
  gap:12px;
  margin-top:12px;
}
.chart{
  display:block;
  width:100%;
  height:305px;
  margin-top:15px;
}
.legend{
  display:flex;
  gap:17px;
  flex-wrap:wrap;
  margin-top:12px;
  color:#c2d2dd;
  font-size:12px;
}
.legend b{
  display:inline-block;
  width:10px;
  height:10px;
  margin-right:6px;
  border-radius:100%;
}
.sidebox{
  background:#14303b;
  border:1px solid #3b5b64;
  border-radius:14px;
  text-align:center;
  padding:18px;
  margin-bottom:13px;
}
.icon{font-size:35px}
.big{font-size:25px;font-weight:750}
.sidegrid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:9px;
}
.sidegrid>div{
  padding:10px;
  background:#192d3c;
  border-radius:11px;
}
.sidegrid strong{display:block;font-size:18px;margin-top:5px}
.controls{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  margin-top:12px;
  padding:14px;
  background:#122633;
  border:1px solid var(--line);
  border-radius:14px;
}
.controls input[type=range]{
  flex:1;
  min-width:160px;
  accent-color:var(--green);
}
.choices{
  display:flex;
  gap:9px;
  flex-wrap:wrap;
  margin:12px 0 0;
}
.choices label{
  border:1px solid var(--line);
  border-radius:9px;
  background:#1c2d3b;
  padding:9px;
  font-size:12px;
}
.choices input{accent-color:var(--green)}
.extras{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:12px;
  margin-top:12px;
}
.extras canvas{height:205px}
.stats{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:10px;
  margin-top:13px;
}
.stat{
  background:#182c3c;
  border-radius:11px;
  padding:13px;
}
.stat .values{
  display:flex;
  gap:22px;
  margin-top:9px;
  flex-wrap:wrap;
}
.stat strong{
  display:block;
  font-size:20px;
  margin-top:3px;
}
.alert{
  background:#58252b;
  color:#ffe7e7;
  padding:14px;
  border-radius:10px;
  margin:13px 0;
  display:none;
}
footer{
  font-size:12px;
  color:var(--muted);
  margin-top:17px;
  line-height:1.7;
}
@media(max-width:950px){
  .grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .layout{grid-template-columns:1fr}
  .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:600px){
  main{padding:13px}
  .extras,.stats{grid-template-columns:1fr}
  .metric strong{font-size:21px}
  .card{padding:13px}
  .tag{font-size:10px}
}
</style>
</head>
<body>
<main>
<header>
  <div>
    <h1>🌱 GreenMind <span style="color:var(--green)">ML</span></h1>
    <small>Automatyka · Raspberry Pi · Machine Learning</small>
  </div>
  <span class="tag">● ODTWARZANIE POMIARÓW</span>
</header>

<div class="heading">
  <div>
    <h2>Porównanie sterowania szklarnią</h2>
    <small>Wyniki dwóch eksperymentów</small>
  </div>
  <div class="modes">
    <button data-mode="pid">PID</button>
    <button data-mode="ml">PI + ML</button>
    <button data-mode="both" class="active">Porównaj oba</button>
  </div>
</div>

<div class="alert" id="alert"></div>

<section class="grid">
  <div class="card metric">
    <small>Temperatura zadana</small>
    <strong id="set">—</strong>
    <small>Wartość zadana w próbie</small>
  </div>
  <div class="card metric">
    <small>PID · temperatura średnia</small>
    <strong id="pidTemp" style="color:var(--orange)">—</strong>
    <small>Pomiar odtwarzany</small>
  </div>
  <div class="card metric">
    <small>PI + ML · temperatura średnia</small>
    <strong id="mlTemp" style="color:var(--green)">—</strong>
    <small>Pomiar odtwarzany</small>
  </div>
  <div class="card metric">
    <small>Czas eksperymentu</small>
    <strong id="currentTime">00:00</strong>
    <small id="length">Wczytywanie danych...</small>
  </div>
</section>

<div class="layout">
  <div class="card">
    <div class="flex">
      <h3>Temperatura w czasie</h3>
      <select id="tempField">
        <option value="temp_srednia">Średnia temperatura</option>
        <option value="temp_gora">Czujnik górny</option>
        <option value="temp_dol">Czujnik dolny</option>
      </select>
    </div>
    <div class="legend">
      <span><b style="background:#dae8f4"></b>Zadana</span>
      <span><b style="background:var(--orange)"></b>PID</span>
      <span><b style="background:var(--green)"></b>PI + ML</span>
    </div>
    <canvas id="mainPlot" class="chart"></canvas>
    <small>Przyspieszone odtwarzanie zapisanych pomiarów.</small>
  </div>

  <div class="card">
    <h3>Stan komory</h3>
    <div class="sidebox">
      <div class="icon">🌡️ 💡</div>
      <div class="big" id="chamberTemp">—</div>
      <small id="chamberMode">Wyświetlane dane PID</small>
    </div>
    <div class="sidegrid">
      <div><small>Moc grzałki</small><strong id="pwm">—</strong></div>
      <div><small>Wentylator</small><strong id="fan">—</strong></div>
      <div><small>Góra komory</small><strong id="top">—</strong></div>
      <div><small>Dół komory</small><strong id="bottom">—</strong></div>
    </div>
  </div>
</div>

<div class="controls">
  <button class="primary" id="play">▶ Start</button>
  <button id="reset">↺ Od początku</button>
  <small>Czas</small>
  <input id="timeline" type="range" min="0" max="1000" value="0">
  <b id="clock">00:00</b>
  <small>Prędkość</small>
  <select id="speed">
    <option value="15">×15</option>
    <option value="30">×30</option>
    <option value="60" selected>×60</option>
    <option value="120">×120</option>
    <option value="240">×240</option>
  </select>
  <small id="status">Gotowy</small>
</div>

<div class="card" style="margin-top:12px">
  <div class="flex">
    <h3>Dodatkowe wykresy</h3>
    <button id="showAll">Pokaż wszystkie</button>
  </div>
  <div class="choices" id="choices">
    <label><input type="checkbox" value="pwm" checked> Moc PWM</label>
    <label><input type="checkbox" value="error" checked> Uchyb temperatury</label>
    <label><input type="checkbox" value="sensors"> Góra i dół</label>
    <label><input type="checkbox" value="fan"> Wentylator</label>
    <label><input type="checkbox" value="prediction"> Prognoza modelu ML</label>
    <label><input type="checkbox" value="parts"> Człony P / I / D</label>
  </div>
</div>

<div class="extras" id="extras"></div>

<div class="card" style="margin-top:12px">
  <h3>Podsumowanie całych eksperymentów</h3>
  <small>Wyniki liczone ze wszystkich zapisanych pomiarów.</small>
  <div class="stats" id="stats"></div>
</div>

<footer>
To panel odtwarzania danych CSV, a nie sterowanie Arduino na żywo.
Model .joblib nie jest tu uruchamiany. Próby miały nieco inne
temperatury początkowe, więc nie należy traktować porównania jako
dowodu przewagi jednego regulatora w każdych warunkach.
</footer>
</main>

<script>
const $ = id => document.getElementById(id);

const color = {
  pid: '#ffb977',
  ml: '#56dfaa',
  set: '#dae8f4',
  top: '#81baff',
  bottom: '#c8a8fa'
};

let data = null;
let mode = 'both';
let time = 0;
let duration = 15;
let playing = false;
let speed = 60;
let previous = null;
let drawAt = 0;
let extras = [];

const fmt = (value, digits=1) =>
  value == null ? '—' : Number(value).toFixed(digits);

const c = value => fmt(value) + '°C';

const clock = t => {
  let s = Math.round(t * 60);
  return String(Math.floor(s / 60)).padStart(2, '0')
    + ':' + String(s % 60).padStart(2, '0');
};

function selected(key) {
  return data[key].reduce(
    (last, row) => row.t <= time ? row : last,
    data[key][0]
  );
}

function series(field) {
  let out = [];

  if (mode !== 'ml') {
    out.push({
      rows: data.pid,
      field,
      color: color.pid,
      label: 'PID'
    });
  }

  if (mode !== 'pid') {
    out.push({
      rows: data.ml,
      field,
      color: color.ml,
      label: 'PI + ML'
    });
  }

  return out;
}

function draw(canvas, lines, unit='', fixed=null) {
  if (!canvas || !lines.length) return;

  const w = Math.max(canvas.clientWidth, 250);
  const h = canvas.clientHeight || 240;
  const dpr = devicePixelRatio || 1;

  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(h * dpr);

  let ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  let left = 51, right = 13, top = 15, bottom = 34;
  let plotW = w - left - right;
  let plotH = h - top - bottom;

  let values = lines
    .flatMap(l => l.rows.map(r => r[l.field]))
    .filter(v => Number.isFinite(v));

  let low = fixed ? fixed[0] : Math.min(...values);
  let high = fixed ? fixed[1] : Math.max(...values);

  if (!Number.isFinite(low) || !Number.isFinite(high)) {
    low = 0;
    high = 1;
  }

  if (high <= low) high = low + 1;

  let pad = (high - low) * 0.10;
  low -= pad;
  high += pad;

  const x = t => left + (t / duration) * plotW;
  const y = v => top + (high - v) / (high - low) * plotH;

  ctx.lineWidth = 1;
  ctx.font = '11px system-ui';
  ctx.fillStyle = '#98adbb';
  ctx.strokeStyle = '#2d4353';

  for (let i = 0; i <= 4; i++) {
    let val = low + (high - low) * i / 4;
    let Y = y(val);

    ctx.beginPath();
    ctx.moveTo(left, Y);
    ctx.lineTo(w - right, Y);
    ctx.stroke();

    ctx.textAlign = 'right';
    ctx.fillText(
      fmt(val, unit === '°C' ? 1 : 0) + unit,
      left - 7, Y + 4
    );
  }

  for (let i = 0; i <= 5; i++) {
    let X = left + plotW * i / 5;

    ctx.beginPath();
    ctx.moveTo(X, top);
    ctx.lineTo(X, h - bottom);
    ctx.stroke();

    ctx.textAlign = 'center';
    ctx.fillText(
      fmt(duration * i / 5, 0) + 'm',
      X, h - 10
    );
  }

  ctx.save();
  ctx.beginPath();
  ctx.rect(left, top, plotW, plotH);
  ctx.clip();

  lines.forEach(line => {
    ctx.beginPath();
    ctx.strokeStyle = line.color;
    ctx.lineWidth = line.dash ? 2 : 2.5;
    ctx.setLineDash(line.dash ? [7, 6] : []);

    let first = true;

    line.rows.forEach(r => {
      let value = r[line.field];
      let at = r.t + (line.shift || 0);

      if (
        value == null ||
        !Number.isFinite(value) ||
        at > time
      ) return;

      let X = x(at);
      let Y = y(value);

      if (first) {
        ctx.moveTo(X, Y);
        first = false;
      } else {
        ctx.lineTo(X, Y);
      }
    });

    ctx.stroke();
    ctx.setLineDash([]);
  });

  ctx.restore();
}

function chartDef(key) {
  const active = mode === 'ml' ? 'ml' : 'pid';

  if (key === 'pwm') {
    return [
      'Moc żarówki PWM (0–255)',
      series('pwm_nadany'),
      '',
      [0, 255]
    ];
  }

  if (key === 'error') {
    return [
      'Uchyb: zadana − zmierzona',
      series('blad'),
      '°C'
    ];
  }

  if (key === 'fan') {
    return [
      'Stan wentylatora (0 / 1)',
      series('wentylator'),
      '',
      [0, 1]
    ];
  }

  if (key === 'sensors') {
    return [
      'Górny i dolny czujnik · ' +
        (active === 'pid' ? 'PID' : 'PI + ML'),
      [
        {
          rows: data[active],
          field: 'temp_gora',
          color: color.top,
          label: 'Góra'
        },
        {
          rows: data[active],
          field: 'temp_dol',
          color: color.bottom,
          label: 'Dół'
        }
      ],
      '°C'
    ];
  }

  if (key === 'prediction') {
    return [
      'Prognoza ML na 60 s naprzód',
      [
        {
          rows: data.ml,
          field: 'temp_srednia',
          color: color.ml,
          label: 'Pomiar'
        },
        {
          rows: data.ml,
          field: 'prognoza_ml',
          shift: 1,
          color: color.top,
          label: 'Prognoza przesunięta o 60 s'
        }
      ],
      '°C'
    ];
  }

  if (key === 'parts') {
    return [
      'Człony regulatora · ' +
        (active === 'pid' ? 'PID' : 'PI + ML'),
      [
        {
          rows: data[active],
          field: 'P',
          color: color.pid,
          label: 'P'
        },
        {
          rows: data[active],
          field: 'I',
          color: color.ml,
          label: 'I'
        },
        ...(active === 'pid' ? [{
          rows: data.pid,
          field: 'D',
          color: color.top,
          label: 'D'
        }] : [])
      ],
      ''
    ];
  }

  return null;
}

function buildExtras() {
  extras = [];
  $('extras').replaceChildren();

  document.querySelectorAll('#choices input:checked')
    .forEach(input => {
      let def = chartDef(input.value);
      if (!def) return;

      let box = document.createElement('article');
      box.className = 'card';

      let title = document.createElement('h3');
      title.textContent = def[0];
      box.append(title);

      let legend = document.createElement('div');
      legend.className = 'legend';

      for (let line of def[1]) {
        let item = document.createElement('span');
        let dot = document.createElement('b');

        dot.style.background = line.color;
        item.append(
          dot,
          document.createTextNode(line.label)
        );
        legend.append(item);
      }

      box.append(legend);

      let canvas = document.createElement('canvas');
      canvas.className = 'chart';
      box.append(canvas);
      $('extras').append(box);

      extras.push({
        canvas,
        lines: def[1],
        unit: def[2],
        fixed: def[3]
      });
    });

  render();
}

function measurements() {
  let a = selected('pid');
  let b = selected('ml');
  let current = mode === 'ml' ? b : a;

  $('set').textContent = c(a.temp_zadana);
  $('pidTemp').textContent = c(a.temp_srednia);
  $('mlTemp').textContent = c(b.temp_srednia);
  $('currentTime').textContent = clock(time);
  $('clock').textContent = clock(time);

  $('timeline').value = Math.round(
    time / duration * 1000
  );

  $('chamberTemp').textContent =
    c(current.temp_srednia);

  $('chamberMode').textContent =
    'Wyświetlane dane ' +
    (mode === 'ml' ? 'PI + ML' : 'PID');

  $('pwm').textContent =
    fmt(current.pwm_nadany / 255 * 100, 0) + '%';

  $('fan').textContent =
    current.wentylator >= 0.5 ? 'WŁ.' : 'WYŁ.';

  $('top').textContent = c(current.temp_gora);
  $('bottom').textContent = c(current.temp_dol);
}

function render() {
  if (!data) return;

  measurements();

  draw(
    $('mainPlot'),
    [
      {
        rows: data.pid,
        field: 'temp_zadana',
        color: color.set,
        dash: true
      },
      ...series($('tempField').value)
    ],
    '°C'
  );

  extras.forEach(e =>
    draw(e.canvas, e.lines, e.unit, e.fixed)
  );
}

function metrics(rows) {
  const avg = a =>
    a.reduce((x, y) => x + y, 0) / a.length;

  let errors = rows.map(r => Math.abs(r.blad));

  let tail = rows.filter(
    r => r.t >= rows.at(-1).t - 5
  );

  let crossing = rows.find(
    r => Math.abs(r.blad) <= 0.5
  );

  let temps = tail.map(r => r.temp_srednia);
  let mean = avg(temps);

  return [
    avg(errors),
    avg(tail.map(r => Math.abs(r.blad))),
    Math.sqrt(avg(temps.map(t => (t - mean) ** 2))),
    Math.max(0, ...rows.map(
      r => r.temp_srednia - r.temp_zadana
    )),
    crossing ? crossing.t : null,
    avg(rows.map(r => r.pwm_nadany))
  ];
}

function showStats() {
  let a = metrics(data.pid);
  let b = metrics(data.ml);

  let labels = [
    ['Średni błąd MAE', '°C'],
    ['Błąd MAE z ostatnich 5 minut', '°C'],
    ['Wahania temperatury w ostatnich 5 min (σ)', '°C'],
    ['Największe przeregulowanie', '°C'],
    ['Pierwsze wejście w ±0,5°C', 'min'],
    ['Średnia moc PWM', '/255']
  ];

  $('stats').innerHTML = labels.map(
    ([label, unit], i) => `
      <div class="stat">
        <small>${label}</small>
        <div class="values">
          <div>
            <small>PID</small>
            <strong style="color:var(--orange)">
              ${fmt(a[i], 2)} ${a[i] == null ? '' : unit}
            </strong>
          </div>
          <div>
            <small>PI + ML</small>
            <strong style="color:var(--green)">
              ${fmt(b[i], 2)} ${b[i] == null ? '' : unit}
            </strong>
          </div>
        </div>
      </div>
    `
  ).join('');
}

function playState(isPlaying) {
  playing = isPlaying;
  previous = null;

  $('play').textContent =
    playing ? '⏸ Pauza' : '▶ Start';

  $('status').textContent =
    playing ? 'Odtwarzanie' : 'Pauza';
}

function tick(now) {
  if (playing && data) {
    if (previous !== null) {
      time = Math.min(
        duration,
        time + (now - previous) / 1000 * speed / 60
      );
    }

    previous = now;

    if (time >= duration) {
      playState(false);
      $('status').textContent = 'Koniec odtwarzania';
    }
  }

  if (data && now - drawAt > 90) {
    render();
    drawAt = now;
  }

  requestAnimationFrame(tick);
}

document.querySelectorAll('[data-mode]')
  .forEach(button => button.addEventListener('click', () => {
    mode = button.dataset.mode;

    document.querySelectorAll('[data-mode]')
      .forEach(b =>
        b.classList.toggle('active', b === button)
      );

    buildExtras();
  }));

$('play').addEventListener('click', () => {
  if (!data) return;
  if (!playing && time >= duration) time = 0;
  playState(!playing);
});

$('reset').addEventListener('click', () => {
  time = 0;
  playState(false);
  render();
});

$('timeline').addEventListener('input', e => {
  if (!data) return;
  time = duration * Number(e.target.value) / 1000;
  render();
});

$('speed').addEventListener('change', e => {
  speed = Number(e.target.value);
});

$('tempField').addEventListener('change', render);

document.querySelectorAll('#choices input')
  .forEach(e =>
    e.addEventListener('change', buildExtras)
  );

$('showAll').addEventListener('click', () => {
  document.querySelectorAll('#choices input')
    .forEach(i => i.checked = true);
  buildExtras();
});

fetch('/api/data', {cache: 'no-store'})
  .then(r => r.json().then(j => {
    if (!r.ok) throw Error(j.error);
    return j;
  }))
  .then(j => {
    data = j;

    duration = Math.max(
      data.pid.at(-1).t,
      data.ml.at(-1).t
    );

    $('length').textContent =
      fmt(duration, 1) + ' min · po ' +
      data.pid.length + '/' +
      data.ml.length + ' próbek';

    showStats();
    buildExtras();

    $('status').textContent =
      'Gotowy do uruchomienia';
  })
  .catch(err => {
    $('alert').textContent =
      'Błąd wczytywania CSV: ' + err.message;
    $('alert').style.display = 'block';
  });

requestAnimationFrame(tick);
</script>
</body>
</html>'''


class App(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.split("?")[0] == "/api/data":
                payload = json.dumps({
                    "pid": read_results("wyniki_pid.csv"),
                    "ml": read_results("wyniki_pi_ml.csv")
                }, ensure_ascii=False).encode("utf-8")

                mime = "application/json; charset=utf-8"
                status = 200

            elif self.path.split("?")[0] in ("/", "/index.html"):
                payload = HTML.encode("utf-8")
                mime = "text/html; charset=utf-8"
                status = 200

            else:
                self.send_error(404)
                return

        except (OSError, ValueError) as error:
            payload = json.dumps(
                {"error": str(error)},
                ensure_ascii=False
            ).encode("utf-8")

            mime = "application/json; charset=utf-8"
            status = 500

        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    for filename in ("wyniki_pid.csv", "wyniki_pi_ml.csv"):
        print(
            filename,
            "-",
            len(read_results(filename)),
            "pomiarów"
        )

    print(f"Panel: http://raspberrypi.local:{PORT}")
    print("Zatrzymanie: Ctrl+C")

    try:
        ThreadingHTTPServer(
            ("0.0.0.0", PORT), App
        ).serve_forever()

    except KeyboardInterrupt:
        print("Serwer zatrzymany.")
