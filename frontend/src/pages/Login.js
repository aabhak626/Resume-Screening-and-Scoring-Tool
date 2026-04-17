import { loginUser } from "../services/api.js";

export function renderLoginPage(root, onLoginSuccess) {
    root.innerHTML = `
        <div class="card" style="max-width: 420px; margin: 48px auto;">
            <h1 class="page-title">Login</h1>
            <div class="stack">
                <input id="email" type="email" placeholder="Email" />
                <input id="password" type="password" placeholder="Password" />
                <button id="login-button">Login</button>
            </div>
        </div>
    `;

    const emailInput = root.querySelector("#email");
    const passwordInput = root.querySelector("#password");
    const loginButton = root.querySelector("#login-button");

    loginButton.addEventListener("click", async () => {
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            alert("Please enter email and password.");
            return;
        }

        loginButton.disabled = true;
        loginButton.textContent = "Logging in...";

        try {
            await loginUser(email, password);
            onLoginSuccess();
        } catch (error) {
            alert(error.message || "Login failed");
        } finally {
            loginButton.disabled = false;
            loginButton.textContent = "Login";
        }
    });
}
