from xrpl.clients import JsonRpcClient
from xrpl.models import (AccountSet, AccountSetFlag, IssuedCurrencyAmount,
                         NFTokenBurn, NFTokenMint, NFTokenMintFlag, Payment,
                         TrustSet, TrustSetFlag)

from Misc import (mm, nft_fee_to_xrp_format, symbol_to_hex,
                  transfer_fee_to_xrp_format, validate_symbol_to_hex)
from x_constants import M_SOURCE_TAG

"""create tokens, nfts"""


class xAsset(JsonRpcClient):
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
    
    """steps to creating a token; must use 2 new accounts"""
    """1"""
    def accountset_issuer(self, issuer_addr: str, ticksize: int, transferfee: float, domain: str, fee: str = None) -> dict:
        txn = AccountSet(account=issuer_addr, set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE, tick_size=ticksize,
        transfer_rate=transfer_fee_to_xrp_format(transferfee), domain=validate_symbol_to_hex(domain), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    """2"""
    def accountset_manager(self, manager_addr: str, domain: str, fee: str = None) -> dict:
        txn = AccountSet(account=manager_addr,
                         set_flag=AccountSetFlag.ASF_REQUIRE_AUTH,
                        domain=validate_symbol_to_hex(domain), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    """3"""
    def create_trustline(self, manager_addr: str, issuer_addr: str, token_name: str, total_supply: str, fee: str = None) -> dict:
        txn = TrustSet(
            account=manager_addr,
            limit_amount=IssuedCurrencyAmount(
                currency=validate_symbol_to_hex(token_name),
                issuer=issuer_addr,
                value=total_supply,
            ),source_tag=M_SOURCE_TAG,
            # flags=TrustSetFlag.TF_SET_NO_RIPPLE,
              fee=fee, memos=mm())
        return txn.to_dict()
    
    """4"""
    def create_token(self, issuer_addr: str, manager_addr: str, token_name: str, total_supply: str, fee: str = None) -> dict:
        txn = Payment(
            account=issuer_addr,
            destination=manager_addr,
            amount=IssuedCurrencyAmount(
                currency=validate_symbol_to_hex(token_name),
                issuer=issuer_addr,
                value=total_supply), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

        

    def burn_token(self, sender_addr: str, token: str, issuer: str, amount: float, fee: str = None) -> dict:
        """burn a token"""
        txn = Payment(
            account=sender_addr,
            destination=issuer,
            amount=IssuedCurrencyAmount(currency=validate_symbol_to_hex(token), issuer=issuer, value=amount), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def mint_nft(self, issuer_addr: str, taxon: int, is_transferable: bool, only_xrp: bool, issuer_burn: bool, transfer_fee: float = None, uri: str = None, fee: str = None) -> dict:
        """mint nft"""
        flag = []
        if is_transferable:
            flag.append(NFTokenMintFlag.TF_TRANSFERABLE) # nft can be transferred
        if only_xrp:
            flag.append(NFTokenMintFlag.TF_ONLY_XRP) # nft may be traded for xrp only
        if issuer_burn:
            flag.append(NFTokenMintFlag.TF_BURNABLE) # If set, indicates that the minted token may be burned by the issuer even if the issuer does not currently hold the token.
        txn = NFTokenMint(
            account=issuer_addr,
            nftoken_taxon=taxon,
            uri=validate_symbol_to_hex(uri), flags=flag, transfer_fee=nft_fee_to_xrp_format(transfer_fee), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    def burn_nft(self, sender_addr: str, nftoken_id: str, holder: str = None, fee: str = None) -> dict:
        """burn an nft, specify the holder if the token is not in your wallet, only issuer and holder can call"""
        txn = NFTokenBurn(account=sender_addr, nftoken_id=nftoken_id, owner=holder, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
# from Wallet import Transaction, Wallet, sign_and_submit

# x = xAsset ("http://amm.devnet.rippletest.net:51234", "", "")#("http://amm.devnet.rippletest.net:51234", "", "")

# wal1 = Wallet("sEdTZb5N6pyxPDfxmGy6qCcjKg3N7AZ", 0)

# wal2 = Wallet("sEdVWvSKnc9jM77oFMDugkMQkNzJkdS", 0)


# iss = x.accountset_issuer(
#     wal1.classic_address,
#     5,
#     2,
#     symbol_to_hex("domain.com"),
# )

# print(wal1.classic_address)
# print(wal2.classic_address)

# mag = x.accountset_manager(
#     wal2.classic_address,
#     domain=symbol_to_hex("url.com").lower()
# )

# ct = x.create_trustline(
#     wal2.classic_address,
#     wal1.classic_address,
#     "USD",
#     1_000_000_000,
# )

# ctt = x.create_token(
#     wal1.classic_address,
#     wal2.classic_address,
#     "USD",
#     1_000_000_000,
# )

# print(sign_and_submit(
#     Transaction.from_dict(iss),
#     wal1,
#     x.client
# ))
# print("done 1")

# print(sign_and_submit(
#     Transaction.from_dict(mag),
#     wal2,
#     x.client
# ))
# print("done 2")

# print(sign_and_submit(
#     Transaction.from_dict(ct),
#     wal2,
#     x.client
# ))
# print("done 3")

# print(sign_and_submit(
#     Transaction.from_dict(ctt),
#     wal1,
#     x.client
# ))
# print("done 4")

