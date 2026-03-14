import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):

	def setUp(self):
		self.service = PricingService()

	#cents
	def test_subtotal_single_item(self):
		items = [CartItem("spinner", 500, 2)]
		self.assertEqual(self.service.subtotal_cents(items), 1000)
	
	def test_subtotal_invalid(self):
		with self.assertRaises(PricingError):
			self.service.subtotal_cents([CartItem("spinner", 500, 0)])

	def test_subtotal_negative_price(self):
		with self.assertRaises(PricingError):
			self.service.subtotal_cents([CartItem("spinner", -100, 1)])
	
	def test_subtotal_empty(self):
		self.assertEqual(self.service.subtotal_cents([]), 0)
	

	#cupones

	def test_cupon_save10(self):
		self.assertEqual(self.service.apply_coupon(9000, "SAVE10"), 8100)
	
	def test_cupon_clp2000(self):
		self.assertEqual(self.service.apply_coupon(5000, "CLP2000"), 3000)
	
	def test_cupon_clp2000_nonegative(self):
		self.assertEqual(self.service.apply_coupon(1500, "CLP2000"), 0)
	
	def test_cupon_none(self):
		self.assertEqual(self.service.apply_coupon(5000, None), 5000)
	
	def test_cupon_white(self):
		self.assertEqual(self.service.apply_coupon(5000, "  "), 5000)

	def test_cupon_invalid(self):
		with self.assertRaises(PricingError):
			self.service.apply_coupon(5000, "INVALID")

	# tax
	def test_tax_cl(self):
		self.assertEqual(self.service.tax_cents(5000, "CL"), 950)

	def test_tax_eu(self):
		self.assertEqual(self.service.tax_cents(5000, "EU"), 1050)

	def test_tax_us(self):
		self.assertEqual(self.service.tax_cents(5000, "US"), 0)

	def test_tax_invalid(self):
		with self.assertRaises(PricingError):
			self.service.tax_cents(5000, "AA")

	def test_shipping_cl_free(self):
		self.assertEqual(self.service.shipping_cents(20000, "CL"), 0)

	def test_shipping_cl_paid(self):
		self.assertEqual(self.service.shipping_cents(15000, "CL"), 2500)

	def test_shipping_us(self):
		self.assertEqual(self.service.shipping_cents(5000, "US"), 5000)
	
	def test_shipping_eu(self):
		self.assertEqual(self.service.shipping_cents(10000, "EU"), 5000)

	def test_shipping_invalid(self):
		with self.assertRaises(PricingError):
			self.service.shipping_cents(5000, "AA")
	
	def test_service_basic(self):
		items = [CartItem("spinner", 10000, 2)]
		self.assertEqual(self.service.total_cents(items, None, "CL"), 23800)