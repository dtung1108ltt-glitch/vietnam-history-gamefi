use anchor_lang::prelude::*;
use crate::AssetProof;
pub fn create(proof: &mut Account<AssetProof>, owner: Pubkey, reward_id: String, metadata_uri: String) -> Result<()> {
    require!(reward_id.len() <= 64 && metadata_uri.len() <= 200, crate::instructions::mint::ErrorCode::MetadataTooLong);
    proof.owner = owner; proof.kind = "reward".into(); proof.reference_id = reward_id; proof.metadata_uri = metadata_uri; Ok(())
}
