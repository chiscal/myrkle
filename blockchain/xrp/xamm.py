from decimal import Decimal
from typing import Union

from xrpl.clients import JsonRpcClient
from xrpl.models import (XRP, AccountObjects, AccountOffers, BookOffers,
                         CheckCancel, CheckCash, CheckCreate, EscrowCancel,
                         EscrowCreate, EscrowFinish, IssuedCurrency,
                         IssuedCurrencyAmount, LedgerEntry, OfferCancel,
                         OfferCreate, Tx)
from xrpl.utils import drops_to_xrp, ripple_time_to_datetime, xrp_to_drops

from .Misc import mm, validate_hex_to_symbol, validate_symbol_to_hex, amm_fee_to_xrp_format
from .x_constants import M_SOURCE_TAG
from typing import Union

from xrpl.clients import JsonRpcClient
from xrpl.models import (XRP, AccountOffers, AMMCreate, AMMVote, BookOffers,
                         IssuedCurrency, IssuedCurrencyAmount, OfferCreate,
                         OfferCreateFlag, AuthAccount, AMMBid)
from xrpl.utils import drops_to_xrp, xrp_to_drops
from xrpl.wallet import Wallet



class xObject(JsonRpcClient):
    def __init__(self, network_url: str, account_url: str, txn_url: str ):
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
    
    def cancel_offer(self, sender_addr: str, offer_seq: int, fee: str = None) -> dict:
        """cancel an offer"""
        txn = OfferCancel(account=sender_addr, offer_sequence=offer_seq, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

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