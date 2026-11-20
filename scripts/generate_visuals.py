#!/usr/bin/env python3
"""
Generates live, animated SVG assets for yigitcnsn's GitHub profile:
1. assets/city.svg    — 52-week 3D Isometric Contribution Graph fetched live from GitHub GraphQL API.
2. assets/toolbox.svg — Single-SVG Nord/GitHub-dark Toolbox with vector icons & staggered rise animation.
"""

import json
import math
import os
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERNAME = os.environ.get("GITHUB_USERNAME", "yigitcnsn")
DATA_PATH = os.path.join(ROOT, "gh_data.json")
OUT_CITY = os.path.join(ROOT, "assets", "city.svg")
OUT_TOOLBOX = os.path.join(ROOT, "assets", "toolbox.svg")

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
    repositories(first: 25, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        isPrivate
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 1) {
                totalCount
              }
            }
          }
        }
      }
    }
  }
}
"""


def get_github_token():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    try:
        out = subprocess.check_output(["gh", "auth", "token"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return None


def load_data():
    token = get_github_token()
    if token:
        payload = json.dumps({"query": GRAPHQL_QUERY, "variables": {"login": USERNAME}}).encode("utf-8")
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=payload,
                headers={
                    "Authorization": f"bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "yigitcnsn-profile-generator",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except Exception:
            out = subprocess.check_output(
                [
                    "curl", "-fsSL", "-X", "POST", "https://api.github.com/graphql",
                    "-H", f"Authorization: bearer {token}",
                    "-H", "Content-Type: application/json",
                    "-d", payload.decode("utf-8"),
                ],
                timeout=20,
            )
            body = json.loads(out.decode("utf-8"))
        if "errors" in body:
            raise RuntimeError(f"GitHub GraphQL errors: {body['errors']}")
        raw = body["data"]["user"]
    elif os.path.exists(DATA_PATH):
        raw = json.load(open(DATA_PATH, "r"))["data"]["user"]
    else:
        raise RuntimeError("No GITHUB_TOKEN / GH_TOKEN available and gh_data.json not found.")

    cal = raw["contributionsCollection"]["contributionCalendar"]
    repos = raw["repositories"]["nodes"]
    return cal, repos


def generate_constellation(cal, repos):
    total_contribs = cal["totalContributions"]

    # Curate 4 distinct engineering constellations from real repos + commit counts
    clusters = [
        {
            "name": "SYSTEMS &amp; SILICON SECTOR",
            "color": "#34D399",
            "glow": "#10B981",
            "delay": 0.0,
            "stars": [
                ("etab-note (C OS)", 135, 118, 23, "23 commits · Bare Linux"),
                ("Vanguard32 (RF)", 215, 76, 8, "ESP32-S3 · 433MHz"),
                ("SensorNode (BLE)", 295, 108, 6, "nRF52 · Zephyr RTOS"),
                ("smart-home (PWM)", 248, 174, 9, "15A MOSFET · KiCad"),
                ("esp-surveillance", 152, 198, 5, "ESP32-CAM · Edge"),
            ],
            "edges": [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (4, 3)],
        },
        {
            "name": "FULL-STACK &amp; WEB CLUSTER",
            "color": "#38BDF8",
            "glow": "#0EA5E9",
            "delay": 1.4,
            "stars": [
                ("home-hub (Pi Hub)", 490, 96, 127, "127 commits · WebSocket"),
                ("fastapi-device-crud", 588, 68, 8, "FastAPI · Async REST"),
                ("gezgin (Flutter)", 625, 146, 12, "8 commits · Dart/Mobile"),
                ("LarGer (Mobile)", 522, 182, 10, "Flutter · Local-First"),
            ],
            "edges": [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)],
        },
        {
            "name": "AI, MCP &amp; SPATIAL CV SECTOR",
            "color": "#A78BFA",
            "glow": "#8B5CF6",
            "delay": 2.8,
            "stars": [
                ("PrismDesk (AR CV)", 795, 92, 42, "42 commits · Homography"),
                ("vaultwire (MCP)", 892, 66, 9, "TypeScript · Claude MCP"),
                ("pi-llm (Ollama)", 912, 152, 9, "Local LLM · KAP AI"),
                ("agent-council", 812, 184, 6, "Multi-Agent Python"),
            ],
            "edges": [(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)],
        },
        {
            "name": "NATIVE MACOS &amp; SWIFT BELT",
            "color": "#FBBF24",
            "glow": "#F59E0B",
            "delay": 4.2,
            "stars": [
                ("Engram (iCloud/PK)", 358, 258, 18, "14 commits · SwiftUI"),
                ("AIUsageTracker", 488, 282, 10, "MenuBar + WidgetKit"),
                ("SilGitsin (macOS)", 618, 256, 14, "9 commits · Native Swift"),
                ("KeyboardManager", 738, 280, 8, "IOKit 0xFF1C HID Driver"),
            ],
            "edges": [(0, 1), (1, 2), (2, 3), (0, 2)],
        },
    ]

    # Long-range inter-constellation bridge links (connecting the whole galaxy)
    bridges = [
        ((295, 108), (490, 96), "#38BDF8", 5.2),   # SensorNode <-> home-hub
        ((490, 96), (795, 92), "#A78BFA", 5.6),    # home-hub <-> PrismDesk
        ((135, 118), (358, 258), "#34D399", 6.0),  # etab-note <-> Engram (iCloud sync!)
        ((618, 256), (812, 184), "#FBBF24", 6.4),  # SilGitsin <-> agent-council
    ]

    # Deterministic background starfield from actual daily contribution counts
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    bg_stars_svg = []
    for idx, d in enumerate(days):
        # Map 365 days across the 1000x360 sky
         col = idx // 7
         row = idx % 7
         gx = 28 + col * 18.2 + ((row * 7 + idx * 3) % 11)
         gy = 52 + row * 40.5 + ((col * 13 + idx * 5) % 23)
         cnt = d["contributionCount"]
         if cnt > 0:
             r = min(2.4, 1.0 + cnt * 0.14)
             op = min(0.85, 0.35 + cnt * 0.06)
             col_hex = "#38BDF8" if (idx % 3 == 0) else ("#34D399" if (idx % 3 == 1) else "#A78BFA")
             dur = 2.2 + (idx % 5) * 0.6
             bg_stars_svg.append(
                 f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="{r:.2f}" fill="{col_hex}" opacity="{op:.2f}">'
                 f'<animate attributeName="opacity" values="{op:.2f};0.12;{op:.2f}" dur="{dur:.1f}s" repeatCount="indefinite"/>'
                 f'</circle>'
             )
         elif idx % 3 == 0:
             bg_stars_svg.append(
                 f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="0.7" fill="#475569" opacity="0.28"/>'
             )

    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 370" width="100%" height="370">
  <defs>
    <radialGradient id="skyBg" cx="50%" cy="45%" r="75%">
      <stop offset="0%" stop-color="#0D1527"/>
      <stop offset="55%" stop-color="#080D1A"/>
      <stop offset="100%" stop-color="#050811"/>
    </radialGradient>
    <radialGradient id="nebula1" cx="22%" cy="38%" r="32%">
      <stop offset="0%" stop-color="#10B981" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="#10B981" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula2" cx="54%" cy="32%" r="30%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula3" cx="84%" cy="36%" r="28%">
      <stop offset="0%" stop-color="#8B5CF6" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0"/>
    </radialGradient>
    <filter id="starGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <clipPath id="skyClip">
      <rect width="1000" height="370" rx="16"/>
    </clipPath>
    <style>
      .hdr-title {{ font: 700 14px 'SF Pro Display', -apple-system, 'Segoe UI', sans-serif; fill: #F8FAFC; letter-spacing: 0.6px; }}
      .hdr-sub   {{ font: 500 11px 'JetBrains Mono', 'SF Mono', monospace; fill: #94A3B8; }}
      .sec-lbl   {{ font: 700 9.5px 'JetBrains Mono', 'SF Mono', monospace; letter-spacing: 1.2px; opacity: 0.75; }}
      .star-lbl  {{ font: 600 11px 'JetBrains Mono', 'SF Mono', monospace; fill: #F1F5F9; }}
      .star-sub  {{ font: 500 9.5px 'JetBrains Mono', 'SF Mono', monospace; fill: #94A3B8; }}
    </style>
  </defs>

  <g clip-path="url(#skyClip)">
    <rect width="1000" height="370" rx="16" fill="url(#skyBg)"/>
    <rect width="1000" height="370" fill="url(#nebula1)"/>
    <rect width="1000" height="370" fill="url(#nebula2)"/>
    <rect width="1000" height="370" fill="url(#nebula3)"/>

    <!-- Subtle Celestial Coordinate Rings -->
    <circle cx="500" cy="185" r="145" fill="none" stroke="#1E293B" stroke-width="0.7" stroke-dasharray="3 6" opacity="0.5"/>
    <circle cx="500" cy="185" r="285" fill="none" stroke="#1E293B" stroke-width="0.7" stroke-dasharray="3 6" opacity="0.5"/>
    <circle cx="500" cy="185" r="425" fill="none" stroke="#1E293B" stroke-width="0.7" stroke-dasharray="3 6" opacity="0.4"/>

    <!-- Top Header Bar -->
    <rect x="0" y="0" width="1000" height="36" fill="#0A101D" fill-opacity="0.75"/>
    <line x1="0" y1="36" x2="1000" y2="36" stroke="#1E293B" stroke-width="1"/>
    <circle cx="22" cy="18" r="4" fill="#38BDF8" filter="url(#starGlow)"/>
    <text x="34" y="22" class="hdr-title">CELESTIAL COMMIT MAP  ·  LIVE REPOSITORY CONSTELLATIONS</text>
    <text x="980" y="22" text-anchor="end" class="hdr-sub">{total_contribs} CONTRIBUTIONS · 20 ACTIVE STAR NODES · NIGHTLY AUTO-SYNC</text>

    <!-- 365-Day Background Starfield (Each daily commit is a twinkling background star) -->
    <g>
      {"".join(bg_stars_svg)}
    </g>
''']

    # Inter-constellation long-range bridge lines
    for (x1, y1), (x2, y2), col, dly in bridges:
        dist = math.hypot(x2 - x1, y2 - y1)
        svg.append(f'''
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.1" stroke-dasharray="4 6" opacity="0">
      <animate attributeName="opacity" values="0;0;0.45;0.45;0" keyTimes="0;{dly/10:.2f};{(dly+0.8)/10:.2f};0.92;1" dur="11s" repeatCount="indefinite"/>
    </line>''')

    # Draw each constellation: sector title, animated laser links, and igniting star nodes
    for c in clusters:
        col = c["color"]
        dly = c["delay"]
        stars = c["stars"]
        # Sector label near average center
        avg_x = sum(s[1] for s in stars) / len(stars)
        min_y = min(s[2] for s in stars) - 22
        svg.append(f'    <text x="{avg_x:.0f}" y="{min_y:.0f}" text-anchor="middle" class="sec-lbl" fill="{col}">{c["name"]}</text>')

        # Animated constellation edges (draw line from star A to star B when stars ignite)
        for idx_e, (i1, i2) in enumerate(c["edges"]):
            x1, y1 = stars[i1][1], stars[i1][2]
            x2, y2 = stars[i2][1], stars[i2][2]
            dist = math.hypot(x2 - x1, y2 - y1)
            t_start = (dly + 0.35 + idx_e * 0.18) / 11.0
            t_done = min(0.85, t_start + 0.08)
            svg.append(f'''
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.7" stroke-opacity="0.65"
          stroke-dasharray="{dist:.1f}" stroke-dashoffset="{dist:.1f}" filter="url(#starGlow)">
      <animate attributeName="stroke-dashoffset" values="{dist:.1f};{dist:.1f};0;0;{dist:.1f}"
               keyTimes="0;{t_start:.3f};{t_done:.3f};0.92;1" dur="11s" repeatCount="indefinite"/>
    </line>''')

        # Draw stars & labels
        for idx_s, (name, sx, sy, commits, sub) in enumerate(stars):
            r_core = min(7.0, 3.5 + math.log2(max(2, commits)) * 0.75)
            r_halo = r_core * 2.5
            t_ignite = (dly + idx_s * 0.15) / 11.0
            t_full = min(0.85, t_ignite + 0.06)
            svg.append(f'''
    <g transform="translate({sx}, {sy})">
      <!-- Outer pulsing halo -->
      <circle cx="0" cy="0" r="{r_halo:.1f}" fill="{col}" opacity="0">
        <animate attributeName="opacity" values="0;0;0.28;0.14;0.28;0"
                 keyTimes="0;{t_ignite:.3f};{t_full:.3f};0.65;0.92;1" dur="11s" repeatCount="indefinite"/>
        <animate attributeName="r" values="{r_core:.1f};{r_halo:.1f};{r_halo*1.25:.1f};{r_halo:.1f}" dur="3.2s" repeatCount="indefinite"/>
      </circle>
      <!-- 4-point star flare cross -->
      <path d="M -{r_halo:.1f} 0 L {r_halo:.1f} 0 M 0 -{r_halo:.1f} L 0 {r_halo:.1f}" stroke="{col}" stroke-width="1.1" opacity="0">
        <animate attributeName="opacity" values="0;0;0.75;0.75;0"
                 keyTimes="0;{t_ignite:.3f};{t_full:.3f};0.92;1" dur="11s" repeatCount="indefinite"/>
      </path>
      <!-- Bright star core -->
      <circle cx="0" cy="0" r="{r_core:.1f}" fill="#FFFFFF" stroke="{col}" stroke-width="2" filter="url(#starGlow)">
        <animate attributeName="opacity" values="0.25;0.25;1;1;0.25"
                 keyTimes="0;{t_ignite:.3f};{t_full:.3f};0.92;1" dur="11s" repeatCount="indefinite"/>
      </circle>
      <!-- Star Label -->
      <text x="0" y="{r_core + 15:.0f}" text-anchor="middle" class="star-lbl">{name}</text>
      <text x="0" y="{r_core + 27:.0f}" text-anchor="middle" class="star-sub">{sub}</text>
    </g>''')

    # Shooting star / comet across the sky
    svg.append('''
    <g>
      <line x1="-80" y1="60" x2="-20" y2="75" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" filter="url(#starGlow)" opacity="0.85">
        <animateTransform attributeName="transform" type="translate" values="0 0; 1180 240; 1180 240" keyTimes="0;0.22;1" dur="9s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0.95;0;0" keyTimes="0;0.08;0.22;1" dur="9s" repeatCount="indefinite"/>
      </line>
    </g>

    <!-- Bottom Legend Bar -->
    <rect x="0" y="338" width="1000" height="32" fill="#080D18" fill-opacity="0.88"/>
    <line x1="0" y1="338" x2="1000" y2="338" stroke="#1E293B" stroke-width="1"/>
    <circle cx="26" cy="354" r="4" fill="#34D399"/><text x="36" y="358" class="hdr-sub">Systems &amp; Bare-Linux (C/RTOS)</text>
    <circle cx="246" cy="354" r="4" fill="#38BDF8"/><text x="256" y="358" class="hdr-sub">Full-Stack &amp; WebSockets (JS/FastAPI)</text>
    <circle cx="508" cy="354" r="4" fill="#A78BFA"/><text x="518" y="358" class="hdr-sub">AI, MCP &amp; Spatial CV (Python/TS)</text>
    <circle cx="754" cy="354" r="4" fill="#FBBF24"/><text x="764" y="358" class="hdr-sub">Native macOS Suite (Swift/IOKit)</text>
  </g>
  <rect x="1" y="1" width="998" height="368" rx="15" fill="none" stroke="#1E293B" stroke-width="1.5"/>
</svg>
''')
    open(OUT_CONSTELLATION, "w").write("\n".join(svg))
    print(f"Generated {OUT_CONSTELLATION}")


def iso_pt(w, d, z=0.0):
    """Convert (week 0..52, day 0..6, height z) to 2D isometric coordinates."""
    # Center the 53x7 board cleanly between y=135..300 so top HUD cards (y=46..102) and bottom legend (y=338) never collide
    ox, oy = 188.0, 128.0
    wx, wy = 13.4, 3.05   # step per week (down-right)
    dx, dy = -12.0, 5.2   # step per weekday (down-left)
    x = ox + w * wx + d * dx
    y = oy + w * wy + d * dy - z
    return x, y


def make_tower_svg(w, d, h, top_col, left_col, right_col, pulse=False):
    """Draw a 3D isometric prism at (w, d) with height h."""
    bw = 0.78  # footprint width in week-units
    bd = 0.78  # footprint depth in day-units

    # Top face 4 corners (at height h)
    t0 = iso_pt(w, d, h)
    t1 = iso_pt(w + bw, d, h)
    t2 = iso_pt(w + bw, d + bd, h)
    t3 = iso_pt(w, d + bd, h)

    # Bottom visible corners (at height 0)
    b1 = iso_pt(w + bw, d, 0)
    b2 = iso_pt(w + bw, d + bd, 0)
    b3 = iso_pt(w, d + bd, 0)

    top_pts = f"{t0[0]:.1f},{t0[1]:.1f} {t1[0]:.1f},{t1[1]:.1f} {t2[0]:.1f},{t2[1]:.1f} {t3[0]:.1f},{t3[1]:.1f}"
    left_pts = f"{t3[0]:.1f},{t3[1]:.1f} {t2[0]:.1f},{t2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {b3[0]:.1f},{b3[1]:.1f}"
    right_pts = f"{t2[0]:.1f},{t2[1]:.1f} {t1[0]:.1f},{t1[1]:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}"

    out = [
        f'<polygon points="{left_pts}" fill="{left_col}"/>',
        f'<polygon points="{right_pts}" fill="{right_col}"/>',
        f'<polygon points="{top_pts}" fill="{top_col}"/>',
    ]
    if pulse:
        cx = (t0[0] + t2[0]) * 0.5
        cy = (t0[1] + t2[1]) * 0.5
        dur = 1.6 + ((w * 3 + d) % 5) * 0.4
        out.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="#FFFFFF" filter="url(#cityGlow)">'
            f'<animate attributeName="opacity" values="1;0.2;1" dur="{dur:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    return "".join(out)


def generate_city(cal, repos):
    total_contribs = cal["totalContributions"]
    weeks = cal["weeks"]

    active_days = 0
    max_cnt = 1
    peak_date = ""
    for w in weeks:
        for d in w["contributionDays"]:
            c = d["contributionCount"]
            if c > 0:
                active_days += 1
            if c > max_cnt:
                max_cnt = c
                peak_date = d["date"]

    # Compute top 3 repositories dynamically from GraphQL commit counts
    repo_counts = []
    for r in repos:
        rname = r.get("name", "")
        if not rname or rname.lower() == USERNAME.lower():
            continue
        cnt = ((r.get("defaultBranchRef") or {}).get("target") or {}).get("history", {}).get("totalCount", 0)
        if cnt > 0:
            repo_counts.append((cnt, rname))
    repo_counts.sort(reverse=True)
    top_repos_str = " · ".join(f"{name} ({cnt})" for cnt, name in repo_counts[:3]) or "updating..."

    # Authentic GitHub Dark Contribution Palette (Top face, Left face, Right face)
    tiers = [
        ("#161B22", "#0D1117", "#12161C"),  # 0: empty slot
        ("#0E4429", "#072516", "#0A331F"),  # 1..2: GitHub level 1 green
        ("#006D32", "#00451F", "#005828"),  # 3..6: GitHub level 2 green
        ("#26A641", "#186E2A", "#1F8835"),  # 7..14: GitHub level 3 green
        ("#39D353", "#229437", "#2DB344"),  # 15+: GitHub level 4 bright green
    ]

    towers_svg = []
    for w_idx, w in enumerate(weeks):
        for d in w["contributionDays"]:
            d_idx = d["weekday"]
            cnt = d["contributionCount"]
            if cnt == 0:
                h = 2.5
                t_col, l_col, r_col = tiers[0]
                pulse = False
            else:
                h = 10.0 + min(68.0, math.pow(cnt, 0.70) * 8.8)
                if cnt <= 2:
                    t_col, l_col, r_col = tiers[1]
                elif cnt <= 6:
                    t_col, l_col, r_col = tiers[2]
                elif cnt <= 14:
                    t_col, l_col, r_col = tiers[3]
                else:
                    t_col, l_col, r_col = tiers[4]
                pulse = (cnt >= 12)
            towers_svg.append(make_tower_svg(w_idx, d_idx, h, t_col, l_col, r_col, pulse))

    p0 = iso_pt(-0.6, -0.6, 0)
    p1 = iso_pt(len(weeks) + 0.4, -0.6, 0)
    p2 = iso_pt(len(weeks) + 0.4, 7.4, 0)
    p3 = iso_pt(-0.6, 7.4, 0)
    plat_pts = f"{p0[0]:.1f},{p0[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"

    s_start_a = iso_pt(0, -0.5, 2)
    s_start_b = iso_pt(0, 7.2, 2)
    dx_sweep = iso_pt(len(weeks), 0, 2)[0] - s_start_a[0]
    dy_sweep = iso_pt(len(weeks), 0, 2)[1] - s_start_a[1]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 350" width="100%" height="350">
  <defs>
    <clipPath id="cityClip">
      <rect width="1000" height="350" rx="10"/>
    </clipPath>
    <filter id="cityGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feComposite in="SourceGraphic" in2="b" operator="over"/>
    </filter>
    <style>
      .hdr-title {{ font: 600 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #E6EDF3; }}
      .hdr-sub   {{ font: 400 11.5px ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace; fill: #8B949E; }}
      .stat-val  {{ font: 600 18px ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace; fill: #E6EDF3; }}
      .stat-lbl  {{ font: 400 11px ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace; fill: #6E7681; }}
    </style>
  </defs>

  <g clip-path="url(#cityClip)">
    <rect width="1000" height="350" rx="10" fill="#0D1117"/>

    <!-- Minimal Header -->
    <text x="28" y="32" class="hdr-title">52-Week Contribution Graph (3D Isometric)</text>
    <text x="972" y="32" text-anchor="end" class="hdr-sub">{total_contribs} contributions in the last year  ·  {active_days} active days  ·  peak: {max_cnt} ({peak_date})</text>
    <line x1="28" y1="46" x2="972" y2="46" stroke="#21262D" stroke-width="1"/>

    <!-- Top-Right Inline Stats (Clean typographic layout, no boxy HUD cards) -->
    <g transform="translate(540, 64)">
      <text x="0"   y="14" class="stat-lbl">TOTAL</text>
      <text x="0"   y="36" class="stat-val" fill="#39D353">{total_contribs}</text>

      <text x="110" y="14" class="stat-lbl">ACTIVE DAYS</text>
      <text x="110" y="36" class="stat-val">{active_days}</text>

      <text x="235" y="14" class="stat-lbl">TOP REPOSITORIES</text>
      <text x="235" y="34" class="hdr-sub" fill="#C9D1D9">{top_repos_str}</text>
    </g>

    <!-- 3D Isometric Base Platform -->
    <polygon points="{plat_pts}" fill="#090D12" stroke="#21262D" stroke-width="1"/>

    <!-- 365 Isometric 3D Towers (Back-to-Front Painter's Order) -->
    <g>
      {"".join(towers_svg)}
    </g>

    <!-- Subtle Playhead Scan Line Across Weeks -->
    <line x1="{s_start_a[0]:.1f}" y1="{s_start_a[1]:.1f}" x2="{s_start_b[0]:.1f}" y2="{s_start_b[1]:.1f}"
          stroke="#39D353" stroke-width="1.5" stroke-opacity="0.55">
      <animateTransform attributeName="transform" type="translate"
                        values="0 0; {dx_sweep:.1f} {dy_sweep:.1f}; 0 0"
                        dur="10s" repeatCount="indefinite"/>
    </line>

    <!-- Authentic GitHub-Style Less/More Legend at Bottom-Right -->
    <text x="28" y="330" class="stat-lbl">Updated nightly via GitHub GraphQL API</text>
    <g transform="translate(810, 320)">
      <text x="0" y="10" class="stat-lbl">Less</text>
      <rect x="34"  y="0" width="11" height="11" rx="2" fill="#161B22" stroke="#21262D" stroke-width="0.8"/>
      <rect x="49"  y="0" width="11" height="11" rx="2" fill="#0E4429"/>
      <rect x="64"  y="0" width="11" height="11" rx="2" fill="#006D32"/>
      <rect x="79"  y="0" width="11" height="11" rx="2" fill="#26A641"/>
      <rect x="94"  y="0" width="11" height="11" rx="2" fill="#39D353"/>
      <text x="112" y="10" class="stat-lbl">More</text>
    </g>
  </g>
  <rect x="0.5" y="0.5" width="999" height="349" rx="9.5" fill="none" stroke="#30363D" stroke-width="1"/>
</svg>
'''
    open(OUT_CITY, "w").write(svg)
    print(f"Generated {OUT_CITY}")


def generate_toolbox():
    """Generate a single Nord/GitHub-dark Toolbox SVG with vector icons & staggered rise animation."""
    # 24x24 vector icon paths (scaled by 0.6667 inside each 30px-tall pill)
    ICONS = {
        "python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm6.79 5.93l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01z",
        "chip":   "M6 2v2H4a2 2 0 0 0-2 2v2H0v2h2v4H0v2h2v2a2 2 0 0 0 2 2h2v2h2v-2h4v2h2v-2h2a2 2 0 0 0 2-2v-2h2v-2h-2v-4h2V8h-2V6a2 2 0 0 0-2-2h-2V2h-2v2h-4V2H6zm2 6h8v8H8V8z",
        "code":   "M8.7 16.6L4.1 12l4.6-4.6L7.3 6l-6 6 6 6 1.4-1.4zm6.6 0l4.6-4.6-4.6-4.6L16.7 6l6 6-6 6-1.4-1.4z",
        "linux":  "M12 2a5 5 0 0 0-5 5v3.5L5.2 14A3 3 0 0 0 8 18.5h8a3 3 0 0 0 2.8-4.5L17 10.5V7a5 5 0 0 0-5-5zm-2 5a1.2 1.2 0 1 1 0 2.4A1.2 1.2 0 0 1 10 7zm4 0a1.2 1.2 0 1 1 0 2.4A1.2 1.2 0 0 1 14 7zm-4 5h4c0 1.4-1 2.4-2 2.4s-2-1-2-2.4z",
        "wave":   "M2 12h3l2.5-7 4 14 3.5-10 2.5 3H22v2h-5.5l-1.5-2-3.5 10-4-14L5.8 14H2v-2z",
        "ai":     "M12 2l2.4 6.6L21 11l-6.6 2.4L12 20l-2.4-6.6L3 11l6.6-2.4L12 2zm6 13l1.1 2.9L22 19l-2.9 1.1L18 23l-1.1-2.9L14 19l2.9-1.1L18 15z",
        "eye":    "M12 5c-5 0-9.3 3.1-11 7.5C2.7 16.9 7 20 12 20s9.3-3.1 11-7.5C21.3 8.1 17 5 12 5zm0 12.5a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
        "box":    "M12 1L2 6v12l10 5 10-5V6L12 1zm0 2.3l7.2 3.6L12 10.5 4.8 6.9 12 3.3zM4 8.7l7 3.5v7.9l-7-3.5V8.7zm9 11.4v-7.9l7-3.5v7.9l-7 3.5z",
        "bolt":   "M13 2L3 14h8l-1 8 10-12h-8l1-8z",
        "pi":     "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-3 6h6v2h-1.5v6h-2v-6h-1v6h-2v-6H8V8h1z",
        "obs":    "M15.07 0L7.61 4.12l.82 4.27 6.37-5.02zm-.18 3.53L8.49 8.58l7.39 15.37 1.18-2.36L19.58 6.4zm-7.43.78L4.41 10.9 9.03 21.5l-.74-12.93z",
        "apple":  "M18.7 19.5c-.8 1.2-1.7 2.4-3.1 2.4-1.3 0-1.8-.8-3.3-.8-1.6 0-2.1.8-3.3.8-1.3 0-2.3-1.3-3.2-2.5-1.7-2.5-3-7-1.2-10 .9-1.5 2.4-2.4 4.1-2.5 1.3 0 2.5.9 3.3.9.8 0 2.2-1.1 3.8-.9.6 0 2.4.2 3.6 1.9-.1.1-2.1 1.2-2.1 3.7 0 3 2.6 4 2.6 4-.1.2-.4 1.4-1.2 3zM15.5 4c.7-.8 1.1-2 1-3.2-1 0-2.2.7-2.9 1.5-.6.7-1.2 1.9-1 3 1.1.1 2.2-.5 2.9-1.3z",
    }

    categories = [
        {
            "title": "Languages",
            "color": "#EBCB8B",
            "items": [
                ("C (C99 / C11)", "code"),
                ("C++20", "code"),
                ("Python", "python"),
                ("Swift 5.10", "apple"),
                ("TypeScript", "code"),
                ("JavaScript", "code"),
                ("Dart", "code"),
                ("C#", "code"),
                ("Shell / Zsh", "code"),
                ("SQL", "box"),
            ],
        },
        {
            "title": "Embedded Systems · RTOS · Bare-Linux",
            "color": "#A3BE8C",
            "items": [
                ("Zephyr RTOS", "chip"),
                ("FreeRTOS", "chip"),
                ("Embedded Linux (Kernel 3.4+ / fb0 / evdev)", "linux"),
                ("STM32", "chip"),
                ("nRF52 (BLE / FOTA)", "chip"),
                ("ESP32-S3", "chip"),
                ("MSP430", "chip"),
                ("DeviceTree (DTS) & Kconfig", "linux"),
                ("Modbus RTU / CAN / SPI / I2C", "wave"),
                ("IOKit USB HID", "apple"),
            ],
        },
        {
            "title": "AI · Computer Vision · Automation",
            "color": "#88C0D0",
            "items": [
                ("OpenCV (Homography & AR)", "eye"),
                ("Model Context Protocol (MCP)", "ai"),
                ("Ollama / Local LLMs", "ai"),
                ("Claude Code & Cursor", "ai"),
                ("NumPy", "python"),
                ("Jupyter", "python"),
                ("PyQt / Industrial ATE", "bolt"),
                ("Optical QC Pipelines", "eye"),
            ],
        },
        {
            "title": "Apps · Full-Stack · Platforms & DevOps",
            "color": "#81A1C1",
            "items": [
                ("SwiftUI & WidgetKit", "apple"),
                ("Flutter", "bolt"),
                ("Node.js & Express", "box"),
                ("FastAPI", "bolt"),
                ("WebSockets", "wave"),
                ("Docker", "box"),
                ("GitHub Actions CI/CD", "box"),
                ("CMake & PlatformIO", "code"),
                ("Zig CC (ARM Cross-Compile)", "bolt"),
                ("Unity / CMock & clang-tidy", "code"),
            ],
        },
        {
            "title": "Hardware Bench · EDA · Creative Tools",
            "color": "#D08770",
            "items": [
                ("KiCad 10 (Schematic & PCB)", "chip"),
                ("Raspberry Pi 5", "pi"),
                ("CC1101 Sub-GHz 433MHz", "wave"),
                ("SEGGER SystemView & JTAG", "wave"),
                ("Logic Analyzer & Oscilloscope", "wave"),
                ("Digilent Analog Discovery", "wave"),
                ("ESPHome & Home Assistant", "bolt"),
                ("Obsidian / Engram", "obs"),
            ],
        },
    ]

    max_w = 972
    x_start = 28
    y = 32
    pill_h = 30
    gap_x = 8
    gap_y = 8

    body_svg = []
    delay = 0.02

    for cat in categories:
        col = cat["color"]
        # Category header with vertical colored bar
        body_svg.append(
            f'<rect x="{x_start}" y="{y}" width="4" height="16" rx="2" fill="{col}"/>'
            f'<text x="{x_start + 12}" y="{y + 12.5}" fill="#ECEFF4" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="13" font-weight="bold">{cat["title"].replace("&", "&amp;")}</text>'
        )
        y += 26
        cx = x_start
        for label, icon_key in cat["items"]:
            # Calculate pill width from character length
            clean_lbl = label.replace("&", "&amp;")
            w = 46 + len(label) * 7.35
            if cx + w > max_w:
                cx = x_start
                y += pill_h + gap_y
            icon_d = ICONS.get(icon_key, ICONS["code"])
            body_svg.append(
                f'<g class="c" style="animation-delay:{delay:.2f}s">'
                f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{pill_h}" rx="7" '
                f'fill="#161B22" stroke="{col}" stroke-opacity="0.38"/>'
                f'<path transform="translate({cx + 11:.1f} {y + 7:.1f}) scale(0.6667)" d="{icon_d}" fill="{col}"/>'
                f'<text x="{cx + 34:.1f}" y="{y + 19.2:.1f}" fill="#E6EDF3" '
                f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
                f'font-size="12">{clean_lbl}</text>'
                f'</g>'
            )
            cx += w + gap_x
            delay += 0.02
        y += pill_h + 24

    total_h = y + 8
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{total_h}" viewBox="0 0 1000 {total_h}" '
        f'role="img" aria-label="Toolbox — languages, embedded systems, AI/CV, full-stack, and hardware bench">'
        f'<title>Toolbox — languages, embedded systems, AI/CV, full-stack, and hardware bench</title>'
        f'<rect width="1000" height="{total_h}" rx="10" fill="#0D1117"/>'
        f'<rect x="0.5" y="0.5" width="999" height="{total_h - 1}" rx="9.5" fill="none" stroke="#30363D" stroke-width="1"/>'
        f'<style>@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}'
        f'.c{{animation:rise .45s ease-out both}}</style>'
        + "".join(body_svg)
        + "</svg>\n"
    )
    open(OUT_TOOLBOX, "w").write(svg)
    print(f"Generated {OUT_TOOLBOX} (height={total_h})")


if __name__ == "__main__":
    cal, repos = load_data()
    generate_city(cal, repos)
    generate_toolbox()
