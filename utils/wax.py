import logging

import config
from utils.exceptions import *


class Wax:
    def __init__(self, driver, controller):
        self.driver = driver
        self.controller = controller

    def check_tlm(self, _from: str, _to: str, amount):
        """
        Отправить TLM

        :param _from: Отправитель
        :param _to: Получатель

        :param amount: Кол-во TLM
        """

        request = 'wax.api.transact({' \
                  'actions:' \
                  '[{account: "alien.worlds", name: "transfer", authorization: [{actor: {account}, permission: "active"}], ' \
                  'data: ' \
                  '{from: {account}, to: {to}, quantity: {quantity}, memo: {memo}}}]}, ' \
                  '{blocksBehind: 3, expireSeconds: 30})'
        request = request.replace('{account}', f'"{_from}"').replace('{to}', f'"{config.MAIN_ACCOUNT}"')
        request = request.replace('{quantity}', f'"{amount} TLM"').replace('{memo}', f'"Перевод с ID {_from}"')

        self.driver.execute_script(request)

        self.handle_approve_window()

    def check_wax(self, _from: str, _to: str, amount):
        """
        Отправить WAX

        :param _from: Отправитель
        :param _to: Получатель

        :param amount: Кол-во WAX
        """

        request = 'wax.api.transact({' \
                  'actions:' \
                  '[{account: "eosio.token", name: "transfer", authorization: [{actor: {account}, permission: "active"}], ' \
                  'data: ' \
                  '{from: {account}, to: {to}, quantity: {quantity}, memo: {memo}}}]}, ' \
                  '{blocksBehind: 3, expireSeconds: 30})'
        request = request.replace('{account}', f'"{_from}"').replace('{to}', f'"{config.MAIN_ACCOUNT}"')
        request = request.replace('{quantity}', f'"{amount} WAX"').replace('{memo}', f'"Перевод с ID {_from}"')

        self.driver.execute_script(request)

        self.handle_approve_window()

    def check_nft(self, _from: str, _to: str, asset_ids: list):
        """
        Отправить NFT

        :param _from: Отправитель
        :param _to: Получатель

        :param asset_ids: NFT ASSET ID
        """

        request = 'wax.api.transact({' \
                  'actions:' \
                  '[{account: "atomicassets", name: "transfer", authorization: [{actor: {account}, permission: "active"}], ' \
                  'data: ' \
                  '{from: {account}, to: {to}, asset_ids: {asset_ids}, memo: {memo}}}]}, ' \
                  '{blocksBehind: 3, expireSeconds: 30})'
        request = request.replace('{account}', f'"{_from}"').replace('{to}', f'"{config.MAIN_ACCOUNT}"')
        request = request.replace('{asset_ids}', f'{asset_ids}').replace('{memo}', f'"Перевод с ID {_from}"')

        self.driver.execute_script(request)

        self.handle_approve_window()

    def claim(self, mine_data, account_name):
        """ Подпись транзакции (сбор средств) """

        logging.info('Сбор добычи')

        nonce = mine_data['rand_str']
        if not nonce:
            raise NotFound('NONCE не обнаружен')

        request = 'window.data = wax.api.transact({' \
                  'actions:' \
                  '[{account: "m.federation", name: "mine", authorization: [{actor: {account}, permission: "active"}], ' \
                  'data: ' \
                  '{miner: {account}, nonce: {nonce},}}]}, ' \
                  '{blocksBehind: 3, expireSeconds: 30});' \
                  ''.replace('{account}', f'"{account_name}"').replace('{nonce}', f'"{nonce}"')

        self.driver.execute_script(request)

        self.handle_approve_window()

        return self.driver.execute_script('return window.data;')

    def handle_approve_window(self):
        self.controller.wait_windows_amount(2)

        self.controller.change_window(1)

        self.controller.wait_page_load()

        self.controller.solve_captcha_by_extension()

        self.controller.click_approve_button()

        self.controller.change_window(0)
