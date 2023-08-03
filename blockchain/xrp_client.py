from decimal import Decimal
from typing import Dict, List, Union

from xrpl.models import AuthAccount, IssuedCurrency, IssuedCurrencyAmount, XRP

from .xrp.Assets import xAsset
from .xrp.Eng import xEng
from .xrp.Exchange import xAmm, xOrderBookExchange
from .xrp.Info import xInfo, status
from .xrp.Nft import xNFT
from .xrp.Objects import xObject
from .xrp.Wallet import xWallet
from .xrp.x_constants import XURLS_
from .xrp.xamm import xObject as XammObject

test_url = XURLS_["TESTNET_URL"]
test_txns = XURLS_["TESTNET_TXNS"]
test_account =  XURLS_["TESTNET_ACCOUNT"]


def transaction_status(txid, mainnet=False):
    return status(txid, mainnet)

class XRPWalletClient():
    wallet = xWallet(test_url, test_account, test_txns)
    
    # switchers
    def switch_to_main_net(self):
        return self.wallet.toMainnet()

    def switch_to_test_net(self):
        return self.wallet.toTestnet()

    # getters

    def get_balance(self, address: str):
        try:
            return self.wallet.xrp_balance(address)
        except Exception as exception:
            raise ValueError(f"Error while running get balance, {str(exception)}")

    def get_transactions(self, address: str):
        try:
            return self.wallet.payment_transactions(address)
        except Exception as exception:
            raise ValueError(f"Error while running get transactions, {str(exception)}")
    
    def get_token_transactions(self, address: str, limit: int=0):
        try:
            return self.wallet.token_transactions(address, limit)
        except Exception as exception:
            raise ValueError(
                f"Error while running get token transactions,\
                {str(exception)}"
            )
    
    def get_xrp_transactions(self, address:str, limit: int=0):
        try:
            return self.wallet.xrp_transactions(address, limit)
        except Exception as exception:
            raise ValueError(
                f"Error while running get xrp transactions, {str(exception)}"
            )

    def get_payment_transactions(self, address:str, limit: int=0):
        try:
            return self.wallet.payment_transactions(address, limit)
        except Exception as exception:
            raise ValueError(
                f"Error while running get payment transactions, {str(exception)}"
            )

    def get_tokens(self, address: str):
        try:
            return self.wallet.account_tokens(address)
        except Exception as exception:
            raise ValueError(
                f"Error while running get tokens, {str(exception)}"
            )
    
    def get_nfts(self, address: str, limit: int=0):
        try:
            return self.wallet.account_nfts(address, limit)
        except Exception as exception:
            raise ValueError(
                f"Error while running get nfts, {str(exception)}"
            )

    def get_root_flags(self, address: str):
        try:
            return self.wallet.account_root_flags(address)
        except Exception as exception:
            raise ValueError(f"Error while running get root flags, {str(exception)}")
    
    # senders
    def send_xrp(
        self, sender_addr: str, receiver_addr: str,
        amount: Union[float, Decimal, int],
        destination_tag: int = 0,
        source_tag: int = 0, fee: str = ""):
        try:
            # Todo: replace source_tag with Nemo
            return self.wallet.send_xrp(
                sender_addr, receiver_addr, amount,
                destination_tag, source_tag, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running send xrp, {str(exception)}")
    
    def send_token(
        self, sender_addr: str, receiver_addr: str, token: str,
        amount: str, issuer: str, is_lp_token: bool = False,
        destination_tag: int = 0, source_tag: int = 0, fee: str = ""
        ) -> dict:
        try:
            # Todo: replace destination_tag with Nemo 
            return self.wallet.send_token(
                sender_addr, receiver_addr,
                token, amount,
                issuer, is_lp_token,
                destination_tag, source_tag, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running send token, {str(exception)}")
    
    def send_nft(
            self, sender_addr: str,
            nftoken_id: str, receiver: str, fee: str = ""
        ):
        try:
            memo = ""
            return self.wallet.send_nft(
                sender_addr, nftoken_id,
                receiver, memo, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running send nft, {str(exception)}")
    
    def receive_nft(self, sender_addr: str, nft_sell_id: str, fee: str):
        try:
            return self.receive_nft(sender_addr, nft_sell_id, fee)
        except Exception as exception:
            raise ValueError(f"Error while running receive nft, {str(exception)}")


class XRPAssetClient():
    asset = xAsset(test_url, test_account, test_txns)

    # switchers
    def switch_to_main_net(self):
        return self.asset.toMainnet()

    def switch_to_test_net(self):
        return self.asset.toTestnet()
    
    def create_token(self, issuer_addr: str, manager_addr: str, token_name: str, total_supply: str, fee: str):
        try:
            self.asset.accountset_issuer(issuer_addr, tick_size, transferfee, domain, fee)
        except Exception as exception:
            raise ValueError(f"Error while running accountset issuer, {str(exception)}")
        
        try:
            self.asset.accountset_manager(manager_addr, fee)
        except Exception as exception:
            raise ValueError(f"Error while running accountset manager, {str(exception)}")
        
        try:
            self.asset.create_trustline(issuer_addr, manager_addr, token_name, total_supply, fee)
        except Exception as exception:
            raise ValueError(f"Error while running create trustline, {str(exception)}")

        try:
            return self.asset.create_token(issuer_addr, manager_addr, token_name, total_supply, fee)
        except Exception as exception:
            raise ValueError(f"Error while running create token, {str(exception)}")

    def burn_token(self, sender_addr: str, token: str, issuer: str, amount: float, fee: str = None):
        try:
            return self.asset.burn_token(sender_addr, token, issuer, amount, fee)
        except Exception as exception:
            raise ValueError(f"Error while running burn token, {str(exception)}")
    
    def mint_nft(self, issuer_addr: str, taxon: int, is_transferable: bool, only_xrp: bool, issuer_burn: bool, transfer_fee: float = None, uri: str = None, fee: str = None):
        try:
            return self.asset.mint_nft(issuer_addr, taxon, is_transferable, only_xrp, issuer_burn, transfer_fee, uri, fee)
        except Exception as exception:
            raise ValueError(f"Error while running mint nft, {str(exception)}")
    
    def burn_nft(self, sender_addr: str, nftoken_id: str, holder: str = None, fee: str = None):
        try:
            return self.asset.burn_nft(sender_addr, nftoken_id, holder, fee)
        except Exception as exception:
            raise ValueError(f"Error while running burn nft, {str(exception)}")


class XRPObjectClient():
    x_object = xObject(test_url, test_account, test_txns)

    def create_xrp_check(
            self, sender_addr: str, receiver_addr: str,
            amount: Union[int, float, Decimal],
            expiry_date: int = None, fee: str = None
        
        ) -> dict:
        try:
            return self.x_object.create_xrp_check(sender_addr, receiver_addr, amount, expiry_date, fee)
        except Exception as exception:
            raise ValueError(f"Error while running create xrp check, {str(exception)}")
        
    def account_checks(self, wallet_addr: str, limit: int = None) -> dict:
        try:
            return self.x_object.account_checks(wallet_addr, limit)
        except Exception as exception:
            raise ValueError(f"Error while running account checks, {str(exception)}")
    
    def cash_xrp_check(
            self, sender_addr: str, check_id: str, amount: int | Decimal | float, fee: str
        ) -> dict:
        try:
            return self.x_object.cash_xrp_check(sender_addr, check_id, amount, fee)
        except Exception as exception:
            raise ValueError(f"Error while running cash xrp check, {str(exception)}")
    
    def cancel_check(self, sender_addr: str, check_id: str, fee: str):
        try:
            return self.x_object.cancel_check(sender_addr, check_id, fee)
        except Exception as exception:
            raise ValueError(f"Error while running cancel check, {str(exception)}")

    def create_token_check(
            self, sender_addr: str, receiver_addr: str,
            token: str, amount: str, issuer: str, expiry_date, fee
        ) -> dict:
        try:
            return self.x_object.create_token_check(
                sender_addr, receiver_addr, token, amount, issuer, expiry_date, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running create token check, {str(exception)}")

    def cash_token_check(
            self, sender_addr: str, check_id: str, token: str,
            amount: str, issuer: str, fee: str
        ) -> dict:
        try:
            return self.x_object.cash_token_check(
                sender_addr, check_id, token, amount,
                issuer, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running cash token check, {str(exception)}")

    def create_xrp_escrow(
            self, sender_addr: str, amount: int | Decimal | float, receiver_addr: str,
            condition: str, claim_date: str, expiry_date: str, fee: str
        ) -> dict:
        try:
            return self.x_object.create_xrp_escrow(
                sender_addr, amount, receiver_addr,
                condition, claim_date, expiry_date, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running create xrp escrow, {str(exception)}")

    def schedule_xrp(
            self, sender_addr: str, amount: int| Decimal| float,
            receiver_addr: str, claim_date: int, expiry_date: int, fee: str
        ) -> dict:
        try:
            return self.x_object.schedule_xrp(
                sender_addr, amount, receiver_addr, claim_date, expiry_date, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running schedule xrp, {str(exception)}")
    
    def account_xrp_escrows(
            self, wallet_addr: str, limit: int
        ) -> dict:
        try:
            return self.x_object.account_xrp_escrows(
                wallet_addr, limit
            )
        except Exception as exception:
            raise ValueError(f"Error while running account xrp escrows, {str(exception)}")
    
    def r_seq_dict(
            self, prev_txn_id: str
        ) -> dict:
        try:
            return self.x_object.r_seq_dict(prev_txn_id)
        except Exception as exception:
            raise ValueError(f"Error while running r_seq_dict, {str(exception)}")
    
    def r_sequence(
            self, prev_txn_id: str
        ) -> int:
        try:
            return self.x_object.r_sequence(prev_txn_id)
        except Exception as exception:
            raise ValueError(f"Error while running r_sequence , {str(exception)}")
    
    def cancel_xrp_escrow(
            self, sender_addr: str, escrow_creator: str,
            prev_txn_id: str, fee: str
        ) -> dict:
        try:
            return self.x_object.cancel_xrp_escrow(sender_addr, escrow_creator, prev_txn_id, fee)
        except Exception as exception:
            raise ValueError(f"Error while running cancel xrp escrow, {str(exception)}")
    
    def finish_xrp_escrow(
            self, sender_addr: str, escrow_creator: str,
            prev_txn_id: str, condition: str, fulfillment: str, fee: str
        ) -> dict:
        try:
            return self.x_object.finish_xrp_escrow(
                sender_addr, escrow_creator,
                prev_txn_id, condition, fulfillment, fee
            )
        except Exception as exception:
            raise ValueError(f"Error while running finish xrp escrow, {str(exception)}")
    
    def create_offer(
            self, sender_addr: str, pay: float,
            receive: float, expiry_date: int, fee: str,
            pay_type: str, receive_type: str,  receive_issuer: str = None,
            pay_issuer: str = None
        ) -> dict:
        try:
            if pay_type == "xrp" and receive_type != "xrp":
                receive = IssuedCurrencyAmount(currency=receive_type, issuer=receive_issuer, value=receive)
                return self.x_object.create_offer(sender_addr, pay, receive, expiry_date, fee)
            if pay_type != "xrp" and receive_type == "xrp":
                pay = IssuedCurrencyAmount(currency=pay_type, issuer=pay_issuer, value=pay)
                return self.x_object.create_offer(sender_addr, pay, receive, expiry_date, fee)
            elif pay_type != "xrp" and receive_type != "xrp":
                pay = IssuedCurrencyAmount(currency=pay_type, issuer=pay_issuer, value=pay)
                receive = IssuedCurrencyAmount(currency=receive_type, issuer=receive_issuer, value=receive)
                return self.x_object.create_offer(sender_addr, pay, receive, expiry_date, fee)
            else:
                raise ValueError("Invalid combination of buy and sell")
            
        except Exception as exception:
            raise ValueError(f"Error while running create offer, {str(exception)}")
    
    def account_offers(
            self, wallet_addr: str, limit: int
        ) -> list:
        try:
            return self.x_object.account_offers(wallet_addr, limit)
        except Exception as exception:
            raise ValueError(f"Error while running account offers, {str(exception)}")
    
    def cancel_offer(
            self, sender_addr: str, offer_seq: int, fee: str
        ) -> dict:
        try:
            return self.x_object.cancel_offer(sender_addr, offer_seq, fee)
        except Exception as exception:
            raise ValueError(f"Error while running cancel offer, {str(exception)}")
    
    def all_offers(
            self, pay: float, receive: float, limit: int
        ) -> list:
        try:
            return self.x_object.all_offers(pay, receive, limit)
        except Exception as exception:
            raise ValueError(f"Error while running all offers, {str(exception)}")


class XRPNFTClient():
    x_nft = xNFT(test_url, test_txns, test_account)

    def toTestnet(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running toTestnet, {str(exception)}")

    def toMainnet(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")

    def create_sell_offer(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")

    def create_buy_offer(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")

    def cancel_offer(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def accept_nft_offer(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def account_nft_offers(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def all_nft_offers(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")


class XRPInfoClient():
    x_info = xInfo(test_url, test_account, test_txns)

    def toTestnet(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def toMainnet(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_account_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_offer_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_xrp_escrow_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_check_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_token_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_nft_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_nft_metadata(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def get_nft_offer_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")
    
    def pay_txn_info(self):
        try:
            pass
        except Exception as exception:
            raise ValueError(f"Error while running to, {str(exception)}")


class XRPOrderBookExchangeClient():
    def __init__(self, network_url, account_url, txn_url):
        self.network_url = network_url
        self.account_url = account_url
        self.txn_url = txn_url
        self.x_exchange = xOrderBookExchange(self.network_url, self.account_url, self.txn_url)

    def toTestnet(self):
        try:
            return self.x_exchange.toTestnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def toMainnet(self):
        try:
            return self.x_exchange.toMainnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def sort_best_offer(
            self, buy_type: str, sell_type: str, best_buy: bool = False,
            best_sell: bool = False, limit: int = None, buy_issuer: str = None,
            sell_issuer: str = None) -> dict:
        try:
            if buy_type == "xrp" and sell_type == "xrp":
                return self.x_exchange.sort_best_offer(buy=XRP, sell=XRP, best_buy=best_buy, best_sell=best_sell, limit=limit)
            elif buy_type == "xrp" and sell_type != "xrp":
                return self.x_exchange.sort_best_offer(buy=XRP, sell=IssuedCurrency(currency=sell_type, issuer=sell_issuer), best_buy=best_buy, best_sell=best_sell, limit=limit)
            if buy_type != "xrp" and sell_type == "xrp":
                return self.x_exchange.sort_best_offer(buy=IssuedCurrency(currency=buy_type, issuer=buy_issuer), sell=XRP, best_buy=best_buy, best_sell=best_sell, limit=limit)
            elif buy_type != "xrp" and sell_type != "xrp":
                return self.x_exchange.sort_best_offer(buy=IssuedCurrency(currency=buy_type, issuer=buy_issuer), sell=IssuedCurrency(currency=sell_type, issuer=sell_issuer), best_buy=best_buy, best_sell=best_sell, limit=limit)
            else:
                raise ValueError("Invalid combination of buy and sell")
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def create_order_book_liquidity(self, sender_addr: str, buy_type: str, sell_type: str, buy_amount: float, sell_amount: float, expiry_date: int = None, fee: str = None, buy_issuer: str = None, sell_issuer: str = None):
        try:
            if buy_type == "xrp" and sell_type == "xrp":
                return self.x_exchange.create_order_book_liquidity(sender_addr, buy_amount, sell_amount, expiry_date, fee)
            elif buy_type == "xrp" and sell_type != "xrp":
                return self.x_exchange.create_order_book_liquidity(
                    sender_addr, buy_amount,
                    IssuedCurrencyAmount(sell_type, sell_issuer, sell_amount),
                    expiry_date, fee
                )
            elif buy_type != "xrp" and sell_type == "xrp":
                return self.x_exchange.create_order_book_liquidity(
                    sender_addr, IssuedCurrencyAmount(buy_type, buy_issuer, buy_amount),
                    sell_amount, expiry_date, fee
                )
            elif buy_type != "xrp" and sell_type != "xrp":
                return self.x_exchange.create_order_book_liquidity(
                    sender_addr, IssuedCurrencyAmount(buy_type, buy_issuer, buy_amount),
                    IssuedCurrencyAmount(sell_type, sell_issuer, sell_amount),
                    expiry_date, fee
                )
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def get_account_order_book_liquidity(self, wallet_addr: str, limit: int =None):
        try:
            return self.x_exchange.get_account_order_book_liquidity(wallet_addr, limit)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def order_book_swap(self, sender_addr: str, buy_amount, sell_amount, buy_type, sell_type, buy_issuer: str = None, sell_issuer: str = None, swap_all: bool = False, fee: str = None) -> dict:
        """create an offer that either matches with existing offers to get entire sell amount or cancels\n
        if swap_all is enabled, this will force exchange all the paying units regardless of profit or loss\n

        if tecKILLED is the result, exchange didnt go through because all of the `buy` couldnt be obtained. recommend enabling swap_all
        """
        try:
            if buy_type == "xrp" and sell_type == "xrp":
                return self.x_exchange.order_book_swap(sender_addr, buy_amount, sell_amount, swap_all, fee)
            elif buy_type != "xrp" and sell_type == "xrp":
                return self.x_exchange.order_book_swap(
                    sender_addr, IssuedCurrencyAmount(buy_type, buy_issuer, buy_amount),
                    sell_amount, fee, buy_issuer, sell_issuer
                )
            elif buy_type != "xrp" and sell_type == "xrp":
                return self.x_exchange.order_book_swap(
                    sender_addr, buy_amount, IssuedCurrencyAmount(sell_type, sell_issuer, buy_amount),
                    swap_all, fee
                )
            elif buy_type != "xrp" and sell_type != "xrp":
                return self.x_exchange.order_book_swap(
                    sender_addr, IssuedCurrencyAmount(buy_type, buy_issuer, buy_amount),
                    IssuedCurrencyAmount(sell_type, sell_issuer, sell_amount), swap_all,
                    fee
                )
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")


class XRPAmmExchange():
    def __init__(self, network_url, account_url, txn_url):
        self.network_url = network_url
        self.account_url = account_url
        self.txn_url = txn_url
        self.x_amm_exchange = xAmm(self.network_url, self.account_url, self.txn_url)

    def toTestnet(self):
        try:
            return self.x_amm_exchange.toTestnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def toMainnet(self):
        try:
            return self.x_amm_exchange.toMainnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def create_amm_liquidity(
            self, sender_addr: str, token_1: Union[float, IssuedCurrencyAmount],
            token_2: Union[float, IssuedCurrencyAmount], trading_fee: float,
            token_1_type, token_2_type, token_1_issuer: str = None, token_2_issuer: str = None, fee: str = None
        ):
        try:
            if token_1_type == "xrp" and token_2_type == "xrp":
                return self.x_amm_exchange.create_amm(sender_addr, token_1, token_2, trading_fee, fee)
            elif token_1_type == "xrp" and token_2_type != "xrp":
                return self.x_amm_exchange.create_amm(
                    sender_addr, token_1, IssuedCurrencyAmount(token_2_type, token_2_issuer, token_2),
                    trading_fee, fee 
                )
            elif token_1_type != "xrp" and token_2_type == "xrp":
                return self.x_amm_exchange.create_amm(
                    sender_addr, IssuedCurrencyAmount(token_1_type, token_1_issuer, token_1),
                    token_2, trading_fee, fee
                )
            elif token_1_type != "xrp" and token_2_type != "xrp":
                return self.x_amm_exchange.create_amm(
                    sender_addr, IssuedCurrencyAmount(token_1_type, token_1_issuer, token_1),
                    IssuedCurrencyAmount(token_2_type, token_2_issuer, token_2)
                )
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def amm_vote(
            self, sender_addr: str, token_1: Union[XRP, IssuedCurrency], token_2: Union[XRP, IssuedCurrency],
            trading_fee: float, token_1_issuer = None, token_2_issuer = None, fee: str = None
        ) -> dict:
        """cast a vote to modify AMM fee"""
        try:
            if token_1 == "xrp" and token_2 == "xrp":
                return self.x_amm_exchange.amm_vote(sender_addr, token_1, token_2, trading_fee, fee)
            elif token_2 == "xrp" and token_2 != "xrp":
                return self.x_amm_exchange.amm_vote(
                    sender_addr, token_1, IssuedCurrency(token_2, token_2_issuer), trading_fee,
                    fee
                )
            elif token_2 != "xrp" and token_2 == "xrp":
                return self.x_amm_exchange.amm_vote(
                    sender_addr, IssuedCurrency(token_1, token_1_issuer),
                    token_2, trading_fee, fee
                )
            elif token_2 != "xrp" and token_2 != "xrp":
                return self.x_amm_exchange.amm_vote(
                    sender_addr, IssuedCurrency(token_1, token_1_issuer),
                    IssuedCurrency(token_2, token_2_issuer), trading_fee,
                    fee
                )
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def amm_bid(self, sender_addr: str, token_1: Union[XRP, IssuedCurrency], token_2: Union[XRP, IssuedCurrency],
        auth_accounts: list[AuthAccount] = None, bid_max: IssuedCurrencyAmount= None, bid_min: IssuedCurrencyAmount = None, fee: str = None):
        """token 1 and 2 are the amm tokens, bid max and bid min are the Lp's token"""
        try:
            return self.x_amm_exchange.amm_bid(sender_addr, token_1, token_2, auth_accounts, bid_max, bid_min, fee)
        except Exception as exception:
            raise ValueError(f"Error runnin AMM Bid: {exception}")

class XRPEngClient():
    def __init__(self, network_url, account_url, txn_url):
        self.network_url = network_url
        self.account_url = account_url
        self.txn_url = txn_url
        self.xengine = xEng(self.network_url, self.account_url, self.txn_url)

    def toTestnet(self):
        try:
            self.xengine.toTestnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def toMainnet(self):
        try:
            self.xengine.toMainnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def created_tokens_issuer(self, wallet_addr: str):
        try:
            return self.xengine.created_tokens_issuer(wallet_addr)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def created_tokens_manager(self, wallet_addr: str):
        try:
            return self.xengine.created_tokens_manager(wallet_addr)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def created_nfts(self, wallet_addr: str, mainnet: bool):
        try:
            return self.xengine.created_nfts(wallet_addr, mainnet)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def created_taxons(self, wallet_addr: str):
        try:
            return self.xengine.created_taxons(wallet_addr)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def created_nfts_taxon(self, wallet_addr: str, taxon: int):
        try:
            return self.xengine.created_nfts_taxon(wallet_addr, taxon)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def add_token(self, sender_addr: str, token: str, issuer: str, rippling: bool, is_lp_token: bool, fee: str) -> dict:
        try:
            return self.xengine.add_token(
                sender_addr, token, issuer,
                rippling, is_lp_token, fee
            )
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def remove_token(self, sender_addr: str, token: str, issuer: str, fee: str = None) -> dict:
        try:
            return self.xengine.remove_token(sender_addr, token, issuer, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_token_freeze_state(self, sender_addr: str, target_addr: str, token_name: str, freeze: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.modify_token_freeze_state(sender_addr, target_addr, token_name, freeze, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def delete_account(self, sender_addr: str, receiver_addr: str, fee: str) -> dict:
        try:
            return self.xengine.delete_account(sender_addr, receiver_addr, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_domain(self, sender_addr: str, domain: str, fee: str) -> dict:
        try:
            return self.xengine.modify_domain(sender_addr, domain, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_token_transfer_fee(self, sender_addr, transfer_fee, fee):
        try:
            return self.xengine.modify_token_transfer_fee(sender_addr, transfer_fee, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_ticksize(self, sender_addr: str, tick_size: int, fee: str = None):
        try:
            return self.xengine.modify_ticksize(sender_addr, tick_size, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_email(self, sender_addr: str, email: str, fee: str = None) -> dict:
        try:
            return self.modify_email(sender_addr, email, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfAccountTxnId(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Track the ID of this account's most recent transaction."""
        try:
            return self.xengine.asfAccountTxnId(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDefaultRipple(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Enable or disable rippling"""
        try:
            return self.xengine.asfDefaultRipple(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDepositAuth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """ Deposit Authorization blocks all transfers from strangers, including transfers of XRP and tokens."""
        try:
            return self.xengine.asfDepositAuth(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisableMaster(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Enable or disable the use of the master key pair"""
        try:
            return self.xengine.asfDisableMaster(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisallowXRP(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.asfDisallowXRP(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfGlobalFreeze(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.asfGlobalFreeze(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfNoFreeze(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.asfNoFreeze(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfRequireAuth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.asfRequireAuth(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfRequireDest(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Configure an account to require a destination tag when receiving transactions"""
        try:
            return self.xengine.asfRequireDest(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfAuthorizedNFTokenMinter(self, sender_addr: str, minter: str, state: bool = False, fee: str = None) -> dict:
        """Allow another account to mint and burn tokens on behalf of this account"""
        try:
            return self.xengine.asfAuthorizedNFTokenMinter(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisallowIncomingNFTokenOffer(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating NFTokenOffers directed at this account."""
        try:
            return self.xengine.asfDisallowIncomingNFTokenOffer(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisallowIncomingCheck(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating Checks directed at this account."""
        try:
            return self.xengine.asfDisallowIncomingCheck(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisallowIncomingPayChan(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating PayChannels directed at this account."""
        try:
            return self.xengine.asfDisallowIncomingPayChan(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def asfDisallowIncomingTrustline(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        try:
            return self.xengine.asfDisallowIncomingTrustline(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_account_rippling(self, sender_addr: str, state: bool, fee: str = None):
        try:
            return self.xengine.modify_account_rippling(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_deposit_auth(self, sender_addr: str, state: bool, fee: str = None):
        try:
            return self.xengine.modify_deposit_auth(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_req_auth(self, sender_addr: str, state: bool, fee: str = None):
        try:
            return self.xengine.modify_req_auth(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def modify_require_dest_tag(
            self, sender_addr: str, state: bool, fee: str = None
        ) -> dict:
        try:
            return self.xengine.modify_req_auth(sender_addr, state, fee)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def sign_and_submit(self, txn, wallet, client):
        try:
            return self.xengine.sign_and_submit(txn, wallet, client)
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")
 

class XammFinance():
    def __init__(self, network_url, account_url, txn_url):
        self.network_url = network_url
        self.account_url = account_url
        self.txn_url = txn_url
        self.xAmm = XammObject(self.network_url, self.account_url, self.txn_url)

    def toTestnet(self):
        try:
            self.xAmm.toTestnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")

    def toMainnet(self):
        try:
            self.xAmm.toMainnet()
        except Exception as exception:
            raise ValueError(f"Error running, {exception}")
    
    def cancel_offer(self, sender_addr: str, offer_seq: int, fee: str = "") -> dict:
        """cancel an offer"""
        try:
            return self.xAmm.cancel_offer(sender_addr, offer_seq, fee)
        except Exception as exception:
            raise ValueError(f"Error running cancel offer, {exception}")

    def create_order_book_liquidity(
            self, sender_addr: str, buy: float, sell: float,
            expiry_date: int = 0, fee: str = "", buy_type="xrp",
            sell_type="xrp", buy_issuer: str = "", sell_issuer: str = ""
        ) -> dict:
        """create an offer as passive;
        it doesn't immediately consume offers that match it,
        just stays on the ledger as an object for liquidity"""
        try:
            if buy_type == "xrp" and sell_type == "xrp":
                return self.xAmm.create_order_book_liquidity(
                    sender_addr, buy, sell, expiry_date, fee
                )
            elif buy_type == "xrp" and sell_type != "xrp":
                return self.xAmm.create_order_book_liquidity(
                    sender_addr, buy,
                    IssuedCurrencyAmount(currency=sell_type, issuer=sell_issuer, value=sell), expiry_date,
                    fee
                )
            elif buy_type != "xrp" and sell_type == "xrp":
                return self.xAmm.create_order_book_liquidity(
                    sender_addr, IssuedCurrencyAmount(currency=buy_type, issuer=buy_issuer, value=buy),
                    sell, expiry_date, fee
                )
            elif buy_type != "xrp" and sell_type != "xrp":
                return self.xAmm.create_order_book_liquidity(
                    sender_addr, IssuedCurrencyAmount(buy_type, buy_issuer, buy),
                    IssuedCurrencyAmount(currency=sell_type, issuer=sell_issuer, value=sell), expiry_date,
                    fee
                )
        except Exception as exception:
            raise ValueError(f"Error running create order book liquidity, {exception}")

    def get_account_order_book_liquidity(
            self, wallet_addr: str, limit: int = 0
        ) -> list:
        """return all offers that are liquidity an account created"""
        try:
            return self.xAmm.get_account_order_book_liquidity(wallet_addr, limit)
        except Exception as exception:
            raise ValueError(
                f"Error running get account order book liquidity, {exception}"
            )


    def order_book_swap(
            self, sender_addr: str, buy: Union[float, IssuedCurrencyAmount],
            sell: Union[float, IssuedCurrencyAmount],
            tf_sell: bool = False, tf_fill_or_kill: bool = False,
        tf_immediate_or_cancel: bool = False, fee: str = "", buy_issuer: str = "",
        sell_issuer: str = "", buy_type: str = "", sell_type: str = ""
        ) -> dict:
        try:
            if buy_type == "xrp" and sell_type == "xrp":
                return self.xAmm.order_book_swap(
                    sender_addr, buy, sell, tf_sell, tf_fill_or_kill,
                    tf_immediate_or_cancel, fee
                )
            elif buy_type == "xrp" and sell_type != "xrp":
                return self.xAmm.order_book_swap(
                    sender_addr, buy,
                    IssuedCurrencyAmount(currency=sell_type, issuer=sell_issuer, value=sell),
                    tf_sell, tf_fill_or_kill,
                    tf_immediate_or_cancel, fee
                )
            elif buy_type != "xrp" and sell_type == "xrp":
                return self.xAmm.order_book_swap(
                    sender_addr, IssuedCurrencyAmount(currency=buy_type, issuer=buy_issuer, value=buy),
                    sell, tf_sell, tf_fill_or_kill, tf_immediate_or_cancel, fee
                )
            elif buy_type != "xrp" and sell_type != "xrp":
                return self.xAmm.order_book_swap(
                    sender_addr, IssuedCurrencyAmount(currency=buy_type, issuer=buy_issuer, value=buy),
                    IssuedCurrencyAmount(currency=sell_type, issuer=sell_issuer, value=sell), tf_sell, tf_fill_or_kill,
                    tf_immediate_or_cancel, fee
                )
        except Exception as exception:
            raise ValueError(f"Error running create order book liquidity, {exception}")

    def sort_best_offer(
            self, buy: str,
            sell: str, best_buy: bool = False,
            best_sell: bool = False, limit: int = 0,
            buy_issuer = None, sell_issuer = None) -> Dict:
        """
        return all available orders and best {option} first,
        choose either best_buy or best_sell
        """
        try:
            if buy == "xrp" and sell == "xrp":
                return self.xAmm.sort_best_offer(XRP, XRP, best_buy, best_sell, limit)
            elif buy == "xrp" and sell != "xrp":
                return self.xAmm.sort_best_offer(
                    XRP(), IssuedCurrency(currency=sell, issuer=sell_issuer), best_buy,
                    best_sell, limit
                )
            elif buy != "xrp" and sell == "xrp":
                return self.xAmm.sort_best_offer(
                    IssuedCurrency(currency=buy, issuer=buy_issuer),
                    XRP(), best_buy, best_sell, limit
                )
            elif buy != "xrp" and sell != "xrp":
                return self.xAmm.sort_best_offer(
                    IssuedCurrency(currency=buy, issuer=buy_issuer),
                    IssuedCurrency(currency=sell, issuer=sell_issuer), best_buy,
                    best_sell, limit
                )
        except Exception as exception:
            raise ValueError(f"Error running sort best offer, {exception}")
    
    def token_balance(self, wallet_addr: str, name: str, issuer_addr: str) -> List:
        try:
            return self.xAmm.token_balance(wallet_addr, name, issuer_addr)
        except Exception as exception:
            raise ValueError(f"Error running token balance, {exception}")

    def status(self, txid: str, mainnet: bool = True) -> dict:
        return self.xAmm.status(txid, mainnet)
    
    def token_exists(self, token: str, issuer: str) -> dict:
        return self.xAmm.token_exists(token, issuer)
