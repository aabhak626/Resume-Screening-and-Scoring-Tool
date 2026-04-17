import { uploadJD } from "../services/api.js";

export function renderUploadJD(container, onUploaded) {
    container.innerHTML = `
        <div class="row">
            <input id="jd-file" type="file" accept=".pdf,.doc,.docx" />
            <button id="jd-upload-button">Upload JD</button>
        </div>
    `;

    const fileInput = container.querySelector("#jd-file");
    const button = container.querySelector("#jd-upload-button");

    button.addEventListener("click", async () => {
        const file = fileInput.files[0];

        if (!file) {
            alert("Please choose a JD file.");
            return;
        }

        button.disabled = true;
        button.textContent = "Uploading...";

        try {
            const result = await uploadJD(file);
            alert(result.message || "JD uploaded successfully.");
            fileInput.value = "";

            if (onUploaded) {
                await onUploaded();
            }
        } catch (error) {
            alert(error.message || "JD upload failed");
        } finally {
            button.disabled = false;
            button.textContent = "Upload JD";
        }
    });
}
