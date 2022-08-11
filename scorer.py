import pandas as pd
from pprint import pprint


class ROIChecker:

    def __init__(
        self,
        start_bank: int = 5000,
        static_bet: int = 50,
        percent_of_bank: float = 0.01,
        roi_threshold: float = 0,
    ):

        self.static_bet = static_bet
        self.dynamic_bet = start_bank * percent_of_bank
        self.start_bank = start_bank
        self.current_dynamic_bank = self.start_bank
        self.current_static_bank = self.start_bank
        self.percent_of_bank = percent_of_bank
        self.roi_threshold = roi_threshold

        self.detail_static_bank_values = [self.start_bank]
        self.batch_static_bank_values = [self.start_bank]
        self.detail_dynamic_bank_values = [self.start_bank]
        self.batch_dynamic_bank_values = [self.start_bank]
        self.full_static_info = []
        self.full_dynamic_info = []

        self.target = None
        self.total_target = None
        self.both_target = None
        self.X_test = None
        self.preds_proba = None
        self.preds_proba_total = None
        self.preds_proba_both = None

    def run_check(
            self,
            X_test: pd.DataFrame,
            result_target,
            total_target,
            both_target,
            preds_proba_result=None,
            preds_proba_total=None,
            preds_proba_both=None,
    ):

        self.preds_proba_result = preds_proba_result
        self.preds_proba_total = preds_proba_total
        self.preds_proba_both = preds_proba_both
        self.X_test = X_test.reset_index()
        self.result_target = result_target.reset_index()['result_target']
        self.total_target = total_target.reset_index()['total_target']
        self.both_target = both_target.reset_index()['both_target']

        predictions = self.make_predictions()
        total_predictions = self.make_total_predictions()
        both_predictions = self.make_both_predictions()

        self.count_static_money(predictions, total_predictions, both_predictions)

    def return_info(self):
        return (self.full_dynamic_info, self.detail_dynamic_bank_values, self.batch_dynamic_bank_values), (
            self.full_static_info, self.detail_static_bank_values, self.batch_static_bank_values)

    def make_predictions(self):
        results = []
        for i, row in self.X_test.iterrows():
            home_value = self.preds_proba_result[i][2] * row['home_win_rate']
            away_value = self.preds_proba_result[i][0] * row['away_win_rate']
            draw_value = self.preds_proba_result[i][1] * row['draw_rate']
            values = [home_value, away_value, draw_value]
            max_value = values.index(max(values))
            if values[max_value] > 1.05:
                if max_value == 0:
                    bet = 3
                    coef = row['home_win_rate']
                    chance = self.preds_proba_result[i][2]
                elif max_value == 1:
                    bet = 0
                    coef = row['away_win_rate']
                    chance = self.preds_proba_result[i][0]
                else:
                    bet = 1
                    coef = row['draw_rate']
                    chance = self.preds_proba_result[i][1]
                result = {
                    'league': row['league'],
                    'country': row['country'],
                    'season': row['season'],
                    'bet': bet,
                    'coef': coef,
                    'chance': chance,
                    'date': row['timestamp_date'],
                    'index': i,
                }
                results.append(result)
        return results

    def make_total_predictions(self):
        results = []
        for i, row in self.X_test.iterrows():
            over_value = self.preds_proba_total[i][1] * row['total_over_25_rate']
            under_value = self.preds_proba_total[i][0] * row['total_under_25_rate']
            values = [under_value, over_value]
            max_value = values.index(max(values))
            if values[max_value] > 1.05:
                if max_value == 0:
                    bet = 0
                    coef = row['total_under_25_rate']
                    chance = self.preds_proba_total[i][0]
                else:
                    bet = 1
                    coef = row['total_over_25_rate']
                    chance = self.preds_proba_total[i][1]
                result = {
                    'league': row['league'],
                    'country': row['country'],
                    'season': row['season'],
                    'bet': bet,
                    'coef': coef,
                    'chance': chance,
                    'date': row['timestamp_date'],
                    'index': i,
                }
                results.append(result)
        return results

    def make_both_predictions(self):
        results = []
        for i, row in self.X_test.iterrows():
            yes_value = self.preds_proba_both[i][1] * row['both_team_to_score_yes']
            no_value = self.preds_proba_both[i][0] * row['both_team_to_score_no']
            values = [no_value, yes_value]
            max_value = values.index(max(values))
            if values[max_value] > 1.05:
                if max_value == 0:
                    bet = 0
                    coef = row['both_team_to_score_no']
                    chance = self.preds_proba_both[i][0]
                else:
                    bet = 1
                    coef = row['both_team_to_score_yes']
                    chance = self.preds_proba_both[i][1]
                result = {
                    'league': row['league'],
                    'country': row['country'],
                    'season': row['season'],
                    'bet': bet,
                    'coef': coef,
                    'chance': chance,
                    'date': row['timestamp_date'],
                    'index': i,
                }
                results.append(result)
        return results

    def count_static_money(self, predictions: list[dict], total_predictions: list[dict], both_predictions: list[dict]):

        initial_bank = self.current_static_bank

        total_profit = 0
        total_coef = 0

        win_bets = 0
        lose_bets = 0

        result_win_bets = 0
        total_win_bets = 0
        both_win_bets = 0

        skipped_bets = 0
        accepted_bets = 0

        result_accepted_bets = 0
        total_accepted_bets = 0
        both_accepted_bets = 0

        win_coef = 0
        lose_coef = 0

        result_win_coef = 0
        total_win_coef = 0
        both_win_coef = 0

        win_bank = 0
        lose_bank = 0
        for index, row in enumerate(predictions):
            if row['chance'] > self.roi_threshold:

                accepted_bets += 1
                result_accepted_bets += 1
                accepted_coef = row['coef']
                i = row['index']

                if self.result_target[i] == row['bet']:

                    current_profit = self.dynamic_bet * (accepted_coef - 1)
                    total_profit += current_profit
                    self.update_static_bank(self.current_static_bank + current_profit)
                    win_coef += accepted_coef
                    result_win_coef += accepted_coef
                    win_bank += current_profit
                    win_bets += 1
                    result_win_bets += 1

                else:
                    total_profit -= self.dynamic_bet
                    self.update_static_bank(self.current_static_bank - self.dynamic_bet)
                    lose_coef += accepted_coef
                    lose_bank -= self.dynamic_bet
                    lose_bets += 1

                total_coef += accepted_coef
                self.detail_static_bank_values.append(self.current_static_bank)

            else:
                skipped_bets += 1
        for index, row in enumerate(total_predictions):
            if row['chance'] > self.roi_threshold:

                accepted_bets += 1
                total_accepted_bets += 1
                accepted_coef = row['coef']
                i = row['index']

                if self.total_target[i] == row['bet']:

                    current_profit = self.dynamic_bet * (accepted_coef - 1)
                    total_profit += current_profit
                    self.update_static_bank(self.current_static_bank + current_profit)
                    win_coef += accepted_coef
                    total_win_coef += accepted_coef
                    win_bank += current_profit
                    win_bets += 1
                    total_win_bets += 1

                else:
                    total_profit -= self.dynamic_bet
                    self.update_static_bank(self.current_static_bank - self.dynamic_bet)
                    lose_coef += accepted_coef
                    lose_bank -= self.dynamic_bet
                    lose_bets += 1

                total_coef += accepted_coef
                self.detail_static_bank_values.append(self.current_static_bank)

            else:
                skipped_bets += 1

        for index, row in enumerate(both_predictions):
            if row['chance'] > self.roi_threshold:

                accepted_bets += 1
                both_accepted_bets += 1
                accepted_coef = row['coef']
                i = row['index']

                if self.both_target[i] == row['bet']:

                    current_profit = self.dynamic_bet * (accepted_coef - 1)
                    total_profit += current_profit
                    self.update_static_bank(self.current_static_bank + current_profit)
                    win_coef += accepted_coef
                    both_win_coef += accepted_coef
                    win_bank += current_profit
                    win_bets += 1
                    both_win_bets += 1

                else:
                    total_profit -= self.dynamic_bet
                    self.update_static_bank(self.current_static_bank - self.dynamic_bet)
                    lose_coef += accepted_coef
                    lose_bank -= self.dynamic_bet
                    lose_bets += 1

                total_coef += accepted_coef
                self.detail_static_bank_values.append(self.current_static_bank)

            else:
                skipped_bets += 1

        try:
            result_average_win_coef = result_win_coef / result_win_bets
        except ZeroDivisionError:
            result_average_win_coef = 0

        try:
            total_average_win_coef = total_win_coef / total_win_bets
        except ZeroDivisionError:
            total_average_win_coef = 0

        try:
            both_average_win_coef = both_win_coef / both_win_bets
        except ZeroDivisionError:
            both_average_win_coef = 0

        try:
            average_win_coef = win_coef / win_bets
        except ZeroDivisionError:
            average_win_coef = 0

        self.batch_static_bank_values.append(self.current_static_bank)
        try:
            percent_profit = (self.current_static_bank - initial_bank) / initial_bank * 100
        except ZeroDivisionError:
            percent_profit = 0
        try:
            average_lose_coef = lose_coef / lose_bets
        except ZeroDivisionError:
            average_lose_coef = 0
        try:
            average_coef = total_coef / accepted_bets
        except ZeroDivisionError:
            average_coef = 0

        result = {
            'initial_bank': initial_bank,
            'total_bank': self.current_static_bank,
            'result_accepted_bets': result_accepted_bets,
            'result_average_win_coef': result_average_win_coef,
            'result_win_rate': result_win_bets / result_accepted_bets if result_accepted_bets > 0 else 0,
            'total_accepted_bets': total_accepted_bets,
            'total_average_win_coef': total_average_win_coef,
            'total_win_rate': total_win_bets / total_accepted_bets if total_accepted_bets > 0 else 0,
            'both_accepted_bets': both_accepted_bets,
            'both_average_win_coef': both_average_win_coef,
            'both_win_rate': both_win_bets / both_accepted_bets if both_accepted_bets > 0 else 0,
            'skipped_bets': skipped_bets,
            'accepted_bets': accepted_bets,
            'profit': total_profit,
            'percent_profit': percent_profit,
            'win_bank': win_bank,
            'lose_bank': lose_bank,
            'win_bets': win_bets,
            'result_win_bets': result_win_bets,
            'total_win_bets': total_win_bets,
            'both_win_bets': both_win_bets,
            'lose_bets': lose_bets,
            'average_coef': average_coef,
            'average_win_coef': average_win_coef,
            'average_lose_coef': average_lose_coef,
            'win_rate': win_bets / accepted_bets if accepted_bets > 0 else 0,

        }
        print(self.current_static_bank)
        print(result)
        self.dynamic_bet = self.current_static_bank * self.percent_of_bank
        print('bet', self.dynamic_bet)
        self.full_static_info.append(result)
        self.count_average_static_info()

    def update_static_bank(self, bank: float):
        """ Count new bank with static bet"""

        self.current_static_bank = bank

    def update_dynamic_bank(self, bank: float):
        """ Count new bank using % of current bank as bet """

        self.current_dynamic_bank = bank
        self.update_dynamic_bet()

    def update_dynamic_bet(self):
        self.dynamic_bet = self.current_dynamic_bank * self.percent_of_bank

    def count_average_static_info(self):
        accepted_bets = 0
        result_accepted_bets = 0
        total_accepted_bets = 0
        both_accepted_bets = 0
        win_bets = 0
        result_win_bets = 0
        total_win_bets = 0
        both_win_bets = 0
        lose_bets = 0
        average_coefs = []
        average_win_coefs = []
        result_average_win_coefs = []
        total_average_win_coefs = []
        both_average_win_coefs = []
        batch = 0
        for result in self.full_static_info:
            accepted_bets += result['accepted_bets']
            result_accepted_bets += result['result_accepted_bets']
            total_accepted_bets += result['total_accepted_bets']
            both_accepted_bets += result['both_accepted_bets']
            win_bets += result['win_bets']
            result_win_bets += result['result_win_bets']
            total_win_bets += result['total_win_bets']
            both_win_bets += result['both_win_bets']
            lose_bets += result['lose_bets']
            average_coefs.append(result['average_coef'])
            average_win_coefs.append(result['average_win_coef'])
            result_average_win_coefs.append(result['result_average_win_coef'])
            total_average_win_coefs.append(result['total_average_win_coef'])
            both_average_win_coefs.append(result['both_average_win_coef'])
            batch += 1
        average_coef = sum(average_coefs) / batch
        average_win_coef = sum(average_win_coefs) / batch
        result_average_win_coef = sum(result_average_win_coefs) / batch
        total_average_win_coef = sum(total_average_win_coefs) / batch
        both_average_win_coef = sum(both_average_win_coefs) / batch
        win_rate = win_bets / accepted_bets if accepted_bets > 0 else 0
        result_win_rate = result_win_bets / result_accepted_bets if result_accepted_bets > 0 else 0
        total_win_rate = total_win_bets / total_accepted_bets if total_accepted_bets > 0 else 0
        both_win_rate = both_win_bets / both_accepted_bets if both_accepted_bets > 0 else 0
        total_bank = self.full_static_info[-1]['total_bank']
        percent_profit = round((total_bank - self.start_bank) / self.start_bank * 100, 2)
        profit = total_bank - self.start_bank
        pprint(
            {
                'result_accepted_bets': result_accepted_bets,
                'result_average_win_coef': result_average_win_coef,
                'result_win_rate': result_win_rate,
                'total_accepted_bets': total_accepted_bets,
                'total_average_win_coef': total_average_win_coef,
                'total_win_rate': total_win_rate,
                'both_accepted_bets': both_accepted_bets,
                'both_average_win_coef': both_average_win_coef,
                'both_win_rate': both_win_rate,
                'accepted_bets': accepted_bets,
                'win_bets': win_bets,
                'lose_bets': lose_bets,
                'win_rate': win_rate,
                'percent_profit': percent_profit,
                'profit': profit,
                'average_coef': average_coef,
                'average_win_coef': average_win_coef,
                'total_bank': total_bank,
            }
        )
