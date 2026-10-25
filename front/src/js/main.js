import {BASE_URL} from "./security/baseUrl.js"
import {createVaultSession} from "./vaultSession.js"

const token = localStorage.getItem("token");
if (!token) {
    window.location.replace("login.html");
}

const session = createVaultSession({baseUrl: BASE_URL, token});
const unlockForm = document.getElementById("unlockForm");
const unlockButton = document.getElementById("unlock");
const vaultPasswordInput = document.getElementById("vaultPassword");
const vaultError = document.getElementById("vaultError");
const vaultStatus = document.getElementById("vaultStatus");
const vaultContents = document.getElementById("vaultContents");
const addSecretButton = document.getElementById("addSecret");
const editor = document.getElementById("secretEditor");
const secretForm = document.getElementById("secretForm");
const editorTitle = document.getElementById("editorTitle");
const editorError = document.getElementById("editorError");
const saveSecretButton = document.getElementById("saveSecret");
const fieldIds = {
    name: "secretName",
    username: "secretUsername",
    password: "secretPassword",
    totpKey: "secretTotpKey",
    notes: "secretNotes",
};
let editingId = null;

document.getElementById("logout").addEventListener("click", function () {
    localStorage.removeItem("token");
    window.location.replace("login.html");
});

unlockForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    unlockButton.disabled = true;
    vaultError.hidden = true;

    try {
        renderVault(await session.unlock(vaultPasswordInput.value));
        document.getElementById("unlockPanel").hidden = true;
        addSecretButton.hidden = false;
    } catch (error) {
        handleRequestError(error);
        vaultError.textContent = error.message || "Could not unlock the vault. Try again.";
        vaultError.hidden = false;
    } finally {
        vaultPasswordInput.value = "";
        unlockButton.disabled = false;
    }
});

addSecretButton.addEventListener("click", function () {
    openEditor();
});

document.getElementById("cancelEdit").addEventListener("click", closeEditor);

secretForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    saveSecretButton.disabled = true;
    editorError.hidden = true;
    vaultStatus.hidden = true;
    const secret = Object.fromEntries(
        Object.entries(fieldIds).map(([field, id]) => {
            const value = document.getElementById(id).value;
            return [field, field === "name" ? value.trim() : value];
        }),
    );

    try {
        const vault = editingId
            ? await session.updateSecret(editingId, secret)
            : await session.addSecret(secret);
        renderVault(vault);
        closeEditor();
    } catch (error) {
        handleRequestError(error);
        editorError.textContent = error.message || "Unable to save secret. Try again.";
        editorError.hidden = false;
    } finally {
        saveSecretButton.disabled = false;
    }
});

vaultContents.addEventListener("click", async function (event) {
    const button = event.target.closest("button[data-action]");
    if (!button) {
        return;
    }

    const id = button.dataset.entryId;
    if (button.dataset.action === "edit") {
        const secret = session.getVault().contents.find((entry) => entry.id === id);
        if (secret) {
            openEditor(secret);
        }
        return;
    }

    if (button.dataset.action === "delete" && window.confirm("Delete this secret?")) {
        button.disabled = true;
        vaultStatus.hidden = true;
        try {
            renderVault(await session.deleteSecret(id));
        } catch (error) {
            handleRequestError(error);
            vaultStatus.textContent = error.message || "Unable to delete secret. Try again.";
            vaultStatus.hidden = false;
            button.disabled = false;
        }
    }
});

function openEditor(secret = null) {
    editingId = secret?.id ?? null;
    editorTitle.textContent = editingId ? "Edit secret" : "Add secret";
    secretForm.reset();
    for (const [field, id] of Object.entries(fieldIds)) {
        document.getElementById(id).value = secret?.[field] ?? "";
    }
    editorError.hidden = true;
    editor.hidden = false;
    document.getElementById("secretName").focus();
}

function closeEditor() {
    editor.hidden = true;
    secretForm.reset();
    editingId = null;
    editorError.hidden = true;
}

function renderVault(vault) {
    vaultContents.replaceChildren();
    const entries = vault.contents;
    if (entries.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.className = "text-secondary";
        emptyMessage.textContent = "Your vault is empty.";
        vaultContents.append(emptyMessage);
        return;
    }

    for (const entry of entries) {
        const card = document.createElement("article");
        card.className = "card border-0 mb-3";
        const body = document.createElement("div");
        body.className = "card-body";
        const header = document.createElement("div");
        header.className = "d-flex justify-content-between align-items-start gap-3";
        const title = document.createElement("h2");
        title.className = "h5 card-title";
        title.textContent = entry.name || "Untitled secret";
        const actions = document.createElement("div");
        actions.className = "d-flex gap-2";
        actions.append(
            createActionButton("edit", entry.id, "Edit"),
            createActionButton("delete", entry.id, "Delete", "btn-outline-danger"),
        );
        header.append(title, actions);
        body.append(header);

        for (const [label, value] of Object.entries(entry)) {
            if (["id", "name", "createdOn", "updatedOn", "trashedOn"].includes(label)
                || value === null || value === "") {
                continue;
            }
            const field = document.createElement("p");
            field.className = "mb-2";
            const fieldLabel = document.createElement("strong");
            fieldLabel.textContent = `${formatLabel(label)}: `;
            field.append(fieldLabel, document.createTextNode(String(value)));
            body.append(field);
        }

        card.append(body);
        vaultContents.append(card);
    }
}

function createActionButton(action, id, label, style = "btn-outline-light") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `btn btn-sm ${style}`;
    button.dataset.action = action;
    button.dataset.entryId = id;
    button.textContent = label;
    return button;
}

function handleRequestError(error) {
    if (error.status === 401) {
        localStorage.removeItem("token");
        window.location.replace("login.html");
    }
}

function formatLabel(label) {
    return label.replace(/([A-Z])/g, " $1").replace(/^./, (character) => character.toUpperCase());
}
