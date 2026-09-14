use anchor_lang::prelude::*;
use crate::AssetProof;
pub fn create(proof: &mut Account<AssetProof>, owner: Pubkey, achievement_id: String, metadata_uri: String) -> Result<()> {
    require!(achievement_id.len() <= 64 && metadata_uri.len() <= 200, crate::instructions::mint::ErrorCode::MetadataTooLong);
    proof.owner = owner; proof.kind = "achievement".into(); proof.reference_id = achievement_id; proof.metadata_uri = metadata_uri; Ok(())
}
