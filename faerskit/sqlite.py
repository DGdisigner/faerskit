from os.path import isfile
from os import remove
import pandas
from sqlalchemy import create_engine, text, or_
from sqlalchemy.orm import sessionmaker
from typing import List

from faerskit.faersmodels import Base, Reaction, Drug
from faerskit.dictmodels import DictBase, MeddraLlt, MeddraPt, MeddraHlt, MeddraHlgt, MeddraSoc, MeddraComb
from faerskit.interface import DbFaers, DbDict


def setup_fears_db():
    from faerskit import config
    database = config['sqlite']['faers_db']
    if isfile(database):
        remove(database)
    # 创建sqlite连接引擎
    engine = create_engine('sqlite:///' + database, echo=config['sqlite'].getboolean('debug'))
    Base.metadata.create_all(engine, checkfirst=True)


def setup_dict_db():
    from faerskit import config
    database = config['sqlite']['dict_db']
    if isfile(database):
        remove(database)
    # 创建sqlite连接引擎
    engine = create_engine('sqlite:///' + database, echo=config['sqlite'].getboolean('debug'))
    DictBase.metadata.create_all(engine, checkfirst=True)


def insert_if_not_exists(session, model, key, data):
    # 检查 id 是否存在
    result = session.query(model).with_for_update().get(key)
    if result is None:
        session.add(data)


class DbFaersSQLite(DbFaers):
    """
    This class is used to create a SQLite database and insert data into it.
    """

    def session(self):
        db_session = sessionmaker(bind=self.engine)
        return db_session()

    def __init__(self):
        from faerskit import config
        # 创建sqlite连接引擎
        self.engine = create_engine('sqlite:///' + config["sqlite"]["faers_db"],
                                    echo=config['sqlite'].getboolean("debug"))

    def get_session(self):
        db_session = sessionmaker(bind=self.engine)
        return db_session()

    def batch_insert_faers_data(self, year, quarter, model, list_data: List[dict]):
        year_q = year * 100 + quarter
        session = self.get_session()
        session.query(model).filter(model.year_q == year_q).delete()
        for item in list_data:
            item['year_q'] = year_q
            item['id'] = None
            if model is Reaction:
                item['pt'] = item['pt'].upper()
        session.bulk_insert_mappings(model, list_data)
        session.commit()

    def batch_insert_data(self, model, list_data: List[dict]):
        session = self.get_session()
        session.bulk_insert_mappings(model, list_data)
        session.commit()

    def exec(self, sql, params):
        session = self.get_session()
        # 使用 text() 构建 SQL 语句
        sql_query = text(sql)
        execute = session.execute(sql_query, params)
        print(execute)
        session.commit()

    def get_reactions_by_pt(self, list_pt: List[str]):
        if not list_pt:
            return pandas.DataFrame()
        session = self.get_session()
        in_clause = ", ".join(f"'{item}'" for item in list_pt)
        query = f"select IFNULL(primaryid, isr) as pid, pt, year_q from reaction where pt in ({in_clause}) group by pid;"
        return pandas.read_sql(query, session.bind)

    def get_drugs_by_pid(self, list_pid: List[int], role_code=None):
        if role_code is None:
            role_code = ["PS"]
        if not list_pid:
            return pandas.DataFrame()
        session = self.get_session()
        in_clause_pid = ", ".join(f"'{item}'" for item in list_pid)
        in_clause_role_code = ", ".join(f"'{item}'" for item in role_code)
        query = f"select IFNULL(primaryid, isr) as pid, drugname, prod_ai, role_cod from drug where (isr in ({in_clause_pid}) or primaryid in ({in_clause_pid})) and role_cod in ({in_clause_role_code});"
        return pandas.read_sql(query, session.bind)

    def get_count_by_drugname(self, drugname=None, role_code=None):
        if role_code is None:
            role_code = ["PS"]
        session = self.get_session()
        in_clause_role_code = ", ".join(f"'{item}'" for item in role_code)
        if drugname is None:
            query = f"select count(pid) from (select IFNULL(primaryid, isr) as pid from drug where role_cod in ({in_clause_role_code})group by pid) t;"
        else:
            in_clause_drugname = ", ".join(f"'{item}'" for item in drugname)
            query = f"select count(pid) from (select IFNULL(primaryid, isr) as pid from drug where drugname in ({in_clause_drugname}) and role_cod in ({in_clause_role_code})group by pid) t;"
        # 执行查询
        result = session.execute(text(query))
        session.commit()
        return result.scalar()


class DbDictSQLite(DbDict):

    def session(self):
        db_session = sessionmaker(bind=self.engine)
        return db_session()

    def __init__(self):
        from faerskit import config
        # 创建sqlite连接引擎
        self.engine = create_engine('sqlite:///' + config['sqlite']["dict_db"],
                                    echo=config['sqlite'].getboolean("debug"))

    def get_session(self):
        db_session = sessionmaker(bind=self.engine)
        return db_session()

    def insert_meddra_row(self, data):
        session = self.get_session()
        # 6. 插入数据
        try:
            # 创建对象实例
            if pandas.isna(data.llt_English) is False:
                llt = MeddraLlt(
                    llt_code=data.llt_code,
                    pt_code=data.pt_code,
                    llt=data.llt_English.strip().upper(),
                    llt_cn=data.llt_Chinese
                )
                insert_if_not_exists(session, MeddraLlt, llt.llt_code, llt)
            pt = MeddraPt(
                pt_code=data.pt_code,
                pt=data.pt_english.strip().upper(),
                pt_cn=data.pt_chinese
            )
            insert_if_not_exists(session, MeddraPt, pt.pt_code, pt)
            hlt = MeddraHlt(
                hlt_code=data.hlt_code,
                hlt=data.hlt_english.strip().upper(),
                hlt_cn=data.hlt_chinese
            )
            insert_if_not_exists(session, MeddraHlt, hlt.hlt_code, hlt)
            hlgt = MeddraHlgt(
                hlgt_code=data.hlgt_code,
                hlgt=data.hlgt_english.strip().upper(),
                hlgt_cn=data.hlgt_chinese
            )
            insert_if_not_exists(session, MeddraHlgt, hlgt.hlgt_code, hlgt)
            soc = MeddraSoc(
                soc_code=data.soc_code,
                soc=data.soc_english.strip().upper(),
                soc_cn=data.soc_chinese
            )
            insert_if_not_exists(session, MeddraSoc, soc.soc_code, soc)
            comb = MeddraComb(
                pt_code=data.pt_code,
                hlt_code=data.hlt_code,
                hlgt_code=data.hlgt_code,
                soc_code=data.soc_code,
                primary_soc=data.primary_soc
            )
            session.add(comb)
            # 提交会话
            session.commit()
        except Exception as e:
            # 回滚事务
            session.rollback()
            print(f"插入数据时发生错误: {e}")
        finally:
            # 关闭会话
            session.close()

    def batch_insert_data(self, model, list_data: List[dict]):
        session = self.get_session()
        session.bulk_insert_mappings(model, list_data)
        session.commit()

    def search_pt(self, pt: str):
        session = self.get_session()
        query = session.query(MeddraPt).filter(or_(MeddraPt.pt.like(f"%{pt}%"), MeddraPt.pt_cn.like(f"%{pt}%")))
        return pandas.read_sql(query.statement, session.bind)
