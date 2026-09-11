/// Logic reward on-chain: treasury shared object giữ SUI reward của game.
/// Backend (giữ RewardAdmin) gọi send_reward sau khi battle có kết quả;
/// event RewardSent + TX Digest là bằng chứng reward đã lên chain.
module history_game::reward {
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};
    use sui::event;
    use sui::object::{Self, UID, ID};
    use sui::sui::SUI;
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};

    const E_INSUFFICIENT_TREASURY: u64 = 1;
    const E_ZERO_AMOUNT: u64 = 2;

    /// Capability của backend reward service.
    public struct RewardAdmin has key { id: UID }

    public struct RewardTreasury has key {
        id: UID,
        vault: Balance<SUI>,
        total_paid: u64,
        reward_count: u64,
    }

    public struct RewardSent has copy, drop {
        recipient: address,
        amount: u64,
        battle_id: u64,
        treasury_id: ID,
    }

    fun init(ctx: &mut TxContext) {
        transfer::transfer(RewardAdmin { id: object::new(ctx) }, tx_context::sender(ctx));
    }

    public entry fun create_treasury(_admin: &RewardAdmin, ctx: &mut TxContext) {
        transfer::share_object(RewardTreasury {
            id: object::new(ctx),
            vault: balance::zero(),
            total_paid: 0,
            reward_count: 0,
        });
    }

    public entry fun fund_treasury(
        _admin: &RewardAdmin,
        treasury: &mut RewardTreasury,
        payment: Coin<SUI>,
    ) {
        balance::join(&mut treasury.vault, coin::into_balance(payment));
    }

    /// Battle Result -> Reward: trả `amount` MIST cho người thắng, gắn battle_id vào event.
    public entry fun send_reward(
        _admin: &RewardAdmin,
        treasury: &mut RewardTreasury,
        recipient: address,
        amount: u64,
        battle_id: u64,
        ctx: &mut TxContext,
    ) {
        assert!(amount > 0, E_ZERO_AMOUNT);
        assert!(treasury.vault.value() >= amount, E_INSUFFICIENT_TREASURY);
        let payout = coin::take(&mut treasury.vault, amount, ctx);
        treasury.total_paid = treasury.total_paid + amount;
        treasury.reward_count = treasury.reward_count + 1;
        event::emit(RewardSent {
            recipient,
            amount,
            battle_id,
            treasury_id: object::id(treasury),
        });
        transfer::public_transfer(payout, recipient);
    }

    public fun vault_value(treasury: &RewardTreasury): u64 { treasury.vault.value() }
    public fun total_paid(treasury: &RewardTreasury): u64 { treasury.total_paid }
    public fun reward_count(treasury: &RewardTreasury): u64 { treasury.reward_count }

    #[test_only]
    public fun init_for_testing(ctx: &mut TxContext) {
        init(ctx)
    }
}
