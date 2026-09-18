// Adapter cho hệ sinh thái SUI Blockchain

export interface SuiWalletAdapter {
  isAvailable: () => boolean;
  connect: () => Promise<string>;
  signMessage: (message: string) => Promise<string>;
  mintFactionNft: (factionId: number) => Promise<{ tx_digest: string; nft_object_id: string }>;
}

export const suiAdapter: SuiWalletAdapter = {
  isAvailable: () => {
    return typeof window !== 'undefined' && ('suiWallet' in window || '__sui__' in window);
  },

  connect: async () => {
    // Nếu có ví Sui thật trong window
    const win = window as any;
    if (win.suiWallet) {
      try {
        const accounts = await win.suiWallet.getAccounts();
        if (accounts && accounts.length > 0) {
          return accounts[0];
        }
        await win.suiWallet.requestPermissions();
        const accs = await win.suiWallet.getAccounts();
        return accs[0];
      } catch (err) {
        console.warn('Sui extension connect error:', err);
      }
    }
    // Fallback địa chỉ Sui Testnet giả lập cho Demo/Khởi động
    const randomHex = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
    return `0x${randomHex}`;
  },

  signMessage: async (message: string) => {
    const win = window as any;
    if (win.suiWallet?.signMessage) {
      try {
        const textEncoder = new TextEncoder();
        const signed = await win.suiWallet.signMessage({ message: textEncoder.encode(message) });
        return signed.signature || btoa(signed);
      } catch (err) {
        console.warn('Real Sui sign failed, using cryptographic format stub:', err);
      }
    }
    // SUI signature: base64 (flag || signature || pubkey)
    const mockBytes = new Uint8Array(97);
    mockBytes[0] = 0; // ed25519 scheme flag
    crypto.getRandomValues(mockBytes.subarray(1));
    return btoa(String.fromCharCode(...mockBytes));
  },

  mintFactionNft: async (factionId: number) => {
    // Giả lập transaction digest và object id trên Sui Testnet
    const hex32 = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
    const txDigest = `SuiTx_${hex32.substring(0, 32)}`;
    const nftObjectId = `0x${hex32}`;
    
    // Đợi 1.2s mô phỏng độ trễ blockchain on-chain
    await new Promise(res => setTimeout(res, 1200));
    return {
      tx_digest: txDigest,
      nft_object_id: nftObjectId,
    };
  }
};
