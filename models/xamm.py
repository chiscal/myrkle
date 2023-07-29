from sqlalchemy import Boolean, Column, Integer, String

from db.base_class import Base

class XAMMWallet(Base):
    __tablename__ = 'xamm_wallets'

    id = Column(Integer, primary_key=True, index=True)
    wallet_addr = Column(String, nullable=True)
    tf_sell = Column(Boolean, default=False)
    tf_fill_or_kill = Column(Boolean, default=False)
    tf_immediate_or_cancel = Column(Boolean, default=False)
