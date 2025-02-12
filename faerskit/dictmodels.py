from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Index

DictBase = declarative_base()


class MeddraSoc(DictBase):
    __tablename__ = 'meddra_soc'
    soc_code = Column(Integer, primary_key=True)
    soc = Column(String)
    soc_cn = Column(String)


class MeddraHlgt(DictBase):
    __tablename__ = 'meddra_hlgt'
    hlgt_code = Column(Integer, primary_key=True)
    hlgt = Column(String)
    hlgt_cn = Column(String)


class MeddraHlt(DictBase):
    __tablename__ = 'meddra_hlt'
    hlt_code = Column(Integer, primary_key=True)
    hlt = Column(String)
    hlt_cn = Column(String)


# 一个LLT只能连接到一个PT，而从PT以上，可以通过多条路径连接到上一个级别水平的术语，即一个PT可以连接到几个HLT。
# 一个HLT可以连接到几个HLGT，每一HLGT又可以连接到几个SOC分类。
# 这种一个医学概念（即PT）隶属于一个以上的SOC的特性被称为“多轴性”。

class MeddraComb(DictBase):
    __tablename__ = 'meddra_comb'
    comb_id = Column(Integer, primary_key=True, autoincrement=True)
    pt_code = Column(Integer)
    hlt_code = Column(Integer)
    hlgt_code = Column(Integer)
    soc_code = Column(Integer)
    primary_soc = Column(String)


class MeddraPt(DictBase):
    __tablename__ = 'meddra_pt'
    pt_code = Column(Integer, primary_key=True)
    pt = Column(String)
    pt_cn = Column(String)
    pt_count = Column(Integer, default=0)


class MeddraLlt(DictBase):
    __tablename__ = 'meddra_llt'
    llt_code = Column(Integer, primary_key=True)
    pt_code = Column(Integer)
    llt = Column(String)
    llt_cn = Column(String)


class DrugDict(DictBase):
    __tablename__ = 'drug_dict'
    id = Column(Integer, primary_key=True, autoincrement=True)
    drugname = Column(String)
    drugname_cn = Column(String)
    prod_ai = Column(String)
    prod_ai_cn = Column(String)
    ae_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_drugname', 'drugname'),
        Index('idx_drugname_cn', 'drugname_cn'),
        Index('idx_prod_ai', 'prod_ai'),
    )


class IndicationDict(DictBase):
    __tablename__ = 'indication_dict'
    id = Column(Integer, primary_key=True, autoincrement=True)
    indi_pt = Column(String)
    indi_pt_cn = Column(String)
    count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_indi_pt', 'indi_pt'),
        Index('idx_indi_pt_cn', 'indi_pt_cn'),
    )
