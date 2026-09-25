import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { layout, SIZES } from "../src/layout.js";
import { visibleGraph } from "../src/model.js";

const graph = JSON.parse(readFileSync(new URL("./fixtures/two-journeys.graph.json", import.meta.url)));

function overlaps(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

describe("layout", () => {
  for (const level of [1, 2, 3]) {
    it(`no two nodes overlap at L${level}`, () => {
      const v = visibleGraph(graph, { level });
      const pos = layout(v.nodes, v.edges);
      const boxes = v.nodes.map((n) => ({ id: n.id, ...pos.get(n.id), w: SIZES[n.kind].width, h: SIZES[n.kind].height }));
      for (let i = 0; i < boxes.length; i++) {
        for (let j = i + 1; j < boxes.length; j++) {
          expect(overlaps(boxes[i], boxes[j]), `${boxes[i].id} / ${boxes[j].id}`).toBe(false);
        }
      }
    });
  }

  it("customer order runs left to right", () => {
    const v = visibleGraph(graph, { level: 1, journey: "invoice-approval" });
    const pos = layout(v.nodes, v.edges);
    const x = (a) => pos.get(`j:invoice-approval/a:${a}`).x;
    expect(x("submit")).toBeLessThan(x("route"));
    expect(x("route")).toBeLessThan(x("approve"));
  });

  it("a pinned position wins over the layout", () => {
    const v = visibleGraph(graph, { level: 1 });
    const pos = layout(v.nodes, v.edges, { "j:invoice-approval/a:route": { x: 5, y: 7 } });
    expect(pos.get("j:invoice-approval/a:route")).toEqual({ x: 5, y: 7 });
  });
});
