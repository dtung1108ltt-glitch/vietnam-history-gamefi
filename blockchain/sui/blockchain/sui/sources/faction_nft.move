/// Faction NFT của game chiến thuật Lịch sử Việt Nam.
/// Metadata NFT được chuẩn hoá từ FactionCatalog (input Artist 1: tên / rarity / ảnh)
/// và expose qua SUI Display để ví / marketplace đọc theo chuẩn NFT chung.
module history_game::faction_nft {
    use std::string::{String, utf8};
    use sui::display::{Self, Display};
    use sui::event;
    use sui::object::{Self, UID, ID};
    use sui::package;
    use sui::table::{Self, Table};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};

    const E_UNKNOWN_FACTION: u64 = 1;
    const E_ALREADY_OWNED_FACTION: u64 = 2;
    const E_NOT_NFT_OWNER: u64 = 3;
    const E_FACTION_EXISTS: u64 = 4;
    const E_RECIPIENT_ALREADY_OWNED: u64 = 5;

    /// Capability của đội vận hành game: đăng ký faction vào catalog.
    public struct FactionAdmin has key { id: UID }

    /// Shared object: catalog metadata + ánh xạ owner -> faction (mỗi wallet 1 faction).
    public struct FactionCatalog has key {
        id: UID,
        names: Table<u8, String>,
        rarities: Table<u8, String>,
        images: Table<u8, String>,
        owners: Table<address, u8>,
        supply: Table<u8, u64>,
    }

    public struct FactionNft has key, store {
        id: UID,
        faction_id: u8,
        faction_name: String,
        rarity: String,
        image: String,
        owner: address,
    }

    public struct FactionMinted has copy, drop {
        faction_id: u8,
        owner: address,
        nft_id: ID,
    }

    public struct FactionTransferred has copy, drop {
        nft_id: ID,
        faction_id: u8,
        from: address,
        to: address,
    }

    /// One-time witness của module `faction_nft` (tên module viết hoa, không field, chỉ có drop).
    /// Runtime tự tạo và truyền vào `init` lúc publish, không được khởi tạo thủ công.
    public struct FACTION_NFT has drop {}

    fun init(witness: FACTION_NFT, ctx: &mut TxContext) {
        let publisher = package::claim(witness, ctx);
        init_with_publisher(publisher, ctx);
    }

    fun init_with_publisher(publisher: package::Publisher, ctx: &mut TxContext) {
        let sender = tx_context::sender(ctx);
        let mut display = display::new_with_fields<FactionNft>(
            &publisher,
            vector[
                utf8(b"name"),
                utf8(b"image"),
                utf8(b"description"),
            ],
            vector[
                utf8(b"@{faction_name}"),
                utf8(b"@{image}"),
                utf8(b"@{faction_name} - rarity @{rarity}"),
            ],
            ctx,
        );
        display::update_version(&mut display);
        transfer::transfer(FactionAdmin { id: object::new(ctx) }, sender);
        transfer::share_object(FactionCatalog {
            id: object::new(ctx),
            names: table::new(ctx),
            rarities: table::new(ctx),
            images: table::new(ctx),
            owners: table::new(ctx),
            supply: table::new(ctx),
        });
        transfer::public_transfer(publisher, sender);
        transfer::public_transfer(display, sender);
    }

    /// Admin đăng ký một faction vào catalog (chuẩn hoá metadata từ Artist 1).
    public entry fun register_faction(
        _admin: &FactionAdmin,
        catalog: &mut FactionCatalog,
        faction_id: u8,
        name: vector<u8>,
        rarity: vector<u8>,
        image: vector<u8>,
    ) {
        assert!(!table::contains(&catalog.names, faction_id), E_FACTION_EXISTS);
        table::add(&mut catalog.names, faction_id, utf8(name));
        table::add(&mut catalog.rarities, faction_id, utf8(rarity));
        table::add(&mut catalog.images, faction_id, utf8(image));
        table::add(&mut catalog.supply, faction_id, 0);
    }

    /// Người chơi tự mint Faction NFT đã chọn; mỗi wallet chỉ sở hữu 1 faction.
    public entry fun mint_faction(
        catalog: &mut FactionCatalog,
        faction_id: u8,
        ctx: &mut TxContext,
    ) {
        mint_internal(catalog, faction_id, tx_context::sender(ctx), ctx);
    }

    /// Backend mint hộ người chơi (giữ FactionAdmin, trả gas) - vẫn ràng buộc 1 faction/wallet.
    public entry fun mint_faction_for(
        _admin: &FactionAdmin,
        catalog: &mut FactionCatalog,
        faction_id: u8,
        recipient: address,
        ctx: &mut TxContext,
    ) {
        mint_internal(catalog, faction_id, recipient, ctx);
    }

    fun mint_internal(
        catalog: &mut FactionCatalog,
        faction_id: u8,
        player: address,
        ctx: &mut TxContext,
    ) {
        assert!(table::contains(&catalog.names, faction_id), E_UNKNOWN_FACTION);
        assert!(!table::contains(&catalog.owners, player), E_ALREADY_OWNED_FACTION);
        let nft = FactionNft {
            id: object::new(ctx),
            faction_id,
            faction_name: *table::borrow(&catalog.names, faction_id),
            rarity: *table::borrow(&catalog.rarities, faction_id),
            image: *table::borrow(&catalog.images, faction_id),
            owner: player,
        };
        table::add(&mut catalog.owners, player, faction_id);
        let supply = table::borrow_mut(&mut catalog.supply, faction_id);
        *supply = *supply + 1;
        event::emit(FactionMinted {
            faction_id,
            owner: player,
            nft_id: object::id(&nft),
        });
        transfer::transfer(nft, player);
    }

    /// Chuyển NFT sang wallet khác; catalog cập nhật lại ánh xạ owner.
    public entry fun transfer_faction(
        catalog: &mut FactionCatalog,
        mut nft: FactionNft,
        to: address,
        ctx: &mut TxContext,
    ) {
        let from = tx_context::sender(ctx);
        assert!(nft.owner == from, E_NOT_NFT_OWNER);
        assert!(!table::contains(&catalog.owners, to), E_RECIPIENT_ALREADY_OWNED);
        table::remove(&mut catalog.owners, from);
        table::add(&mut catalog.owners, to, nft.faction_id);
        event::emit(FactionTransferred {
            nft_id: object::id(&nft),
            faction_id: nft.faction_id,
            from,
            to,
        });
        nft.owner = to;
        transfer::transfer(nft, to);
    }

    public fun faction_id(nft: &FactionNft): u8 { nft.faction_id }
    public fun faction_name(nft: &FactionNft): String { nft.faction_name }
    public fun rarity(nft: &FactionNft): String { nft.rarity }
    public fun image(nft: &FactionNft): String { nft.image }
    public fun owner(nft: &FactionNft): address { nft.owner }
    public fun nft_id(nft: &FactionNft): ID { object::id(nft) }

    public fun metadata(nft: &FactionNft): (u8, String, String, String, address) {
        (nft.faction_id, nft.faction_name, nft.rarity, nft.image, nft.owner)
    }

    public fun faction_of(catalog: &FactionCatalog, player: address): (bool, u8) {
        if (table::contains(&catalog.owners, player)) {
            (true, *table::borrow(&catalog.owners, player))
        } else {
            (false, 0)
        }
    }

    public fun supply_of(catalog: &FactionCatalog, faction_id: u8): u64 {
        *table::borrow(&catalog.supply, faction_id)
    }

    /// Witness giả cho unit test (không có publish thật nên không nhận được FACTION_NFT).
    #[test_only]
    public struct FactionNftTestOtw has drop {}

    #[test_only]
    public fun init_for_testing(ctx: &mut TxContext) {
        let publisher = package::test_claim(FactionNftTestOtw {}, ctx);
        init_with_publisher(publisher, ctx);
    }

    #[test_only]
    public fun destroy_for_testing(nft: FactionNft) {
        let FactionNft { id, faction_id: _, faction_name: _, rarity: _, image: _, owner: _ } = nft;
        object::delete(id);
    }
}
