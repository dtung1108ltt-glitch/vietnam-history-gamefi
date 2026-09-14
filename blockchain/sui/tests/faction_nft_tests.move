#[test_only]
module history_game::faction_nft_tests {
    use std::string;
    use sui::test_scenario::{Self, Scenario};
    use history_game::faction_nft::{Self, FactionAdmin, FactionCatalog, FactionNft};

    const ADMIN: address = @0xA1;
    const PLAYER: address = @0xB2;
    const PLAYER_2: address = @0xC3;

    const TRAN_NAME: vector<u8> = b"Nhà Trần";
    const TRAN_IMAGE: vector<u8> = b"https://assets.vnhistory.gamefi/factions/tran.png";

    fun setup(scenario: &mut Scenario): (FactionAdmin, FactionCatalog) {
        faction_nft::init_for_testing(test_scenario::ctx(scenario));
        scenario.next_tx(ADMIN);
        let catalog = scenario.take_shared<FactionCatalog>();
        let admin = scenario.take_from_sender<FactionAdmin>();
        (admin, catalog)
    }

    #[test]
    fun mint_uses_catalog_metadata_and_records_owner() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        faction_nft::register_faction(&admin, &mut catalog, 2, TRAN_NAME, b"rare", TRAN_IMAGE);
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let mut catalog = scenario.take_shared<FactionCatalog>();
        faction_nft::mint_faction(&mut catalog, 2, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(catalog);

        scenario.next_tx(PLAYER);
        let nft = scenario.take_from_sender<FactionNft>();
        assert!(faction_nft::faction_id(&nft) == 2, 100);
        assert!(faction_nft::faction_name(&nft) == string::utf8(TRAN_NAME), 101);
        assert!(faction_nft::rarity(&nft) == string::utf8(b"rare"), 102);
        assert!(faction_nft::image(&nft) == string::utf8(TRAN_IMAGE), 103);
        assert!(faction_nft::owner(&nft) == PLAYER, 104);

        let catalog = scenario.take_shared<FactionCatalog>();
        let (has, faction_id) = faction_nft::faction_of(&catalog, PLAYER);
        assert!(has, 105);
        assert!(faction_id == 2, 106);
        assert!(faction_nft::supply_of(&catalog, 2) == 1, 107);
        test_scenario::return_shared(catalog);

        faction_nft::destroy_for_testing(nft);
        test_scenario::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 2)]
    fun mint_second_faction_aborts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        faction_nft::register_faction(&admin, &mut catalog, 1, b"Nhà Lý", b"common", b"ly.png");
        faction_nft::register_faction(&admin, &mut catalog, 2, TRAN_NAME, b"rare", TRAN_IMAGE);
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let mut catalog = scenario.take_shared<FactionCatalog>();
        faction_nft::mint_faction(&mut catalog, 1, test_scenario::ctx(&mut scenario));
        faction_nft::mint_faction(&mut catalog, 2, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(catalog);
        test_scenario::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 1)]
    fun mint_unregistered_faction_aborts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let mut catalog = scenario.take_shared<FactionCatalog>();
        faction_nft::mint_faction(&mut catalog, 9, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(catalog);
        test_scenario::end(scenario);
    }

    #[test]
    fun transfer_updates_catalog_owner() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        faction_nft::register_faction(&admin, &mut catalog, 3, b"Nhà Lê", b"rare", b"le.png");
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let mut catalog = scenario.take_shared<FactionCatalog>();
        faction_nft::mint_faction(&mut catalog, 3, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(catalog);

        scenario.next_tx(PLAYER);
        let nft = scenario.take_from_sender<FactionNft>();
        let mut catalog = scenario.take_shared<FactionCatalog>();
        faction_nft::transfer_faction(&mut catalog, nft, PLAYER_2, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(catalog);

        scenario.next_tx(PLAYER_2);
        let nft = scenario.take_from_sender<FactionNft>();
        assert!(faction_nft::owner(&nft) == PLAYER_2, 200);

        let catalog = scenario.take_shared<FactionCatalog>();
        let (old_has, _) = faction_nft::faction_of(&catalog, PLAYER);
        let (new_has, new_faction) = faction_nft::faction_of(&catalog, PLAYER_2);
        assert!(!old_has, 201);
        assert!(new_has && new_faction == 3, 202);
        test_scenario::return_shared(catalog);

        faction_nft::destroy_for_testing(nft);
        test_scenario::end(scenario);
    }

    #[test]
    fun admin_mints_for_another_wallet() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        faction_nft::register_faction(&admin, &mut catalog, 4, b"Tây Sơn", b"epic", b"tayson.png");
        faction_nft::mint_faction_for(
            &admin,
            &mut catalog,
            4,
            PLAYER,
            test_scenario::ctx(&mut scenario),
        );
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let nft = scenario.take_from_sender<FactionNft>();
        assert!(faction_nft::owner(&nft) == PLAYER, 300);
        assert!(faction_nft::faction_id(&nft) == 4, 301);

        let catalog = scenario.take_shared<FactionCatalog>();
        let (has, faction_id) = faction_nft::faction_of(&catalog, PLAYER);
        assert!(has && faction_id == 4, 302);
        assert!(faction_nft::supply_of(&catalog, 4) == 1, 303);
        test_scenario::return_shared(catalog);

        faction_nft::destroy_for_testing(nft);
        test_scenario::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 2)]
    fun admin_mint_twice_for_same_wallet_aborts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut catalog) = setup(&mut scenario);
        faction_nft::register_faction(
            &admin,
            &mut catalog,
            5,
            b"Nhà Nguyễn",
            b"legendary",
            b"nguyen.png",
        );
        faction_nft::mint_faction_for(
            &admin,
            &mut catalog,
            5,
            PLAYER,
            test_scenario::ctx(&mut scenario),
        );
        faction_nft::mint_faction_for(
            &admin,
            &mut catalog,
            5,
            PLAYER,
            test_scenario::ctx(&mut scenario),
        );
        test_scenario::return_shared(catalog);
        test_scenario::return_to_sender(&scenario, admin);
        test_scenario::end(scenario);
    }
}
