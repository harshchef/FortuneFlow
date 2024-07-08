import requests

def get_exchange_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/c34eb65e8181fda34335eed1/latest/{base_currency}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        conversion_rate = data['conversion_rates'].get(target_currency)
        return conversion_rate
    else:
        return None

# Example usage:
base_currency = 'USD'
target_currency = 'EUR'
conversion_rate = get_exchange_rate(base_currency, target_currency)

if conversion_rate is not None:
    print(f"1 {base_currency} = {conversion_rate} {target_currency}")
else:
    print(f"Failed to retrieve exchange rate for {base_currency} to {target_currency}")
