from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Index

Base = declarative_base()


class Demographic(Base):
    __tablename__ = 'demographic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    caseversion = Column(Integer)
    case_num = Column(Integer)
    i_f_cod = Column(String)
    foll_seq = Column(String)
    image = Column(String)
    event_dt = Column(String)
    mfr_dt = Column(String)
    init_fda_dt = Column(String)
    fda_dt = Column(String)
    rept_cod = Column(String)
    auth_num = Column(Integer)
    mfr_num = Column(String)
    mfr_sndr = Column(String)
    lit_ref = Column(String)
    age = Column(String)
    age_cod = Column(String)
    age_grp = Column(String)
    sex = Column(String)
    gndr_cod = Column(String)
    e_sub = Column(String)
    wt = Column(String)
    wt_cod = Column(String)
    rept_dt = Column(String)
    occp_cod = Column(String)
    death_dt = Column(String)
    to_mfr = Column(String)
    confid = Column(String)
    reporter_country = Column(String)
    occr_country = Column(String)
    year_q = Column(Integer)


class Drug(Base):
    __tablename__ = 'drug'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    drug_seq = Column(Integer)
    role_cod = Column(String)
    drugname = Column(String)
    prod_ai = Column(String)
    val_vbm = Column(Integer)
    route = Column(String)
    dose_vbm = Column(String)
    cum_dose_chr = Column(String)
    cum_dose_unit = Column(String)
    dechal = Column(String)
    rechal = Column(String)
    lot_num = Column(String)
    exp_dt = Column(String)
    nda_num = Column(String)
    dose_amt = Column(String)
    dose_unit = Column(String)
    dose_form = Column(String)
    dose_freq = Column(String)
    year_q = Column(Integer)


class Reaction(Base):
    __tablename__ = 'reaction'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    pt = Column(String, nullable=False)
    drug_rec_act = Column(String)
    year_q = Column(Integer)

    __table_args__ = (
        Index('idx_pt', 'pt'),                 # 联合索引
    )


class Outcome(Base):
    __tablename__ = 'outcome'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    outc_cod = Column(String, nullable=False)
    year_q = Column(Integer)


class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    rpsr_cod = Column(String, nullable=False)
    year_q = Column(Integer)


class Therapy(Base):
    __tablename__ = 'therapy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    drug_seq = Column(Integer)
    start_dt = Column(String)
    end_dt = Column(String)
    dur = Column(String)
    dur_cod = Column(String)
    year_q = Column(Integer)


class Indication(Base):
    __tablename__ = 'indication'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isr = Column(Integer)
    primaryid = Column(Integer)
    caseid = Column(Integer)
    drug_seq = Column(Integer)
    indi_drug_seq = Column(Integer)
    indi_pt = Column(String)
    year_q = Column(Integer)
