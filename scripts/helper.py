from brownie import accounts, network, config

LOCAL_TEST = ["development", "ganache-local", "mainnet-fork"]

def get_account():
    if(network.show_active() in LOCAL_TEST):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

