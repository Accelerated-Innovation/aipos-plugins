// Entry point. Reads the graph render_map.py embedded in the page and mounts the
// diagram over the fallback tables' placeholder. If anything here fails, the
// page still has the tables, and says so.
import { createRoot } from "react-dom/client";
import "@xyflow/react/dist/style.css";
import "./viewer.css";
import { App } from "./App.jsx";

function mount() {
  const root = document.getElementById("journey-root");
  const data = document.getElementById("journey-data");
  if (!root || !data) return;
  try {
    const { graph, config } = JSON.parse(data.textContent);
    document.documentElement.classList.add("jv-ready");
    createRoot(root).render(<App graph={graph} config={config || {}} />);
    // The tables start open so they are there without script. Once the diagram
    // is up they collapse to a "Table view" disclosure, and reopen for printing,
    // because a canvas does not print and the tables do.
    const tables = document.querySelectorAll("details.wftables");
    tables.forEach((d) => d.removeAttribute("open"));
    const wasOpen = new Map();
    window.addEventListener("beforeprint", () => tables.forEach((d) => { wasOpen.set(d, d.open); d.open = true; }));
    window.addEventListener("afterprint", () => tables.forEach((d) => { d.open = wasOpen.get(d) ?? false; }));
  } catch (err) {
    document.documentElement.classList.remove("jv-ready");
    root.textContent = "The interactive diagram could not load; the tables below show the same journeys.";
    console.error(err);
  }
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
else mount();
