import storage
import constants as const

import pandas as pd

def export_hlasovanie(col, cisloObdobia, meta_filename, individual_filename):
    meta_keys = [const.HLASOVANIE_OBDOBIE, const.HLASOVANIE_SCHODZA,
        const.HLASOVANIE_CAS, const.HLASOVANIE_CISLO, const.HLASOVANIE_NAZOV,
        const.HLASOVANIE_SURHN_PRITOMNI, const.HLASOVANIE_SURHN_HLASUJUCICH, 
        const.HLASOVANIE_SURHN_ZA, const.HLASOVANIE_SURHN_PROTI,
        const.HLASOVANIE_SURHN_ZDRZALO, const.HLASOVANIE_SURHN_NEHLASOVALO,
        const.HLASOVANIE_SUHRN_NEPRITOMNI, const.HLASOVANIE_VYSLEDOK]
    entries = col.get_all({const.HLASOVANIE_OBDOBIE: cisloObdobia})
    meta_entries = {entry[const.MONGO_ID]:
        {key: entry.get(key, None) for key in meta_keys} 
        for entry in entries
    }
    meta_df = pd.DataFrame(meta_entries)
    meta_df.to_csv(meta_filename)

    individual_entries = {
        entry[const.MONGO_ID]: {
            int(key): const.HLASOVAL_HLAS_DICT[value[const.HLASOVANIE_HLAS]]
            for key, value in entry[const.HLASOVANIE_INDIVIDUALNE].items()
        }
        for entry in entries if const.HLASOVANIE_INDIVIDUALNE in entry
    }
    individual_df = pd.DataFrame(individual_entries)
    individual_df.to_csv(individual_filename)

def export_poslanec(col, cisloObdobia, poslanec_filename):
    poslanec_keys = [const.POSLANEC_OBDOBIE, const.POSLANEC_PRIEZVISKO, const.POSLANEC_MENO,
        const.POSLANEC_TITUL, const.POSLANEC_KANDIDOVAL, const.POSLANEC_NARODENY,
        const.POSLANEC_NARODNOST, const.POSLANEC_BYDLISKO, const.POSLANEC_KRAJ]
    entries = col.get_all({const.POSLANEC_OBDOBIE: cisloObdobia})
    poslanec_entries = {entry[const.MONGO_ID]: {
        key: entry.get(key, None) for key in poslanec_keys
        }
        for entry in entries
    }
    poslanec_df = pd.DataFrame(poslanec_entries)
    poslanec_df.to_csv(poslanec_filename)