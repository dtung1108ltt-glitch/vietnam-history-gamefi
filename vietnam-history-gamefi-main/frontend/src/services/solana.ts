// Adapter cho hệ sinh thái SOLANA Blockchain

export interface SolanaWalletAdapter {
  isAvailable: () => boolean;
  connect: () => Promise<string>;
  signMessage: (message: string) => Promise<string>;
  mintFactionNft: (factionId: number) => Promise<{ tx_digest: string; nft_object_id: string }>;
}

export const solanaAdapter: SolanaWalletAdapter = {
  isAvailable: () => {
    return typeof window !== 'undefined' && ('solana' in window || 'phantom' in window);
  },

  connect: async () => {
    const win = window as any;
    const provider = win.solana || win.phantom?.solana;
    if (provider) {
      try {
        const resp = await provider.connect();
        return resp.publicKey.toString();
      } catch (err) {
        console.warn('Phantom wallet connect error:', err);
      }
    }
    // Mock Solana base58 address
    const chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    let addr = '';
    for (let i = 0; i < 44; i++) {
      addr += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return addr;
  },

  signMessage: async (message: string) => {
    const win = window as any;
    const provider = win.solana || win.phantom?.solana;
    if (provider && provider.signMessage) {
      try {
        const encodedMessage = new TextEncoder().encode(message);
        const signed = await provider.signMessage(encodedMessage, 'utf8');
        return btoa(String.fromCharCode(...signed.signature));
      } catch (err) {
        console.warn('Solana signMessage failed:', err);
      }
    }
    // Mock base58 format signature
    const chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    let sig = '';
    for (let i = 0; i < 88; i++) {
      sig += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return sig;
  },

  mintFactionNft: async (factionId: number) => {
    const chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    let txDigest = 'SolTx_';
    for (let i = 0; i < 64; i++) {
      txDigest += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    let nftMint = '';
    for (let i = 0; i < 44; i++) {
      nftMint += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    await new Promise(res => setTimeout(res, 1200));
    return {
      tx_digest: txDigest,
      nft_object_id: nftMint,
    };
  }
};
