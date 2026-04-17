import { fetchScreeningResults } from "../services/api.js";

export async function renderResultsTable(container, jdId) {
    container.innerHTML = `<p class="muted">Running screening...</p>`;

    try {
        const results = await fetchScreeningResults(jdId);

        if (!results.length) {
            container.innerHTML = `<p class="muted">No results found.</p>`;
            return;
        }

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Explanation</th>
                        <th>Reasons</th>
                    </tr>
                </thead>
                <tbody>
                    ${results
                        .map(
                            (result) => `
                                <tr>
                                    <td>${escapeHtml(result.name || "")}</td>
                                    <td>${escapeHtml(result.status || "")}</td>
                                    <td>${escapeHtml(String(result.score ?? ""))}</td>
                                    <td>${escapeHtml(result.explanation || "")}</td>
                                    <td>${escapeHtml((result.reasons || []).join(", "))}</td>
                                </tr>
                            `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        container.innerHTML = `<p class="muted">Could not load results.</p>`;
        alert(error.message || "Failed to fetch screening results");
    }
}

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
