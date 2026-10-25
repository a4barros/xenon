import {generateAuthenticationKey, generateMasterKey} from "./security/keyGen.js"
import {protectMasterKey, protectVault} from "./security/encryption.js"
import {BASE_URL} from "./security/baseUrl.js"


const createAccountForm = document.getElementById("createAccountForm");
const createAccountButton = document.getElementById("createAccount");
const createAccountError = document.getElementById("createAccountError");

createAccountForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    createAccountButton.disabled = true;
    createAccountError.hidden = true;

    try {
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;
        const vaultPassword = document.getElementById("vaultPassword").value;

        const authenticationKey = await generateAuthenticationKey(password);
        const masterKey = await generateMasterKey();
        const protectedMasterKey = await protectMasterKey(masterKey, vaultPassword);
        const vault = createVault();
        const protectedVault = await protectVault(vault, masterKey);

        await sendProtectedPayloadToServer(username, authenticationKey, protectedMasterKey, protectedVault);
        window.location.href = "login.html";
    } catch (error) {
        createAccountError.textContent = error.message || "Account creation failed. Please try again.";
        createAccountError.hidden = false;
        createAccountButton.disabled = false;
    }
});

async function sendProtectedPayloadToServer(username, authenticationKey, protectedMasterKey, protectedVault) {
    const payload = {
        "username": username,
        "authentication_key": authenticationKey.authentication_key,
        "salt": authenticationKey.salt,
        "protected_master_key": protectedMasterKey,
        "protected_vault": protectedVault
    }
    const response = await fetch(`${BASE_URL}/user/`, {
        "body": JSON.stringify(payload),
        "headers": {
            "Content-Type": "application/json",
        },
        "method": "POST",
    });

    if (response.status === 409) {
        throw new Error("An account with that username already exists.");
    }
    if (!response.ok) {
        throw new Error(`Account creation failed (${response.status}). Please try again.`);
    }
}

function createVault() {
    return {
        "version": "1",
        "contents": [
            {
                "name": "example",
                "username": "user",
                "password": "123",
                "totpKey": null,
                "notes": "",
                "createdOn": "2020-01-01",
                "updatedOn": "2020-01-01",
                "trashedOn": null
            }
        ]
    }
}