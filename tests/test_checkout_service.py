import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	def setUp(self):
		self.payment = Mock()
		self.email = Mock()
		self.fraud = Mock()
		self.repo = Mock()
		self.pricing = PricingService()
		self.service = CheckoutService(self.payment, self.email, self.fraud, self.repo)
		self.items = [CartItem("spinner", 500, 2)]

	def test_invalid_empty_user(self):
		self.assertEqual(self.service.checkout("", self.items, "token", "CL"), "INVALID_USER")

	def test_invalid_user_whitespace(self):
		self.assertEqual(self.service.checkout("   ", self.items, "token", "CL"), "INVALID_USER")
	
	def test_invalid_cart(self):
		result = self.service.checkout("user1", [CartItem("spinner", 500, 0)], "token", "CL")
		self.assertTrue(result.startswith("INVALID_CART:"))

	def test_reject_fraud(self):
		self.fraud.score.return_value = 100
		self.assertEqual(self.service.checkout("user1", self.items, "token", "CL"), "REJECTED_FRAUD")

	def test_payment_failure(self):
		self.fraud.score.return_value = 2
		self.payment.charge.return_value = ChargeResult(ok=False, charge_id=None, reason="no_funds")
		self.assertEqual(self.service.checkout("user1", self.items, "token", "CL"), "PAYMENT_FAILED:no_funds") 

	def test_successful_checkout(self):
		self.fraud.score.return_value = 2
		charge = ChargeResult(ok=True, charge_id="ch_123", reason=None)
		self.payment.charge.return_value = charge
		result = self.service.checkout("user1", self.items, "token", "CL")
		self.assertTrue(result.startswith("OK:"))
		self.repo.save.assert_called_once()
		self.email.send_receipt.assert_called_once()