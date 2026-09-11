import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SuiClientProvider, WalletProvider, createNetworkConfig } from "@mysten/dapp-kit";
import "@mysten/dapp-kit/dist/index.css";
import type { ReactNode } from "react";
import { SUI_CONFIG, SUI_RPC_URL } from "./services/sui";

const { networkConfig } = createNetworkConfig({
  [SUI_CONFIG.network]: {
    url: SUI_RPC_URL,
    network: SUI_CONFIG.network,
  },
});

const queryClient = new QueryClient();

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <SuiClientProvider networks={networkConfig} defaultNetwork={SUI_CONFIG.network}>
        <WalletProvider autoConnect>
          {children}
        </WalletProvider>
      </SuiClientProvider>
    </QueryClientProvider>
  );
}
