XURLS_ = {
    "TESTNET_URL": "https://s.altnet.rippletest.net:51234",
    "MAINNET_URL": "https://xrplcluster.com",
    "TESTNET_TXNS": "https://testnet.xrpl.org/transactions/",
    "MAINNET_TXNS": "https://livenet.xrpl.org/transactions/",
    "MAINNET_ACCOUNT": "https://livenet.xrpl.org/accounts/",
    "TESTNET_ACCOUNT": "https://testnet.xrpl.org/accounts/",
}

"""
xrp max decimals is 6
0.000001
"""
M_SOURCE_TAG = 10011001
D_TYPE = "Done-with-Myrkle"
D_DATA = "https://myrkle.app"

ACCOUNT_ROOT_FLAGS = [
    {
        "flagname": "lsfDefaultRipple",
        "hex": 0x00800000,
        "decimal": 8388608,
        "asf": "asfDefaultRipple",
        "description": "Enable rippling on this addresses's trust lines by default. Required for issuing addresses; discouraged for others."
    },
    {
        "flagname": "lsfDepositAuth",
        "hex": 0x01000000,
        "decimal": 16777216,
        "asf": "asfDepositAuth",
        "description": "This account can only receive funds from transactions it sends, and from preauthorized accounts, It has DepositAuth enabled."
    },
    {
        "flagname": "lsfDisableMaster",
        "hex": 0x00100000,
        "decimal": 1048576,
        "asf": "asfDisableMaster",
        "description": "Disallows use of the master key to sign transactions for this account."
    },
    {
        "flagname": "lsfDisallowIncomingCheck",
        "hex": 0x08000000,
        "decimal": 134217728,
        "asf": "asfDisallowIncomingCheck",
        "description": ""
    },
    {
        "flagname": "lsfDisallowIncomingNFTokenOffer",
        "hex": 0x04000000,
        "decimal": 134217728,
        "asf": "asfDisallowIncomingNFTokenOffer",
        "description": ""
    },
    {
        "flagname": "lsfDisallowIncomingPayChan",
        "hex": 0x10000000,
        "decimal": 268435456,
        "asf": "asfDisallowIncomingPayChan",
        "description": ""
    },
    {
        "flagname": "lsfDisallowIncomingTrustline",
        "hex": 0x20000000,
        "decimal": 536870912,
        "asf": "asfDisallowIncomingTrustline",
        "description": ""
    },
    {
        "flagname": "lsfDisallowXRP",
        "hex": 0x00080000,
        "decimal": 524288,
        "asf": "asfDisallowXRP",
        "description": "Client applications should not send XRP to this account. Not enforced by rippled."
    },
    {
        "flagname": "lsfGlobalFreeze",
        "hex": 0x00400000,
        "decimal": 4194304,
        "asf": "asfGlobalFreeze",
        "description": "All assets issued by this address are frozen."
    },    
    {
        "flagname": "lsfNoFreeze",
        "hex": 0x00200000,
        "decimal": 2097152,
        "asf": "asfNoFreeze",
        "description": "This address cannot freeze trust lines connected to it. Once enabled, cannot be disabled."
    },
    {
        "flagname": "lsfPasswordSpent",
        "hex": 0x00010000,
        "decimal": 65536,
        "asf": "",
        "description": "The account has used its free SetRegularKey transaction."
    },
    {
        "flagname": "lsfRequireAuth",
        "hex": 0x00040000,
        "decimal": 262144,
        "asf": "asfRequireAuth",
        "description": "This account must individually approve other users for those users to hold this account's tokens."
    },
    {
        "flagname": "lsfRequireDestTag",
        "hex": 0x00020000,
        "decimal": 131072,
        "asf": "asfRequireDest",
        "description": "Requires incoming payments to specify a Destination Tag."
    }, 
    {
        "flagname": "lsfAMM",
        "hex": 0x02000000,
        "decimal": 33554432,
        "asf": "",
        "description": "This account is an Automated Market Maker instance.",
    },  
]

NFTOKEN_FLAGS = [
    {
        "flagname": "tfBurnable",
        "hex": 0x00000001,
        "decimal": 1,
        "description": "Allow the issuer (or an entity authorized by the issuer) to destroy the minted NFToken. (The NFToken's owner can always do so.)",
    },
    {
        "flagname": "tfOnlyXRP",
        "hex": 0x00000002,
        "decimal": 2,
        "description": "The minted NFToken can only be bought or sold for XRP. This can be desirable if the token has a transfer fee and the issuer does not want to receive fees in non-XRP currencies.",
    },
    {
        "flagname": "tfTransferable",
        "hex": 0x00000008,
        "decimal": 8,
        "description": "The minted NFToken can be transferred to others. If this flag is not enabled, the token can still be transferred from or to the issuer.",
    },
]

NFTOKEN_OFFER_FLAGS = [
    {
        "flagname": "tfSellNFToken",
        "hex": 0x00000001,
        "decimal": 1,
        "description": "If enabled, the offer is a sell offer. Otherwise, the offer is a buy offer.",
    },
]

OFFER_FLAGS = [
    {
        "flagname": "tfPassive",
        "hex": 0x00010000,
        "decimal": 65536,
        "description": "If enabled, the Offer does not consume Offers that exactly match it, and instead becomes an Offer object in the ledger. It still consumes Offers that cross it.",
    },
    {
        "flagname": "tfImmediateOrCancel",
        "hex": 0x00020000,
        "decimal": 131072,
        "description": "Treat the Offer as an Immediate or Cancel order . The Offer never creates an Offer object in the ledger: it only trades as much as it can by consuming existing Offers at the time the transaction is processed. If no Offers match, it executes 'successfully' without trading anything. In this case, the transaction still uses the result code tesSUCCESS.",
    },
    {
        "flagname": "tfFillOrKill",
        "hex": 0x00040000,
        "decimal": 131072,
        "description": "Treat the offer as a Fill or Kill order . The Offer never creates an Offer object in the ledger, and is canceled if it cannot be fully filled at the time of execution. By default, this means that the owner must receive the full TakerPays amount; if the tfSell flag is enabled, the owner must be able to spend the entire TakerGets amount instead.",
    },
    {
        "flagname": "tfSell",
        "hex": 0x00080000,
        "decimal": 524288,
        "description": "Exchange the entire TakerGets amount, even if it means obtaining more than the TakerPays amount in exchange.",
    },
]

PAYMENT_FLAGS = [
    {
        "flagname": "tfNoDirectRipple",
        "hex": 0x00010000,
        "decimal": 65536,
        "description": "Do not use the default path; only use paths included in the Paths field. This is intended to force the transaction to take arbitrage opportunities. Most clients do not need this.",
    },
    {
        "flagname": "tfPartialPayment",
        "hex": 0x00020000,
        "decimal": 131072,
        "description": "If the specified Amount cannot be sent without spending more than SendMax, reduce the received amount instead of failing outright. See Partial Payments for more details.",
    },
    {
        "flagname": "tfLimitQuality",
        "hex": 0x00040000,
        "decimal": 262144,
        "description": "Only take paths where all the conversions have an input:output ratio that is equal or better than the ratio of Amount:SendMax. See Limit Quality for details.",
    },
]

TOKEN_MARKET_INFO = {
    # sample response type for token_market_info
    "currency": "USD",
    "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
    "meta": {
        "token": {
            "description": "Bitstamp's USD is a fully backed U.S. Dollar IOU on the XRPL. It can be redeemed into real Dollars on bitstamp.net. For support, visit their website or Twitter @BitstampSupport",
            "icon": "https://static.xrplmeta.org/icons/USD.png",
            "name": "US Dollar",
            "trust_level": 3
        },
        "issuer": {
            "description": "World's longest running crypto exchange. Original since 2011. Support: @BitstampSupport, Telegram: http://bit.ly/3v9QYo9, Media Inquiries: press@bitstamp.net",
            "domain": "bitstamp.net",
            "followers": 494002,
            "icon": "https://static.xrplmeta.org/icons/bitstamp.png",
            "kyc": False,
            "name": "Bitstamp",
            "trust_level": 3,
            "weblinks": [
                {
                    "url": "https://bitstamp.net"
                },
                {
                    "url": "https://twitter.com/Bitstamp",
                    "type": "socialmedia"
                },
                {
                    "url": "https://twitter.com/BitstampSupport",
                    "type": "support",
                    "title": "Support Twitter Page"
                }
            ]
        }
    },
    "metrics": {
        "trustlines": 26709,
        "holders": 8718,
        "supply": "11417379.8901519",
        "marketcap": "33170620.9071712",
        "price": "2.90527434720663",
        
        "volume_24h": "102329.224597",
        "volume_7d": "1435464.294449",
        "exchanges_24h": "155",
        "exchanges_7d": "1972",
        "takers_24h": "40",
        "takers_7d": "147"
    }
}
