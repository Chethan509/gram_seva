"""
Generates clean SVG graphical assets for Grama Seva Portal:
- Official Emblem
- Village Hero Vector Art
- Sample Complaint Photographic/Vector Previews
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')
UPLOADS_DIR = os.path.join(IMG_DIR, 'uploads')

os.makedirs(UPLOADS_DIR, exist_ok=True)

# 1. Official Grama Seva Emblem SVG
emblem_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <linearGradient id="saffronGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF9933" />
      <stop offset="100%" stop-color="#E65100" />
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#166534" />
      <stop offset="100%" stop-color="#14532d" />
    </linearGradient>
  </defs>

  <!-- Outer Ring with decorative border -->
  <circle cx="100" cy="100" r="95" fill="#FFFFFF" stroke="#166534" stroke-width="4"/>
  <circle cx="100" cy="100" r="88" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="3,3"/>
  <circle cx="100" cy="100" r="82" fill="#F0FDF4" stroke="#166534" stroke-width="1.5"/>

  <!-- Tricolor Arc Accent -->
  <path d="M 30,100 A 70,70 0 0,1 170,100" fill="none" stroke="#FF9933" stroke-width="6" stroke-linecap="round"/>
  <path d="M 30,100 A 70,70 0 0,0 170,100" fill="none" stroke="#138808" stroke-width="6" stroke-linecap="round"/>

  <!-- Inner Crest -->
  <circle cx="100" cy="100" r="54" fill="#FFFFFF" stroke="#166534" stroke-width="2"/>

  <!-- Sprouting Grain / Village Growth Leaves -->
  <path d="M 100,135 Q 85,115 86,95 Q 98,110 100,135 Z" fill="#15803d"/>
  <path d="M 100,135 Q 115,115 114,95 Q 102,110 100,135 Z" fill="#166534"/>
  <path d="M 100,140 Q 100,100 100,75" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>

  <!-- Sun of Progress in center -->
  <circle cx="100" cy="72" r="14" fill="#F59E0B"/>
  <!-- Sun rays -->
  <g stroke="#F59E0B" stroke-width="2" stroke-linecap="round">
    <line x1="100" y1="52" x2="100" y2="46"/>
    <line x1="100" y1="92" x2="100" y2="98"/>
    <line x1="80" y1="72" x2="74" y2="72"/>
    <line x1="120" y1="72" x2="126" y2="72"/>
    <line x1="86" y1="58" x2="81" y2="53"/>
    <line x1="114" y1="86" x2="119" y2="91"/>
    <line x1="86" y1="86" x2="81" y2="91"/>
    <line x1="114" y1="58" x2="119" y2="53"/>
  </g>

  <!-- Small Civic Emblem Symbol -->
  <circle cx="100" cy="72" r="6" fill="#FFFFFF"/>
  <circle cx="100" cy="72" r="2.5" fill="#166534"/>

  <!-- Ribbon at bottom -->
  <path d="M 45,150 L 155,150 L 145,168 L 100,162 L 55,168 Z" fill="#166534"/>
  <text x="100" y="161" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">GRAMA SEVA</text>
</svg>
"""

with open(os.path.join(IMG_DIR, 'emblem.svg'), 'w', encoding='utf-8') as f:
    f.write(emblem_svg.strip())

# 2. Village Hero Vector Illustration
village_hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 450" width="100%" height="100%">
  <defs>
    <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#E0F2FE"/>
      <stop offset="70%" stop-color="#BAE6FD"/>
      <stop offset="100%" stop-color="#FEF08A"/>
    </linearGradient>
    <linearGradient id="hill1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#86EFAC"/>
      <stop offset="100%" stop-color="#22C55E"/>
    </linearGradient>
    <linearGradient id="hill2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#4ADE80"/>
      <stop offset="100%" stop-color="#15803D"/>
    </linearGradient>
    <linearGradient id="fieldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#BBF7D0"/>
      <stop offset="100%" stop-color="#166534"/>
    </linearGradient>
  </defs>

  <!-- Sky -->
  <rect width="600" height="450" fill="url(#skyGrad)"/>

  <!-- Golden Morning Sun -->
  <circle cx="480" cy="110" r="45" fill="#F59E0B" opacity="0.9"/>
  <circle cx="480" cy="110" r="60" fill="#FDE68A" opacity="0.4"/>

  <!-- Distant Blue Hills -->
  <path d="M 0,260 Q 120,180 240,240 T 480,210 Q 540,230 600,250 L 600,450 L 0,450 Z" fill="#93C5FD" opacity="0.5"/>

  <!-- Middle Rolling Green Hills -->
  <path d="M 0,280 Q 150,220 310,270 Q 450,240 600,275 L 600,450 L 0,450 Z" fill="url(#hill1)"/>
  <path d="M 0,310 Q 180,260 380,315 Q 500,290 600,310 L 600,450 L 0,450 Z" fill="url(#hill2)"/>

  <!-- Foreground Agricultural Terraced Fields -->
  <path d="M 0,350 Q 200,320 400,360 L 600,350 L 600,450 L 0,450 Z" fill="url(#fieldGrad)"/>

  <!-- Panchayat Office Building with Indian Flag -->
  <g transform="translate(140, 240)">
    <!-- Main Hall -->
    <rect x="0" y="30" width="130" height="65" fill="#FFFFFF" stroke="#0F766E" stroke-width="2" rx="3"/>
    <!-- Roof with Saffron Band -->
    <polygon points="-10,30 65,0 140,30" fill="#166534"/>
    <rect x="15" y="10" width="100" height="6" fill="#F59E0B" rx="2"/>
    <!-- Pillars -->
    <rect x="15" y="45" width="8" height="50" fill="#E2E8F0"/>
    <rect x="40" y="45" width="8" height="50" fill="#E2E8F0"/>
    <rect x="82" y="45" width="8" height="50" fill="#E2E8F0"/>
    <rect x="107" y="45" width="8" height="50" fill="#E2E8F0"/>
    <!-- Doorway -->
    <rect x="55" y="55" width="20" height="40" fill="#047857" rx="3"/>
    <!-- Windows -->
    <rect x="26" y="52" width="10" height="15" fill="#BAE6FD" stroke="#94A3B8"/>
    <rect x="94" y="52" width="10" height="15" fill="#BAE6FD" stroke="#94A3B8"/>
    <!-- Flag Post -->
    <line x1="65" y1="0" x2="65" y2="-35" stroke="#334155" stroke-width="2.5"/>
    <!-- Tiranga -->
    <rect x="66" y="-35" width="22" height="5" fill="#FF9933"/>
    <rect x="66" y="-30" width="22" height="5" fill="#FFFFFF"/>
    <circle cx="77" cy="-27.5" r="2" fill="#000080"/>
    <rect x="66" y="-25" width="22" height="5" fill="#138808"/>
    <!-- Label -->
    <text x="65" y="40" font-family="sans-serif" font-size="7" font-weight="bold" fill="#166534" text-anchor="middle">GRAM PANCHAYAT</text>
  </g>

  <!-- Water Overhead Tank (Jal Jeevan Mission) -->
  <g transform="translate(370, 225)">
    <!-- Staging pillars -->
    <line x1="15" y1="50" x2="10" y2="100" stroke="#64748B" stroke-width="3"/>
    <line x1="45" y1="50" x2="50" y2="100" stroke="#64748B" stroke-width="3"/>
    <line x1="12" y1="75" x2="48" y2="75" stroke="#64748B" stroke-width="2"/>
    <line x1="10" y1="100" x2="50" y2="100" stroke="#64748B" stroke-width="3"/>
    <line x1="12" y1="50" x2="48" y2="100" stroke="#94A3B8" stroke-width="1"/>
    <line x1="48" y1="50" x2="12" y2="100" stroke="#94A3B8" stroke-width="1"/>
    <!-- Cylindrical Tank -->
    <rect x="5" y="15" width="50" height="35" rx="5" fill="#0284C7"/>
    <ellipse cx="30" cy="15" rx="25" ry="7" fill="#38BDF8"/>
    <!-- Droplet Icon -->
    <path d="M 30,23 C 30,23 35,32 35,36 C 35,39 32.8,41 30,41 C 27.2,41 25,39 25,36 C 25,32 30,23 30,23 Z" fill="#FFFFFF"/>
    <text x="30" y="47" font-family="sans-serif" font-size="5" font-weight="bold" fill="#FFFFFF" text-anchor="middle">JAL JEEVAN</text>
  </g>

  <!-- Smart Solar Streetlight -->
  <g transform="translate(70, 270)">
    <line x1="20" y1="150" x2="20" y2="40" stroke="#475569" stroke-width="4"/>
    <path d="M 20,40 Q 20,20 38,20 L 45,20" fill="none" stroke="#475569" stroke-width="3"/>
    <!-- Solar Panel -->
    <line x1="10" y1="28" x2="30" y2="20" stroke="#0284C7" stroke-width="5" stroke-linecap="round"/>
    <!-- LED Light fixture -->
    <rect x="42" y="20" width="12" height="6" fill="#F8FAFC" rx="2" stroke="#334155"/>
    <polygon points="40,26 25,70 65,70 54,26" fill="#FEF08A" opacity="0.4"/>
  </g>

  <!-- Paved Village Road -->
  <path d="M 0,450 L 180,350 L 250,350 L 380,450 Z" fill="#475569"/>
  <!-- Road Center Dashed Line -->
  <line x1="215" y1="355" x2="225" y2="375" stroke="#FFFFFF" stroke-width="2.5" stroke-dasharray="8,6"/>
  <line x1="230" y1="385" x2="250" y2="415" stroke="#FFFFFF" stroke-width="3.5" stroke-dasharray="12,8"/>
  <line x1="260" y1="425" x2="280" y2="450" stroke="#FFFFFF" stroke-width="4.5"/>

  <!-- Green Coconut Trees -->
  <g transform="translate(480, 250)">
    <path d="M 20,120 Q 25,60 15,10" fill="none" stroke="#78350F" stroke-width="6" stroke-linecap="round"/>
    <!-- Fronds -->
    <path d="M 15,10 Q -15,0 -30,20" fill="none" stroke="#15803D" stroke-width="4" stroke-linecap="round"/>
    <path d="M 15,10 Q 5,-15 -5,-25" fill="none" stroke="#16A34A" stroke-width="4" stroke-linecap="round"/>
    <path d="M 15,10 Q 30,-20 45,-15" fill="none" stroke="#15803D" stroke-width="4" stroke-linecap="round"/>
    <path d="M 15,10 Q 45,5 55,25" fill="none" stroke="#16A34A" stroke-width="4" stroke-linecap="round"/>
  </g>

  <g transform="translate(520, 270)">
    <path d="M 20,100 Q 15,50 25,10" fill="none" stroke="#78350F" stroke-width="5" stroke-linecap="round"/>
    <!-- Fronds -->
    <path d="M 25,10 Q -5,0 -20,15" fill="none" stroke="#15803D" stroke-width="3" stroke-linecap="round"/>
    <path d="M 25,10 Q 15,-15 5,-20" fill="none" stroke="#16A34A" stroke-width="3" stroke-linecap="round"/>
    <path d="M 25,10 Q 45,-15 55,-10" fill="none" stroke="#15803D" stroke-width="3" stroke-linecap="round"/>
  </g>

  <!-- Modern Floating Badge in Bottom Left -->
  <g transform="translate(25, 380)">
    <rect width="180" height="45" rx="8" fill="#FFFFFF" filter="drop-shadow(0 4px 6px rgba(0,0,0,0.1))"/>
    <circle cx="22" cy="22" r="14" fill="#DCFCE7"/>
    <path d="M 17,22 L 21,26 L 27,18" fill="none" stroke="#166534" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="44" y="19" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534">Smart Gram Panchayat</text>
    <text x="44" y="32" font-family="sans-serif" font-size="9" fill="#64748B">Digital Village Initiative</text>
  </g>
</svg>
"""

with open(os.path.join(IMG_DIR, 'village-hero.svg'), 'w', encoding='utf-8') as f:
    f.write(village_hero_svg.strip())


# Sample Complaint Previews
def create_complaint_sample(filename, title, subtitle, color, icon_symbol):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad)"/>
  <!-- Photo frame styling with date stamp -->
  <rect x="20" y="20" width="360" height="260" rx="12" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
  <rect x="35" y="35" width="330" height="180" rx="8" fill="{color}15" stroke="{color}40" stroke-width="1.5"/>
  
  <!-- Icon Center -->
  <circle cx="200" cy="110" r="42" fill="{color}25"/>
  <circle cx="200" cy="110" r="32" fill="{color}"/>
  <text x="200" y="118" font-family="'Segoe UI', sans-serif" font-size="24" fill="#FFFFFF" text-anchor="middle">{icon_symbol}</text>

  <!-- Camera overlay badge -->
  <rect x="45" y="45" width="110" height="24" rx="4" fill="#1E293B" opacity="0.8"/>
  <text x="100" y="61" font-family="sans-serif" font-size="10" font-weight="bold" fill="#FFFFFF" text-anchor="middle">📷 SITE EVIDENCE</text>

  <!-- Title & Subtitle -->
  <text x="40" y="240" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1E293B">{title}</text>
  <text x="40" y="260" font-family="sans-serif" font-size="11" fill="#64748B">{subtitle}</text>
  <rect x="290" y="235" width="75" height="22" rx="11" fill="{color}20"/>
  <text x="327" y="250" font-family="sans-serif" font-size="10" font-weight="bold" fill="{color}" text-anchor="middle">VERIFIED</text>
</svg>"""
    with open(os.path.join(UPLOADS_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(svg.strip())

create_complaint_sample("sample_water_leak.svg", "Water Pipeline Leakage", "Ward 2, Anjaneya Temple Circle", "#0284c7", "💧")
create_complaint_sample("sample_school_issue.svg", "Govt School Classroom Roof", "Ward 2, GHPS Primary School", "#8b5cf6", "🏫")
create_complaint_sample("sample_streetlight.svg", "Non-working Streetlights", "Ward 2, Basaveshwara Street", "#eab308", "💡")
create_complaint_sample("sample_garbage.svg", "Overflowing Garbage Dump", "Ward 3, Weekly Haat Road", "#16a34a", "🗑️")
create_complaint_sample("sample_potholes.svg", "Severe Road Potholes", "Ward 1, Kerekoppalu Link", "#ea580c", "🛣️")
create_complaint_sample("sample_drainage.svg", "Blocked Stormwater Drain", "Ward 4, Near Anganwadi", "#0d9488", "🚰")
create_complaint_sample("sample_clinic.svg", "Sub-Center Handpump Defect", "Ward 2, Village Health Clinic", "#ef4444", "🏥")

print("All vector assets and sample previews generated successfully.")
