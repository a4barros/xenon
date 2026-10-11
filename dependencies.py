from database import connect
from repository.user import UserRepository
from repository.protected_vault import ProtectedVaultRepository
from repository.protected_master_key import ProtectedMasterKeyRepository



def get_user_repository() -> UserRepository:
    return UserRepository(connect)

def get_protected_vault_repository() -> ProtectedVaultRepository:
    return ProtectedVaultRepository(connect)

def get_protected_master_key_repository() -> ProtectedMasterKeyRepository:
    return ProtectedMasterKeyRepository(connect)