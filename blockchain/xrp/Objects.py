from decimal import Decimal
from typing import Union

from xrpl.clients import JsonRpcClient
from xrpl.models import (XRP, AccountObjects, AccountOffers, BookOffers,
                         CheckCancel, CheckCash, CheckCreate, EscrowCancel,
                         EscrowCreate, EscrowFinish, IssuedCurrency,
                         IssuedCurrencyAmount, LedgerEntry, OfferCancel,
                         OfferCreate, Tx, OfferCreateFlag)
from xrpl.utils import drops_to_xrp, ripple_time_to_datetime, xrp_to_drops

from .Misc import mm, validate_hex_to_symbol, validate_symbol_to_hex
from .x_constants import M_SOURCE_TAG



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

    def create_xrp_check(self, sender_addr: str, receiver_addr: str, amount: Union[int, float, Decimal], expiry_date: int = None, fee: str = None) -> dict:
        """create xrp check"""
        txn = CheckCreate(account=sender_addr, destination=receiver_addr, send_max=xrp_to_drops(amount), expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
        
    def account_checks(self, wallet_addr: str, limit: int = None) -> dict:
        """return a dict of checks an account sent or received"""
        checks_dict = {}
        sent = []
        receive = []
        req = AccountObjects(account=wallet_addr, ledger_index="validated", type="check", limit=limit)
        response = self.client.request(req)
        result = response.result
        if "account_objects" in result:
            account_checks = result["account_objects"]
            for check in account_checks:
                check_data = {}
                check_data["check_id"] = check["index"]
                check_data["sender"] = check["Account"]
                check_data["receiver"] = check["Destination"]
                check_data["expiry_date"] = ""
                if isinstance(check["SendMax"], str):
                    check_data["token"] = "XRP"
                    check_data["issuer"] = ""
                    check_data["amount"] = str(drops_to_xrp(check["SendMax"]))
                if isinstance(check["SendMax"], dict):
                    check_data["token"] = validate_hex_to_symbol(check["SendMax"]["currency"])
                    check_data["issuer"] = check["SendMax"]["issuer"]
                    check_data["amount"] = check["SendMax"]["value"]
                if "Expiration" in check:
                    check_data["expiry_date"] = str(ripple_time_to_datetime(check["Expiration"]))

                if check_data["sender"] == wallet_addr:
                    sent.append(check_data)
                elif check_data["sender"] != wallet_addr:
                    receive.append(check_data)
        checks_dict["sent"] = sent
        checks_dict["receive"] = receive
        return checks_dict

    def cash_xrp_check(self, sender_addr: str, check_id: str, amount: Union[int, Decimal, float], fee: str = None) -> dict:
        """cash a check, only the receiver defined on creation can cash a check"""
        txn = CheckCash(account=sender_addr, check_id=check_id, amount=xrp_to_drops(amount), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    def cancel_check(self, sender_addr: str, check_id: str, fee: str = None) -> dict:
        """cancel a check"""
        txn = CheckCancel(account=sender_addr, check_id=check_id, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict() 

    def create_token_check(self, sender_addr: str, receiver_addr: str, token: str, amount: str, issuer: str, expiry_date: Union[int, None], fee: str = None) -> dict:
        """create a token check"""
        txn = CheckCreate(account=sender_addr, destination=receiver_addr,
        send_max=IssuedCurrencyAmount(
            currency=validate_symbol_to_hex(token), 
            issuer=issuer, 
            value=amount), expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    def cash_token_check(self, sender_addr: str, check_id: str, token: str, amount: str, issuer: str, fee: str = None) -> dict:
        """cash a check, only the receiver defined on creation
        can cash a check"""
        txn = CheckCash(account=sender_addr, check_id=check_id, amount=IssuedCurrencyAmount(
            currency=validate_symbol_to_hex(token),
            issuer=issuer,
            value=amount), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    def create_xrp_escrow(self, sender_addr: str, amount: Union[int, float, Decimal], receiver_addr: str, condition: Union[str, None], claim_date: Union[int, None], expiry_date: Union[int, None], fee: str = None) -> dict:
        """create an Escrow\n
        fill condition with `Misc.gen_condition_fulfillment["condition"]`\n
        You must use one `claim_date` or `expiry_date` unless this will fail"""
        txn = EscrowCreate(account=sender_addr, amount=xrp_to_drops(amount), destination=receiver_addr, finish_after=claim_date, cancel_after=expiry_date, condition=condition, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def schedule_xrp(self, sender_addr: str, amount: Union[int, float, Decimal], receiver_addr: str, claim_date: int, expiry_date: Union[int, None], fee: str = None) -> dict:
        """schedule an Xrp payment
        \n expiry date must be greater than claim date"""
        txn = EscrowCreate(account=sender_addr, amount=xrp_to_drops(amount), destination=receiver_addr, finish_after=claim_date, cancel_after=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def account_xrp_escrows(self, wallet_addr: str, limit: int = None) -> dict:
        """returns all account escrows, used for returning scheduled payments"""
        escrow_dict = {}
        sent = []
        received = []
        req = AccountObjects(account=wallet_addr, ledger_index="validated", type="escrow", limit=limit)
        response = self.client.request(req)
        result = response.result
        if "account_objects" in result:
            escrows = result["account_objects"]
            for escrow in escrows:
                if isinstance(escrow["Amount"], str):
                    escrow_data = {}
                    escrow_data["escrow_id"] = escrow["index"]
                    escrow_data["sender"] = escrow["Account"]
                    escrow_data["receiver"] = escrow["Destination"]
                    escrow_data["amount"] = str(drops_to_xrp(escrow["Amount"]))
                    escrow_data["prev_txn_id"] = ""
                    escrow_data["redeem_date"] = ""
                    escrow_data["expiry_date"] = ""
                    escrow_data["condition"] = ""
                    if "PreviousTxnID" in escrow:
                        escrow_data["prev_txn_id"] = escrow["PreviousTxnID"] # needed to cancel or complete the escrow
                    if "FinishAfter" in escrow:
                        escrow_data["redeem_date"] = str(ripple_time_to_datetime(escrow["FinishAfter"]))
                    if "CancelAfter" in escrow:
                        escrow_data["expiry_date"] = str(ripple_time_to_datetime(escrow["CancelAfter"]))
                    if "Condition" in escrow:
                        escrow_data["condition"] = escrow["Condition"]
                        
                    if escrow_data["sender"] == wallet_addr:
                        sent.append(escrow_data)
                    else:
                        received.append(escrow_data)
        escrow_dict["sent"] = sent
        escrow_dict["received"] = received
        return escrow_dict
    
    def r_seq_dict(self, prev_txn_id: str) -> dict:
        """return escrow seq or ticket sequence for finishing or cancelling \n use seq_back_up if seq is null"""
        info_dict = {}
        info_dict["sequence"] = ""
        info_dict["seq_back_up"] = ""
        req = Tx(transaction=prev_txn_id)
        response = self.client.request(req)
        result = response.result
        if "Sequence" in result:
            info_dict["sequence"] = result["Sequence"]
        if "TicketSequence" in result:
            info_dict["seq_back_up"] = result["TicketSequence"]
        return info_dict
    
    def r_sequence(self, prev_txn_id: str) -> int:
        """return escrow seq for finishing or cancelling escrow"""
        seq = 0
        req = Tx(transaction=prev_txn_id)
        response = self.client.request(req)
        result = response.result
        if "Sequence" in result:
            seq = result["Sequence"]
        return seq

    def cancel_xrp_escrow(self, sender_addr: str, escrow_creator: str, prev_txn_id: str, fee: str = None) -> dict:
        """cancel an escrow\n
        If the escrow does not have a CancelAfter time, it never expires """
        seq = self.r_sequence(prev_txn_id)
        txn = EscrowCancel(account=sender_addr, owner=escrow_creator, offer_sequence=seq, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def finish_xrp_escrow(self, sender_addr: str, escrow_creator: str, prev_txn_id: str, condition: Union[str, None], fulfillment: Union[str, None], fee: str = None) -> dict:
        """complete an escrow\n
        cannot be called until the finish time is reached"""
        seq = self.r_sequence(prev_txn_id)
        txn = EscrowFinish(account=sender_addr, owner=escrow_creator, offer_sequence=seq, condition=condition, fulfillment=fulfillment, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()
    
    def create_offer(self, sender_addr: str, pay: Union[float, IssuedCurrencyAmount], receive: Union[float, IssuedCurrencyAmount], expiry_date: int = None,
        tf_passive: bool = False, tf_immediate_or_cancel: bool = False, tf_fill_or_kill: bool = False, tf_sell: bool = False, fee: str = None) -> dict:
        """create an offer"""
        flags = []
        if tf_passive:
            flags.append(OfferCreateFlag.TF_PASSIVE)
        if tf_immediate_or_cancel:
            flags.append(OfferCreateFlag.TF_IMMEDIATE_OR_CANCEL)
        if tf_fill_or_kill:
            flags.append(OfferCreateFlag.TF_FILL_OR_KILL)
        if tf_sell:
            flags.append(OfferCreateFlag.TF_SELL)
        txn_dict = {}
        if isinstance(receive, float) and isinstance(pay, IssuedCurrencyAmount): # check if give == xrp and get == asset
            txn = OfferCreate(account=sender_addr, taker_pays=xrp_to_drops(receive), taker_gets=pay, expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG, flags=flags)
            txn_dict = txn.to_dict()
        if isinstance(receive, IssuedCurrencyAmount) and isinstance(pay, float): # check if give == asset and get == xrp
            txn = OfferCreate(account=sender_addr, taker_pays=receive, taker_gets=xrp_to_drops(pay), expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG, flags=flags)
            txn_dict = txn.to_dict()
        if isinstance(receive, IssuedCurrencyAmount) and isinstance(pay, IssuedCurrencyAmount): # check if give and get are == asset
            txn = OfferCreate(account=sender_addr, taker_pays=receive, taker_gets=pay, expiration=expiry_date, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG, flags=flags)
            txn_dict = txn.to_dict()
        return txn_dict
    
    def account_offers(self, wallet_addr: str, limit: int = None) -> list:
        """return all offers an account created"""
        offer_list = []
        req = AccountOffers(account=wallet_addr, ledger_index="validated", limit=limit)
        response = self.client.request(req)
        result = response.result
        if "offers" in result:
            offers = result["offers"]
            for offer in offers:
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
    
    def cancel_offer(self, sender_addr: str, offer_seq: int, fee: str = None) -> dict:
        """cancel an offer"""
        txn = OfferCancel(account=sender_addr, offer_sequence=offer_seq, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def all_offers(self, pay: Union[XRP, IssuedCurrency], receive: Union[XRP, IssuedCurrency], limit: int = None) -> list:
        """returns all offers for 2 pairs"""
        all_offers_list = []
        req = BookOffers(taker_gets=pay, taker_pays=receive, ledger_index="validated", limit=limit)
        response = self.client.request(req)
        result = response.result
        if "offers" in result:
            offers = result["offers"]
            for offer in offers:
                of = {}
                of["creator"] = offer["Account"]
                of["offer_id"] = offer["index"]
                of["sequence"] = offer["Sequence"] # offer id
                of["rate"] = offer["quality"]
                of["flags"] = offer["Flags"]
                of["creator_liquidity"] = ""
                if "owner_funds" in offer and isinstance(offer["TakerGets"], str):
                    of["creator_liquidity"] = f'{float(drops_to_xrp(offer["owner_funds"]))} XRP' # Amount of the TakerGets currency the side placing the offer has available to be traded.
                if "owner_funds" in offer and isinstance(offer["TakerGets"], dict):
                    of["creator_liquidity"] = f'{offer["owner_funds"]}  {validate_hex_to_symbol(offer["TakerGets"]["currency"])}' # Amount of the TakerGets currency the side placing the offer has available to be traded.
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
                all_offers_list.append(of)
        return all_offers_list
    
# from xrpl.wallet import Wallet

# o = xObject("https://s.altnet.rippletest.net:51234", "", "")
# print(o.account_offers(Wallet("sEd7K2Qve1VGS1MqKtYfeY2SEggaPGD",0).classic_address))
# print(o.all_offers(
#     XRP(),
#     IssuedCurrency(
#     currency="USD",
#     issuer = "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
#     )
# ))

# req = BookOffers(taker_gets=XRP(), taker_pays=IssuedCurrency(
#     currency="USD",
#     issuer = "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"
#     ), ledger_index="validated")

# req = LedgerEntry(ledger_index="validated", offer="2E6BFB6EEF28584C588A10B6C3921F3CACF7CA24BC9175371F7D6732075CC0F1")
# response = o.client.request(req)
# result = response.result
# print(result)