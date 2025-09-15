from typing import Tuple
import requests

from rocalert.roc_web_handler import Captcha


class RocApiCaptchaSolver:
    def __init__(self, solve_url: str, report_url: str) -> None:
        self._solve_url = solve_url
        self._report_url = report_url
        self._hash_requestid_map = {}
        
    def solve(self, captcha: Captcha) -> Tuple[str, float]:
        """
        Solves a captcha using the RocApiSolver
        Args:
            captcha (Captcha): The captcha to solve

        Raises:
            Exception: Failed to solve captcha

        Returns:
            Captcha: Tuple of predicted answer and confidence
        """
        files = {
            'image': ('captcha.png', captcha.img, 'image/png')
        }
        data = {
            'captcha_hash': captcha.hash
        }
        
        response = requests.post(self._solve_url, files=files, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to solve captcha: {response.text}")
        
        resp_json = response.json()
        
        self._hash_requestid_map[captcha.hash] = resp_json['request_id']
        
        return (resp_json['predicted_answer'], resp_json['confidence'])
        
    def report(self, captcha_hash: str, is_correct: bool) -> None:
        """
        Reports a captcha to the RocApiSolver

        Args:
            captcha_hash (str): The hash of the captcha
            is_correct (bool): Whether the captcha was correct
        """
        data = {
            'request_id': self._hash_requestid_map[captcha_hash],
            'is_correct': str(is_correct).lower(),
        } 
        
        response = requests.post(self._report_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        if response.status_code != 200:
            print(f"Failed to report captcha: {response.text}")