# Walkthrough video — what it is and what is in it

`urbanag-walkthrough-moi-je-prouve.mp4` — two-and-a-half-minute captioned tour of
the manuscript, built from the rendered PDF (`manuscript/manuscript.pdf`) rather
than from screenshots, so every page shown is the page in the paper.

- Cover: the paper's headline figure, the LISA map, with the title and author block.
- Body: the abstract; the three questions and the fourth that was withdrawn; why
  coverage is the threat; the study area and the unit of analysis; Table 1 with
  Moran's I; Figure 1 (the LISA clusters); Table 2 (the scale effect); Table 3
  (the coverage correction); the Ikorodu–Tarauni comparison; Figure 2; the climate
  hypothesis the data could not test; what the pattern implies for policy; the
  Conclusion; and data and code availability.
- Closing: a card listing what the paper set out to do and what it delivered.

The silent master is `urbanag-walkthrough.mp4`, identical in picture and 0.2 s
longer, and carries no audio. It is the version to use anywhere the music cannot
be used.

Rebuilt with `build_walk.py` (slides, from the PDF) plus ffmpeg (assembly); the
script lived in the session temporary folder, not in this repository.

## Number discipline

Every figure spoken in a caption is a figure printed on the page it sits over:
Moran's I 0.300 and 0.274 (Table 1), 0.341 per doubling and about 66 per cent
(Section 5.2), −1.001 to −1.421 with ΔAIC 20.0 (Table 3), 19 of 775 areal units,
13 in Kano and 6 in Lagos, Tarauni 1.058 against Ikorodu 0.143 km⁻² (Section 5.4),
p = 0.58 across five cities (Section 5.5). Nothing new is asserted.

The PDF used here is the 24 November render. It states 774 LGAs for Nigeria and
775 areal units tested, following the Lake Chad correction of that date (D-20);
the version submitted to African Geographical Review on 13 November says 775 LGAs
in the abstract, and that correction belongs in the revision.

## Music

The audio is **Tayc, "Moi je prouve" (speed-up version)**, taken from the file in
the repository root and included here as a personal demonstration only. It is not
licensed from the rights holders, is not part of the manuscript or any submitted
or published result, and is not redistributed as an audio file — only as the
soundtrack of this demo. The track was trimmed to the video length, faded in over
3 s and out over the last 5 s, and reduced 2 dB.

If a rights holder objects, delete this file; the silent master is unaffected and
is the one to keep. Do not attach the music cut to a journal submission or a
public post without a licence.

## What the video does not show

Page 15 of the current PDF prints a raw `@fig-extent` instead of a figure number:
the cross-reference is dangling in the Discussion, because the study-extent figure
lives in the supplementary file. The page was left out of the video. The same text
is in the file submitted to the journal (`manuscript-anonymised.docx`), so it will
need fixing in the revision.
