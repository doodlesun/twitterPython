import unittest
from filtering import filterForTokens
from datetime import datetime
from unittest.mock import Mock, patch, call

class FilteringTest(unittest.TestCase):

    @patch('filtering.requests.get')
    def test_should_filter_token_from_text_and_return_filtered_dict(self, mock_get):
        twitterData = {
            "data": [
                {
                    "id": "1376920611323314188",
                    "text": "Check out $POL token gonna go 10x",
                    "author_id": "1078362309687472134"
                },
            ]
        }
        mock_get.status_code.return_value = 200
        allCoinsCall = Mock()
        allCoinsCall.json = lambda: [
            {
                'id': 'id',
                'symbol': 'pol',
                'name': 'Polli',
            }
        ]
        currentPriceCall = Mock()
        currentPriceCall.json = lambda: {
                'id': {
                    'usd': 1000
        }}
        sevenPriceCall = Mock()
        sevenPriceCall.json = lambda: {
                'market_data': {
                    'current_price': {
                        'usd': 500
                    }
                }
        }
        mock_get.side_effect = [allCoinsCall, currentPriceCall, sevenPriceCall]
        result = filterForTokens(twitterData['data'])
        assert twitterData['data'][0].items() <= result[0].items()
        self.assertEqual(result[0]['token_prices']['$POL']['usd'], 1000)
        self.assertIn(datetime.now().strftime('%Y-%m-%d'),result[0]['token_prices']['$POL']['time'] )
        self.assertEqual(result[0]['token_prices']['$POL']['seven_delta'], '100.00%')

if __name__ == '__main__':
    unittest.main()
