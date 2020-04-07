"""Эволюция параметров модели и хранение в MongoDB."""
from typing import Tuple

import pandas as pd

from poptimizer.evolve import population

# Коллекция для хранения моделей
MODELS = "models"

# Метки ключей документа

MAX_POPULATION = 100


class Evolution:
    """Эволюция параметров модели и хранение в MongoDB."""

    def __init__(self, max_population: int = MAX_POPULATION):
        self._max_population = max_population

    def evolve(self, tickers: Tuple[str, ...], end: pd.Timestamp):
        """Осуществляет одну эпоху эволюции."""
        self._setup(tickers, end)

        new_children = 0

        for step in range(1, self._max_population + 1):
            print(f"***Шаг эпохи - {step}/{self._max_population}***")
            population.print_stat()
            print()

            print("Родитель:")
            parent = population.get_random_organism()
            print(parent)
            parent_sharpe = parent.sharpe(tickers, end)
            print(f"Коэффициент Шарпа: {parent_sharpe}")
            print()

            print("Потомок:")
            child = parent.make_child()
            new_children += 1
            print(child)
            child_sharpe = child.sharpe(tickers, end)
            print(f"Коэффициент Шарпа: {child_sharpe}")
            print()

            excess = population.count() > self._max_population

            if child_sharpe < parent_sharpe:
                child.kill()
                new_children -= 1
                print("Удаляю потомка.")
            elif excess:
                parent.kill()
                print("Удаляю родителя.")

            print(f"Добавлено потомков - {new_children}...")
            print()

    def _setup(self, tickers, end):
        """Нужно минимум 4 генотипа."""
        # TODO: добавить удаление лишних
        count = population.count()
        print(f"Имеется {count} организмов из {self._max_population}")
        print()

        if count > self._max_population:
            print("Имеются лишние - сравниваю два организма.")
            print()

            print("Первый:")
            first = population.get_random_organism()
            print(first)
            first_sharpe = first.sharpe(tickers, end)
            print(f"Коэффициент Шарпа: {first_sharpe}")
            print()

            print("Второй:")
            second = population.get_random_organism()
            print(second)
            second_sharpe = second.sharpe(tickers, end)
            print(f"Коэффициент Шарпа: {second_sharpe}")
            print()

            if first_sharpe < second_sharpe:
                first.kill()
                print("Удаляю первого.")
                print()
            else:
                second.kill()
                print("Удаляю второго.")
                print()

        for i in range(1, 4 - count + 1):
            print(f"Создаю базовые генотипы - {i}/{count}")
            organism = population.create_new_organism()
            print(organism)
            print()


if __name__ == "__main__":
    pos = dict(
        AKRN=7 + 715 + 88 + 4 + (140 + 0),
        ALRS=2690,
        BANEP=1097 + 13 + 107 + 235,
        BSPB=4890 + 0 + 3600 + 150,
        CBOM=0 + 4400 + 71000 + (197_200 + 0),
        CHMF=114 + 1029 + 170,
        GCHE=0 + 0 + 24,
        GMKN=0 + 109 + 1,
        KRKNP=66 + 0 + 43,
        KZOS=490 + 5080 + 2090,
        LSNGP=2280 + 670 + 2410,
        LSRG=0 + 649 + 0 + 80,
        MGTSP=485 + 0 + 9,
        MOEX=2110 + 200 + 290 + (6730 + 0),
        MTSS=2340 + 4800 + 1500 + 2120 + (3540 + 0),
        MVID=90 + 0 + 800 + (1940 + 0),
        NMTP=29000 + 74000 + 13000 + 67000,
        PHOR=497 + 271 + 248 + 405 + (420 + 0),
        PIKK=0 + 3090 + 0 + 90,
        PLZL=86 + 21 + 23,
        PMSBP=0 + 0 + 1160,
        PRTK=0 + 6980,
        RNFT=0 + 318 + 487 + 112,
        # RTKM=(2180 + 0),
        # RTKMP=0 + 29400,
        # SELG=1300 + 11100 + 1000 + (41800 + 0),
        # SNGSP=56300 + 12200 + 16800 + 4300 + (28500 + 0),
        # TRCN=41 + 0 + 4 + 3,
        # TRNFP=7 + (8 + 0),
        # UPRO=345_000 + 451_000 + 283_000 + 85000,
        # VSMO=39 + 161 + 3,
        # DSKY=0,
        # CNTLP=0,
        # BANE=0,
        # IRKT=0,
        # MRKV=0,
        # TATNP=0,
        # SIBN=0,
        # UNAC=0,
        # MRKC=0,
        # LSNG=0,
        # MSRS=0,
        # SVAV=0,
        # TGKA=0,
        # NKNC=0,
        # NVTK=0,
        # LKOH=0,
        # OGKB=0,
        # AFLT=0,
        # SNGS=0,
        # MRKZ=0,
        # ROSN=0,
        # SBERP=0,
        # VTBR=0,
        # ENRU=0,
        # TATN=0,
        # RASP=0,
        # NLMK=0,
        # NKNCP=0,
        # FEES=0,
        # HYDR=0,
        # MRKP=0,
        # MTLRP=0,
        # MAGN=0,
        # GAZP=0,
        # SBER=0,
        # MGNT=0,
        # RSTI=0,
        # MSNG=0,
        # AFKS=0,
        # SFIN=0,
        # MTLR=0,
        # ISKJ=0,
        # TRMK=0,
        # RSTIP=0,
        # OBUV=0,
        # APTK=0,
        # LNZL=0,
        # GTRK=0,
        # ROLO=0,
        # FESH=0,
        # IRAO=0,
        # AMEZ=0,
        # YAKG=0,
        # AQUA=0,
        # RGSS=0,
        # LIFE=0,
        # KBTK=0,
        # KMAZ=0,
        # TTLK=0,
        # TGKD=0,
        # TGKB=0,
        # RBCM=0,
        # KZOSP
    )
    ev = Evolution()
    ev.evolve(tuple(pos), pd.Timestamp("2019-06-04"))