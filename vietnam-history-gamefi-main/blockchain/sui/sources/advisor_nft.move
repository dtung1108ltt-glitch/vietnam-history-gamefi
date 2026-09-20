/// Advisor General NFT & Ownership Module cho game chiến thuật Lịch sử Việt Nam.
/// Tuân thủ nguyên tắc:
/// - NFT chỉ lưu trữ định danh (advisor_id, faction_id, rarity, metadata_uri, owner).
/// - Không nhúng logic combat, damage, hay balance lên blockchain.
/// - Cho phép chuyển nhượng (transfer), niêm yết (listing) và hoán đổi (trading).
module history_game::advisor_nft {
    use std::string::{String, utf8};
    use sui::display::{Self, Display};
    use sui::event;
    use sui::object::{Self, UID, ID};
    use sui::package;
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};

    const E_NOT_OWNER: u64 = 1;

    /// Capability quản trị của hệ thống
    public struct AdvisorAdmin has key { id: UID }

    /// Tướng Cố Vấn (Advisor General) dưới dạng NFT
    public struct AdvisorNft has key, store {
        id: UID,
        advisor_id: String,
        advisor_name: String,
        faction_id: u8,
        rarity: String,
        metadata_uri: String,
        owner: address,
    }

    /// Sự kiện khi mint Tướng Cố Vấn
    public struct AdvisorMinted has copy, drop {
        nft_id: ID,
        advisor_id: String,
        faction_id: u8,
        owner: address,
    }

    /// Sự kiện khi chuyển nhượng Tướng Cố Vấn
    public struct AdvisorTransferred has copy, drop {
        nft_id: ID,
        advisor_id: String,
        from: address,
        to: address,
    }

    /// One-time witness
    public struct ADVISOR_NFT has drop {}

    fun init(witness: ADVISOR_NFT, ctx: &mut TxContext) {
        let publisher = package::claim(witness, ctx);
        let sender = tx_context::sender(ctx);

        let mut display = display::new_with_fields<AdvisorNft>(
            &publisher,
            vector[
                utf8(b"name"),
                utf8(b"advisor_id"),
                utf8(b"image_url"),
                utf8(b"description"),
            ],
            vector[
                utf8(b"@{advisor_name}"),
                utf8(b"@{advisor_id}"),
                utf8(b"@{metadata_uri}"),
                utf8(b"Advisor General for faction @{faction_id} - rarity @{rarity}"),
            ],
            ctx,
        );
        display::update_version(&mut display);

        transfer::transfer(AdvisorAdmin { id: object::new(ctx) }, sender);
        transfer::public_transfer(publisher, sender);
        transfer::public_transfer(display, sender);
    }

    /// Mint Tướng Cố Vấn cho người chơi
    public entry fun mint_advisor(
        _admin: &AdvisorAdmin,
        recipient: address,
        advisor_id: vector<u8>,
        advisor_name: vector<u8>,
        faction_id: u8,
        rarity: vector<u8>,
        metadata_uri: vector<u8>,
        ctx: &mut TxContext,
    ) {
        let nft = AdvisorNft {
            id: object::new(ctx),
            advisor_id: utf8(advisor_id),
            advisor_name: utf8(advisor_name),
            faction_id,
            rarity: utf8(rarity),
            metadata_uri: utf8(metadata_uri),
            owner: recipient,
        };

        event::emit(AdvisorMinted {
            nft_id: object::id(&nft),
            advisor_id: nft.advisor_id,
            faction_id,
            owner: recipient,
        });

        transfer::public_transfer(nft, recipient);
    }

    /// Chuyển quyền sở hữu Tướng Cố Vấn
    public entry fun transfer_advisor(
        nft: AdvisorNft,
        recipient: address,
        ctx: &mut TxContext,
    ) {
        let sender = tx_context::sender(ctx);
        event::emit(AdvisorTransferred {
            nft_id: object::id(&nft),
            advisor_id: nft.advisor_id,
            from: sender,
            to: recipient,
        });
        transfer::public_transfer(nft, recipient);
    }
}

