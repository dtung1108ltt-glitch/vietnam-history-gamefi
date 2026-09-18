from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "vn-history-gamefi-backend"

    sui_network: str = "testnet"
    # Public fullnode của Mysten đã bỏ JSON-RPC/GraphQL; để trống GraphQL thì adapter
    # bỏ qua bước đó và đọc thẳng JSON-RPC.
    sui_graphql_url: str = ""
    sui_rpc_url: str = "https://testnet.suiet.app"
    sui_package_id: str = ""
    sui_catalog_id: str = ""
    sui_treasury_id: str = ""
    sui_faction_admin_id: str = ""
    sui_reward_admin_id: str = ""
    sui_cli_path: str = "sui"
    sui_cli_config: str = ""
    sui_gas_budget: int = 50_000_000
    reward_amount_mist: int = 5_000_000

    # --- Solana ---
    solana_network: str = "devnet"
    solana_rpc_url: str = "https://api.devnet.solana.com"
    solana_program_id: str = ""
    solana_gas_budget_lamports: int = 5_000_000
    reward_amount_lamports: int = 5_000_000

    nonce_ttl_seconds: int = 300
    factions_file: str = "assets/nft/factions.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
