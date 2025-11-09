// ---------------- CONFIG ----------------
const API_BASE = "http://127.0.0.1:8000"; // FastAPI backend root URL

// ---------------- HTTP HELPER ----------------
async function http(path, opts = {}) {
  const token = localStorage.getItem("jwt");

  const fullUrl = path.startsWith("http")
    ? path
    : `${API_BASE}${path.startsWith("/") ? path : "/" + path}`;

  const res = await fetch(fullUrl, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opts.headers || {}),
    },
  });

  if (!res.ok) {
    let msg;
    try {
      const data = await res.json();
      msg = data.message || data.detail || res.statusText;
    } catch {
      msg = `HTTP ${res.status}`;
    }
    throw new Error(msg);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : {};
}

// ---------------- AUTH ----------------
async function login() {
  const email = document.getElementById("email")?.value.trim();
  const password = document.getElementById("password")?.value.trim();
  const err = document.getElementById("error");
  if (err) err.textContent = "";

  if (!email || !password) {
    if (err) err.textContent = "Please enter email and password.";
    return;
  }

  try {
    const data = await http("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    const token = data.access_token;
    const role = data.role?.toLowerCase() || "patient";

    if (!token) throw new Error("Invalid credentials");

    localStorage.setItem("jwt", token);
    localStorage.setItem("role", role);
    localStorage.setItem("email", email);

    // Redirect based on role (lowercase, consistent paths)
    if (role === "caretaker") {
      window.location.href = "./caretaker/Dashboard.html";
    } else {
      window.location.href = "./patient/Dashboard.html";
    }
  } catch (e) {
    console.error("Login error:", e);
    if (err) err.textContent = e.message || "Login failed.";
  }
}

async function register() {
  const name = document.getElementById("name")?.value.trim();
  const email = document.getElementById("email")?.value.trim();
  const password = document.getElementById("password")?.value.trim();
  const role =
    document.getElementById("role")?.value.trim().toLowerCase() || "patient";
  const err = document.getElementById("error");
  if (err) err.textContent = "";

  if (!name || !email || !password) {
    if (err) err.textContent = "Please fill all fields.";
    return;
  }

  try {
    await http("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role }),
    });
    alert("Registration successful! Please login.");
    window.location.href = "index.html";
  } catch (e) {
    console.error("Register error:", e);
    if (err) err.textContent = e.message || "Registration failed.";
  }
}

function logout() {
  localStorage.removeItem("jwt");
  localStorage.removeItem("role");
  localStorage.removeItem("email");
  window.location.href = "../index.html";
}

// ---------------- DASHBOARD PROTECTION + HYDRATION ----------------
function protectAndHydrateDashboard() {
  const token = localStorage.getItem("jwt");
  const role = localStorage.getItem("role");
  const email = localStorage.getItem("email") || "";

  // Redirect if not logged in
  if (!token || !role) {
    alert("Please login to continue.");
    window.location.href = "../index.html";
    return;
  }

  const path = window.location.pathname.toLowerCase();

  // Patient-only pages
  const patientPages = [
    "/frontend/patient/dashboard.html",
    "/frontend/patient/mood.html",
    "/frontend/patient/reminders.html",
    "/frontend/patient/sos.html",
  ];

  // Caretaker-only pages
  const caretakerPages = [
    "/frontend/caretaker/dashboard.html",
    "/frontend/caretaker/reminders.html",
    "/frontend/caretaker/logs.html",
    "/frontend/caretaker/patientoverview.html",
  ];

  // Role checks
  if (role === "patient" && caretakerPages.some((p) => path.endsWith(p))) {
    alert("Access denied. Only caretakers allowed.");
    window.location.href = "../index.html";
    return;
  }

  if (role === "caretaker" && patientPages.some((p) => path.endsWith(p))) {
    alert("Access denied. Only patients allowed.");
    window.location.href = "../index.html";
    return;
  }

  // Personalization
  const welcome = document.getElementById("welcome");
  const subtitle = document.getElementById("subtitle");

  if (welcome) {
    welcome.textContent =
      role === "caretaker"
        ? "Welcome back, Caretaker 💙"
        : "Welcome, dear friend 💜";
  }

  if (subtitle) subtitle.textContent = `Signed in as ${email}`;
}

// ---------------- DYNAMIC DATA ----------------
// Reminders (used by both roles)
async function fetchReminders() {
  try {
    const data = await http("/api/reminders");
    console.log("Reminders:", data);
    return data;
  } catch (e) {
    console.warn("Failed to fetch reminders:", e.message);
    return [];
  }
}

// Logs (caretaker only)
async function fetchLogs() {
  try {
    const data = await http("/api/logs");
    console.log("Logs:", data);
    return data;
  } catch (e) {
    console.warn("Failed to fetch logs:", e.message);
    return [];
  }
}

// Render reminders dynamically
async function renderReminders(containerId) {
  const list = document.getElementById(containerId);
  if (!list) return;

  const reminders = await fetchReminders();
  if (!reminders.length) {
    list.innerHTML = `<p class="text-gray-500 text-center">No reminders found.</p>`;
    return;
  }

  list.innerHTML = reminders
    .map(
      (r) => `
      <div class="bg-white shadow rounded-2xl p-5 transition hover:shadow-md">
        <h4 class="text-lg font-bold text-[#3a2e6e]">${r.patient_name || "Unknown"}</h4>
        <p class="text-sm text-gray-600">${r.text}</p>
        <p class="text-xs text-gray-400">${r.time || "Not specified"}</p>
      </div>`
    )
    .join("");
}

// Render logs dynamically
async function renderLogs(containerId) {
  const list = document.getElementById(containerId);
  if (!list) return;

  const logs = await fetchLogs();
  if (!logs.length) {
    list.innerHTML = `<p class="text-gray-500 text-center">No logs found yet.</p>`;
    return;
  }

  list.innerHTML = logs
    .map(
      (l) => `
      <div class="bg-white rounded-2xl p-5 shadow-md hover:shadow-lg">
        <h4 class="text-lg font-bold text-[#3a2e6e]">${l.patient_name}</h4>
        <p class="text-gray-500">${l.mood || "No mood data"}</p>
        <p class="text-gray-400 text-sm">${l.timestamp || "Unknown time"}</p>
        <p class="mt-2 text-sm">📝 ${l.notes || "No notes provided"}</p>
      </div>`
    )
    .join("");
}

// ---------------- EXPORT ----------------
window.login = login;
window.register = register;
window.logout = logout;
window.protectAndHydrateDashboard = protectAndHydrateDashboard;
window.renderReminders = renderReminders;
window.renderLogs = renderLogs;
