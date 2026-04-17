import { renderLoginPage } from "./pages/Login.js";
import { renderDashboardPage } from "./pages/Dashboard.js";
import { getStoredRole, getToken, logoutUser } from "./services/api.js";

function renderRoute() {
    const root = document.getElementById("app");
    if (!root) {
        return;
    }

    const token = getToken();
    const role = getStoredRole();

    if (!token || !role) {
        renderLoginPage(root, renderRoute);
        return;
    }

    renderDashboardPage(root, {
        role,
        onLogout: () => {
            logoutUser();
            renderRoute();
        },
    });
}

export function renderApp() {
    window.addEventListener("hashchange", renderRoute);
    renderRoute();
}
