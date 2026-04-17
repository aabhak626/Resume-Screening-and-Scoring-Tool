import { uploadResume } from "../services/api.js";

export function renderUploadResume(container) {
    container.innerHTML = `
        <div class="row">
            <input id="resume-file" type="file" accept=".pdf,.doc,.docx" />
            <button id="resume-upload-button">Upload Resume</button>
        </div>
    `;

    const fileInput = container.querySelector("#resume-file");
    const button = container.querySelector("#resume-upload-button");

    button.addEventListener("click", async () => {
        const file = fileInput.files[0];

        if (!file) {
            alert("Please choose a resume file.");
            return;
        }

        button.disabled = true;
        button.textContent = "Uploading...";

        try {
            const result = await uploadResume(file);
            alert(result.message || "Resume uploaded successfully.");
            fileInput.value = "";
        } catch (error) {
            alert(error.message || "Resume upload failed");
        } finally {
            button.disabled = false;
            button.textContent = "Upload Resume";
        }
    });
}
