import requests
from xrpl.clients import JsonRpcClient
from xrpl.models import (AccountDelete, AccountInfo, AccountSet,
                         AccountSetFlag, GatewayBalances, IssuedCurrencyAmount,
                         TrustSet, TrustSetFlag, Transaction)
from xrpl.transaction import (safe_sign_and_autofill_transaction,
                              send_reliable_submission)
from xrpl.wallet import Wallet

from Misc import (mm, transfer_fee_to_xrp_format, validate_hex_to_symbol,
                  validate_symbol_to_hex, xrp_format_to_nft_fee, amm_fee_to_xrp_format)
from x_constants import M_SOURCE_TAG


class xEng(JsonRpcClient):
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

    def created_tokens_issuer(self, wallet_addr: str) -> list:
        """returns all tokens an account has created as the issuer"""
        created_assets = []
        req = GatewayBalances(account=wallet_addr, ledger_index="validated")
        response = self.client.request(req)
        result = response.result
        if 'obligations' in result:
            obligations = result["obligations"]
            for key, value in obligations.items():
                asset = {}
                asset["token"] = validate_hex_to_symbol(key)
                asset["amount"] = value
                asset["issuer"] = wallet_addr
                asset["domain"] = ""
                acc_info = AccountInfo(account=wallet_addr, ledger_index="validated")
                account_data = self.client.request(acc_info).result["account_data"]
                if "Domain" in account_data:
                    asset["domain"] = validate_hex_to_symbol(
                        account_data["Domain"])
                created_assets.append(asset)
        return created_assets

    def created_tokens_manager(self, wallet_addr: str) -> list:
        """returns all tokens an account thas created as the manager"""
        created_assets = []
        req = GatewayBalances(account=wallet_addr, ledger_index="validated")
        response = self.client.request(req)
        result = response.result
        if 'assets' in result:
            assets = result["assets"]
            for issuer, issuings in assets.items():
                for iss_cur in issuings:
                    asset = {}
                    asset["issuer"] = issuer
                    asset["token"] = validate_hex_to_symbol(iss_cur["currency"])
                    asset["amount"] = iss_cur["value"]
                    asset["manager"] = wallet_addr
                    asset["domain"] = ""
                    acc_info = AccountInfo(account=asset["cold_address"], ledger_index="validated")
                    account_data = self.client.request(acc_info).result["account_data"]
                    if "Domain" in account_data:
                        asset["domain"] = validate_hex_to_symbol(account_data["Domain"])
                    created_assets.append(asset)
        return created_assets

    def created_nfts(self, wallet_addr: str, mainnet: bool = True) -> list:
        """return all nfts an account created as an issuer \n this method uses an external api"""
        created_nfts = []
        result = requests.get(f"https://api.xrpldata.com/api/v1/xls20-nfts/issuer/{wallet_addr}").json() if mainnet else requests.get(f"https://test-api.xrpldata.com/api/v1/xls20-nfts/issuer/{wallet_addr}").json()
        if "data" in result and "nfts" in result["data"]:
            nfts = result["data"]["nfts"]
            for nft in nfts:
                nft_data = {}
                nft_data["nftoken_id"] = nft["NFTokenID"]
                nft_data["issuer"] = nft["Issuer"]
                nft_data["owner"] = nft["Owner"]
                nft_data["taxon"] = nft["Taxon"]
                nft_data["sequence"] = nft["Sequence"]
                nft_data["transfer_fee"] = xrp_format_to_nft_fee(nft["TransferFee"])
                nft_data["flags"] = nft["Flags"]
                nft_data["uri"] = validate_hex_to_symbol(nft["URI"])
                created_nfts.append(nft_data)
        return created_nfts

    def created_taxons(self, wallet_addr: str) -> list:
        """return all taxons an account has used to create nfts"""
        taxons = []
        result = requests.get(
            f"https://api.xrpldata.com/api/v1/xls20-nfts/taxon/{wallet_addr}").json()
        if "data" in result and "taxons" in result["data"]:
            taxons = result["data"]["taxons"]
        return taxons

    def created_nfts_taxon(self, wallet_addr: str, taxon: int):
        """return all nfts with similar taxon an account has created"""
        created_nfts = []
        result = requests.get(
            f"https://api.xrpldata.com/api/v1/xls20-nfts/issuer/{wallet_addr}/taxon/{taxon}").json()
        if "data" in result and "nfts" in result["data"]:
            nfts = result["data"]["nfts"]
            for nft in nfts:
                nft_data = {}
                nft_data["nftoken_id"] = nft["NFTokenID"]
                nft_data["issuer"] = nft["Issuer"]
                nft_data["owner"] = nft["Owner"]
                nft_data["taxon"] = nft["Taxon"]
                nft_data["sequence"] = nft["Sequence"]
                nft_data["transfer_fee"] = xrp_format_to_nft_fee(
                    nft["TransferFee"])
                # nft_data["flags"] = nft["Flags"]
                nft_data["uri"] = validate_hex_to_symbol(nft["URI"])
                created_nfts.append(nft_data)
        return created_nfts

    def add_token(self, sender_addr: str, token: str, issuer: str, rippling: bool = False, is_lp_token: bool = False, fee: str = None) -> dict:
        """enable transacting with a token"""
        flag = TrustSetFlag.TF_SET_NO_RIPPLE
        cur = token if is_lp_token else validate_symbol_to_hex(token)
        if rippling:
            flag = TrustSetFlag.TF_CLEAR_NO_RIPPLE
        cur = IssuedCurrencyAmount(
            currency=cur, issuer=issuer, value=1_000_000_000)
        txn = TrustSet(account=sender_addr, limit_amount=cur, flags=flag, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    # can only be called if user empties balance
    def remove_token(self, sender_addr: str, token: str, issuer: str, fee: str = None) -> dict:
        """disable transacting with a token"""
        trustset_cur = IssuedCurrencyAmount(
            currency=validate_symbol_to_hex(token), issuer=issuer, value=0)
        txn = TrustSet(account=sender_addr, limit_amount=trustset_cur, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def modify_token_freeze_state(self, sender_addr: str, target_addr: str, token_name: str, freeze: bool = False, fee: str = None) -> dict:
        """Freeze a token for an account, only the issuer can call this"""
        state = TrustSetFlag.TF_CLEAR_FREEZE
        if freeze:
            state = TrustSetFlag.TF_SET_FREEZE
        cur = IssuedCurrencyAmount(currency=validate_symbol_to_hex(token_name), issuer=target_addr, value=1_000_000_000)
        txn = TrustSet(account=sender_addr, limit_amount=cur, flags=state, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def delete_account(self, sender_addr: str, receiver_addr: str, fee: str = None) -> dict:
        """delete accounts on the ledger \n
        account must not own any ledger object, costs 2 xrp_chain fee, acc_seq + 256 > current_ledger_seq \n
        account can still be created after merge"""
        txn = AccountDelete(account=sender_addr, destination=receiver_addr, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def modify_domain(self, sender_addr: str, domain: str, fee: str = None) -> dict:
        """modify the domain of an account"""
        txn = AccountSet(account=sender_addr, domain=validate_symbol_to_hex(domain), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def modify_token_transfer_fee(self, sender_addr: str, transfer_fee: float, fee: str = None):
        """modify the transfer fee of a token | account"""
        txn = AccountSet(account=sender_addr, transfer_rate=transfer_fee_to_xrp_format(transfer_fee), fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def modify_ticksize(self, sender_addr: str, tick_size: int, fee: str = None):
        """modify the ticksize of a token | account"""
        txn = AccountSet(account=sender_addr, tick_size=tick_size, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def modify_email(self, sender_addr: str, email: str, fee: str = None) -> dict:
        """modify the email of a token | account"""
        txn = AccountSet(account=sender_addr, email_hash=email, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfAccountTxnId(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Track the ID of this account's most recent transaction."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_ACCOUNT_TXN_ID, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_ACCOUNT_TXN_ID, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDefaultRipple(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Enable or disable rippling"""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDepositAuth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """ Deposit Authorization blocks all transfers from strangers, including transfers of XRP and tokens."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DEPOSIT_AUTH, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DEPOSIT_AUTH, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisableMaster(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Enable or disable the use of the master key pair"""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISABLE_MASTER, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISABLE_MASTER, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisallowXRP(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISALLOW_XRP, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISALLOW_XRP, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfGlobalFreeze(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_GLOBAL_FREEZE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_GLOBAL_FREEZE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfNoFreeze(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_NO_FREEZE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_NO_FREEZE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfRequireAuth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_REQUIRE_AUTH, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_REQUIRE_AUTH, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfRequireDest(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Configure an account to require a destination tag when receiving transactions"""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_REQUIRE_DEST, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_REQUIRE_DEST, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfAuthorizedNFTokenMinter(self, sender_addr: str, minter: str, state: bool = False, fee: str = None) -> dict:
        """Allow another account to mint and burn tokens on behalf of this account"""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER, fee=fee, nftoken_minter=minter, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisallowIncomingNFTokenOffer(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating NFTokenOffers directed at this account."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISABLE_INCOMING_NFTOKEN_OFFER, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISABLE_INCOMING_NFTOKEN_OFFER, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisallowIncomingCheck(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating Checks directed at this account."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISABLE_INCOMING_CHECK, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISABLE_INCOMING_CHECK, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisallowIncomingPayChan(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating PayChannels directed at this account."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISABLE_INCOMING_PAYCHAN, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISABLE_INCOMING_PAYCHAN, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()

    def asfDisallowIncomingTrustline(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Disallow other accounts from creating Trustlines directed at this account."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DISABLE_INCOMING_TRUSTLINE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DISABLE_INCOMING_TRUSTLINE, fee=fee, memos=mm(), source_tag=M_SOURCE_TAG)
        return txn.to_dict()


    def modify_account_rippling(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Enable or disable rippling"""
        txn = AccountSet(account=sender_addr,clear_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE, fee=fee, memos=mm())
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE, fee=fee, memos=mm())
        return txn.to_dict()


    def modify_deposit_auth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """ Deposit Authorization blocks all transfers from strangers, including transfers of XRP and tokens."""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_DEPOSIT_AUTH, fee=fee, memos=mm())
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_DEPOSIT_AUTH, fee=fee, memos=mm())
        return txn.to_dict()


    def modify_req_auth(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_REQUIRE_AUTH, fee=fee, memos=mm())
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_REQUIRE_AUTH, fee=fee, memos=mm())
        return txn.to_dict()


    def modify_require_dest_tag(self, sender_addr: str, state: bool = False, fee: str = None) -> dict:
        """Configure an account to require a destination tag when receiving transactions"""
        txn = AccountSet(account=sender_addr, clear_flag=AccountSetFlag.ASF_REQUIRE_DEST, fee=fee, memos=mm())
        if state:
            txn = AccountSet(account=sender_addr, set_flag=AccountSetFlag.ASF_REQUIRE_DEST, fee=fee, memos=mm())
        return txn.to_dict()


    def sign_and_submit(self, txn, wallet, client):
        stxn_payment = safe_sign_and_autofill_transaction(txn, wallet, client)
        stxn_response = send_reliable_submission(stxn_payment, client)
        stxn_result = stxn_response.result
        return {
            "result": stxn_result["meta"]["TransactionResult"],
            "txid": stxn_result["hash"],
        }


# client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
# client = JsonRpcClient("http://amm.devnet.rippletest.net:51234")
# eng = xEng(client.url, "", "")
# tw = Wallet("sEd7dtFEiBbjG8dr5TNyYWM1hwx7oNq", 0)

# print(eng.created_nfts("rKgR5LMCU1opzENpP7Qz7bRsQB4MKPpJb4"))

# txn = eng.add_token(
#     tw.classic_address,
#     "030ADB868027B0185A6577C34F857236E359E88D",
#     "rU9qUW2skB7Z71JKV7H7fVWc6AU1DXiWVm",
#     True,
# )


# print(sign_and_submit(Transaction.from_dict(txn), tw, client))
