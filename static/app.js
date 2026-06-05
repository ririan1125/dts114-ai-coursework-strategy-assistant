const form = document.getElementById("taskForm");
const saveBtn = document.getElementById("saveBtn");
const sampleBtn = document.getElementById("sampleBtn");
const docsBtn = document.getElementById("docsBtn");
const refreshBtn = document.getElementById("refreshBtn");
const toast = document.getElementById("toast");

const priorityLabel = document.getElementById("priorityLabel");
const priorityScore = document.getElementById("priorityScore");
const hoursLeft = document.getElementById("hoursLeft");
const strategyList = document.getElementById("strategyList");
const riskList = document.getElementById("riskList");
const taskList = document.getElementById("taskList");
const docsOutput = document.getElementById("docsOutput");
const healthStatus = document.getElementById("healthStatus");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2600);
}

function getPayload() {
  return {
    title: document.getElementById("title").value.trim(),
    deadline: document.getElementById("deadline").value,
    importance: Number(document.getElementById("importance").value),
    complexity: Number(document.getElementById("complexity").value),
    estimated_hours: Number(document.getElementById("estimatedHours").value),
    notes: document.getElementById("notes").value.trim()
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `${response.status} ${response.statusText}`);
  }
  return data;
}

function renderStrategy(result) {
  priorityLabel.textContent = result.priority_label || "unknown";
  priorityScore.textContent = result.priority_score ?? 0;
  hoursLeft.textContent = result.hours_left ?? 0;

  strategyList.innerHTML = "";
  (result.strategy || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    strategyList.appendChild(li);
  });

  riskList.innerHTML = "";
  (result.risk_flags || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    riskList.appendChild(li);
  });
}

async function previewStrategy() {
  const data = await api("/api/strategy", {
    method: "POST",
    body: JSON.stringify(getPayload())
  });
  renderStrategy(data);
  showToast(data.llm_used ? "LLM-assisted strategy generated" : "Deterministic strategy generated");
}

async function saveTask() {
  const data = await api("/api/tasks", {
    method: "POST",
    body: JSON.stringify(getPayload())
  });
  renderStrategy(data.item.strategy);
  await loadTasks();
  showToast("Task saved");
}

function renderTasks(items) {
  taskList.innerHTML = "";
  if (!items.length) {
    taskList.innerHTML = "<p>No saved tasks yet.</p>";
    return;
  }
  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = `task-item ${item.strategy?.priority_label || ""}`;
    div.innerHTML = `
      <h3>${escapeHtml(item.title)}</h3>
      <p>Priority: ${escapeHtml(item.strategy?.priority_label || "unknown")} | Score: ${escapeHtml(item.strategy?.priority_score ?? 0)} | Deadline: ${escapeHtml(item.deadline)}</p>
    `;
    taskList.appendChild(div);
  });
}

async function loadTasks() {
  const data = await api("/api/tasks");
  renderTasks(data.items || []);
}

async function generateDocs() {
  const tasks = await api("/api/tasks");
  const data = await api("/api/sdlc-documents", {
    method: "POST",
    body: JSON.stringify({ tasks: tasks.items || [] })
  });
  docsOutput.textContent = JSON.stringify(data, null, 2);
  showToast("SDLC snapshot generated");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setDefaultDeadline() {
  const date = new Date();
  date.setDate(date.getDate() + 2);
  date.setHours(23, 59, 0, 0);
  document.getElementById("deadline").value = date.toISOString().slice(0, 16);
}

async function checkHealth() {
  try {
    await api("/health");
    healthStatus.textContent = "API online";
  } catch {
    healthStatus.textContent = "API offline";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await previewStrategy();
  } catch (error) {
    showToast(error.message);
  }
});

saveBtn.addEventListener("click", async () => {
  try {
    await saveTask();
  } catch (error) {
    showToast(error.message);
  }
});

sampleBtn.addEventListener("click", () => {
  document.getElementById("title").value = "DTS114TC Report and Software Coursework";
  document.getElementById("importance").value = 5;
  document.getElementById("complexity").value = 5;
  document.getElementById("estimatedHours").value = 16;
  document.getElementById("notes").value = "Need Notebook, Flask API, website, generated image, UML, tests, CI/CD, deployment screenshots, and handwritten report evidence.";
  setDefaultDeadline();
  showToast("Sample loaded");
});

docsBtn.addEventListener("click", generateDocs);
refreshBtn.addEventListener("click", loadTasks);

setDefaultDeadline();
checkHealth();
loadTasks();
generateDocs();

window.addEventListener("load", () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
});

