"""Generates architecture.png: campus telecom, security and mass notification design.

Run from this folder:  .venv/bin/python architecture.py
Requires: Graphviz + librsvg (brew install graphviz) and the `diagrams` Python package.

Labels are deliberately generic (no client, site, building or room numbers).
"""
import subprocess
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom

HERE = Path(__file__).parent
ICONS = HERE / "icons"
OUTPUT = HERE / "architecture"  # diagrams adds the .png extension

# One colour per domain, same idea as the AWS icon families.
NET, SEC, NOTIFY, SUPPORT, OWNER, PLANT = "#8C4FFF", "#DD344C", "#E7157B", "#7AA116", "#5A6B7B", "#ED7100"

# name -> (tile colour, white line glyph on a 64x64 grid)
GLYPHS = {
    "switch": (NET, '<rect x="9" y="22" width="46" height="20" rx="3"/><path d="M16 32h4M24 32h4M32 32h4M40 32h4"/><circle cx="49" cy="32" r="1.5" fill="#fff"/>'),
    "rack": (NET, '<rect x="17" y="8" width="30" height="48" rx="2"/><path d="M17 20h30M17 32h30M17 44h30M23 14h6M23 26h6M23 38h6M23 50h6"/>'),
    "cabinet": (NET, '<rect x="17" y="8" width="30" height="48" rx="2"/><path d="M17 22h30M23 15h6M32 30v20M23.3 35l17.4 10M23.3 45l17.4-10"/>'),
    "wap": (NET, '<circle cx="32" cy="46" r="3" fill="#fff"/><path d="M22 38a14 14 0 0 1 20 0M15 31a24 24 0 0 1 34 0M8 24a34 34 0 0 1 48 0"/>'),
    "drop": (NET, '<rect x="12" y="12" width="40" height="40" rx="4"/><path d="M22 24h20v14h-5v5H27v-5h-5z"/>'),
    "dmarc": (NET, '<path d="M12 24h36M40 16l8 8-8 8M52 40H16M24 32l-8 8 8 8"/>'),
    "core": (OWNER, '<circle cx="32" cy="32" r="22"/><path d="M32 16v32M16 32h32M27 21l5-5 5 5M27 43l5 5 5-5M21 27l-5 5 5 5M43 27l5 5-5 5"/>'),
    "server": (OWNER, '<rect x="12" y="12" width="40" height="16" rx="3"/><rect x="12" y="36" width="40" height="16" rx="3"/><path d="M28 20h16M28 44h16"/><circle cx="20" cy="20" r="1.5" fill="#fff"/><circle cx="20" cy="44" r="1.5" fill="#fff"/>'),
    "oldswitch": (OWNER, '<rect x="9" y="22" width="46" height="20" rx="3"/><path d="M16 32h4M24 32h4M32 32h4M40 32h4"/><circle cx="49" cy="32" r="1.5" fill="#fff"/>'),
    "camera": (SEC, '<path d="M10 22h44M24 12h16v10M16 22a16 16 0 0 0 32 0"/><circle cx="32" cy="29" r="5"/>'),
    "reader": (SEC, '<rect x="20" y="8" width="24" height="48" rx="4"/><path d="M27 17h10"/><g fill="#fff" stroke="none"><circle cx="26" cy="29" r="2"/><circle cx="32" cy="29" r="2"/><circle cx="38" cy="29" r="2"/><circle cx="26" cy="37" r="2"/><circle cx="32" cy="37" r="2"/><circle cx="38" cy="37" r="2"/><circle cx="26" cy="45" r="2"/><circle cx="32" cy="45" r="2"/><circle cx="38" cy="45" r="2"/></g>'),
    "key": (SEC, '<circle cx="20" cy="32" r="10"/><path d="M30 32h26M46 32v9M54 32v6"/>'),
    "shield": (SEC, '<path d="M32 8l20 7v15c0 13-9 21-20 26-11-5-20-13-20-26V15z"/><path d="M23 31l7 7 12-13"/>'),
    "beacon": (NOTIFY, '<path d="M22 44V32a10 10 0 0 1 20 0v12zM16 44h32v8H16zM32 8v8M12 16l6 6M52 16l-6 6"/>'),
    "ipava": (NOTIFY, '<rect x="8" y="18" width="48" height="28" rx="3"/><path d="M14 32h7l3-8 5 16 4-11 2 3h15"/>'),
    "amp": (NOTIFY, '<path d="M18 12v40l34-20zM6 32h12M52 32h8"/>'),
    "speaker": (NOTIFY, '<path d="M10 26h10l14-12v36L20 38H10zM42 24a12 12 0 0 1 0 16M48 18a20 20 0 0 1 0 28"/>'),
    "ups": (SUPPORT, '<rect x="8" y="20" width="42" height="24" rx="3"/><path d="M50 27h5v10h-5M31 23l-8 10h7l-3 9 10-12h-7z"/>'),
    "plant": (PLANT, '<path d="M10 52V28l14 8v-8l14 8V14h12v38z"/>'),
    "hazard": (PLANT, '<path d="M32 6l22 13v26L32 58 10 45V19z"/><text x="32" y="39" font-family="Helvetica" font-size="19" font-weight="bold" text-anchor="middle" fill="#fff" stroke="none">Ex</text>'),
}


def build_icons():
    ICONS.mkdir(exist_ok=True)
    for name, (colour, glyph) in GLYPHS.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            f'<rect width="64" height="64" rx="8" fill="{colour}"/>'
            '<g fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
            f"{glyph}</g></svg>"
        )
        subprocess.run(
            ["rsvg-convert", "-w", "256", "-o", str(ICONS / f"{name}.png")],
            input=svg.encode(), check=True,
        )


def group(label, **attrs):
    return Cluster(label, graph_attr={"fontsize": "17", **attrs})


def node(icon, label):
    return Custom(label, str(ICONS / f"{icon}.png"))


# Edge styles: one colour per flow so each story is easy to follow.
DATA = {"fontsize": "16", "color": "#232F3E", "penwidth": "2"}
FIBER = {"fontsize": "16", "color": "#232F3E", "penwidth": "4"}
EXISTING = {"fontsize": "16", "color": "#7D8998", "penwidth": "2"}
SECURITY = {"fontsize": "16", "color": "#1F6FEB", "style": "dashed", "penwidth": "1.5"}
ALERT = {"fontsize": "16", "color": "#E7157B", "style": "dashed", "penwidth": "1.5"}
POWER = {"fontsize": "16", "color": "#7AA116", "style": "dotted", "penwidth": "1.5"}

graph_attr = {
    "fontsize": "22",
    "pad": "0.5",
    "nodesep": "0.45",
    "ranksep": "1.1",
    "splines": "spline",
    "compound": "true",
    "labelloc": "t",
}

TITLE = (
    "Defense Manufacturing Campus - Telecom, Security and Mass Notification Architecture\n"
    "thick = fiber backbone   solid = structured cabling   blue dashed = security   "
    "pink dashed = mass notification   green dotted = power   grey = existing / owner-operated"
)

build_icons()

with Diagram(TITLE, filename=str(OUTPUT), outformat="png", show=False, direction="LR", graph_attr=graph_attr,
             node_attr={"fontsize": "15"}):
    with group("Admin Building (new construction, 11,000 sf)"):
        with group("Work areas"):
            drops = node("drop", "CAT6A drops\noffices, conference\nheadwall + floor trench")
            waps = node("wap", "Wireless APs x3\nPoE, ceiling drops")

        with group("Physical security"):
            cams = node("camera", "Multisensor cameras x2\nopposite corners,\n270 deg each")
            readers = node("reader", "Card + keypad readers\nelectric strikes,\nfail-secure")
            acp = node("key", "Access control\npanel")
            ids = node("shield", "Intrusion panel\nhardwired PIR zones,\nno wireless")

        with group("Mass notification + PA"):
            beacons = node("beacon", "Alert beacons x5")
            ipava = node("ipava", "IP-to-audio\npaging interface")
            amp = node("amp", "PA amplifier")
            speakers = node("speaker", "Speakers\nanalog, daisy-chained,\n+20 dB over ambient")

        with group("Telecom room - 5 x 4-in entrance conduits (2 active, 2 spare, 1 carrier)"):
            patch = node("rack", "3 racks\npatch panels,\nladder tray, ground bar")
            switch = node("switch", "PoE access switch\n(owner furnished)")
            ups = node("ups", "UPS\ndouble conversion,\n60 min runtime")
            dmarc = node("dmarc", "Carrier DMARC")

    with group("Fire Station (existing)"):
        fs = node("oldswitch", "Existing\nfiber switch")

    with group("Manufacturing Building (existing, renovation)", labeljust="r", labelloc="b"):  # title clear of the incoming fiber
        m_drops = node("plant", "New CAT6A drops +\nprocess equipment tie-ins\n(presses, sealers)")
        m_haz = node("hazard", "Hazardous test cell\nexplosion-proof devices,\nstainless conduit")
        m_cams = node("camera", "Existing cameras\n(remain)")
        m_tr = node("rack", "3 existing telecom rooms\nnew racks + patch panels,\ngrounding busbars")

    with group("Magazine D (new fit-out)"):
        d_dev = node("camera", "Camera, keypad reader,\nintrusion, beacon,\npaging interface + PA")
        d_cab = node("cabinet", "12U wall cabinet\nself-cooled,\n6-8 drops")

    with group("Magazine C (new fit-out)"):
        c_dev = node("camera", "Camera, keypad reader,\nintrusion, beacon,\npaging interface + PA")
        c_cab = node("cabinet", "12U wall cabinet\nself-cooled,\n6-8 drops")

    with group("Owner-operated head-end (existing, on-prem, no cloud services)"):
        core = node("core", "Campus core\nnetwork")
        alertus = node("server", "Mass notification\nserver")
        acs = node("server", "Access control\nserver")
        vms = node("server", "Video management\n(IP / NVR)")
        mon = node("server", "Intrusion\nmonitoring")

    # 1-4: data path, device to core
    drops >> Edge(label="1. CAT6A horizontal", **DATA) >> patch
    waps >> Edge(**DATA) >> patch
    cams >> Edge(label="PoE", **DATA) >> patch
    acp >> Edge(**DATA) >> patch
    ids >> Edge(**DATA) >> patch
    patch >> Edge(label="2. patch", **DATA) >> switch
    dmarc >> Edge(label="carrier handoff", **DATA) >> switch
    ups >> Edge(label="power", **POWER) >> switch
    switch >> Edge(label="3. 48-strand OS2 single-mode\n3,200 LF new duct bank,\n7 handholes, no splices", **FIBER) >> fs
    fs >> Edge(label="4. existing\ncampus fiber", **EXISTING) >> core

    d_dev >> Edge(**DATA) >> d_cab
    c_dev >> Edge(**DATA) >> c_cab
    d_cab >> Edge(label="12-strand OS2", constraint="false", **FIBER) >> c_cab
    c_cab >> Edge(label="24-strand OS2\n(existing conduit)", **FIBER) >> m_tr
    m_drops >> Edge(**DATA) >> m_tr
    m_haz >> Edge(**DATA) >> m_tr
    m_cams >> Edge(**EXISTING) >> m_tr
    m_tr >> Edge(label="existing\nuplink", **EXISTING) >> core

    # i-iii: security, edge to head-end
    readers >> Edge(label="door wiring", **SECURITY) >> acp
    core >> Edge(label="i. badge events", **SECURITY) >> acs
    core >> Edge(label="ii. video streams", **SECURITY) >> vms
    core >> Edge(label="iii. alarms", **SECURITY) >> mon

    # A-D: mass notification, head-end to every building
    core << Edge(label="A. alert", **ALERT) << alertus
    switch >> Edge(label="B. PoE drop", **ALERT) >> beacons
    switch >> Edge(label="B. HTTPS 8443\nover PoE drop", **ALERT) >> ipava
    ipava >> Edge(label="C. line-level audio", **ALERT) >> amp
    amp >> Edge(label="D. page", **ALERT) >> speakers
