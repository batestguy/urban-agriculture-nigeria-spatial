#!/usr/bin/env python3
"""
build_diagram.py — Generate Figure 1: Urban Agriculture–Food Security–Climate-Smart Nexus
Uses matplotlib to create a conceptual framework diagram as PNG.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def main():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Colors
    c_ua = '#2E86AB'      # Urban Agriculture - blue
    c_cs = '#A23B72'      # Climate-Smart - purple
    c_ce = '#F18F01'      # Circular Economy - orange
    c_up = '#C73E1D'      # Urban Planning - red
    c_fs = '#3B1F2B'      # Food Security - dark
    c_pf = '#44AF69'      # Policy Frameworks - green

    def box(x, y, w, h, text, color, fontsize=9, bold=False, alpha=0.85):
        fancy = FancyBboxPatch((x, y), w, h,
                               boxstyle="round,pad=0.1",
                               facecolor=color, edgecolor='white',
                               linewidth=1.5, alpha=alpha)
        ax.add_patch(fancy)
        weight = 'bold' if bold else 'normal'
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=fontsize, color='white', fontweight=weight,
                wrap=True)

    def arrow(x1, y1, x2, y2, color='#555555'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color,
                                    lw=2, connectionstyle='arc3,rad=0'))

    # === TOP: URBAN AGRICULTURE ===
    box(0.5, 5.8, 9, 1.0,
        'URBAN AGRICULTURE IN NIGERIA',
        c_ua, fontsize=13, bold=True)

    # Sub-boxes under UA
    ua_types = [
        (0.7, 5.1, 2.0, 'Peri-urban\nFadama'),
        (2.9, 5.1, 2.0, 'Rooftop &\nVertical'),
        (5.1, 5.1, 2.0, 'Community\nGardens'),
        (7.3, 5.1, 2.0, 'Vacant-Lot\nFarming'),
    ]
    for x, y, w, txt in ua_types:
        box(x, y, w, 0.6, txt, c_ua, fontsize=8, alpha=0.7)

    # === MIDDLE: THREE PATHWAYS ===
    # Arrow down from UA types
    for x_off in [1.7, 3.9, 6.1, 8.3]:
        arrow(x_off, 5.1, 5.0, 4.65, '#888888')

    # Pathway label
    ax.text(5.0, 4.55, 'THREE ENABLING PATHWAYS', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#333333',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#EEEEEE', edgecolor='#CCCCCC'))

    # Three pathway boxes
    box(0.3, 3.2, 2.8, 1.1,
        'CLIMATE-SMART\nPRACTICES\n\n• Composting\n• Rainwater harvest\n• Heat-tolerant crops',
        c_cs, fontsize=7.5)

    box(3.6, 3.2, 2.8, 1.1,
        'CIRCULAR ECONOMY\nMECHANISMS\n\n• Waste → Compost\n• Soil → Food → Waste\n• Closed nutrient loop',
        c_ce, fontsize=7.5)

    box(6.9, 3.2, 2.8, 1.1,
        'URBAN PLANNING\n& ZONING\n\n• LGA zoning\n• Peri-urban buffers\n• NUP 2022',
        c_up, fontsize=7.5)

    # Arrows from pathways down
    arrow(1.7, 3.2, 5.0, 2.75, '#888888')
    arrow(5.0, 3.2, 5.0, 2.75, '#888888')
    arrow(8.3, 3.2, 5.0, 2.75, '#888888')

    # === BOTTOM: FOOD SECURITY OUTCOMES ===
    box(1.0, 1.6, 8.0, 1.1,
        'FOOD SECURITY OUTCOMES\n\nAvailability  •  Access  •  Utilisation  •  Stability',
        c_fs, fontsize=10, bold=True)

    # === SIDE: POLICY FRAMEWORKS ===
    box(0.3, 0.2, 9.4, 1.1,
        'POLICY FRAMEWORKS:  NUP 2022  •  SDG 2 (Zero Hunger)  •  AU Malabo Declaration  •  FAO Urban Agriculture Guidelines',
        c_pf, fontsize=9, bold=True)

    # Arrow from policy to food security
    arrow(5.0, 1.3, 5.0, 1.6, c_pf)

    # Feedback arrow (food security back to UA) — curved
    ax.annotate('', xy=(9.2, 6.3), xytext=(9.2, 1.6),
                arrowprops=dict(arrowstyle='->', color=c_ua,
                                lw=1.5, connectionstyle='arc3,rad=-0.3',
                                linestyle='dashed'))
    ax.text(9.7, 4.0, 'Feedback', ha='center', va='center',
            fontsize=7, color=c_ua, rotation=90, style='italic')

    # Title
    ax.text(5.0, 6.95, 'Figure 1: Urban Agriculture–Food Security–Climate-Smart Nexus',
            ha='center', va='center', fontsize=12, fontweight='bold')

    plt.tight_layout()

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'conceptual_framework.png')
    fig.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    main()
