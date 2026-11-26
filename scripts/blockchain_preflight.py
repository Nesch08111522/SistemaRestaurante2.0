"""Comprobación de solo lectura, sin imprimir credenciales ni enviar transacciones."""
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

def main():
    try:
        w = Web3(Web3.HTTPProvider(os.environ['CHAIN_RPC_URL'], request_kwargs={'timeout': 15}))
        if not w.is_connected():
            print('RPC conectado: False')
            return 1
        print('RPC conectado: True')
        chain_ok = w.eth.chain_id == 80002 and int(os.environ['CHAIN_ID']) == 80002
        print('Red Amoy correcta:', chain_ok)
        contract = Web3.to_checksum_address(os.environ['ANCHOR_CONTRACT'])
        code_ok = bool(w.eth.get_code(contract))
        print('Contrato con código:', code_ok)
        account = w.eth.account.from_key(os.environ['ANCHOR_PRIVATE_KEY'])
        funded = w.eth.get_balance(account.address) > 0
        print('Billetera con saldo para gas:', funded)
        return 0 if chain_ok and code_ok and funded else 1
    except Exception:
        print('Error: no se pudo completar la verificación RPC; revisa la configuración y conectividad.')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
