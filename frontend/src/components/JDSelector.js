import { fetchJDs } from "../services/api.js";

export function renderJDSelector(container) {
    container.innerHTML = `
        <select id="jd-select">
            <option value="">Loading job descriptions...</option>
        </select>
    `;

    const select = container.querySelector("#jd-select");

    async function refresh() {
        try {
            const jds = await fetchJDs();

            if (!jds.length) {
                select.innerHTML = `<option value="">No job descriptions found</option>`;
                return;
            }

            select.innerHTML = `
                <option value="">Select a job description</option>
                ${jds
                    .map(
                        (jd) =>
                            `<option value="${jd.id}">${jd.file_path}</option>`
                    )
                    .join("")}
            `;
        } catch (error) {
            select.innerHTML = `<option value="">Unable to load job descriptions</option>`;
            alert(error.message || "Failed to load job descriptions");
        }
    }

    refresh();

    return {
        refresh,
        getSelectedJD() {
            return select.value;
        },
    };
}
