from loguru import logger
import requests
import random
import time
import csv

SHUFFLE_ACCOUNTS = True
SLEEP_START = 1
SLEEP_END = 5

def check_nodes(id, auth_token, proxy):
    logger.info(f'{id} : start checking nodes : {proxy}')
    try:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en,en-GB;q=0.9,en-US;q=0.8',
            'authorization': auth_token,
            'origin': 'https://testnet.openledger.xyz',
            'priority': 'u=1, i',
            'referer': 'https://testnet.openledger.xyz/',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }

        response = requests.get('https://apitn.openledger.xyz/api/v1/users/workers', headers=headers, proxies={'http': proxy, 'https': proxy})
        data = response.json()['data']

        stats = {}
        for node in data:
            stats[node['identity']] = node['is_awake']

        with open('data/openledger_stats.txt', 'a', encoding='utf-8') as file:
            file.write(f'{id}\n')

        row = [id]

        count = 0
        for machine_id, is_awake in stats.items():
            row.extend([machine_id, is_awake])
            if is_awake == True:
                count += 1

        row.extend([count])
        with open('data/openledger_stats.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(row)

        logger.success(f'{id} : running {count} nodes')
    except Exception as ex:
        logger.error(f'{id} : You should probably stop the code and think about whats wrong with you or proxy or code...\nThe error is {ex}')

def menu():
    options = ["Check nodes (continue)", "Check all accs again (clean stats)"]
    for i, option in enumerate(options, start=1):
        print(f'[{i}] {option}')

    selected = int(input('Enter process ( 1 | 2 ): '))
    if selected == 1:
        logger.info(f'Starting the script...')
        openledger_nodes()
    elif selected == 2:
        with open('data/openledger_stats.txt', 'w') as file:
            file.write('')
        with open('data/openledger_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'machine_id', 'is_awake'])
        logger.info(f'Starting with cleaned data/openledger_stats.txt and data/openledger_stats.csv')
        openledger_nodes()
    else:
        print('You are bad boy. Won\'t work with you...')

def openledger_nodes():
    with open('data/openledger_tokens.txt', 'r', encoding='utf-8') as file:
        tokens = [row.strip() for row in file.readlines()]

    with open('data/openledger-proxies.txt', 'r', encoding='utf-8') as file:
        proxies = [row.strip() for row in file.readlines()]

    while True:
        with open('data/openledger_stats.txt', 'r', encoding='utf-8') as file:
            completed_accounts = [row.strip() for row in file.readlines()]

        accounts = {id: [token, proxies[id-1]] for id, token in enumerate(tokens, start=1) if str(id) not in completed_accounts}
        if SHUFFLE_ACCOUNTS:
            accounts = dict(random.sample(list(accounts.items()), len(accounts)))

        if len(accounts) == 0:
            logger.info('Finishing...')
            break
        else:
            logger.info(f'Processing {len(accounts)} accounts')

        for id, value in accounts.items():
            check_nodes(id, value[0], value[1])
            time.sleep(random.randint(SLEEP_START, SLEEP_END))

if __name__ == '__main__':
    menu()