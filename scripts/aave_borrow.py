from scripts.helper import get_account


from brownie import config, network, interface
from scripts.get_weth import convert_weth
from scripts.helper import get_account

from web3 import Web3

amount = Web3.toWei(0.1, "ether")

weth_token_config = config["networks"][network.show_active()]["weth_token"]
dai_to_eth_config = config["networks"][network.show_active()]["dai_to_eth"]
dai_token_config  =  config["networks"][network.show_active()]["dai_token"]

def main():
    account = get_account()
    erc20_address = weth_token_config
    if network.show_active() in ["mainnet-fork"]:
        convert_weth()
    spender = lending_pool()
    approve_erc20(spender.address, amount, erc20_address, account) # first i need to approve
    print(f"Depositing...")
    tx = spender.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited")
    # borrow section (how much can I borrow?)
    availableBorrowsETH, totalDebtETH = getUserData(spender, account)
    dai_to_eth = get_asset_price(dai_to_eth_config)
    # converting ETH TO DAI
    amount_dai_to_borrow = (1 / dai_to_eth) * (availableBorrowsETH * 0.95) # COMES IN WEI
    # multiplying by 95% because is a safe percentage for not get liquidated

    print(f"I am going to borrow {amount_dai_to_borrow} of DAI")
    dai_token_address = dai_token_config # DAI token from etherscan
    borrow_tx = spender.borrow(dai_token_address, Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account.address, {"from": account})
    borrow_tx.wait(1)
    print("I borrowed some DAI")
    getUserData(spender, account)
    # REPAY
    repay(spender, Web3.toWei(amount_dai_to_borrow, "ether"), account)
    getUserData(spender, account)


def repay(lending_pool, amount, account):
    approve_erc20(lending_pool, Web3.toWei(amount, "ether"), dai_token_config, account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"], amount, 1, account.address, {"from": account})
    repay_tx.wait(1)
    print("REPAID")

def getUserData(lending_pool, account):
    (totalCollateralETH, 
    totalDebtETH, 
    availableBorrowsETH, 
    currentLiquidationThreshold, 
    ltv, healthFactor) = lending_pool.getUserAccountData(account.address)

    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")

    print(f"You have {totalCollateralETH} worth of ETH deposited.")
    print(f"You have {totalDebtETH} worth of ETH borrowed.")
    print(f"You can borrow {availableBorrowsETH} worth of ETH.")
    return (float(availableBorrowsETH), float(totalDebtETH))


def get_asset_price(price_feed_address):
    #abi
    dai_eth_price = interface.AggregatorV3Interface(price_feed_address)
    lastest_price = dai_eth_price.latestRoundData()[1]
    dai_to_eth = Web3.fromWei(lastest_price, "ether")
    print(f"The DAI price to ETH is: ${dai_to_eth}")
    return float(dai_to_eth)

def approve_erc20(spender, amount, erc20_address, account):
    print(f"Approving token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved")
    return tx


def lending_pool():
    #abi -> interface
    #address
    lending_pool = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["ilending_pool_addresses_provider"])
    lending_pool_address = lending_pool.getLendingPool()
    pool = interface.ILendingPool(lending_pool_address)
    return pool
