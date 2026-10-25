import {generateAuthenticationKeyForLogin} from "./security/keyDer.js"
import {BASE_URL} from "./security/baseUrl.js"

const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("login");
const loginError = document.getElementById("loginError");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    loginButton.disabled = true;
    loginError.hidden = true;

    try {
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;
        const salt = await getUserSalt(username);
        const authenticationKey = await generateAuthenticationKeyForLogin(password, salt);
        const token = await login(username, authenticationKey);
        localStorage.setItem("token", token);
        window.location.href = "index.html";
    } catch (error) {
        loginError.textContent = error.message || "Login failed. Please try again.";
        loginError.hidden = false;
        loginButton.disabled = false;
    }
});

async function getUserSalt(username) {
    const response = await fetch(`${BASE_URL}/user/${encodeURIComponent(username)}/salt`);
    if (!response.ok) {
        throw new Error("Unable to find that account. Check your username and try again.");
    }

    const data = await response.json();
    if (!data.salt) {
        throw new Error("The server did not return the account salt.");
    }
    return data.salt;
}

async function login(username, authenticationKey) {
    const formData = new URLSearchParams({
        username,
        password: authenticationKey,
    });
    const response = await fetch(`${BASE_URL}/user/token`, {
        body: formData,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method: "POST",
    });
    if (!response.ok) {
        throw new Error("Login failed. Check your username and password.");
    }

    const data = await response.json();
    if (!data.access_token || !data.token_type) {
        throw new Error("The server returned an invalid login response.");
    }
    return `${data.token_type} ${data.access_token}`;
}
