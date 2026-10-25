import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {before, test} from "node:test";

globalThis.window = {crypto: webcrypto};

let protectedMasterKey;
let initialProtectedVault;
const vaultPassword = "test-vault-password";

before(async () => {
    const {generateMasterKey} = await import("../src/js/security/keyGen.js");
    const {protectMasterKey, protectVault} = await import("../src/js/security/encryption.js");
    const masterKey = await generateMasterKey();
    protectedMasterKey = await protectMasterKey(masterKey, vaultPassword);
    initialProtectedVault = await protectVault({
        version: "1",
        contents: [{
            name: "Email",
            username: "person@example.com",
            password: "initial-password",
            totpKey: null,
            notes: "",
            createdOn: "2025-01-01",
            updatedOn: "2025-01-01",
            trashedOn: null,
        }],
    }, masterKey);
});

function createMockServer() {
    let protectedVault = structuredClone(initialProtectedVault);
    const requests = [];
    let failNextSave = false;

    return {
        requests,
        failNextSave() {
            failNextSave = true;
        },
        async fetch(url, options = {}) {
            requests.push({url, options});
            assert.equal(options.headers.Authorization, "Bearer test-token");

            if (url.endsWith("/master/")) {
                return jsonResponse(protectedMasterKey);
            }
            if (url.endsWith("/vault/") && options.method !== "POST") {
                return jsonResponse(protectedVault);
            }
            if (url.endsWith("/vault/") && options.method === "POST") {
                if (failNextSave) {
                    failNextSave = false;
                    return jsonResponse({detail: "save failed"}, 500);
                }
                protectedVault = JSON.parse(options.body);
                return jsonResponse(protectedVault);
            }
            return jsonResponse({detail: "not found"}, 404);
        },
        async readVault() {
            const {unlockMasterKey, unlockVault} = await import("../src/js/security/decryption.js");
            const masterKey = await unlockMasterKey(
                protectedMasterKey.encrypted_master_key,
                protectedMasterKey.iv,
                protectedMasterKey.salt,
                vaultPassword,
            );
            return await unlockVault(protectedVault.encrypted_vault, protectedVault.iv, masterKey);
        },
    };
}

function jsonResponse(body, status = 200) {
    return {
        ok: status >= 200 && status < 300,
        status,
        async json() {
            return structuredClone(body);
        },
    };
}

async function createSession(server) {
    const {createVaultSession} = await import("../src/js/vaultSession.js");
    let nextId = 0;
    return createVaultSession({
        baseUrl: "https://xenon.test",
        token: "Bearer test-token",
        fetchImpl: server.fetch,
        createId: () => `secret-${++nextId}`,
    });
}

test("unlock, add, edit, delete, and reload secrets through encrypted storage", async () => {
    const server = createMockServer();
    const session = await createSession(server);

    await assert.rejects(session.unlock("wrong-password"));
    const openedVault = await session.unlock(vaultPassword);
    assert.equal(openedVault.contents[0].name, "Email");
    assert.equal(openedVault.contents[0].id, "secret-1");

    const addedVault = await session.addSecret({
        name: "Wi-Fi",
        username: "guest",
        password: "wifi-password",
        totpKey: "",
        notes: "Guest network",
    });
    assert.equal(addedVault.contents.length, 2);
    assert.equal(addedVault.contents[1].id, "secret-2");

    const editedVault = await session.updateSecret("secret-1", {
        name: "Personal Email",
        username: "owner@example.com",
        password: "updated-password",
        totpKey: "",
        notes: "Updated email credentials",
    });
    assert.equal(editedVault.contents[0].name, "Personal Email");
    assert.equal(editedVault.contents[0].createdOn, "2025-01-01");
    assert.notEqual(editedVault.contents[0].updatedOn, editedVault.contents[0].createdOn);

    const deletedVault = await session.deleteSecret("secret-2");
    assert.deepEqual(deletedVault.contents.map((secret) => secret.name), ["Personal Email"]);

    const reloadedSession = await createSession(server);
    const reloadedVault = await reloadedSession.unlock(vaultPassword);
    assert.deepEqual(reloadedVault.contents, deletedVault.contents);
    assert.equal(server.requests.filter(({options}) => options.method === "POST").length, 3);

    const savedPayload = JSON.parse(server.requests.findLast(({options}) => options.method === "POST").options.body);
    assert.ok(savedPayload.encrypted_vault);
    assert.equal(JSON.stringify(savedPayload).includes("updated-password"), false);
});

test("failed saves leave the in-memory vault unchanged", async () => {
    const server = createMockServer();
    const session = await createSession(server);
    const originalVault = await session.unlock(vaultPassword);
    server.failNextSave();

    await assert.rejects(
        session.addSecret({name: "Not saved", username: "", password: "", totpKey: "", notes: ""}),
        /Unable to save vault/,
    );
    assert.deepEqual(session.getVault(), originalVault);
    assert.deepEqual((await server.readVault()).contents.map((secret) => secret.name), ["Email"]);
});

test("rejects edits and deletes for unknown secret IDs", async () => {
    const server = createMockServer();
    const session = await createSession(server);
    await session.unlock(vaultPassword);

    await assert.rejects(session.updateSecret("missing", {name: "Missing"}), /Secret not found/);
    await assert.rejects(session.deleteSecret("missing"), /Secret not found/);
    assert.equal(server.requests.filter(({options}) => options.method === "POST").length, 0);
});
