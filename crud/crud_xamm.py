from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.xamm import XAMMWallet
from schemas.xamm import XAMMWallet as XAMMWALLETSCHEMA


class CRUDUser(CRUDBase[XAMMWallet, XAMMWALLETSCHEMA, XAMMWALLETSCHEMA]):
    def get_by_address(self, db: Session, *, wallet_addr: str) -> Optional[XAMMWallet]:
        return db.query(
            XAMMWallet
        ).filter(XAMMWallet.wallet_addr == wallet_addr).first()

    def create(self, db: Session, *, obj_in: XAMMWALLETSCHEMA) -> XAMMWallet:
        db_obj = XAMMWallet(
            wallet_addr=obj_in.wallet_addr,
            tf_sell=obj_in.tf_sell,
            tf_fill_or_kill=obj_in.tf_fill_or_kill,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *,
        db_obj: XAMMWallet, obj_in: Union[XAMMWALLETSCHEMA, Dict[str, Any]]
    ) -> XAMMWallet:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


xamm_wallet = CRUDUser(XAMMWallet)
