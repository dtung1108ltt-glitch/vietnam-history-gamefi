#[test_only]
module history_game::reward_tests {
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::test_scenario::{Self, Scenario};
    use sui::transfer;
    use history_game::reward::{Self, RewardAdmin, RewardTreasury};

    const ADMIN: address = @0xA1;
    const PLAYER: address = @0xB2;

    fun setup(scenario: &mut Scenario): (RewardAdmin, RewardTreasury) {
        reward::init_for_testing(test_scenario::ctx(scenario));
        scenario.next_tx(ADMIN);
        let admin = scenario.take_from_sender<RewardAdmin>();
        reward::create_treasury(&admin, test_scenario::ctx(scenario));
        scenario.next_tx(ADMIN);
        let treasury = scenario.take_shared<RewardTreasury>();
        (admin, treasury)
    }

    #[test]
    fun send_reward_pays_from_treasury_and_counts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut treasury) = setup(&mut scenario);

        let funding = coin::mint_for_testing<SUI>(1_000, test_scenario::ctx(&mut scenario));
        reward::fund_treasury(&admin, &mut treasury, funding);
        assert!(reward::vault_value(&treasury) == 1_000, 1);

        reward::send_reward(&admin, &mut treasury, PLAYER, 400, 77, test_scenario::ctx(&mut scenario));
        assert!(reward::vault_value(&treasury) == 600, 2);
        assert!(reward::total_paid(&treasury) == 400, 3);
        assert!(reward::reward_count(&treasury) == 1, 4);
        test_scenario::return_shared(treasury);
        test_scenario::return_to_sender(&scenario, admin);

        scenario.next_tx(PLAYER);
        let payout = scenario.take_from_sender<Coin<SUI>>();
        assert!(coin::value(&payout) == 400, 5);
        transfer::public_transfer(payout, PLAYER);
        test_scenario::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 1)]
    fun send_reward_over_balance_aborts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut treasury) = setup(&mut scenario);
        let funding = coin::mint_for_testing<SUI>(10, test_scenario::ctx(&mut scenario));
        reward::fund_treasury(&admin, &mut treasury, funding);
        reward::send_reward(&admin, &mut treasury, PLAYER, 11, 1, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(treasury);
        test_scenario::return_to_sender(&scenario, admin);
        test_scenario::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 2)]
    fun send_reward_zero_amount_aborts() {
        let mut scenario = test_scenario::begin(ADMIN);
        let (admin, mut treasury) = setup(&mut scenario);
        let funding = coin::mint_for_testing<SUI>(10, test_scenario::ctx(&mut scenario));
        reward::fund_treasury(&admin, &mut treasury, funding);
        reward::send_reward(&admin, &mut treasury, PLAYER, 0, 1, test_scenario::ctx(&mut scenario));
        test_scenario::return_shared(treasury);
        test_scenario::return_to_sender(&scenario, admin);
        test_scenario::end(scenario);
    }
}
