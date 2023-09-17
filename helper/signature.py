import web3
import pydash as py_
from config import Config
from lib import dt_utcnow
from eth_utils import to_int


class SignatureHelper:
    @staticmethod
    def generate_buy_nft_signature(data):
        _web3 = web3.Web3()

        _chain_id = py_.get(data, 'chain_id')
        _order_id = py_.get(data, 'order_id')
        _to_address = _web3.to_checksum_address(py_.get(data, 'to_address'))
        _nft_address = _web3.to_checksum_address(py_.get(data, 'nft_address'))
        _currency_address = _web3.to_checksum_address(py_.get(data, 'currency_address'))
        _nft_id = to_int(text=py_.get(data, 'token_id'))

        _price = py_.get(data, 'price')
        _owner_address = _web3.to_checksum_address(py_.get(data, 'owner_address'))
        _currency_decimal = py_.get(data, 'currency_decimal')
        _standard = py_.get(data, 'standard')

        _price = _web3.to_wei(str(_price), py_.get(Config.BLOCKCHAIN_DECIMALS, str(_currency_decimal), 'ether'))

        _allAmounts = [_price]

        _from_to = [_owner_address, _to_address]
        _nft_and_token = [_nft_address, _currency_address]
        _id_and_amount = [_nft_id, _standard]
        
        # FIXME: current is only have seller does not have any other
        _additional_token_receivers = []
        
        # FIXME: current is only owner get all amount
        _all_amounts = [_price]
        
        if Config.MARKETPLACE_FEE_TREASURY:
            _additional_token_receivers.append(Config.MARKETPLACE_FEE_TREASURY)
            _all_amounts = [
                int(_price * (1000 - Config.MARKETPLACE_FEE_PERCENT) / 1000), int(_price * Config.MARKETPLACE_FEE_PERCENT / 1000)
            ]
            
        print(_additional_token_receivers)
        print(_all_amounts)
            
        

        

        _deadline = int((dt_utcnow().timestamp() + Config.SIGNATURE_BUY_NFT_EXPIRE_TIME))

        _type_list = [
            "uint256",
            "uint256",
            "address[2]",
            "address[2]",
            "uint256[2]",
            "address[]",
            "uint256[]",
            "uint256",
        ]

        _value_list = [
            _chain_id,
            _order_id,
            _from_to,
            _nft_and_token,
            _id_and_amount,
            _additional_token_receivers,
            _all_amounts,
            _deadline
        ]

        print(_value_list)

        _message_hash = web3.Web3.solidity_keccak(_type_list, _value_list).hex()
        _msg = web3.Web3.solidity_keccak(
            ["string", "bytes32"],
            ["\x19Ethereum Signed Message:\n32", _message_hash],
        ).hex()
        _signed_message = _web3.eth.account.signHash(
            _msg,
            private_key=Config.AUTH_PRIVATE_KEY
        )
        return {
            'signature': _signed_message.signature.hex(),
            'data': {
                'order_id': py_.to_string(_order_id),
                'from_to': [py_.to_string(x) for x in _from_to],
                'nft_and_token': [py_.to_string(x) for x in _nft_and_token],
                'id_and_amount': [py_.to_string(x) for x in _id_and_amount],
                'additional_token_receivers': [py_.to_string(x) for x in _additional_token_receivers],
                'all_amounts': [py_.to_string(x) for x in _all_amounts],
            },
            'deadline': _deadline
        }
