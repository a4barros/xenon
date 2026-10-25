import {protectVault} from "./security/encryption.js"
import {unlockMasterKey, unlockVault} from "./security/decryption.js"

function createVaultSession({baseUrl, token, fetchImpl = fetch, createId = () => crypto.randomUUID()}) {
    let masterKey;
    let vault;

    async function request(resource, options = {}) {
        const response = await fetchImpl(`${baseUrl}/${resource}/`, {
            ...options,
            headers: {
                ...options.headers,
                "Authorization": token,
            },
        });
        if (!response.ok) {
            const error = new Error(`Unable to ${options.method === "POST" ? "save" : "load"} ${resource} (${response.status}).`);
            error.status = response.status;
            throw error;
        }
        return await response.json();
    }

    function ensureUnlocked() {
        if (!masterKey || !vault) {
            throw new Error("Unlock the vault before changing secrets.");
        }
    }

    async function commitVault(nextVault) {
        const protectedVault = await protectVault(nextVault, masterKey);
        await request("vault", {
            body: JSON.stringify(protectedVault),
            headers: {
                "Content-Type": "application/json",
            },
            method: "POST",
        });
        vault = nextVault;
        return getVault();
    }

    function getVault() {
        return vault ? structuredClone(vault) : null;
    }

    return {
        async unlock(vaultPassword) {
            const [protectedMasterKey, protectedVault] = await Promise.all([
                request("master"),
                request("vault"),
            ]);
            const unlockedMasterKey = await unlockMasterKey(
                protectedMasterKey.encrypted_master_key,
                protectedMasterKey.iv,
                protectedMasterKey.salt,
                vaultPassword,
            );
            const unlockedVault = await unlockVault(
                protectedVault.encrypted_vault,
                protectedVault.iv,
                unlockedMasterKey,
            );
            if (!unlockedVault || !Array.isArray(unlockedVault.contents)) {
                throw new Error("The decrypted vault has an invalid format.");
            }

            unlockedVault.contents = unlockedVault.contents.map((secret) => ({
                ...secret,
                id: secret.id || createId(),
            }));
            masterKey = unlockedMasterKey;
            vault = unlockedVault;
            return getVault();
        },

        getVault,

        async addSecret(secret) {
            ensureUnlocked();
            const today = new Date().toISOString().slice(0, 10);
            const newSecret = {
                ...secret,
                id: createId(),
                createdOn: today,
                updatedOn: today,
                trashedOn: null,
            };
            return await commitVault({
                ...vault,
                contents: [...vault.contents, newSecret],
            });
        },

        async updateSecret(id, changes) {
            ensureUnlocked();
            const existingSecret = vault.contents.find((secret) => secret.id === id);
            if (!existingSecret) {
                throw new Error("Secret not found.");
            }
            const updatedSecret = {
                ...existingSecret,
                ...changes,
                id,
                createdOn: existingSecret.createdOn,
                updatedOn: new Date().toISOString().slice(0, 10),
            };
            return await commitVault({
                ...vault,
                contents: vault.contents.map((secret) => secret.id === id ? updatedSecret : secret),
            });
        },

        async deleteSecret(id) {
            ensureUnlocked();
            if (!vault.contents.some((secret) => secret.id === id)) {
                throw new Error("Secret not found.");
            }
            return await commitVault({
                ...vault,
                contents: vault.contents.filter((secret) => secret.id !== id),
            });
        },
    };
}

export {createVaultSession};
