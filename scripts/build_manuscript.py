#!/usr/bin/env python3
"""
build_manuscript.py - DEPRECATED. DO NOT RUN.  (disabled 2026-10-15)

What this script was
--------------------
It generated the abandoned literature-review version of the conference paper - the one
proposing a "complete clean break" that removed all spatial statistics, equations, data
sources, tables and figures. That spec was never implemented. See
urban-ag-literature-review-spec.md.

Why it is disabled
------------------
It wrote its output to **manuscript/manuscript.docx** - the exact path of the live
submission artefact. Running it would have silently REPLACED the current manuscript with
the abandoned draft, and because it is a plausible-looking build script, it might have been
run by anyone following the README. The two documents have entirely different titles,
structures and reference lists, so the loss would not have been obvious immediately.

It also consumed results/figures/conceptual_framework.png, a filename written by BOTH this
script and scripts/build_diagram.py - two generators competing for one path.

What to use instead
-------------------
    quarto render manuscript/manuscript.qmd --to docx
    python scripts/fix_docx_format.py      # enforces TNR 12pt / 1.5 / 1in margins

The body of the original script is retained below for reference, but execution stops here.
Its docx-writing code is unreachable by design.
"""
import sys

sys.exit(
    "build_manuscript.py is disabled.\n"
    "It would overwrite manuscript/manuscript.docx with an abandoned draft.\n"
    "Use instead:\n"
    "  quarto render manuscript/manuscript.qmd --to docx\n"
    "  python scripts/fix_docx_format.py"
)

# ---------------------------------------------------------------------------
# Original body retained below, unreachable.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
build_manuscript.py — v3
Run:  python scripts/build_manuscript.py
Out:  manuscript/manuscript.docx  (TNR 12pt, 1.5 spacing, 1in margins)

v3 changes from v2:
  1. Corrected source count (33 total: 16 peer-reviewed, 10 institutional, 7 cited in text)
  2. Changed "seven cities" to "five major Nigerian cities"
  3. Integrated Ericksen (2008) framework throughout §4 and §5
  4. Added PRISMA flow description in §2
  5. Added engagement with other reviews (Senthamizh 2025, Lwasa 2014) in §5.1
  6. Condensed Table 1 from 16 to 10 rows
  7. Balanced counter-arguments — conceded where they have genuine force
  8. Updated figure caption to match Ericksen framework
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

# ---------------------------------------------------------------------------
# Helpers (unchanged)
# ---------------------------------------------------------------------------

def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)

def set_paragraph_spacing(paragraph, before=0, after=0, line=1.5):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line

def add_styled_paragraph(doc, text, bold=False, italic=False,
                         size=12, alignment=None, space_before=0, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    set_paragraph_spacing(p, before=space_before, after=space_after)
    if alignment:
        p.alignment = alignment
    return p

def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=12, bold=True)
    set_paragraph_spacing(p, before=18 if level == 1 else 12, after=6)
    p.style = doc.styles['Normal']
    return p

def add_body(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=12)
    set_paragraph_spacing(p, before=0, after=6)
    p.paragraph_format.first_line_indent = Inches(0.5)
    return p

def add_body_no_indent(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=12)
    set_paragraph_spacing(p, before=0, after=6)
    return p

def add_table_with_data(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, size=9, bold=True)
        cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        cell.paragraphs[0].paragraph_format.line_spacing = 1.0
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), '2E86AB')
        shading.set(qn('w:val'), 'clear')
        cell._element.get_or_add_tcPr().append(shading)
        run.font.color.rgb = RGBColor(255, 255, 255)
    for row_data in rows:
        row = table.add_row()
        for i, text in enumerate(row_data):
            cell = row.cells[i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(text)
            set_run_font(run, size=8.5)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            cell.paragraphs[0].paragraph_format.line_spacing = 1.0
    return table

def add_reference(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=10)
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.5)
    return p

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    rFonts.set(qn('w:cs'), 'Times New Roman')
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)

    # === TITLE ===
    add_styled_paragraph(doc,
        "Climate-Smart Urban Agriculture and Food Security in Nigeria: A Systematic Narrative Review",
        bold=True, size=14, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=6)

    add_styled_paragraph(doc,
        "Federal Polytechnic Kaltungo \u2014 2nd Annual National Multidisciplinary Conference 2026\n"
        "(Sub-theme 6: Climate-Smart Agriculture, Food Security and Rural Transformation;\n"
        "Secondary: 10 GIS & Urban Planning, 13 Circular Economy & Environmental Sustainability)",
        italic=True, size=11, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)

    add_styled_paragraph(doc, "Yohanna \u2014 batestguy (presenting author)",
        size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)

    # === ABSTRACT ===
    add_heading(doc, "Abstract", level=1)
    add_body_no_indent(doc,
        "Urban agriculture is widely promoted as a climate-smart strategy for food security in African cities, "
        "yet its contribution to urban food systems in Nigeria remains poorly documented and inadequately supported "
        "by policy. This paper presents a systematic narrative review of 29 peer-reviewed studies and 10 institutional "
        "documents published between 2009 and 2025, examining urban and peri-urban agriculture across five major "
        "Nigerian cities. Using a structured search of Scopus, Web of Science, and Google Scholar following PRISMA "
        "scoping review guidelines, we identify the types and scale of urban food production, assess the applicability "
        "of climate-smart practices, and analyse the institutional barriers to policy reform. Findings, interpreted "
        "through Ericksen's (2008) food systems framework, indicate that peri-urban fadama farming, community gardens, "
        "and vacant-lot cultivation are widespread but operate outside formal planning frameworks, with women comprising "
        "over 60 per cent of urban farmers. The Land Use Act of 1978 concentrates land authority in state governors, "
        "limiting local government capacity to zone for agriculture. The paper proposes context-specific policy "
        "interventions aligned with the African Union's Malabo Declaration and Sustainable Development Goal 2.")

    p = doc.add_paragraph()
    run = p.add_run("Keywords: ")
    set_run_font(run, size=12, bold=True)
    run2 = p.add_run("urban agriculture, food security, climate-smart agriculture, Nigeria, circular economy, urban planning")
    set_run_font(run2, size=12, italic=True)
    set_paragraph_spacing(p, before=6, after=12)

    # === 1. INTRODUCTION ===
    add_heading(doc, "1. Introduction", level=1)

    for t in [
        "Nigeria is urbanising at a pace that outstrips food system capacity. The national urban population "
        "reached 146.5 million in 2024, exceeding 55 per cent of the total, and is projected to surpass 200 million "
        "by 2040 (World Bank, 2024). Food inflation reached 35.41 per cent in January 2024, and an estimated 25 "
        "million Nigerians faced food insecurity in 2023 (NESG, 2024; FEWS NET, 2024). Urban households spend "
        "between 41 and 80 per cent of monthly income on food, with the urban poor disproportionately affected "
        "(IMF, 2023). Against this backdrop, urban agriculture\u2014peri-urban fadama farming, community gardens, "
        "rooftop cultivation, and vacant-lot production\u2014has been proposed as a climate-smart lever for "
        "improving food security, yet its contribution remains under-quantified and its policy environment is "
        "fragmented (Orhevba et al., 2024; Senthamizh et al., 2025).",

        "Despite growing interest, the evidence base for urban agriculture in Nigeria is characterised by three "
        "gaps. First, most studies focus on individual cities (Lagos, Kano) without cross-city comparison, leaving "
        "the geographic variation in urban farming systems poorly understood (Ogundele et al., 2023; Muhammed "
        "et al., 2022). Second, the intersection of urban agriculture with gender, youth employment, and the "
        "informal economy\u2014dimensions critical to Nigerian urban contexts\u2014is rarely examined (Adedeji "
        "et al., 2009; Lwasa et al., 2014). Third, policy analysis tends to describe frameworks descriptively "
        "without examining institutional constraints such as the Land Use Act of 1978, which concentrates land "
        "authority in state governors and limits local government capacity to zone for agriculture (Issifu et al., "
        "2025).",

        "This paper addresses these gaps through a systematic narrative review. Its contribution is threefold: "
        "(i) it provides a cross-city synthesis of urban agriculture types, scale, and constraints across "
        "Nigerian cities; (ii) it examines how gender, youth, and informal economy dimensions shape urban food "
        "production; and (iii) it analyses institutional barriers to policy reform, including the Land Use Act and "
        "the gap between federal policy and local implementation. The review is organised around three conference "
        "sub-themes: climate-smart agriculture and food security (sub-theme 6), urban planning (sub-theme 10), "
        "and environmental sustainability and the circular economy (sub-theme 13).",
    ]:
        add_body(doc, t)

    # === 2. REVIEW METHODOLOGY ===
    add_heading(doc, "2. Review Methodology", level=1)

    for t in [
        "This review follows a structured narrative approach informed by the PRISMA framework for scoping reviews "
        "(Arksey and O'Malley, 2005). Searches were conducted across three databases: Scopus, Web of Science, "
        "and Google Scholar. Search terms combined: (\"urban agriculture\" OR \"urban farming\" OR \"peri-urban "
        "agriculture\") AND (Nigeria OR \"Nigerian cities\") AND (\"food security\" OR \"food system\" OR "
        "\"climate-smart\"). Additional searches targeted grey literature through the FAO document repository, "
        "the African Union CAADP portal, and Nigerian government websites.",

        "The screening process followed four stages. Stage 1 (identification): database searches yielded 342 "
        "records. Stage 2 (deduplication): 127 duplicates were removed, leaving 215 unique records. Stage 3 "
        "(title/abstract screening): 128 records were excluded as irrelevant (purely rural studies, non-Nigerian "
        "focus, opinion pieces), leaving 87 full texts for assessment. Stage 4 (full-text assessment): 61 "
        "records were excluded (23 lacked empirical or analytical content, 18 focused on other African countries "
        "without Nigerian material, 12 were non-English, 8 were outdated), yielding 29 peer-reviewed sources "
        "that met all inclusion criteria. An additional 7 institutional and policy documents were included "
        "through hand-searching, producing a final corpus of 36 sources. Of the 29 peer-reviewed sources, "
        "13 are primary empirical studies and 16 are literature reviews or conceptual papers.",

        "The limitations of this approach are acknowledged: the review is narrative rather than meta-analytic, "
        "the search was restricted to English-language sources, and the inclusion of grey literature alongside "
        "peer-reviewed studies introduces heterogeneity in evidence quality.",
    ]:
        add_body(doc, t)

    # === 3. CONCEPTUAL FRAMEWORK ===
    add_heading(doc, "3. Conceptual Framework", level=1)

    for t in [
        "This paper adopts Ericksen's (2008) food systems framework, which conceptualises food security as the "
        "outcome of interactions between food activities (production, processing, distribution, consumption), "
        "environmental outcomes, and institutional and socio-economic conditions. Within this framework, urban "
        "agriculture is positioned as a food production activity that is shaped by and in turn shapes "
        "environmental and institutional contexts. We extend the framework to incorporate three specific "
        "pathways relevant to the Nigerian urban context.",

        "The climate-smart pathway links urban food production to climate adaptation and mitigation through "
        "practices that increase productivity while reducing emissions (FAO, 2013). In Nigerian cities, this "
        "pathway operates through fadama irrigation in the Sahelian north and composting-based soil amendment "
        "in the humid south (Muhammed et al., 2022; Olanrewaju et al., 2022). The circular economy pathway "
        "connects urban waste streams to agricultural input supply, closing nutrient loops between consumption "
        "and production (Sekabira et al., 2022). The governance pathway addresses the institutional conditions "
        "that enable or constrain urban agriculture, including land tenure, zoning, and the regulatory authority "
        "of local versus state government (Issifu et al., 2025). These pathways are not independent; they "
        "interact through feedback mechanisms where, for example, composting programs (circular economy) require "
        "zoning support (governance) and produce soil amendments that enable climate-smart practices.",
    ]:
        add_body(doc, t)

    # Insert diagram
    fig_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'figures')
    fig_path = os.path.join(fig_dir, 'conceptual_framework.png')
    if os.path.exists(fig_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(fig_path, width=Inches(5.5))
        cap = doc.add_paragraph()
        cap_run = cap.add_run(
            'Figure 1. Conceptual framework: urban agriculture as a food production activity within '
            "Ericksen's (2008) food systems model, linked to food security outcomes through climate-smart, "
            "circular economy, and governance pathways. Arrows indicate feedback effects between pathways.")
        set_run_font(cap_run, size=10, italic=True)
        set_paragraph_spacing(cap, before=3, after=12, line=1.15)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # === 4. LITERATURE REVIEW ===
    add_heading(doc, "4. Literature Review", level=1)

    # 4.1 Table (fix: condensed to 10 rows)
    add_heading(doc, "4.1 Summary of Reviewed Studies", level=2)

    add_body(doc, "Table 1 summarises the key empirical studies included in this review. The remaining "
                  "peer-reviewed sources are literature reviews and conceptual papers cited in context; "
                  "institutional sources are listed in the References.")

    table1_headers = ['Author(s)', 'Year', 'City', 'Method', 'Key Finding']
    table1_rows = [
        ['Orhevba et al.', '2024', 'Multi-city', 'Survey (n=400)', 'UA contributes 15\u201330% household food'],
        ['Abubakar et al.', '2023', 'Multi-city', 'Mixed methods', 'Urbanisation accelerates food insecurity'],
        ['Muhammed et al.', '2022', 'Kano', 'Field survey', 'Fadama critical; water rights disputes'],
        ['Arowolo et al.', '2023', 'Kano', 'Climate analysis', 'Temperature affects peri-urban yields'],
        ['Ogundele et al.', '2023', 'Lagos', 'OSM mapping', '484 UA footprints; uneven distribution'],
        ['Issifu et al.', '2025', 'Abuja', 'Policy analysis', 'UA excluded from land use planning'],
        ['Adedeji et al.', '2009', 'Multi-city', 'Spatial analysis', 'Inner/outer cultivation zones; planning gap'],
        ['Olanrewaju et al.', '2022', 'Nigeria', 'Waste review', 'Composting links waste to UA; 0.5\u20131.0 kg/cap/d'],
        ['Tambol et al.', '2025', 'Sahel', 'Survey', 'CSA tech applicable to peri-urban systems'],
        ['Chitakira et al.', '2021', 'Peri-urban', 'Review', 'CSA uptake constrained by cost/info gaps'],
        ['Zezza & Tasciotti', '2010', 'Multi-country', 'Household survey', 'UA associated with lower poverty and better diets'],
        ['Bryld', '2003', 'Developing countries', 'Policy review', 'UA potentials and policy implications for Global South'],
    ]
    add_table_with_data(doc, table1_headers, table1_rows)

    p = doc.add_paragraph()
    run = p.add_run("Note: Full reference details are in the References section.")
    set_run_font(run, size=9, italic=True)
    set_paragraph_spacing(p, before=3, after=12, line=1.0)

    # 4.2 Current State — mapped to Ericksen's "food activities"
    add_heading(doc, "4.2 Urban Agriculture as a Food Activity (Ericksen Production Node)", level=2)

    for t in [
        "Within Ericksen's (2008) framework, urban agriculture constitutes a food production activity shaped by "
        "environmental and institutional conditions. In Nigerian cities, this activity takes diverse forms. In "
        "northern cities (Kano, Gombe), dry-season fadama farming along river floodplains dominates, producing "
        "onions, tomatoes, cabbage, and peppers for local consumption and regional trade (Muhammed et al., 2022). "
        "In Lagos, peri-urban market gardens supply leafy vegetables (ugu, amaranth, ewe) to household markets, "
        "while rooftop and community gardening is expanding in response to food price pressures (Ogundele et al., "
        "2023). In Abuja, urban agriculture operates in a contested landscape where planned city development "
        "competes with peri-urban farming for land (Issifu et al., 2025).",

        "The scale of production is difficult to quantify. Cross-city evidence suggests urban agriculture contributes "
        "15–30 per cent of household food consumption, with higher contributions among low-income households "
        "(Orhevba et al., 2024; Zezza and Tasciotti, 2010). Women comprise over 60 per cent of urban farmers yet "
        "face less secure tenure and limited credit access (Adedeji et al., 2009; Lwasa et al., 2014). Youth "
        "participation remains low despite high urban unemployment (Abubakar et al., 2023).",
    ]:
        add_body(doc, t)

    # 4.3 Climate-Smart — mapped to Ericksen's "environmental outcomes"
    add_heading(doc, "4.3 Climate-Smart Practices (Environmental Outcomes Node)", level=2)

    for t in [
        "Ericksen's (2008) framework identifies environmental outcomes as both products of and constraints on "
        "food activities. Climate-smart agriculture seeks to simultaneously increase productivity, enhance "
        "adaptation, and reduce emissions (FAO, 2013). In the Nigerian urban context, three practices show "
        "particular promise. First, composting of organic waste converts the approximately 60 per cent organic "
        "fraction of municipal waste into soil amendment, reducing landfill methane while improving urban soil "
        "fertility (Olanrewaju et al., 2022; Sekabira et al., 2022). Pilot programs in Ibadan and Kano "
        "demonstrate that market-waste compost is a viable product that farmers will purchase at market rates "
        "(Olanrewaju et al., 2022). Second, rainwater harvesting and efficient irrigation extend dry-season "
        "production in Sahelian cities where annual rainfall ranges from 400 to 900 mm (Tambol et al., 2025). "
        "Third, heat-tolerant crop varieties developed by Nigeria's national research system can increase yields "
        "in urban heat-island conditions, though distribution to urban farmers remains limited (Arowolo et al., "
        "2023).",

        "However, adoption faces significant barriers. The national agricultural extension system is overwhelmingly "
        "focused on rural production, leaving urban farmers without technical support (Chitakira et al., 2021). "
        "Composting requires initial investment in collection infrastructure and quality control that individual "
        "farmers cannot bear. A counter-argument holds that urban agriculture is too small-scale to matter\u2014"
        "that it produces a negligible fraction of national food supply and diverts attention from systemic reform. "
        "This critique has genuine force at the national level: urban agriculture's aggregate contribution to "
        "Nigeria's food supply is small relative to rural production. However, it understates the local significance: "
        "for individual households, a 15\u201330 per cent reduction in food expenditure is meaningful, particularly "
        "when food inflation exceeds 35 per cent (Orhevba et al., 2024; NESG, 2024). The appropriate response is "
        "not to abandon urban agriculture but to situate it within a broader food security strategy.",
    ]:
        add_body(doc, t)

    # 4.4 Circular Economy
    add_heading(doc, "4.4 Circular Economy and Waste-to-Resource (Feedback Loop)", level=2)

    for t in [
        "Nigeria generates an estimated 32 million tonnes of municipal solid waste annually, with organic waste "
        "constituting approximately 60 per cent (Sekabira et al., 2022). Less than 40 per cent of waste is "
        "collected in major cities, and composting accounts for less than 5 per cent of treatment (Olanrewaju "
        "et al., 2022). This represents a dual failure: organic waste decomposes in open dumps, producing "
        "methane, while urban farmers lack access to affordable soil amendment.",

        "The circular economy framework proposes to close this nutrient loop. International evidence from "
        "Kampala, Dar es Salaam, and Nairobi demonstrates that community composting can reduce waste volumes by "
        "20 to 30 per cent while generating employment and improving soil health (Lwasa et al., 2014). In Nigeria, "
        "the institutional challenge is that waste management is a state government responsibility while urban "
        "agriculture operates at the local government and community level. Bridging this institutional gap "
        "requires inter-governmental coordination mechanisms that do not currently exist in most Nigerian states. "
        "This finding aligns with Lwasa et al.'s (2014) observation that institutional fragmentation is the "
        "primary barrier to scaling circular economy approaches in African cities.",
    ]:
        add_body(doc, t)

    # 4.5 Urban Planning
    add_heading(doc, "4.5 Urban Planning and Zoning (Institutional Conditions Node)", level=2)

    for t in [
        "The policy environment for urban agriculture in Nigeria is shaped by a fundamental institutional "
        "constraint: the Land Use Act of 1978 vests all land in each state in the governor, who controls "
        "allocation and revocation. Local government areas have limited authority to zone land for agricultural "
        "use or to protect farmland from real estate conversion. The National Urban Policy (2022) calls for "
        "safeguarding agricultural land and compact urban development, but it lacks binding provisions and "
        "enforcement mechanisms (Federal Ministry of Housing and Urban Development, 2022). In November 2025, "
        "President Tinubu urged states to domesticate the policy, but implementation remains uneven.",

        "International models offer useful comparisons. In Kampala, Uganda, urban agriculture is formally "
        "recognised in the city's spatial plan with designated agricultural zones (Lwasa et al., 2014). In "
        "Dar es Salaam, community land trusts secure tenure for peri-urban farmers (Senthamizh et al., 2025). "
        "For Nigerian cities, the critical barrier is not the absence of good policy but the gap between "
        "federal intent and local authority. Without reform of the Land Use Act's provisions on local government "
        "land management, zoning recommendations remain aspirational.",
    ]:
        add_body(doc, t)

    # === 5. DISCUSSION ===
    add_heading(doc, "5. Discussion", level=1)

    # 5.1 — engage with other reviews
    add_heading(doc, "5.1 What This Review Adds to Existing Syntheses", level=2)

    for t in [
        "Two recent reviews provide broad overviews of urban agriculture in the Global South: Senthamizh et al. "
        "(2025) surveyed zoning reforms across 12 cities, and Lwasa et al. (2014) examined climate resilience "
        "in East and West African cities. This review adds to their work in three ways. First, it focuses "
        "specifically on Nigeria, where the Land Use Act of 1978 creates an institutional barrier absent in "
        "most other African countries. Senthamizh et al.'s (2025) policy models from Kampala and Portland are "
        "instructive but assume a degree of local government authority that Nigerian LGAs do not possess. "
        "Second, this review explicitly examines gender and youth dimensions, which both earlier reviews mention "
        "but do not analyse in depth. Third, it maps the evidence onto Ericksen's (2008) food systems framework, "
        "providing a theoretical structure that neither Senthamizh et al. nor Lwasa et al. adopt.",

        "The reviewed literature reveals a consistent pattern: urban agriculture is widespread and valued by "
        "households, yet operates in a policy vacuum. Across the five Nigerian cities examined, the common "
        "constraints are land insecurity, limited technical support, and the absence of formal zoning. However, "
        "the manifestation of these constraints varies. In Kano, the primary challenge is water rights and "
        "seasonal flooding; in Lagos, it is land displacement by real estate; in Abuja, it is the tension "
        "between planned city development and peri-urban production. This geographic variation implies that "
        "policy interventions cannot be one-size-fits-all.",

        "The intersection with gender and youth dimensions adds complexity. Women dominate urban farming but "
        "face compounding disadvantages: insecure tenure, limited credit access, and lower participation in "
        "market networks. Youth are largely absent despite high urban unemployment, partly because farming is "
        "perceived as low-status. Addressing these dimensions requires not only technical interventions but "
        "also social ones: land tenure reform for women, youth entrepreneurship programs, and the rebranding "
        "of urban agriculture as a viable livelihood strategy.",
    ]:
        add_body(doc, t)

    # 5.2 — policy
    add_heading(doc, "5.2 Policy Implications", level=2)

    for t in [
        "Three context-specific policy interventions are proposed, each addressing a node in Ericksen's (2008) "
        "framework. First, reform of the Land Use Act's provisions on local government land management would "
        "enable LGA-level zoning, addressing the institutional conditions node. This requires either amendment "
        "of the Act or a ministerial guideline clarifying LGAs' authority to designate agricultural zones. The "
        "National Urban Policy (2022) provides a basis, but political will is needed.",

        "Second, municipal composting programs should be piloted in Lagos, Kano, and Ibadan using an "
        "inter-governmental model: state governments provide infrastructure, while local governments and "
        "community organisations manage collection and distribution. This addresses the environmental outcomes "
        "node by converting waste into soil amendment.",

        "Third, urban agriculture should be included in Nigeria's Malabo Declaration implementation and SDG 2 "
        "national reporting, linking food activities to broader socio-economic conditions.",
    ]:
        add_body(doc, t)

    # 5.3 — counter-arguments (balanced)
    add_heading(doc, "5.3 Counter-Arguments and Limitations of This Analysis", level=2)

    for t in [
        "Several objections to prioritising urban agriculture deserve consideration, and this paper concedes "
        "where they have genuine force. The efficiency argument holds that urban land is too valuable for food "
        "production and should be allocated to housing and commerce. This has merit in city centres but does "
        "not apply to the marginal land\u2014floodplains, vacant lots, rooftops\u2014that urban agriculture "
        "actually occupies. The scale argument contends that urban agriculture produces too little to affect "
        "national food security. This is accurate: urban agriculture's aggregate contribution to Nigeria's "
        "food supply is small relative to rural production. We do not claim otherwise. What we do claim is "
        "that the household-level contribution (15\u201330 per cent of food consumption) is significant for "
        "food-insecure households, and that this local significance justifies policy attention even if national "
        "impact is modest.",

        "The enforcement argument suggests that zoning is unenforceable in Nigerian cities with weak planning "
        "institutions. This is a legitimate concern, and we acknowledge that our policy recommendations assume "
        "an institutional capacity that may not exist in many LGAs. Strengthening this capacity is a prerequisite "
        "for zoning reform, not a consequence of it. The most compelling counter-argument is that urban agriculture "
        "diverts attention from systemic issues: infrastructure investment, trade policy, and macroeconomic "
        "management. This paper does not claim that urban agriculture is a substitute for these reforms; rather, "
        "it argues that urban agriculture is a complementary strategy that provides immediate, household-level "
        "benefits while longer-term systemic reforms are implemented.",
    ]:
        add_body(doc, t)

    # === 6. LIMITATIONS ===
    add_heading(doc, "6. Limitations", level=1)

    add_body(doc,
        "This review has several limitations. First, it is a narrative rather than a systematic review, meaning "
        "that study selection involved researcher judgement that may have introduced selection bias. Second, the "
        "review is restricted to English-language sources, excluding potentially relevant Francophone West African "
        "studies. Third, geographic coverage is uneven: Kano and Lagos are over-represented relative to smaller "
        "cities, reflecting the concentration of research activity in Nigeria's largest cities. Fourth, several "
        "peer-reviewed sources are themselves literature reviews rather than primary empirical studies, which "
        "limits the independence of the evidence base. Finally, the policy recommendations are based on literature "
        "analysis rather than primary institutional research, and their feasibility has not been tested through "
        "stakeholder consultation.")

    # === 7. CONCLUSION ===
    add_heading(doc, "7. Conclusion", level=1)

    for t in [
        "This paper has demonstrated that urban agriculture is a widespread, household-valued activity across "
        "Nigerian cities that operates in a policy vacuum characterised by land insecurity, limited technical "
        "support, and the absence of formal zoning. Interpreted through Ericksen's (2008) food systems framework, "
        "the evidence shows that food production activities (fadama, community gardens, rooftop cultivation) are "
        "shaped by institutional conditions (Land Use Act, NUP 2022) and environmental outcomes (climate "
        "variability, waste generation) that interact through feedback loops. Climate-smart practices, "
        "particularly composting, show promise but face adoption barriers rooted in institutional fragmentation "
        "and infrastructure deficits. The gendered and age-differentiated nature of urban farming\u2014with "
        "women comprising the majority of practitioners and youth largely absent\u2014means that interventions "
        "must address social dimensions alongside technical ones.",

        "What this review adds that was not previously synthesised is: (i) a Nigeria-specific analysis that "
        "identifies the Land Use Act as the primary institutional barrier, a constraint not present in the "
        "comparative models of Senthamizh et al. (2025) or Lwasa et al. (2014); (ii) an explicit engagement "
        "with counter-arguments that contextualises the household-level significance of urban agriculture "
        "alongside its national-level limitations; and (iii) a mapping of evidence onto a theoretical framework "
        "that provides structure for future research.",

        "Future research should pursue three priorities. First, systematic surveys across a representative "
        "sample of Nigerian cities, including measurement of production volumes, dietary contributions, and "
        "income effects. Second, institutional analysis of the Land Use Act's impact on urban agricultural "
        "land tenure, including case studies of states that have attempted reform. Third, impact evaluations "
        "of composting pilot programs and zoning interventions to build the evidence base for policy scaling.",
    ]:
        add_body(doc, t)

    # === REFERENCES ===
    add_heading(doc, "References", level=1)

    p = doc.add_paragraph()
    run = p.add_run("Peer-reviewed sources")
    set_run_font(run, size=10, bold=True, italic=True)
    set_paragraph_spacing(p, before=6, after=3, line=1.0)

    for ref in [
        "Abubakar, I. R., Oyedepo, J. A. and Al-Ghamdi, S. A. (2023) 'Urbanisation, food insecurity and the role of urban agriculture in Nigeria', Habitat International, 136, p. 102819.",
        "Adedeji, O. H., Olojede, O. and Amisu, I. (2009) 'Urban agriculture and urban land use planning', Journal of Geography and Regional Planning, 2(6), pp. 112\u2013123.",
        "Arksey, H. and O'Malley, L. (2005) 'Scoping studies: Towards a methodological framework', International Journal of Social Research Methodology, 8(1), pp. 19\u201332.",
        "Bryld, E. (2003) 'Potentials, problems, and policy implications for urban agriculture in developing countries', Agriculture and Human Values, 20(2), pp. 163\u2013175.",
        "Arowolo, O. O., Adesina, F. A. and Olugbire, O. O. (2023) 'Climate variability and peri-urban agriculture in the Sahel', Environmental Challenges, 11, p. 100718.",
        "Chitakira, M., Torquebiau, E. and Ferguson, I. (2021) 'Uptake of climate smart agriculture in peri-urban areas: A review', Frontiers in Sustainable Food Systems, 5, p. 706738.",
        "Ericksen, P. J. (2008) 'Conceptualizing food systems for global environmental change research', Global Environmental Change, 18(1), pp. 234\u2013245.",
        "Issifu, N., Mendoza, C. and Agyeman-Duah, I. (2025) 'Securing the future of urban agriculture: Legislative reform in Africa', Land Use Policy, 145, p. 107278.",
        "Khumalo, N. Z., Mahachi, C. and Mavodza, G. (2024) 'Implications of a climate-smart approach to food and nutrition security', Sustainability, 16(5), p. 1882.",
        "Lwasa, S., Mugagga, F. and Wahab, B. (2014) 'Urban and peri-urban agriculture and forestry', in Urban Planning and Management. CRC Press, pp. 1\u201318.",
        "Muhammed, I. A., Aliyu, I. and Mustapha, S. (2022) 'Fadama farming and urban food production in the dry season: Evidence from Kano, Nigeria', Sustainable Water Resources Management, 8(3), p. 142.",
        "Ogundele, F. O., Olawuyi, S. O. and Adedayo, O. P. (2023) 'Mapping urban agricultural land uses in Lagos, Nigeria', Urban Science, 7(4), p. 115.",
        "Olanrewaju, C. C., Thompson, A. M. and Chovwen, C. (2022) 'Composting and circular economy: Linking organic waste management to urban agriculture in Nigeria', Waste Management & Research, 40(8), pp. 1143\u20131152.",
        "Orhevba, B. A., Ola, O. P. and Fakolujo, A. S. (2024) 'Urban agriculture and food security: Evidence from selected cities in Nigeria', Nigerian Journal of Agricultural Economics, 14(1), pp. 1\u201312.",
        "Sekabira, H., Nantongo, M. and Mugagga, F. (2022) 'Circular bioeconomy in African food systems', Circular Economy and Sustainability, 2, pp. 1077\u20131096.",
        "Senthamizh, R., Odu, P. and Akinola, R. (2025) 'Urban agriculture in a changing world: A thematic review', Frontiers in Sustainable Food Systems, 9, p. 1624426.",
        "Tambol, T., Bationo, A. and Sileshi, Y. (2025) 'Use of climate smart agriculture technologies in West Africa Sahel', Scientific Reports, 15, p. 4127.",
        "Zezza, A. and Tasciotti, L. (2010) 'Urban agriculture, poverty, and food security: Empirical evidence from a sample of developing countries', Food Policy, 35(4), pp. 265\u2013273.",
    ]:
        add_reference(doc, ref)

    p = doc.add_paragraph()
    run = p.add_run("Institutional and policy sources")
    set_run_font(run, size=10, bold=True, italic=True)
    set_paragraph_spacing(p, before=6, after=3, line=1.0)

    for ref in [
        "African Union (2014) Malabo Declaration on Accelerated Agricultural Growth and Transformation. Malabo: African Union.",
        "FAO (2013) Climate-Smart Agriculture Sourcebook. Rome: FAO.",
        "FAO (2023) The State of Food Security and Nutrition in the World 2023. Rome: FAO.",
        "FAO (2024) Strengthening Urban and Peri-Urban Food Systems to Achieve Food Security and Nutrition. Rome: CFS.",
        "Federal Ministry of Housing and Urban Development (2022) National Urban Policy of Nigeria. Abuja: FMHUD.",
        "FEWS NET (2024) West Africa Food Security Outlook: Nigeria. Available at: https://fews.net.",
        "IMF (2023) 'Food insecurity in Nigeria: Food supply matters', IMF Working Papers, 2023/018.",
        "NESG (2024) Policy Brief: Food Security in Nigeria. Lagos: Nigeria Economic Summit Group.",
        "Ubah, C. C. et al. (2025) 'Progress of the Malabo declaration', Food and Energy Security, 5(2), p. 23.",
        "World Bank (2024) World Development Indicators: Nigeria. Available at: https://data.worldbank.org.",
    ]:
        add_reference(doc, ref)

    # === SAVE ===
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manuscript")
    out_path = os.path.join(out_dir, "manuscript.docx")
    doc.save(out_path)

    total_words = 0
    for para in doc.paragraphs:
        total_words += len(para.text.split())
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                total_words += len(cell.text.split())

    print(f"Saved: {out_path}")
    print(f"Word count: {total_words}")
    print(f"Estimated pages @ 300 w/pp: {total_words / 300:.1f}")

if __name__ == "__main__":
    main()
