import os

from faerskit.faersmodels import Therapy, Source, Reaction, Outcome, Indication, Drug, Demographic
import math
from faerskit.sqlite import DbFaersSQLite, DbDictSQLite
import configparser

abspath = os.path.abspath(os.curdir)
# 创建 ConfigParser 对象
config = configparser.ConfigParser()
config.read(os.path.join(abspath, "config.ini"))


def get_config(key):
    return config[key]


def get_db_faers() -> DbFaersSQLite:
    return DbFaersSQLite()


def get_db_dict() -> DbDictSQLite:
    return DbDictSQLite()


class DdFields:
    def __init__(self, year, quarter):
        self.yearq = year + 0.1 * quarter
        self.trans = {
            'THER': [Therapy, self.therapy_fields],
            'RPSR': [Source, self.source_fields],
            'REAC': [Reaction, self.react_fields],
            'OUTC': [Outcome, self.outcome_fields],
            'INDI': [Indication, self.indication_fields],
            'DRUG': [Drug, self.drug_fields],
            'DEMO': [Demographic, self.demo_fields],
        }

    def translate(self, first_four):
        model = self.trans[first_four][0]
        table_fields = self.trans[first_four][1]()
        return {'model': model, 'table_fields': table_fields}

    def therapy_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'drug_seq', 'start_dt', 'end_dt', 'dur', 'dur_cod']
        else:
            return ['primaryid', 'caseid', 'drug_seq', 'start_dt', 'end_dt', 'dur', 'dur_cod']

    def source_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'rpsr_cod']
        else:
            return ['primaryid', 'caseid', 'rpsr_cod']

    def react_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'pt']
        elif self.yearq < 2014.3:
            return ['primaryid', 'caseid', 'pt']
        else:
            return ['primaryid', 'caseid', 'pt', 'drug_rec_act']

    def outcome_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'outc_cod']
        else:
            return ['primaryid', 'caseid', 'outc_cod']

    def indication_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'drug_seq', 'indi_pt']
        else:
            return ['primaryid', 'caseid', 'indi_drug_seq', 'indi_pt']

    def drug_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'drug_seq', 'role_cod', 'drugname', 'val_vbm', 'route', 'dose_vbm', 'dechal', 'rechal',
                    'lot_num', 'exp_dt', 'nda_num']
        elif self.yearq < 2014.3:
            return ['primaryid', 'caseid', 'drug_seq', 'role_cod', 'drugname', 'val_vbm', 'route', 'dose_vbm',
                    'cum_dose_chr', 'cum_dose_unit',
                    'dechal', 'rechal', 'lot_num', 'exp_dt', 'nda_num', 'dose_amt', 'dose_unit', 'dose_form',
                    'dose_freq']
        else:
            return ['primaryid', 'caseid', 'drug_seq', 'role_cod', 'drugname', 'prod_ai', 'val_vbm', 'route',
                    'dose_vbm', 'cum_dose_chr', 'cum_dose_unit',
                    'dechal', 'rechal', 'lot_num', 'exp_dt', 'nda_num', 'dose_amt', 'dose_unit', 'dose_form',
                    'dose_freq']

    def demo_fields(self):
        if self.yearq < 2012.4:
            return ['isr', 'case_num', 'i_f_cod', 'foll_seq', 'image', 'event_dt', 'mfr_dt', 'fda_dt', 'rept_cod',
                    'mfr_num', 'mfr_sndr', 'age', 'age_cod',
                    'gndr_cod', 'e_sub', 'wt', 'wt_cod', 'rept_dt', 'occp_cod', 'death_dt', 'to_mfr', 'confid',
                    'reporter_country']
        elif self.yearq < 2014.3:
            return ['primaryid', 'caseid', 'caseversion', 'i_f_cod', 'event_dt', 'mfr_dt', 'init_fda_dt', 'fda_dt',
                    'rept_cod', 'mfr_num', 'mfr_sndr',
                    'age', 'age_cod', 'gndr_cod', 'e_sub', 'wt', 'wt_cod', 'rept_dt', 'to_mfr', 'occp_cod',
                    'reporter_country', 'occr_country']
        else:
            return ['primaryid', 'caseid', 'caseversion', 'i_f_cod', 'event_dt', 'mfr_dt', 'init_fda_dt', 'fda_dt',
                    'rept_cod', 'auth_num', 'mfr_num',
                    'mfr_sndr', 'lit_ref', 'age', 'age_cod', 'age_grp', 'sex', 'e_sub', 'wt', 'wt_cod', 'rept_dt',
                    'to_mfr', 'occp_cod', 'reporter_country', 'occr_country']


def get_PRR(a, b, c, d):
    if a == 0 or b == 0 or c == 0 or d == 0:
        return 0
    else:
        return (a / float(a + b)) / (c / float(c + d))


def get_ROR(a, b, c, d):
    if a == 0 or b == 0 or c == 0 or d == 0:
        return [0, 0, 0]
    else:
        ROR = (a / float(c)) / (b / float(d))
        UpperCI = math.exp(math.log(ROR) + 1.96 * math.sqrt(1 / float(a) + 1 / float(b) + 1 / float(c) + 1 / float(d)))
        LowerCI = math.exp(math.log(ROR) - 1.96 * math.sqrt(1 / float(a) + 1 / float(b) + 1 / float(c) + 1 / float(d)))
        return [ROR, LowerCI, UpperCI]
