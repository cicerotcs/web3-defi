# 1. aave converts eth to weth

# first i need to convert my eth from kovan network to weth

from scripts.helper import get_account

from brownie import interface, config, network

def convert_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"]) # i am depositing directly to the eth pool
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18}) # 0.1 eth
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx


def main():
    convert_weth()