from typing import Union

from xrpl.clients import JsonRpcClient
from xrpl.models import (XRP, AccountOffers, AMMCreate, AMMVote, BookOffers,
                         IssuedCurrency, IssuedCurrencyAmount, OfferCreate,
                         OfferCreateFlag, AuthAccount, AMMBid)
from xrpl.utils import drops_to_xrp, xrp_to_drops
from xrpl.wallet import Wallet

from .Misc import (amm_fee_to_xrp_format, mm,
                  validate_hex_to_symbol)
from .x_constants import M_SOURCE_TAG

"""
Swap objects

Manages AMM and order book objects

Call order book swaps Non determinstic swap (sounds cool)
"""



class xOrderBookExchange(JsonRpcClient):
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
    
    def sort_best_offer(self, buy: Union[XRP, IssuedCurrency], sell: Union[XRP, IssuedCurrency], best_buy: bool = False, best_sell: bool = False, limit: int = None) -> dict:
        """return all available orders and best {option} first, choose either best_buy or best_sell"""
        best = {}

        if best_sell:
            req = BookOffers(taker_gets=sell, taker_pays=buy, ledger_index="validated", limit=limit)
            response = self.client.request(req)
            result = response.result
            if "offers" in result:
                offers: list = result["offers"]
                # sort offer list and return highest rate first
                offers.sort(key=lambda object: object["quality"], reverse=True)
                index = 0
                for offer in offers:
                    of = {}
                    of["creator"] = offer["Account"]
                    of["offer_id"] = offer["index"]
                    of["flags"] = offer["Flags"]
                    of["sequence"] = offer["Sequence"] # offer id
                    of["rate"] = offer["quality"]
                    of["creator_liquidity"] = ""
                    if "owner_funds" in offer:
                        of["creator_liquidity"] = offer["owner_funds"] # available amount the offer creator of `sell_token` is currently holding
                    if isinstance(offer["TakerPays"], dict):
                        of["buy_token"] = validate_hex_to_symbol(offer["TakerPays"]["currency"])
                        of["buy_issuer"] = offer["TakerPays"]["issuer"]
                        of["buy_amount"] = offer["TakerPays"]["value"]
                    elif isinstance(offer["TakerPays"], str):
                        of["buy_token"] = "XRP"
                        of["buy_issuer"] = ""
                        of["buy_amount"] = str(drops_to_xrp(offer["TakerPays"]))

                    if isinstance(offer["TakerGets"], dict):
                        of["sell_token"] = validate_hex_to_symbol(offer["TakerGets"]["currency"])
                        of["sell_issuer"] = offer["TakerGets"]["issuer"]
                        of["sell_amount"] = offer["TakerGets"]["value"]
                    elif isinstance(offer["TakerGets"], str):
                        of["sell_token"] = "XRP"
                        of["sell_issuer"] = ""
                        of["sell_amount"] = str(drops_to_xrp(offer["TakerGets"]))                    
                    index += 1
                    best[index] = of

        if best_buy:
            req = BookOffers(taker_gets=sell, taker_pays=buy, ledger_index="validated", limit=limit)
            response = self.client.request(req)
            result = response.result
            if "offers" in result:
                offers: list = result["offers"]
                # sort offer list and return lowest rate first
                offers.sort(key=lambda object: object["quality"])
                index = 0
                for offer in offers:
                    of = {}
                    of["creator"] = offer["Account"]
                    of["offer_id"] = offer["index"]
                    of["flags"] = offer["Flags"]
                    of["sequence"] = offer["Sequence"] # offer id
                    of["rate"] = offer["quality"]
                    of["creator_liquidity"] = ""
                    if "owner_funds" in offer:
                        of["creator_liquidity"] = offer["owner_funds"] # available amount the offer creator is currently holding
                    if isinstance(offer["TakerPays"], dict):
                        of["buy_token"] = validate_hex_to_symbol(offer["TakerPays"]["currency"])
                        of["buy_issuer"] = offer["TakerPays"]["issuer"]
                        of["buy_amount"] = offer["TakerPays"]["value"]
                    elif isinstance(offer["TakerPays"], str):
                        of["buy_token"] = "XRP"
                        of["buy_issuer"] = ""
                        of["buy_amount"] = str(drops_to_xrp(offer["TakerPays"]))

                    if isinstance(offer["TakerGets"], dict):
                        of["sell_token"] = validate_hex_to_symbol(offer["TakerGets"]["currency"])
                        of["sell_issuer"] = offer["TakerGets"]["issuer"]
                        of["sell_amount"] = offer["TakerGets"]["value"]
                    elif isinstance(offer["TakerGets"], str):
                        of["sell_token"] = "XRP"
                        of["sell_issuer"] = ""
                        of["sell_amount"] = str(drops_to_xrp(offer["TakerGets"]))                    
                    index += 1
                    best[index] = of
        return best
    
    def create_order_book_liquidity(self, sender_addr: str, buy: Union[float, IssuedCurrencyAmount], sell: Union[float, IssuedCurrencyAmount], expiry_date: int = None, fee: str = None) -> dict:
        """create an offer as passive; it doesn't immediately consume offers that match it, just stays on the ledger as an object for liquidity"""
        flags = [OfferCreateFlag.TF_PASSIVE]
        tx_dict = {}
        if isinstance(buy, float) and isinstance(sell, IssuedCurrencyAmount): # check if give == xrp and get == asset
            txn = OfferCreate(account=sender_addr, taker_pays=xrp_to_drops(buy), taker_gets=sell, flags=flags, expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        if isinstance(buy, IssuedCurrencyAmount) and isinstance(sell, float): # check if give == asset and get == xrp
            txn = OfferCreate(account=sender_addr, taker_pays=buy, taker_gets=xrp_to_drops(sell), flags=flags, expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        if isinstance(buy, IssuedCurrencyAmount) and isinstance(sell, IssuedCurrencyAmount): # check if give and get are == asset
            txn = OfferCreate(account=sender_addr, taker_pays=buy, taker_gets=sell, flags=flags, expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        return tx_dict
    
    def get_account_order_book_liquidity(self, wallet_addr: str, limit: int = None) -> list:
        """return all offers that are liquidity an account created"""
        offer_list = []
        req = AccountOffers(account=wallet_addr, ledger_index="validated", limit=limit)
        response = self.client.request(req)
        result = response.result
        if "offers" in result:
            offers = result["offers"]
            for offer in offers:
                if 0x00010000 & offer["flags"] == 0x00010000:
                    of = {}
                    of["flags"] = offer["flags"]
                    of["sequence"] = offer["seq"]
                    of["quality"] = offer["quality"]# str(drops_to_xrp(offer["quality"])) # rate is subject to error from the blockchain because xrp returned in this call has no decimal  # The exchange rate of the offer, as the ratio of the original taker_pays divided by the original taker_gets. rate = pay/get
                    if isinstance(offer["taker_pays"], dict):
                        of["buy_token"] = validate_hex_to_symbol(offer["taker_pays"]["currency"])
                        of["buy_issuer"] = offer["taker_pays"]["issuer"]
                        of["buy_amount"] = offer["taker_pays"]["value"]
                    elif isinstance(offer["taker_pays"], str):
                        of["buy_token"] = "XRP"
                        of["buy_issuer"] = ""
                        of["buy_amount"] = str(drops_to_xrp(offer["taker_pays"]))
                    if isinstance(offer["taker_gets"], dict):
                        of["sell_token"] = validate_hex_to_symbol(offer["taker_gets"]["currency"])
                        of["sell_issuer"] = offer["taker_gets"]["issuer"]
                        of["sell_amount"] = offer["taker_gets"]["value"]
                    elif isinstance(offer["taker_gets"], str):
                        of["sell_token"] = "XRP"
                        of["sell_issuer"] = ""
                        of["sell_amount"] = str(drops_to_xrp(offer["taker_gets"]))
                    of["rate"] = float(of["sell_amount"])/float(of["buy_amount"])
                    offer_list.append(of)
        return offer_list


    def order_book_swap(self, sender_addr: str, buy: Union[float, IssuedCurrencyAmount], sell: Union[float, IssuedCurrencyAmount], swap_all: bool = False, fee: str = None) -> dict:
        """create an offer that either matches with existing offers to get entire sell amount or cancels\n
        if swap_all is enabled, this will force exchange all the paying units regardless of profit or loss\n

        if tecKILLED is the result, exchange didnt go through because all of the `buy` couldnt be obtained. recommend enabling swap_all
        """
        flags = [OfferCreateFlag.TF_FILL_OR_KILL]
        if swap_all:
            flags.append(OfferCreateFlag.TF_SELL)
        tx_dict = {}
        if isinstance(buy, float) and isinstance(sell, IssuedCurrencyAmount): # check if give == xrp and get == asset
            txn = OfferCreate(account=sender_addr, taker_pays=xrp_to_drops(buy), taker_gets=sell, flags=flags, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        if isinstance(buy, IssuedCurrencyAmount) and isinstance(sell, float): # check if give == asset and get == xrp
            txn = OfferCreate(account=sender_addr, taker_pays=buy, taker_gets=xrp_to_drops(sell), flags=flags, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        if isinstance(buy, IssuedCurrencyAmount) and isinstance(sell, IssuedCurrencyAmount): # check if give and get are == asset
            txn = OfferCreate(account=sender_addr, taker_pays=buy, taker_gets=sell, flags=flags, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
            tx_dict = txn.to_dict()
        return tx_dict

    
    """The AMM ERA is here"""
    

"""Liquidity providers can vote to set the fee from 0% to 1%, in increments of 0.%."""

class xAmm(JsonRpcClient):
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
    
    def create_amm(self, sender_addr: str, token_1: Union[float, IssuedCurrencyAmount], token_2: Union[float, IssuedCurrencyAmount], trading_fee: float, fee: str = None) -> dict:
        """create a liquidity pool for asset pairs if one doesnt already exist"""      
        token1 = xrp_to_drops(token_1) if isinstance(token_1, float) else token_1
        token2 = xrp_to_drops(token_2) if isinstance(token_2, float) else token_2
        txn = AMMCreate(
            account=sender_addr,
            amount=token1,
            amount2=token2,
            trading_fee=amm_fee_to_xrp_format(trading_fee), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict() 
    
    def amm_vote(self, sender_addr: str, token_1: Union[XRP, IssuedCurrency], token_2: Union[XRP, IssuedCurrency], trading_fee: float, fee: str = None) -> dict:
        """cast a vote to modify AMM fee"""
        txn = AMMVote(
            account=sender_addr,
            asset=token_1,
            asset2=token_2,
            trading_fee=amm_fee_to_xrp_format(trading_fee), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict() 
    

    """work this"""
    def amm_bid(self, sender_addr: str, token_1: Union[XRP, IssuedCurrency], token_2: Union[XRP, IssuedCurrency],
        auth_accounts: list[AuthAccount] = None, bid_max: IssuedCurrencyAmount= None, bid_min: IssuedCurrencyAmount = None, fee: str = None):
        """token 1 and 2 are the amm tokens, bid max and bid min are the Lp's token"""
        txn = AMMBid(
            account=sender_addr,
            asset=token_1,
            asset2=token_2,
            auth_accounts=auth_accounts,
            bid_max=bid_max,
            bid_min=bid_min, source_tag=M_SOURCE_TAG)
        return txn.to_dict() 
        
# from Wallet import Transaction, Wallet, sign_and_submit

# tw = Wallet("sEd7K2Qve1VGS1MqKtYfeY2SEggaPGD",0) 

# add1 = "rw787k9xc1sTmYN151btHFiCjKUA6zrgvT"
# o = xOrderBookExchange("https://s.altnet.rippletest.net:51234", "", "")
# of = o.create_order_book_liquidity(
#     tw.classic_address,
#     10.0,
#     IssuedCurrencyAmount('USD', '', 1003),
# )

# print(sign_and_submit(Transaction.from_dict(value= o.create_order_book_liquidity(
#     tw.classic_address,
#     IssuedCurrencyAmount(
#     currency="BTC",
#     issuer = "raNu1iJVaSofuR9yKkUK63X5h9FBWUEJ3N",
#     value=5103.4
#     ),
#     10.0,
# )), tw, o.client))
# print(o.get_account_order_book_liquidity(tw.classic_address))


# req = AccountOffers(account="rBEvLUA3AksHBknWJVrUz7VZPTsGan81y2", ledger_index="validated")
# response = o.client.request(req)
# result = response.result
# print(result)
