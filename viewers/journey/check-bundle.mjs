// Fails when the committed bundle is not what the source builds to.
//
// The bundle in plugins/aipos/skills/aipos-map-render/scripts/assets is what
// ships, so it is reviewed as generated code. This rebuilds it into a temporary
// folder and compares byte for byte; run `npm run build` and commit if it fails.
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const committed = resolve(here, "../../plugins/aipos/skills/aipos-map-render/scripts/assets");
const fresh = mkdtempSync(join(tmpdir(), "journey-viewer-"));
execFileSync(process.execPath, [join(here, "build.mjs")], {
  env: { ...process.env, JOURNEY_VIEWER_OUT: fresh }, stdio: "ignore",
});

let stale = [];
for (const f of ["journey-viewer.js", "journey-viewer.css", "THIRD_PARTY_NOTICES.txt"]) {
  let a = null;
  try { a = readFileSync(join(committed, f)); } catch { /* missing counts as stale */ }
  if (!a || !a.equals(readFileSync(join(fresh, f)))) stale.push(f);
}
if (stale.length) {
  console.error(`stale: ${stale.join(", ")}. Run \`npm run build\` in viewers/journey and commit the result.`);
  process.exit(1);
}
console.log("committed bundle matches the source");
