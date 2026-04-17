const API_BASE_URL = "http://127.0.0.1:8000";

export function getToken() {
    return localStorage.getItem("token") || "";
}

export function getStoredRole() {
    return localStorage.getItem("role") || "";
}

export function getStoredEmail() {
    return localStorage.getItem("email") || "";
}

export function getAuthHeaders() {
    return {
        Authorization: "Bearer " + getToken(),
    };
}

export function logoutUser() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("email");
}

export async function loginUser(email, password) {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
    });

    const data = await parseJsonResponse(response);

    if (!data.access_token) {
        throw new Error("Login token missing in response");
    }

    const payload = decodeJwtPayload(data.access_token);
    const role = data.user?.role || payload.role || "";
    const storedEmail = data.user?.email || payload.sub || email;

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", role);
    localStorage.setItem("email", storedEmail);

    return data;
}

export async function uploadResume(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/user/upload-resume`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData,
    });

    return parseJsonResponse(response);
}

export async function uploadJD(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/hr/upload-jd`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData,
    });

    return parseJsonResponse(response);
}

export async function fetchJDs() {
    const response = await fetch(`${API_BASE_URL}/hr/jds`, {
        headers: getAuthHeaders(),
    });

    return parseJsonResponse(response);
}

export async function fetchScreeningResults(jdId) {
    const response = await fetch(`${API_BASE_URL}/hr/screen/${jdId}`, {
        headers: getAuthHeaders(),
    });

    return parseJsonResponse(response);
}

async function parseJsonResponse(response) {
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || data.error || "API request failed");
    }

    return data;
}

function decodeJwtPayload(token) {
    try {
        const payloadPart = token.split(".")[1];
        if (!payloadPart) {
            return {};
        }

        const base64 = payloadPart.replace(/-/g, "+").replace(/_/g, "/");
        const normalized = decodeURIComponent(
            atob(base64)
                .split("")
                .map((char) => "%" + char.charCodeAt(0).toString(16).padStart(2, "0"))
                .join("")
        );

        return JSON.parse(normalized);
    } catch {
        return {};
    }
}
