import fs from "node:fs/promises";
import path from "node:path";

const assetDir = path.join(process.cwd(), "assets");
await fs.mkdir(assetDir, { recursive: true });

const targets = [
  {
    label: "Hugging Face",
    value: "https://huggingface.co/spaces/mickeystk/ps2-stay-or-switch-memory-portability",
    file: "hugging_face_qr.png",
  },
  {
    label: "GitHub",
    value: "https://github.com/micL1222/gt-tools-demos/tree/ps2-memory-portability",
    file: "github_qr.png",
  },
];

for (const target of targets) {
  const endpoint = new URL("https://api.qrserver.com/v1/create-qr-code/");
  endpoint.searchParams.set("size", "1024x1024");
  endpoint.searchParams.set("margin", "20");
  endpoint.searchParams.set("ecc", "M");
  endpoint.searchParams.set("data", target.value);
  const response = await fetch(endpoint);
  if (!response.ok) throw new Error(`QR generation failed for ${target.label}: HTTP ${response.status}`);
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("image/png")) throw new Error(`Unexpected QR response type: ${contentType}`);
  await fs.writeFile(path.join(assetDir, target.file), new Uint8Array(await response.arrayBuffer()));
  console.log(`CREATED ${target.label}: ${target.value}`);
}
