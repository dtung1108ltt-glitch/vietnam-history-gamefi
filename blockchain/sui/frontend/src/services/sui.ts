export const SUI_CONFIG = {
  network: (import.meta.env.VITE_SUI_NETWORK ?? "testnet") as "testnet" | "localnet",
  packageId: import.meta.env.VITE_SUI_PACKAGE_ID ?? "",
  catalogId: import.meta.env.VITE_SUI_CATALOG_ID ?? "",
};

// Public fullnode của Mysten đã bỏ JSON-RPC, nên SDK trả về URL chết -> tự map RPC.
const DEFAULT_RPC: Record<string, string> = {
  testnet: "https://testnet.suiet.app",
  localnet: "http://127.0.0.1:9000",
};

export const SUI_RPC_URL: string =
  import.meta.env.VITE_SUI_RPC_URL || DEFAULT_RPC[SUI_CONFIG.network] || DEFAULT_RPC.testnet;

export function explorerTxUrl(digest: string): string {
  const base =
    SUI_CONFIG.network === "testnet"
      ? "https://suiscan.xyz/testnet/tx"
      : "http://localhost:9001/tx";
  return `${base}/${digest}`;
}

export function explorerObjectUrl(objectId: string): string {
  const base =
    SUI_CONFIG.network === "testnet"
      ? "https://suiscan.xyz/testnet/object"
      : "http://localhost:9001/object";
  return `${base}/${objectId}`;
}

export function shorten(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}
