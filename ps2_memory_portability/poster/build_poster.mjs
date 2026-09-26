import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/mickeyxiaoliuliu/Desktop/DKU curriculums/cs206/gt-tools-demos";
const projectDir = path.join(workspaceDir, "ps2_memory_portability");
const posterDir = path.join(projectDir, "poster");
const buildDir = path.join(posterDir, ".build");
const submissionDir = path.join(projectDir, "submission");
const sourceTemplatePath = "/Users/mickeyxiaoliuliu/Desktop/DKU curriculums/cs206/ps2的一些模版/COMSCI_ECON206_PS2_A0_Poster_Template.pptx";
const skillDir = "/Users/mickeyxiaoliuliu/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations";
const runtimePython = "/Users/mickeyxiaoliuliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const outputVersion = process.env.POSTER_BUILD_VERSION ?? "v1";
const finalizerPath = path.join(buildDir, `finalized-${outputVersion}.pptx`);
const deliveryPath = path.join(submissionDir, "PS2_Yiqiao_Liu_review_ready_A0_poster.pptx");

const BLUE = "#003399";
const GREEN = "#006633";
const INK = "#212A33";
const MUTED = "#56616B";
const PALE = "#F4F6F8";
const WHITE = "#FFFFFF";
const FONT = "Calibri";

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(submissionDir, { recursive: true });
await fs.mkdir(path.join(workspaceDir, ".validation"), { recursive: true });

const templateBytes = await fs.readFile(sourceTemplatePath);
const templateSha256 = crypto.createHash("sha256").update(templateBytes).digest("hex");
const presentation = await PresentationFile.importPptx(await FileBlob.load(sourceTemplatePath));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 40000,
});
await fs.writeFile(path.join(buildDir, "template-before.ndjson"), snapshot.ndjson);

const records = snapshot.ndjson.trim().split("\n").filter(Boolean).map((line) => JSON.parse(line));
const idsByName = new Map(records.filter((r) => r.name && r.id).map((r) => [r.name, r.id]));
const get = (name) => {
  const id = idsByName.get(name);
  if (!id) throw new Error(`Template object not found: ${name}`);
  return presentation.resolve(id);
};
const slideRecord = records.find((r) => r.kind === "slide" && r.slide === 1);
if (!slideRecord) throw new Error("Template slide not found");
const slide = presentation.resolve(slideRecord.id);

function setText(name, value, style = {}) {
  const shape = get(name);
  shape.text = value;
  shape.text.style = {
    typeface: FONT,
    color: INK,
    alignment: "left",
    verticalAlignment: "top",
    autoFit: "shrinkText",
    wrap: "square",
    ...style,
  };
  return shape;
}

function setRichText(name, paragraphs, style = {}) {
  const shape = get(name);
  shape.text.set(paragraphs);
  shape.text.style = {
    typeface: FONT,
    color: INK,
    alignment: "left",
    verticalAlignment: "top",
    autoFit: "shrinkText",
    wrap: "square",
    ...style,
  };
  return shape;
}

function lead(label, text, spaceAfter = 450) {
  return {
    runs: [
      { run: label, textStyle: { bold: true, color: BLUE } },
      { run: text },
    ],
    spaceAfter,
  };
}

setText("version", "REVIEW-READY V1", { fontSize: 28, bold: true, color: GREEN, alignment: "right" });
setText("project-title", "Stay or Switch? Strategic Memory Portability\nin Competing AI Assistants", {
  fontSize: 108,
  bold: true,
  color: BLUE,
  lineSpacing: 0.91,
});
setText("authors", "Yiqiao Liu (Mickey), solo team, Team FP10", {
  fontSize: 48,
  bold: true,
  color: INK,
});
setText("course-instructor", "Course instructor: Professor Luyao Zhang", {
  fontSize: 38,
  color: INK,
});
setText("takeaway", "Portability can be socially valuable yet strategically absent. At the benchmark, lock-in and low-type portability are both pure Bayesian equilibria, while user switching remains an untested behavioral question.", {
  fontSize: 50,
  bold: true,
  color: WHITE,
  verticalAlignment: "middle",
  lineSpacing: 0.94,
});

setRichText("research-question", [
  lead("Shared question: ", "When do competing AI assistants with private implementation costs supply portable memory, and when does that availability improve user mobility?", 600),
  lead("Verified gap: ", "Switching-cost and compatibility research explains lock-in, but does not jointly test this Bayesian game, its welfare and incentive comparisons, and AI-user choice [1, 3].", 0),
], { fontSize: 35, lineSpacing: 0.95 });

setRichText("model", [
  lead("Players and timing: ", "Two platforms privately observe cost cᵢ in {.2, 1.2}, with Pr(cᵢ=.2)=.7, then simultaneously choose Portable (P) or Locked (L).", 480),
  lead("Payoffs: ", "EU(P|c)=3q-1-c and EU(L|c)=q.", 480),
  lead("Solution concept: ", "Bayesian Nash equilibrium fits private types [2]. Direct enumeration checks all 16 strategy profiles.", 0),
], { fontSize: 34, lineSpacing: 0.94 });

setRichText("lenses", [
  lead("Game theory: ", "Exactly two pure BNE, (LL,LL) and (PL,PL). The low-type mixed probability is 6/7.", 380),
  lead("Social choice: ", "At m=1, welfare is 0, 2.17, and 4 for LL, PL, and PP. PP is a comparator, not a BNE.", 380),
  lead("Mechanism design: ", "At p=.4, benefit τ=.4 weakly sustains PL. LL remains weak through τ=1.2.", 0),
], { fontSize: 32, lineSpacing: 0.93 });

setRichText("auction", [
  lead("Mapping: ", "One primary-assistant slot and two iid U[0,1] platform values.", 340),
  lead("Rules: ", "First price uses b(v;r)=(v²+r²)/(2v). Second price uses truthful bids [4].", 340),
  lead("Comparison: ", "Lowering the assumed reserve from .50 to .20 raises allocation from .75193 to .96004. Conditional efficiency is 1.", 340),
  lead("Boundary: ", "This is an allocation analogy. The user is not auctioned.", 0),
], { fontSize: 31, lineSpacing: 0.92 });

setText("research-design-label", "", { fontSize: 1 });
setText("research-design-prompt", "", { fontSize: 1 });
get("research-design-area").fill = PALE;
get("research-design-area").line = { style: "solid", fill: "#D5DCE2", width: 1 };

const diagramBoxes = [
  { name: "diagram-economics", left: 1465, title: "Economics", body: "Private costs\nBNE, welfare, incentive" },
  { name: "diagram-computation", left: 1975, title: "Computation", body: "16 profiles, PyGambit\nsweeps, seeded auction" },
  { name: "diagram-behavior", left: 2485, title: "Behavior", body: "12 fixed scenarios\nno participant inference" },
].map((item) => {
  const box = slide.shapes.add({
    geometry: "rect",
    name: item.name,
    position: { left: item.left, top: 1240, width: 430, height: 170 },
    fill: WHITE,
    line: { style: "solid", fill: BLUE, width: 2 },
  });
  box.text.set([
    [{ run: item.title, textStyle: { bold: true, color: BLUE, fontSize: "34pt" } }],
    [{ run: item.body, textStyle: { color: INK, fontSize: "27pt" } }],
  ]);
  box.text.style = {
    typeface: FONT,
    alignment: "center",
    verticalAlignment: "middle",
    autoFit: "shrinkText",
    lineSpacing: 0.94,
    insets: { top: 12, right: 10, bottom: 10, left: 10 },
  };
  return box;
});
slide.shapes.connect(diagramBoxes[0], diagramBoxes[1], {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: GREEN, width: 3 },
  head: { type: "triangle", width: "sm", length: "sm" },
});
slide.shapes.connect(diagramBoxes[1], diagramBoxes[2], {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: GREEN, width: 3 },
  head: { type: "triangle", width: "sm", length: "sm" },
});
const synthesis = slide.shapes.add({
  geometry: "textbox",
  name: "diagram-synthesis",
  position: { left: 1500, top: 1455, width: 1495, height: 135 },
  fill: "none",
  line: { fill: "none", width: 0 },
});
synthesis.text = "Availability, collective value, and user adoption require distinct evidence.";
synthesis.text.style = {
  typeface: FONT,
  fontSize: 34,
  bold: true,
  color: GREEN,
  alignment: "center",
  verticalAlignment: "middle",
  autoFit: "shrinkText",
};
setText("design-caption", "Figure 1. One evidence chain links platform incentives, reproducible verification, and a bounded future user test.", {
  fontSize: 31,
  color: MUTED,
  lineSpacing: 0.94,
});

setText("main-result-label", "", { fontSize: 1 });
setText("main-result-prompt", "", { fontSize: 1 });
get("main-result-area").fill = WHITE;
get("main-result-area").line = { style: "solid", fill: "#D5DCE2", width: 1 };
const resultTable = slide.tables.add({
  rows: 5,
  columns: 3,
  left: 1435,
  top: 1885,
  width: 1625,
  height: 600,
  columnWidths: [270, 970, 385],
  values: [
    ["Evidence", "Verified output", "Status"],
    ["Model", "Pure BNE: (LL,LL) and (PL,PL). Low-type mix: 6/7.", "Analytical and computed"],
    ["Welfare", "At m=1: WLL=0, WPL=2.17, WPP=4.", "PP is a comparator"],
    ["Incentive", "At p=.4, τ=.4 sustains PL. LL remains weak through τ=1.2.", "Threshold sweep"],
    ["Auction", "Allocation is .75193 at r=.50 and .96004 at r=.20.", "N=100,000, seed 20603"],
  ],
});
resultTable.rows[0].height = 78;
for (let i = 1; i < 5; i += 1) resultTable.rows[i].height = 130.5;
resultTable.borders.assign({ style: "solid", fill: "#B8C1C9", width: 1 });
resultTable.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 3 }).assign({
  fill: BLUE,
  textStyle: { typeface: FONT, fontSize: 30, bold: true, color: WHITE, alignment: "left" },
  margins: { top: 9, right: 12, bottom: 7, left: 12 },
  anchor: "middle",
});
resultTable.cells.block({ row: 1, column: 0, rowCount: 4, columnCount: 3 }).assign({
  textStyle: { typeface: FONT, fontSize: 27, color: INK, alignment: "left" },
  margins: { top: 8, right: 12, bottom: 8, left: 12 },
  anchor: "middle",
});
resultTable.cells.block({ row: 1, column: 0, rowCount: 4, columnCount: 1 }).assign({
  fill: "#EEF3FA",
  textStyle: { typeface: FONT, fontSize: 28, bold: true, color: BLUE, alignment: "left" },
});
resultTable.cells.block({ row: 1, column: 2, rowCount: 4, columnCount: 1 }).assign({
  fill: "#F0F7F3",
  textStyle: { typeface: FONT, fontSize: 25, color: GREEN, alignment: "left" },
});
setRichText("result-caption", [
  lead("Table 1. ", "Verified outputs at GitHub snapshot f9523b0.", 340),
  lead("Interpretation: ", "Portability can improve the collective comparator and allocation access while equilibrium multiplicity remains.", 340),
  lead("Verification: ", "PyGambit agreement, 85/85 tests, and seed 20603.", 340),
  lead("Evidence status: ", "Platform results are analytical or simulated. The user test has no participant data.", 0),
], { fontSize: 29, lineSpacing: 0.93 });

setRichText("real-world", [
  lead("Case: ", "A student or writer moving years of assistant context between platforms.", 450),
  lead("Decision: ", "Whether institutions and platforms should support secure export and import.", 450),
  lead("Potential benefit: ", "Lower switching friction and greater contestability.", 450),
  lead("Risks: ", "Privacy leakage, incomplete transfer, and inaccessible tools.", 450),
  lead("Evidence before adoption: ", "Transfer fidelity, security, access, and switching outcomes.", 0),
], { fontSize: 33, lineSpacing: 0.93 });

setRichText("interdisciplinary", [
  lead("Behavioral science: Hugging Face\n", "Twelve fixed scenarios compare initial and final Stay/Switch choices around g>r. Six predict each choice. The Space stores page-session aggregates only. No participant conclusion.", 600),
  lead("Computer science: GitHub\n", "Direct enumeration, a PyGambit cross-check, integer-built sweeps, a seeded auction simulation, and 85/85 tests make every result inspectable.", 600),
  lead("Integration\n", "The public artifact tests whether modeled portability translates into user mobility without changing the platform game.", 0),
], { fontSize: 31, lineSpacing: 0.92 });

setRichText("limits", [
  lead("Main limit: ", "Normalized costs and reserves are assumptions, not market estimates. The public Space has no participant dataset.", 420),
  lead("Next test: ", "Compare switching across portability scenarios while measuring privacy and personalization concerns.", 420),
  lead("Symposium question: ", "Which omitted concern is most likely to overturn the benchmark?", 0),
], { fontSize: 31, lineSpacing: 0.92 });

setText("ack", "Course instructor: Professor Luyao Zhang. Official PS2 template, open-source Python and PyGambit tools, and OpenAI Codex assistance for drafting, implementation, and QA. Yiqiao Liu remains responsible for all claims.", {
  fontSize: 25,
  color: INK,
  lineSpacing: 0.92,
});

setText("references", [
  "[1] Farrell, J., & Klemperer, P. (2007). Coordination and lock-in. Handbook of Industrial Organization. doi:10.1016/S1573-448X(06)03031-7",
  "[2] Harsanyi, J. C. (1968). Games with incomplete information, II. Management Science, 14(5), 320-334. doi:10.1287/mnsc.14.5.320",
  "[3] Jeon, D.-S., Menicucci, D., & Nasr, N. (2023). Compatibility choices, switching costs, and data portability. AEJ Microeconomics, 15(1), 30-73. doi:10.1257/mic.20200309",
  "[4] Vickrey, W. (1961). Counterspeculation, auctions, and competitive sealed tenders. Journal of Finance, 16(1), 8-37. doi:10.1111/j.1540-6261.1961.tb02789.x",
], { fontSize: 18, color: INK, lineSpacing: 0.91 });

const hfUrl = "https://huggingface.co/spaces/mickeystk/ps2-stay-or-switch-memory-portability";
const githubUrl = "https://github.com/micL1222/gt-tools-demos/tree/ps2-memory-portability";
const access = setRichText("access-links", [
  { runs: [{ run: "Hugging Face: ", textStyle: { bold: true, color: BLUE } }, { run: hfUrl, textStyle: { color: BLUE, underline: "sng" }, link: { uri: hfUrl, isExternal: true } }], spaceAfter: 260 },
  { runs: [{ run: "GitHub: ", textStyle: { bold: true, color: GREEN } }, { run: githubUrl, textStyle: { color: GREEN, underline: "sng" }, link: { uri: githubUrl, isExternal: true } }] },
], { fontSize: 18, lineSpacing: 0.9, color: INK });
access.position = { left: 3193.86, top: 2975, width: 880, height: 125 };

setText("hf-qr-label", "HF", { fontSize: 18, bold: true, color: BLUE, alignment: "center", verticalAlignment: "middle" });
get("hf-qr-label").position = { left: 4118.86, top: 3076, width: 92, height: 28 };
setText("github-qr-label", "GH", { fontSize: 18, bold: true, color: GREEN, alignment: "center", verticalAlignment: "middle" });
get("github-qr-label").position = { left: 4251.86, top: 3076, width: 92, height: 28 };

const hfQr = await fs.readFile(path.join(posterDir, "assets", "hugging_face_qr.png"));
const ghQr = await fs.readFile(path.join(posterDir, "assets", "github_qr.png"));
slide.images.add({
  blob: hfQr,
  contentType: "image/png",
  alt: `QR code for ${hfUrl}`,
  fit: "contain",
  position: { left: 4118.86, top: 2982, width: 92, height: 92 },
});
slide.images.add({
  blob: ghQr,
  contentType: "image/png",
  alt: `QR code for ${githubUrl}`,
  fit: "contain",
  position: { left: 4251.86, top: 2982, width: 92, height: 92 },
});

setText("format-note", "A0 landscape, 1189 × 841 mm. Editable PPTX and PDF. Actual evidence remains separate from planned tests.", {
  fontSize: 24,
  color: MUTED,
});

slide.speakerNotes.append([
  "",
  "Poster evidence record, review-ready v1:",
  "Paper baseline: commit 43a2941184d8130852af3c1f88fc90e8b2fd9fc6.",
  "Model/output evidence: ps2_memory_portability/outputs and tests at snapshot f9523b0.",
  "Public URLs returned HTTP 200 on 2026-09-26: " + hfUrl + " and " + githubUrl + ".",
  "QR targets were generated locally and decoded back to the displayed URLs.",
  "No participant result, symposium feedback, or classroom auction-play evidence is claimed.",
].join("\n"));

const preview = await slide.export({ format: "png", scale: 1 });
await fs.writeFile(path.join(buildDir, `poster-${outputVersion}.png`), new Uint8Array(await preview.arrayBuffer()));
const layout = await slide.export({ format: "layout" });
await fs.writeFile(path.join(buildDir, `poster-${outputVersion}.layout.json`), await layout.text());
const after = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 50000,
});
await fs.writeFile(path.join(buildDir, `poster-${outputVersion}.inspect.ndjson`), after.ndjson);

const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools", "artifact_tool_utils.mjs"),
).href);
const stagingDir = path.join(buildDir, `.finalizer-${outputVersion}`);
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const result = await finalizePresentation({
  explicitTotalSlideCount: 1,
  requiredNativeTableOwnerSlides: [1],
  requiredNativeChartOwnerSlides: [],
  sourceTemplatePath,
  requiredTemplateReferenceSlides: [1],
  minimumTemplateCoverageRatio: 0.7,
  requireExactTemplateDimensions: true,
  workspaceDir,
  candidatePath,
  finalPath: finalizerPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "42804000,30276000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--require-native-table-slide", "1",
  ],
  fontPolicy: {
    basis: "reference",
    families: ["Calibri"],
    referencePath: sourceTemplatePath,
    referenceSha256: templateSha256,
  },
  verifyArtifactToolImport: true,
  receiptPath: path.join(workspaceDir, ".validation", `poster-${outputVersion}.json`),
});
await fs.copyFile(finalizerPath, deliveryPath);
console.log(JSON.stringify({ deliveryPath, finalizerPath, templateSha256, result }, null, 2));
