import { useCurrentAccount, useDisconnectWallet } from "@mysten/dapp-kit";

export function useWallet() {
  const account = useCurrentAccount();
  const { mutate: disconnect } = useDisconnectWallet();
  return {
    address: account?.address ?? null,
    isConnected: !!account,
    disconnect: () => disconnect(),
  };
}
