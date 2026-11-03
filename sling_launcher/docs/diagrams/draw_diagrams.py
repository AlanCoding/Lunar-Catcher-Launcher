"""Generate review schematics as SVG; coordinates are page pixels, not a design.

Run with Python 3 from any directory. No physical calculations or dependencies.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent
INK, BLUE, RED, GREEN, GRAY = '#182c40', '#1967a3', '#c03932', '#287650', '#687887'


class Drawing:
    def __init__(self, title, subtitle):
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700" role="img">
<title>{escape(title)}</title><desc>{escape(subtitle)}</desc>
<defs><marker id="force" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="{RED}"/></marker>
<marker id="motion" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="{GREEN}"/></marker></defs>
<rect width="1200" height="700" fill="#fff"/>
<style>text{{font-family:DejaVu Sans,sans-serif;fill:{INK};font-size:18px}} .small{{font-size:15px}} .title{{font-size:27px;font-weight:bold}} .sub{{font-size:16px;fill:{GRAY}}}</style>''']
        self.text(35, 42, title, 'title')
        self.text(35, 73, subtitle, 'sub')
        self.line(35, 94, 1165, 94, '#dce3eb', 1)

    def text(self, x, y, s, cls='', anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>')

    def line(self, x1, y1, x2, y2, color=BLUE, width=3, dash='', arrow=None):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'
                          + (f' stroke-dasharray="{dash}"' if dash else '')
                          + (f' marker-end="url(#{arrow})"' if arrow else '') + '/>')

    def path(self, d, color=BLUE, width=3, dash='', arrow=None):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
                          + (f' stroke-dasharray="{dash}"' if dash else '')
                          + (f' marker-end="url(#{arrow})"' if arrow else '') + '/>')

    def circle(self, x, y, r=7, fill=BLUE, stroke=INK):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def box(self, x, y, w, h, label, fill='#eef4fa'):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{BLUE}" stroke-width="2"/>')
        self.text(x+w/2, y+h/2+6, label, anchor='middle')

    def force(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, RED, 3, arrow='force')

    def motion(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, GREEN, 2, '7 5', 'motion')

    def save(self, name, footer):
        self.text(35, 661, footer, 'small')
        self.text(35, 685, 'Blue: hardware / geometry    Red: applied forces    Green dashed: motion / acceleration    Not to scale', 'small')
        (OUT / name).write_text('\n'.join(self.parts) + '</svg>\n')


def main():
    d = Drawing('01  Whole machine · top view', 'Geometry G1–G3; ground-level pivot O is distinct from the overhead main tie B05.')
    d.circle(600, 365, 155, 'none', '#b5c2d0')
    d.line(445, 365, 755, 365, BLUE, 7)
    d.line(445, 376, 600, 376, GRAY, 2, '5 5')
    d.line(600, 386, 755, 386, GRAY, 2, '5 5')
    d.line(145, 365, 445, 365, BLUE, 3)
    d.line(755, 365, 1055, 365, BLUE, 3)
    for x in [445, 755]:
        d.circle(x, 365, 12)
    d.circle(600, 365, 6, '#fff')
    d.box(120, 342, 70, 46, 'rock', '#f5eee3')
    d.box(1010, 342, 100, 46, 'payload')
    d.circle(310, 365, 12, '#fff'); d.circle(890, 365, 12, '#fff')
    d.text(290, 416, 'B14 climber −'); d.text(850, 416, 'B14 climber +')
    d.text(425, 318, 'A−'); d.text(745, 318, 'A+')
    d.text(600, 288, 'B05 direct apex-to-apex tie', anchor='middle')
    d.text(600, 444, 'O / B12: below tie; no tie attachment here', 'small', 'middle')
    d.text(600, 470, 'B06 stabilizers shown offset and dashed for visibility', 'small', 'middle')
    d.text(170, 330, 'B04 outward sling −'); d.text(820, 330, 'B04 outward sling +')
    d.text(600, 550, 'Wheel paths: B08 drive wheels + B10 passive steering wheels', anchor='middle')
    d.motion(755, 350, 755, 215); d.text(785, 220, '+eₜ / vA = ωRₐ')
    d.motion(1055, 330, 1055, 180); d.text(930, 150, 'v tip ≠ wheel speed')
    d.motion(445, 395, 445, 510)
    d.path('M 705 250 A 155 155 0 0 0 535 225', GREEN, 2, '7 5', 'motion')
    d.text(575, 190, 'ω, α'); d.line(600, 355, 745, 355, GRAY, 1)
    d.text(640, 342, 'Rₐ', 'small')
    d.text(42, 590, 'At release, rotate the page geometry so +eₜ is east: useful payload east, rock west.', 'small')
    d.text(42, 615, 'Slings remain deployed; the two climbers move outward and return. Only one useful payload.', 'small')
    d.save('01_geometry.svg', 'Lag under acceleration is resolved in Figure 03; straight top-view slings here show the symmetric reference case.')

    d = Drawing('02  Radial plane · tie, stabilizers and sling droop', 'Assembly force balance R1; cable shape C1–C3. +eᵣ is right; +e_z is up.')
    d.line(55, 555, 1135, 555, GRAY, 2)
    d.text(60, 585, 'Prepared lunar surface: reference sketch; actual clearance uses terrain + curvature.', 'small')
    d.circle(125, 555, 9, GRAY); d.text(75, 610, 'O / B12–13')
    d.line(125, 555, 430, 260, GRAY, 3)
    d.text(165, 440, 'B06 stabilizer', 'small')
    d.path('M 55 280 Q 240 340 430 260', BLUE, 5)
    d.text(55, 210, 'B05 continues to opposite apex', 'small')
    d.text(55, 233, 'Main tie passes ABOVE pivot', 'small')
    d.line(430, 260, 430, 530, BLUE, 6); d.circle(430, 538, 17, '#fff')
    d.text(453, 465, 'B01–03 assembly', 'small')
    d.path('M 430 260 C 620 300 810 410 1070 420', BLUE, 4)
    d.circle(1070, 420, 13); d.text(945, 465, 'B14 + B23 load', 'small')
    d.text(760, 305, 'B04 sling: shape is an output')
    d.force(430, 260, 300, 285); d.text(285, 320, 'Fᴅ', 'small')
    d.force(430, 260, 575, 300); d.text(560, 250, 'Fˢ', 'small')
    d.force(423, 272, 355, 340); d.text(285, 373, 'Fᵇ', 'small')
    d.force(445, 425, 445, 505); d.text(465, 512, 'Mg', 'small')
    d.force(430, 552, 430, 485); d.text(345, 510, 'ΣNᵢ', 'small')
    d.force(430, 550, 520, 550); d.text(525, 546, 'ΣYᵢ (signed)', 'small')
    d.motion(450, 165, 335, 165); d.text(470, 170, 'aᵣ = −ω²Rₐ', 'small')
    d.line(1135, 260, 1135, 420, GRAY, 1, '4 4'); d.text(1100, 350, 'δ', '', 'middle')
    d.line(1100, 420, 1100, 555, GRAY, 1, '4 4'); d.text(915, 520, 'minimum gap ≥ 3 m', 'small')
    d.save('02_radial_droop.svg', 'Wheelbase extends out of this radial section. Main tie and stabilizer endpoint forces follow their local cable tangents.')

    d = Drawing('03  Tangential plane · A-frame and drive forces', 'Assembly force and moment balance T1–T2. +eₜ / travel is right; +e_z is up.')
    d.line(75, 555, 1115, 555, GRAY, 2)
    d.line(600, 250, 600, 525, BLUE, 8)
    d.line(600, 250, 320, 525, BLUE, 8)
    d.line(320, 470, 600, 470, BLUE, 3)
    d.circle(320, 530, 25, '#fff'); d.circle(600, 530, 25, '#fff')
    d.box(555, 200, 90, 50, 'B03/11')
    d.text(620, 395, 'B01 leading leg'); d.text(205, 345, 'B01 trailing leg')
    d.text(345, 450, 'B02 bracing / mounts', 'small')
    d.force(600, 250, 450, 250); d.text(340, 220, 'Fᴬₜ from sling / tie / stays')
    d.force(320, 555, 320, 445); d.text(255, 430, 'N trailing')
    d.force(600, 555, 600, 445); d.text(640, 455, 'N leading')
    d.force(335, 550, 430, 550); d.text(345, 585, 'X trailing', 'small')
    d.force(615, 550, 710, 550); d.text(630, 585, 'X leading', 'small')
    d.force(470, 390, 470, 480); d.text(490, 410, 'Mg at C', 'small')
    d.circle(470, 390, 5, GRAY)
    d.motion(770, 190, 925, 190); d.text(785, 165, 'aₜ = αRₐ', 'small')
    d.text(795, 280, 'B08 wheels + B09 motors')
    d.text(795, 315, 'B20 retention + B21 ballast')
    d.text(795, 350, 'B10 steer wheels omitted here;')
    d.text(795, 375, 'fore/aft placement: Figure 04.', 'small')
    d.text(795, 440, 'Rolling resistance opposes travel.', 'small')
    d.text(795, 465, 'Reactions are solved, not prescribed.', 'small')
    d.text(795, 490, 'No negative wheel normal force.', 'small')
    d.save('03_tangential.svg', 'Sling lag during acceleration creates tangential apex force. Leg forces can include axial load, shear and bending.')

    d = Drawing('04  Wheels of ONE A-frame · plan view', 'Per frame: 2 powered + 2 passive wheels. Two frames total: 4 powered + 4 passive wheels.')
    d.text(65, 145, 'One frame = one A structure = two poles = four wheels')
    d.motion(425, 190, 650, 190); d.text(430, 170, '+eₜ / direction of travel', 'small')
    d.path('M 65 290 Q 365 275 690 290', GRAY, 2, '5 5')
    d.box(80, 267, 115, 46, 'powered T')
    d.box(235, 274, 95, 32, 'passive T')
    d.box(410, 267, 115, 46, 'powered L')
    d.box(565, 274, 95, 32, 'passive L')
    d.line(195, 290, 235, 290, BLUE, 3); d.line(525, 290, 565, 290, BLUE, 3)
    d.text(110, 245, 'trailing pole / leg', 'small')
    d.text(440, 245, 'leading pole / leg', 'small')
    d.line(138, 315, 138, 360, BLUE, 3); d.line(468, 315, 468, 360, BLUE, 3)
    d.line(138, 360, 468, 360, BLUE, 3)
    d.text(225, 390, 'B02 mounts / frame connection', 'small')
    d.text(65, 445, 'B08: powered wheels. B10: smaller passive steering wheels.', 'small')
    d.text(65, 480, 'Each passive wheel is ahead of its powered wheel, not beside it.', 'small')
    d.text(65, 505, 'Ahead is illustrative; fore/aft choice is not optimized here.', 'small')
    d.text(65, 540, 'Detailed passive-wheel traction/load sharing is outside this model.', 'small')
    d.text(65, 575, 'Circular path locally flattened; spacing is not dimensioned.', 'small')
    d.line(740, 125, 740, 590, '#dce3eb', 1)
    d.text(795, 145, 'ONE powered wheel/contact i')
    d.circle(940, 360, 65, '#eef4fa')
    d.line(800, 425, 1125, 425, GRAY, 2)
    d.force(940, 425, 940, 295); d.text(960, 290, 'Nᵢ')
    d.force(940, 425, 1090, 425); d.text(1060, 460, 'Xᵢ')
    d.force(940, 425, 850, 500); d.text(790, 520, 'Yᵢ (out of section)')
    d.path('M 985 325 A 50 50 0 0 1 975 395', RED, 3, arrow='force')
    d.text(1035, 355, 'τᵢ', 'small')
    d.text(795, 560, 'Hub forces act at axle (omitted here);', 'small')
    d.text(795, 585, 'wheel spin balance includes inertia/losses.', 'small')
    d.save('04_contacts.svg', 'T / L identify the trailing / leading POLES, not wheel propulsion. Right inset: powered-wheel force convention only.')

    d = Drawing('05  Cable element, climber and apex interfaces', 'Cable equation C1, climber equation C4 and spool equation A1. Three separate free bodies.')
    d.text(60, 145, 'Cable element ds: outward tangent t̂ →')
    d.line(160, 270, 330, 310, BLUE, 8)
    d.force(160, 270, 70, 248); d.text(55, 220, '−T t̂ at s', 'small')
    d.force(330, 310, 445, 338); d.text(300, 380, '+T t̂ at s+ds', 'small')
    d.force(245, 290, 245, 405); d.text(75, 435, 'λ ds g downward; acceleration a(s)', 'small')
    d.text(65, 490, 'Distributed gravity + rotation + elasticity', 'small')
    d.text(65, 515, 'determine tension, taper and sag.', 'small')
    d.line(475, 120, 475, 590, '#dce3eb', 1)
    d.text(510, 145, 'B14 climber + attached load')
    d.line(515, 270, 760, 320, BLUE, 4)
    d.box(585, 255, 100, 70, 'm moving')
    d.force(635, 290, 735, 310); d.text(680, 350, 'F contact', 'small')
    d.force(635, 325, 635, 440); d.text(655, 435, 'mg', 'small')
    d.motion(570, 215, 700, 240); d.text(530, 190, 'out / back on same sling', 'small')
    d.text(510, 490, 'Equal/opposite force enters cable.', 'small')
    d.text(510, 515, 'No free outward-motion energy credit.', 'small')
    d.line(795, 120, 795, 590, '#dce3eb', 1)
    d.text(830, 145, 'B03 apex / B11 spool')
    d.circle(975, 300, 48, '#eef4fa')
    d.line(975, 252, 1110, 252, BLUE, 4)
    d.force(1000, 252, 1125, 252); d.text(1050, 220, 'T side', 'small')
    d.force(960, 310, 855, 345); d.text(825, 380, 'bearing reaction', 'small')
    d.path('M 1000 340 A 45 45 0 0 1 935 315', RED, 3, arrow='force')
    d.text(960, 410, 'τ hold / drive', 'small')
    d.text(825, 490, 'Routing decides net drum torque.', 'small')
    d.text(825, 515, 'Main tie attaches to apex structure.', 'small')
    d.save('05_interfaces.svg', 'Apex also receives main-tie and stabilizer forces (Figure 02). Cable/climber contact forces are internal to their combined body.')

    d = Drawing('06  Whole-system balance and permanent support equipment', 'System equations S1–S3 and power condition P1. Power arrows are energy flow, not force arrows.')
    d.box(70, 185, 220, 80, 'B16 solar + supports')
    d.box(380, 185, 250, 80, 'B17 conversion / control')
    d.box(750, 165, 365, 120, 'B09 drives + B14 climbers')
    d.line(290, 225, 380, 225, GREEN, 3, arrow='motion')
    d.line(630, 225, 750, 225, GREEN, 3, arrow='motion')
    d.text(70, 150, 'Sunlight → instantaneous electrical supply; no storage')
    d.box(70, 340, 290, 70, 'B18 sensing / communications')
    d.box(415, 340, 290, 70, 'B19 thermal / dust protection')
    d.box(760, 340, 355, 70, 'B07 / B15 cable interfaces')
    d.text(70, 460, 'Moving system boundary: frames + all tethers + wheels + climbers + attached loads')
    d.text(70, 500, 'External forces: gravity, wheel/ground reactions, ground-pivot stabilizer reactions.')
    d.text(70, 535, 'B05 main tie forces cancel internally for the COMPLETE moving system.')
    d.text(70, 570, 'At release: remove B23 useful payload and B22 rock with their momentum and energy.')
    d.text(70, 610, 'B20 ballast retention is imported; B21 local ballast still contributes inertia and wheel loads.', 'small')
    d.save('06_system.svg', 'Power transfer topology is intentionally unspecified; permanent power equipment, losses and mass remain in the accounting.')


if __name__ == '__main__':
    main()
