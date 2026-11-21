from inventory.stock import StockService


def test_reserve_ok():
    stock = StockService()
    assert stock.reserve("sku-1", 5) == 35
