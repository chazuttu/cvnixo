const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign
} = require('docx');
const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outputDir = process.argv[3];

const {
  candidate_name, email, phone, location, linkedin,
  match_score, strong_points, missing_skills, improvement_tips,
  ats_keywords_found, ats_keywords_missing,
  summary, work_experience, projects, education,
  skills_technical, skills_tools, achievements, certifications
} = data;

const BLUE      = "2E75B6";
const DARK      = "1A1A2E";
const GRAY      = "666666";
const LIGHT     = "F5F7FA";
const GREEN     = "00A651";
const ORANGE    = "E67E22";
const RED       = "C0392B";
const WHITE     = "FFFFFF";
const DIVIDER   = "D0D8E8";
const DARKBLUE  = "1B4F72";

const score = Math.max(5, parseInt(match_score) || 0);

function scoreColor(s) {
  if (s >= 70) return GREEN;
  if (s >= 40) return ORANGE;
  return RED;
}
function scoreLabel(s) {
  if (s >= 70) return "STRONG MATCH — Ready to apply!";
  if (s >= 40) return "MODERATE MATCH — Few improvements needed";
  return "KEEP BUILDING — Focus on missing skills first";
}
function scoreMessage(s) {
  if (s >= 70) return "Your profile is well aligned with this role. Apply with confidence and prepare for the interview.";
  if (s >= 40) return "You have a solid foundation. Work on the missing skills below to significantly improve your chances.";
  return "Do not be discouraged. This role needs more preparation. Follow the improvement roadmap below and reapply when ready.";
}

const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const sColor = scoreColor(score);

function divLine(color = DIVIDER) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color, space: 1 } },
    children: []
  });
}

function secHead(text, color = BLUE) {
  return new Paragraph({
    spacing: { before: 140, after: 60 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color, space: 2 } },
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 20, color, font: "Calibri" })]
  });
}

function bullet(text, color = DARK, size = 18) {
  return new Paragraph({
    spacing: { after: 30 },
    indent: { left: 320, hanging: 200 },
    children: [
      new TextRun({ text: "•  ", bold: true, size, color: BLUE, font: "Calibri" }),
      new TextRun({ text: text.replace(/^[-•]\s*/, ''), size, color, font: "Calibri" })
    ]
  });
}

// ══════════════════════════════════════════════
// DOCUMENT 1 — ATS ANALYSIS REPORT
// ══════════════════════════════════════════════

const reportBanner = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [9360],
  rows: [new TableRow({
    children: [new TableCell({
      shading: { fill: DARKBLUE, type: ShadingType.CLEAR },
      borders: noBorders,
      margins: { top: 180, bottom: 180, left: 360, right: 360 },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "CVNIXO", bold: true, size: 36, color: WHITE, font: "Calibri" }),
            new TextRun({ text: "  ·  ATS RESUME ANALYSIS REPORT", size: 22, color: "90C4F0", font: "Calibri" })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40 },
          children: [
            new TextRun({ text: `Candidate: ${candidate_name}`, size: 18, color: "C8DFF5", italics: true, font: "Calibri" })
          ]
        })
      ]
    })]
  })]
});

const scoreCard = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [2800, 6560],
  rows: [new TableRow({
    children: [
      new TableCell({
        shading: { fill: LIGHT, type: ShadingType.CLEAR },
        borders: noBorders,
        margins: { top: 220, bottom: 220, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: `${score}%`, bold: true, size: 96, color: sColor, font: "Calibri" })]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 20 },
            children: [new TextRun({ text: "ATS MATCH SCORE", bold: true, size: 15, color: GRAY, font: "Calibri" })]
          }),
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 40 },
            children: [new TextRun({ text: scoreLabel(score), bold: true, size: 17, color: sColor, font: "Calibri" })]
          })
        ]
      }),
      new TableCell({
        shading: { fill: WHITE, type: ShadingType.CLEAR },
        borders: {
          top: noBorder, bottom: noBorder, right: noBorder,
          left: { style: BorderStyle.SINGLE, size: 6, color: sColor }
        },
        margins: { top: 220, bottom: 220, left: 300, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({
            spacing: { after: 100 },
            children: [new TextRun({ text: scoreMessage(score), size: 20, color: DARK, font: "Calibri" })]
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "Keywords Found: ", bold: true, size: 18, color: GREEN, font: "Calibri" }),
              new TextRun({ text: `${ats_keywords_found}     `, size: 18, color: GREEN, font: "Calibri" }),
              new TextRun({ text: "Keywords Missing: ", bold: true, size: 18, color: RED, font: "Calibri" }),
              new TextRun({ text: `${ats_keywords_missing}`, size: 18, color: RED, font: "Calibri" })
            ]
          })
        ]
      })
    ]
  })]
});

const analysisTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4620, 4740],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          shading: { fill: "E8F5E9", type: ShadingType.CLEAR },
          borders: noBorders,
          margins: { top: 120, bottom: 60, left: 200, right: 100 },
          children: [new Paragraph({
            children: [new TextRun({ text: "✓  WHAT MATCHES WELL", bold: true, size: 19, color: GREEN, font: "Calibri" })]
          })]
        }),
        new TableCell({
          shading: { fill: "FDEDEC", type: ShadingType.CLEAR },
          borders: { top: noBorder, bottom: noBorder, right: noBorder, left: { style: BorderStyle.SINGLE, size: 2, color: DIVIDER } },
          margins: { top: 120, bottom: 60, left: 200, right: 100 },
          children: [new Paragraph({
            children: [new TextRun({ text: "✗  NEEDS IMPROVEMENT", bold: true, size: 19, color: RED, font: "Calibri" })]
          })]
        })
      ]
    }),
    new TableRow({
      children: [
        new TableCell({
          shading: { fill: "E8F5E9", type: ShadingType.CLEAR },
          borders: noBorders,
          margins: { top: 60, bottom: 120, left: 200, right: 100 },
          children: strong_points.filter(p => p.trim()).map(p =>
            new Paragraph({
              spacing: { after: 60 },
              children: [new TextRun({ text: "• " + p.replace(/^[-•]\s*/, ''), size: 18, color: DARK, font: "Calibri" })]
            })
          )
        }),
        new TableCell({
          shading: { fill: "FDEDEC", type: ShadingType.CLEAR },
          borders: { top: noBorder, bottom: noBorder, right: noBorder, left: { style: BorderStyle.SINGLE, size: 2, color: DIVIDER } },
          margins: { top: 60, bottom: 120, left: 200, right: 100 },
          children: missing_skills.filter(p => p.trim()).map(p =>
            new Paragraph({
              spacing: { after: 60 },
              children: [new TextRun({ text: "• " + p.replace(/^[-•]\s*/, ''), size: 18, color: DARK, font: "Calibri" })]
            })
          )
        })
      ]
    })
  ]
});

const roadmapItems = (improvement_tips || []).map((tip, i) =>
  new Paragraph({
    spacing: { after: 80 },
    indent: { left: 360, hanging: 260 },
    children: [
      new TextRun({ text: `${i + 1}.  `, bold: true, size: 19, color: BLUE, font: "Calibri" }),
      new TextRun({ text: tip, size: 19, color: DARK, font: "Calibri" })
    ]
  })
);

const tipBox = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [9360],
  rows: [new TableRow({
    children: [new TableCell({
      shading: { fill: "EBF5FB", type: ShadingType.CLEAR },
      borders: {
        left: { style: BorderStyle.SINGLE, size: 12, color: BLUE },
        top: noBorder, bottom: noBorder, right: noBorder
      },
      margins: { top: 120, bottom: 120, left: 240, right: 200 },
      children: [
        new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: "PRO TIP", bold: true, size: 19, color: BLUE, font: "Calibri" })]
        }),
        new Paragraph({
          children: [new TextRun({
            text: "Adding even 2-3 missing keywords naturally into your resume can increase your ATS score by 20-30%. Focus on the most important requirements first.",
            size: 18, color: GRAY, font: "Calibri"
          })]
        })
      ]
    })]
  })]
});

const analysisDoc = new Document({
  styles: { default: { document: { run: { font: "Calibri", size: 20, color: DARK } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 720, right: 1008, bottom: 720, left: 1008 }
      }
    },
    children: [
      reportBanner,
      new Paragraph({ spacing: { after: 120 }, children: [] }),
      scoreCard,
      new Paragraph({ spacing: { after: 100 }, children: [] }),
      secHead("Detailed Analysis", DARKBLUE),
      analysisTable,
      new Paragraph({ spacing: { after: 100 }, children: [] }),
      secHead("Improvement Roadmap", ORANGE),
      ...roadmapItems,
      new Paragraph({ spacing: { after: 100 }, children: [] }),
      tipBox,
      new Paragraph({
        spacing: { before: 160 },
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: DIVIDER } },
        children: [new TextRun({ text: "Generated by Cvnixo  •  AI Resume Tailoring Tool", size: 15, color: "AAAAAA", italics: true, font: "Calibri" })]
      })
    ]
  }]
});

// ══════════════════════════════════════════════
// DOCUMENT 2 — ONE PAGE TAILORED RESUME
// ══════════════════════════════════════════════

const nameBanner = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [9360],
  rows: [new TableRow({
    children: [new TableCell({
      shading: { fill: DARK, type: ShadingType.CLEAR },
      borders: noBorders,
      margins: { top: 160, bottom: 120, left: 300, right: 300 },
      children: [
        new Paragraph({
          children: [new TextRun({ text: candidate_name.toUpperCase(), bold: true, size: 36, color: WHITE, font: "Calibri" })]
        }),
        new Paragraph({
          spacing: { before: 40 },
          children: [
            new TextRun({ text: [email, phone, location, linkedin].filter(Boolean).join("   |   "), size: 16, color: "A0C4FF", font: "Calibri" })
          ]
        })
      ]
    })]
  })]
});

const workSection = [];
work_experience.forEach(job => {
  workSection.push(new Paragraph({
    spacing: { before: 100, after: 20 },
    children: [
      new TextRun({ text: job.title, bold: true, size: 19, color: DARK, font: "Calibri" }),
      new TextRun({ text: "  ·  ", size: 18, color: GRAY, font: "Calibri" }),
      new TextRun({ text: job.company, bold: true, size: 18, color: BLUE, font: "Calibri" }),
      new TextRun({ text: "  ·  " + job.dates + "  ·  " + job.location, size: 16, color: GRAY, italics: true, font: "Calibri" })
    ]
  }));
  job.bullets.slice(0, 2).forEach(b => workSection.push(bullet(b, DARK, 17)));
});

const projSection = [];
projects.slice(0, 2).forEach(proj => {
  projSection.push(new Paragraph({
    spacing: { before: 80, after: 20 },
    children: [new TextRun({ text: proj.name, bold: true, size: 18, color: BLUE, font: "Calibri" })]
  }));
  proj.bullets.slice(0, 1).forEach(b => projSection.push(bullet(b, DARK, 17)));
});

const skillsTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4680, 4680],
  rows: [new TableRow({
    children: [
      new TableCell({
        shading: { fill: LIGHT, type: ShadingType.CLEAR },
        borders: noBorders,
        margins: { top: 80, bottom: 80, left: 160, right: 80 },
        children: [
          new Paragraph({ children: [new TextRun({ text: "Technical Skills", bold: true, size: 17, color: BLUE, font: "Calibri" })] }),
          new Paragraph({ spacing: { before: 40 }, children: [new TextRun({ text: skills_technical.join("  •  "), size: 16, color: DARK, font: "Calibri" })] })
        ]
      }),
      new TableCell({
        shading: { fill: LIGHT, type: ShadingType.CLEAR },
        borders: { top: noBorder, bottom: noBorder, right: noBorder, left: { style: BorderStyle.SINGLE, size: 2, color: DIVIDER } },
        margins: { top: 80, bottom: 80, left: 160, right: 80 },
        children: [
          new Paragraph({ children: [new TextRun({ text: "Tools & Technologies", bold: true, size: 17, color: BLUE, font: "Calibri" })] }),
          new Paragraph({ spacing: { before: 40 }, children: [new TextRun({ text: skills_tools.join("  •  "), size: 16, color: DARK, font: "Calibri" })] })
        ]
      })
    ]
  })]
});

const eduParas = education.map(e => new Paragraph({
  spacing: { before: 60, after: 20 },
  children: [
    new TextRun({ text: e.degree, bold: true, size: 18, color: DARK, font: "Calibri" }),
    new TextRun({ text: "  ·  " + e.institution + "  ·  " + e.year + (e.cgpa ? "  ·  CGPA: " + e.cgpa : ""), size: 17, color: GRAY, font: "Calibri" })
  ]
}));

const resumeDoc = new Document({
  styles: { default: { document: { run: { font: "Calibri", size: 20, color: DARK } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 600, right: 1008, bottom: 600, left: 1008 }
      }
    },
    children: [
      nameBanner,
      new Paragraph({ spacing: { after: 60 }, children: [] }),
      secHead("Professional Summary"),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({ text: summary, size: 18, color: DARK, italics: true, font: "Calibri" })]
      }),
      secHead("Work Experience"),
      ...workSection,
      secHead("Projects"),
      ...projSection,
      secHead("Skills"),
      skillsTable,
      secHead("Education"),
      ...eduParas,
      secHead("Achievements"),
      ...achievements.slice(0, 3).map(a => bullet(a, DARK, 17)),
      secHead("Certifications"),
      ...certifications.slice(0, 3).map(c => bullet(c, DARK, 17)),
      new Paragraph({
        spacing: { before: 160 },
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: DIVIDER } },
        children: [new TextRun({ text: "Tailored with Cvnixo  •  AI Resume Tool", size: 15, color: "AAAAAA", italics: true, font: "Calibri" })]
      })
    ]
  }]
});

// ── Save both documents ───────────────────────────────────────────────────
Promise.all([
  Packer.toBuffer(analysisDoc).then(buf => {
    fs.writeFileSync(path.join(outputDir, 'cvnixo_analysis.docx'), buf);
  }),
  Packer.toBuffer(resumeDoc).then(buf => {
    fs.writeFileSync(path.join(outputDir, 'cvnixo_resume.docx'), buf);
  })
]).then(() => {
  console.log('SUCCESS');
}).catch(err => {
  console.error('ERROR:', err.message);
  process.exit(1);
});