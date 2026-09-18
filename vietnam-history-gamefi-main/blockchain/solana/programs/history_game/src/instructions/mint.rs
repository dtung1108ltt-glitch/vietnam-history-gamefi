use anchor_lang::prelude::*;
use crate::AssetProof;
pub fn create(proof: &mut Account<AssetProof>, owner: Pubkey, faction_id: String, metadata_uri: String) -> Result<()> {
    require!(faction_id.len() <= 64 && metadata_uri.len() <= 200, ErrorCode::MetadataTooLong);
    proof.owner = owner; proof.kind = "faction".into(); proof.reference_id = faction_id; proof.metadata_uri = metadata_uri; Ok(())
}
#[error_code]
pub enum ErrorCode { #[msg("Field exceeds allocated account space")] MetadataTooLong }
