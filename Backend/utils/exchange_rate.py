import requests

def get_exchange_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/c34eb65e8181fda34335eed1/latest/{base_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get(target_currency)
    else:
        return None
