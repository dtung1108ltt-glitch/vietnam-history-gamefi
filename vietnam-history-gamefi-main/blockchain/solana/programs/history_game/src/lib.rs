use anchor_lang::prelude::*;

declare_id!("11111111111111111111111111111111"); // replace after `anchor keys list`

pub mod instructions;
use instructions::*;

#[program]
pub mod history_game {
    use super::*;
    pub fn mint_faction(ctx: Context<MintProof>, faction_id: String, metadata_uri: String) -> Result<()> {
        mint::create(&mut ctx.accounts.proof, ctx.accounts.owner.key(), faction_id, metadata_uri)
    }
    pub fn record_reward(ctx: Context<MintProof>, reward_id: String, metadata_uri: String) -> Result<()> {
        reward::create(&mut ctx.accounts.proof, ctx.accounts.owner.key(), reward_id, metadata_uri)
    }
    pub fn record_achievement(ctx: Context<MintProof>, achievement_id: String, metadata_uri: String) -> Result<()> {
        achievement::create(&mut ctx.accounts.proof, ctx.accounts.owner.key(), achievement_id, metadata_uri)
    }
}

#[derive(Accounts)]
pub struct MintProof<'info> {
    #[account(init, payer = owner, space = AssetProof::SPACE)]
    pub proof: Account<'info, AssetProof>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct AssetProof {
    pub owner: Pubkey,
    pub kind: String,
    pub reference_id: String,
    pub metadata_uri: String,
}
impl AssetProof { pub const SPACE: usize = 8 + 32 + 4 + 16 + 4 + 64 + 4 + 200; }
