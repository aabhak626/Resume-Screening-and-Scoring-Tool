import { renderUploadResume } from "../components/UploadResume.js";
import { renderUploadJD } from "../components/UploadJD.js";
import { renderJDSelector } from "../components/JDSelector.js";
import { renderResultsTable } from "../components/ResultsTable.js";
import { getStoredEmail } from "../services/api.js";

export function renderDashboardPage(root, { role, onLogout }) {
    root.innerHTML = `
        <div class="card">
            <div class="row" style="justify-content: space-between;">
                <div>
                    <h1 class="page-title">Dashboard</h1>
                    <p class="muted">Signed in as ${getStoredEmail() || "Unknown"} (${role})</p>
                </div>
                <button id="logout-button" class="secondary">Logout</button>
            </div>
        </div>
        <div id="dashboard-content" class="stack"></div>
    `;

    root.querySelector("#logout-button").addEventListener("click", onLogout);

    const content = root.querySelector("#dashboard-content");

    if (role === "admin") {
        renderAdminDashboard(content);
        return;
    }

    renderUserDashboard(content);
}

function renderUserDashboard(container) {
    container.innerHTML = `
        <div class="card">
            <h2 class="section-title">Upload Resume</h2>
            <div id="resume-upload"></div>
        </div>
    `;

    renderUploadResume(container.querySelector("#resume-upload"));
}

function renderAdminDashboard(container) {
    container.innerHTML = `
        <div class="card">
            <h2 class="section-title">Upload Job Description</h2>
            <div id="jd-upload"></div>
        </div>
        <div class="card">
            <h2 class="section-title">Select Job Description</h2>
            <div id="jd-selector"></div>
            <div class="row" style="margin-top: 12px;">
                <button id="run-screening">Run Screening</button>
            </div>
        </div>
        <div class="card">
            <h2 class="section-title">Results</h2>
            <div id="results-table">
                <p class="muted">Choose a JD and click "Run Screening".</p>
            </div>
        </div>
    `;

    renderUploadJD(container.querySelector("#jd-upload"), async () => {
        await selector.refresh();
    });

    const selector = renderJDSelector(container.querySelector("#jd-selector"));
    const resultsContainer = container.querySelector("#results-table");

    container.querySelector("#run-screening").addEventListener("click", async () => {
        const jdId = selector.getSelectedJD();

        if (!jdId) {
            alert("Please select a job description first.");
            return;
        }

        await renderResultsTable(resultsContainer, jdId);
    });
}
