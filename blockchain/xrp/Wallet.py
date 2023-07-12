from decimal import Decimal
from typing import Union

from xrpl.clients import JsonRpcClient
from xrpl.ledger import get_fee
from xrpl.models import (AccountInfo, AccountLines, AccountNFTs, AccountTx,
                         IssuedCurrencyAmount, Memo, NFTokenAcceptOffer,
                         NFTokenCreateOffer, NFTokenCreateOfferFlag, Payment,
                         PaymentFlag)
from xrpl.utils import drops_to_xrp, ripple_time_to_datetime, xrp_to_drops
from xrpl.wallet import generate_faucet_wallet

from Misc import (hex_to_symbol, is_hex, memo_builder, validate_hex_to_symbol, validate_symbol_to_hex,
                  xrp_format_to_nft_fee)
from x_constants import D_DATA, D_TYPE, M_SOURCE_TAG

"""update add support for modifying fees"""


class xWallet(JsonRpcClient):
    def __init__(self, network_url: str, account_url: str, txn_url: str):
        self.network_url = network_url
        self.account_url = account_url
        self.txn_url = txn_url
        self.client = JsonRpcClient(network_url)

    def toTestnet(self) -> bool:
        self.network_url = "https://s.altnet.rippletest.net:51234"
        self.account_url = "https://testnet.xrpl.org/accounts/"
        self.txn_url = "https://testnet.xrpl.org/transactions/"
        self.client = JsonRpcClient(self.network_url)
        return True

    def toMainnet(self) -> bool:
        self.network_url = "https://xrplcluster.com"
        self.account_url = "https://livenet.xrpl.org/accounts/"
        self.txn_url = "https://livenet.xrpl.org/transactions/"
        self.client = JsonRpcClient(self.network_url)
        return True

    def show_account_in_explorer(self, wallet_addr: str) -> str:
        """show account in explorer"""
        return f"{self.account_url}{wallet_addr}"

    def show_transaction_in_explorer(self, txid: str) -> str:
        """show transaction in explorer"""
        return f"{self.txn_url}{txid}"

    def get_network_fee(self) -> str:
        """return transaction fee, to populate interface and carry out transactions"""
        return get_fee(self.client)

    def xrp_balance(self, wallet_addr: str) -> dict:
        """return xrp balance and objects count"""
        balance = 0
        owner_count = 0
        spend_balance = 0
        acc_info = AccountInfo(account=wallet_addr, ledger_index="validated")
        result = self.client.request(acc_info).result
        if "account_data" in result:
            balance = int(result["account_data"]["Balance"]) - 10000000
            owner_count = int(result["account_data"]["OwnerCount"])
            spend_balance = balance - (2000000 * owner_count)
        return {
            "balance": balance + 10000000,
            "object_count": owner_count,
            "spend_balance": str(drops_to_xrp(str(spend_balance)))}

    def xrp_transactions(self, wallet_addr: str, limit: int = None) -> dict:
        """return all xrp payment transactions an address has carried out"""
        transactions_dict = {}
        sent = []
        received = []
        acc_tx = AccountTx(account=wallet_addr, limit=limit)
        result = self.client.request(acc_tx).result
        if "transactions" in result:
            for transaction in result["transactions"]:
                if transaction["tx"]["TransactionType"] == "Payment" and isinstance(transaction["meta"]["delivered_amount"], str):
                    transact = {}
                    transact["sender"] = transaction["tx"]["Account"]
                    transact["receiver"] = transaction["tx"]["Destination"]
                    transact["amount"] = str(drops_to_xrp(str(transaction["meta"]["delivered_amount"])))
                    transact["fee"] = str(drops_to_xrp(str(transaction["tx"]["Fee"])))
                    transact["timestamp"] = str(ripple_time_to_datetime(transaction["tx"]["date"]))
                    transact["result"] = transaction["meta"]["TransactionResult"]
                    transact["txid"] = transaction["tx"]["hash"]
                    transact["link"] = f'{self.txn_url}{transaction["tx"]["hash"]}'
                    transact["tx_type"] = transaction["tx"]["TransactionType"]
                    # transact["memo"] = transaction["tx"]["Memo"] // this is a list that contains dicts 'parse later'
                    if transact["sender"] == wallet_addr:
                        sent.append(transact)
                    elif transact["sender"] != wallet_addr:
                        received.append(transact)
        transactions_dict["sent"] = sent
        transactions_dict["received"] = received
        return transactions_dict

    def token_transactions(self, wallet_addr: str, limit: int = None) -> dict:
        """return all token payment transactions an account has carried out"""
        transactions_dict = {}
        sent = []
        received = []
        acc_tx = AccountTx(account=wallet_addr, limit=limit)
        result = self.client.request(acc_tx).result
        if "transactions" in result:
            for transaction in result["transactions"]:
                if transaction["tx"]["TransactionType"] == "Payment" and isinstance(transaction["meta"]["delivered_amount"], dict):  
                    transact = {}
                    transact["sender"] = transaction["tx"]["Account"]
                    transact["receiver"] = transaction["tx"]["Destination"]
                    transact["token"] = validate_hex_to_symbol(transaction["meta"]["delivered_amount"]["currency"])
                    transact["issuer"] = transaction["meta"]["delivered_amount"]["issuer"]
                    transact["amount"] = transaction["meta"]["delivered_amount"]["value"]
                    transact["fee"] = str(drops_to_xrp(str(transaction["tx"]["Fee"])))
                    transact["timestamp"] = str(ripple_time_to_datetime(transaction["tx"]["date"]))
                    transact["result"] = transaction["meta"]["TransactionResult"]
                    transact["txid"] = transaction["tx"]["hash"]
                    transact["link"] = f'{self.txn_url}{transaction["tx"]["hash"]}'
                    transact["tx_type"] = transaction["tx"]["TransactionType"]
                    # transact["memo"] = transaction["tx"]["Memo"] // this is a list that contains dicts 'parse later'
                    if transact["sender"] == wallet_addr:
                        sent.append(transact)
                    elif transact["sender"] != wallet_addr:
                        received.append(transact)
        transactions_dict["sent"] = sent
        transactions_dict["received"] = received
        return transactions_dict

    def payment_transactions(self, wallet_addr: str, limit: int = None) -> dict:
        """return all payment transactions for xrp and tokens both sent and received"""
        transactions_dict = {}
        sent = []
        received = []
        acc_tx = AccountTx(account=wallet_addr, limit=limit)
        result = self.client.request(acc_tx).result
        if "transactions" in result:
            for transaction in result["transactions"]:
                if transaction["tx"]["TransactionType"] == "Payment":
                    transact = {}
                    transact["sender"] = transaction["tx"]["Account"]
                    transact["receiver"] = transaction["tx"]["Destination"]
                    if isinstance(transaction["meta"]["delivered_amount"], dict):
                        transact["token"] = validate_hex_to_symbol(transaction["meta"]["delivered_amount"]["currency"])
                        transact["issuer"] = transaction["meta"]["delivered_amount"]["issuer"]
                        transact["amount"] = transaction["meta"]["delivered_amount"]["value"]
                    if isinstance(transaction["meta"]["delivered_amount"], str):
                        transact["token"] = "XRP"
                        transact["issuer"] = ""
                        transact["amount"] = str(drops_to_xrp(str(transaction["meta"]["delivered_amount"])))
                    transact["fee"] = str(drops_to_xrp(str(transaction["tx"]["Fee"])))
                    transact["timestamp"] = str(ripple_time_to_datetime(transaction["tx"]["date"]))
                    transact["result"] = transaction["meta"]["TransactionResult"]
                    transact["txid"] = transaction["tx"]["hash"]
                    transact["link"] = f'{self.txn_url}{transaction["tx"]["hash"]}'
                    transact["tx_type"] = transaction["tx"]["TransactionType"]
                    # transact["memo"] = transaction["tx"]["Memo"] // this is a list that contains dicts 'parse later'
                    if transact["sender"] == wallet_addr:
                        sent.append(transact)
                    elif transact["sender"] != wallet_addr:
                        received.append(transact)
        transactions_dict["sent"] = sent
        transactions_dict["received"] = received
        return transactions_dict

    def send_xrp(self, sender_addr: str, receiver_addr: str, amount: Union[float, Decimal, int],
        destination_tag: int = None, memo: Memo = None, fee: str = None) -> dict:
        """send xrp"""
        txn = Payment(
            account=sender_addr,
            amount=xrp_to_drops(amount),
            destination=receiver_addr,
            destination_tag=destination_tag,
            source_tag=M_SOURCE_TAG, fee=fee, memos=[memo])
        return txn.to_dict()

    def send_token(self, sender_addr: str, receiver_addr: str, token: str, amount: str, issuer: str, partial: bool = False ,is_lp_token: bool = False,
        destination_tag: int = None, memo: Memo = None, fee: str = None) -> dict:
        """send asset...
        max amount = 15 decimal places"""
        cur = token if is_lp_token else validate_symbol_to_hex(token)
        flags = 0
        if partial:
            flags = PaymentFlag.TF_PARTIAL_PAYMENT
        txn = Payment(
            account=sender_addr,
            destination=receiver_addr,
            amount=IssuedCurrencyAmount(currency=cur, issuer=issuer, value=amount),
            destination_tag=destination_tag,
            fee=fee, flags=flags, 
            send_max=IssuedCurrencyAmount(currency=cur, issuer=issuer, value=amount),
            memos=[memo],
            source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def account_tokens(self, wallet_addr: str) -> list:
        """returns all tokens except LP tokens a wallet address is holding with their respective issuers, limit and balances"""
        assets = []
        acc_info = AccountLines(account=wallet_addr, ledger_index="")
        response = self.client.request(acc_info)
        result = response.result
        if "lines" in result:
            lines = result["lines"]
            for line in lines:
                if isinstance(is_hex(line["currency"]), Exception):
                    pass
                else:
                    asset = {}
                    # filter lp tokens
                    asset["token"] = validate_hex_to_symbol(line["currency"])
                    asset["issuer"] = line["account"]
                    asset["amount"] = line["balance"]
                    asset["limit"] = line["limit"]  # the max an account can handle
                    asset["freeze_status"] = ""
                    asset["ripple_status"] = ""
                    if "no_ripple" in line:
                        asset["ripple_status"] = line["no_ripple"]  # no ripple = true, means rippling is disabled which is good; else bad
                    if "freeze" in line:
                        asset["freeze_status"] = line["freeze"]
                    """Query for domain and transfer rate with info.get_token_info()"""
                    assets.append(asset)
        return assets

    def account_nfts(self, wallet_addr: str, limit: int = None) -> list:
        "return all nfts an account is holding"
        account_nft = []
        acc_info = AccountNFTs(account=wallet_addr, id="validated", limit=limit)
        response = self.client.request(acc_info)
        result = response.result
        if "account_nfts" in result:
            account_nfts = result["account_nfts"] 
            for nfts in account_nfts:
                nft = {}
                nft["flags"] = nfts["Flags"] if "Flags" in nfts else 0
                nft["issuer"] = nfts["Issuer"]
                nft["id"] = nfts["NFTokenID"]
                nft["taxon"] = nfts["NFTokenTaxon"]
                nft["serial"] = nfts["nft_serial"]
                nft["uri"] = nfts["URI"] if "URI" in nfts else ""
                nft["transfer_fee"] = xrp_format_to_nft_fee(nfts["TransferFee"]) if "TransferFee" in nfts else 0
                account_nft.append(nft)
        return account_nft
    
    def send_nft(self, sender_addr: str, nftoken_id: str, receiver: str, memo: Memo = None, fee: str = None) -> dict:
        """send an nft"""
        txn = NFTokenCreateOffer(
            account=sender_addr,
            nftoken_id=nftoken_id,
            amount="0",
            destination=receiver,
            flags=NFTokenCreateOfferFlag.TF_SELL_NFTOKEN,
            memos=[memo],
            source_tag=M_SOURCE_TAG,
            fee=fee)
        return txn.to_dict()
    
    def receive_nft(self, sender_addr: str, nft_sell_id: str, fee: str = None) -> dict:
        """receive an nft"""
        txn = NFTokenAcceptOffer(
            account=sender_addr,
            nftoken_sell_offer=nft_sell_id, fee=fee, source_tag=M_SOURCE_TAG, memos=[memo_builder(D_TYPE, D_DATA)])
        return txn.to_dict()




# from xrpl.core import keypairs
# from xrpl.models import Transaction
# from xrpl.transaction import safe_sign_and_autofill_transaction
# from xrpl.transaction.reliable_submission import send_reliable_submission

# w = xWallet("https://s.altnet.rippletest.net:51234", "", "")
# from xrpl.clients.websocket_client import WebsocketClient
# from xrpl.wallet import Wallet

# from Misc import get_test_xrp

# # print(get_test_xrp(Wallet("sEdT1DxxEcgsR3FfcWrYGdHJHjKmBBT", sequence=0)))

# # print(w.account_root_flags(Wallet(sequence=0, seed="sEdT1DxxEcgsR3FfcWrYGdHJHjKmBBT").classic_address))
# # print(w.get_network_fee())
# # print(w.send_xrp(
# #     "sEdT1DxxEcgsR3FfcWrYGdHJHjKmBBT",
# #     "TVTza8KZ6KUSk49Qs67zE7oP6ryPZehWGfBYi9b92fmZG5T",
# #     10.00
# # ))




# def generate_xrp_wallet(name: str) -> dict:
#     """generate a new xrp wallet"""
#     wallet_info = {}
#     wallet = Wallet.create()
#     seed = wallet.seed
#     public, private = keypairs.derive_keypair(seed)
#     wallet_info["name"] = name
#     wallet_info["classic_address"] = wallet.classic_address
#     wallet_info["private_key"] = private
#     wallet_info["public_key"] = public
#     wallet_info["seed"] = seed
#     return wallet_info

# def get_test_xrp(wallet: Wallet) -> None:
#     """fund your account with free 1000 test xrp"""
#     testnet_url = "http://amm.devnet.rippletest.net:51234"
#     client = JsonRpcClient(testnet_url)
#     generate_faucet_wallet(client, wallet)

# # testnet_url = ""
# # client = JsonRpcClient(testnet_url)
# # for i in range(10):
# #     g = generate_xrp_wallet("")
# #     print(g)
# #     generate_faucet_wallet(client, Wallet(seed=g["seed"], sequence=0))
# #     print("done")

# # for i in range(10):
# #     get_test_xrp(Wallet(seed="sEd7dtFEiBbjG8dr5TNyYWM1hwx7oNq", sequence=0))
# #     get_test_xrp(Wallet(seed="sEdVUSpic5Z9pBouWa7zXJeb6WyJPUP", sequence=0))
# #     get_test_xrp(Wallet(seed="sEd7X5zNW5uhLdcbT4Rcab9hjuVgLDz", sequence=0))
# #     get_test_xrp(Wallet(seed="sEdVGVr8ch6VAnzbmeXKG453k5j1nKT", sequence=0))
# #     get_test_xrp(Wallet(seed="sEdVWvSKnc9jM77oFMDugkMQkNzJkdS", sequence=0))
# #     get_test_xrp(Wallet(seed="sEdSvouU24Dq7YjQttG4rnnQ2KRdmnk", sequence=0))
# #     get_test_xrp(Wallet(seed="sEdVZc9GF92YRbaDCjSWMVQUofaS9YR", sequence=0))
# #     get_test_xrp(Wallet(seed="sEd7XyyRYFEvvWCa4WB4U7nq1uE6uWu", sequence=0))

# #     print("done")

# aw = xWallet("http://amm.devnet.rippletest.net:51234", "", "")
# print(aw.account_tokens(
#     "rKsDNENiGA6CdC2V6NEmw3V7dTTJ5S5dPH"
# ))


# # sw = Wallet()
# def sign_and_submit(txn, wallet, client):
#     stxn_payment = safe_sign_and_autofill_transaction(txn, wallet, client)
#     stxn_response = send_reliable_submission(stxn_payment, client)
#     stxn_result = stxn_response.result
#     return {
#         "result": stxn_result["meta"]["TransactionResult"],
#         "txid": stxn_result["hash"],
# }

# twc = Wallet(seed="sEdVUSpic5Z9pBouWa7zXJeb6WyJPUP", sequence=0)

# # print(int("10011001", 2))

# # print(sign_and_submit(
# #     Transaction.from_dict(
# #         aw.send_token(
# #             twc.classic_address,
# #             "rKsDNENiGA6CdC2V6NEmw3V7dTTJ5S5dPH",
# #             "030ADB868027B0185A6577C34F857236E359E88D",
# #             str(50000),
# #             "rU9qUW2skB7Z71JKV7H7fVWc6AU1DXiWVm",
# #             True,
# #             is_lp_token=True,
# #             memo=memo_builder("Done-with-Myrkle", "https://myrkle.app"),
# #         )), twc, aw.client))



# # f = Transaction.from_dict(aw.send_token(
# #     twc.classic_address,
# #     "rKsDNENiGA6CdC2V6NEmw3V7dTTJ5S5dPH",
# #     "030ADB868027B0185A6577C34F857236E359E88D",
# #     str(50000),
# #     "rU9qUW2skB7Z71JKV7H7fVWc6AU1DXiWVm",
# #     True,
# #     is_lp_token=True,
# #     memo=memo_builder("Done-with-Myrkle", "https://myrkle.app"),
# # ))

# # print(f.blob())


# # print(Transaction.from_dict(txn).blob())