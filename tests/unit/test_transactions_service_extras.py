"""Additional unit tests for transactions service to improve coverage."""

from banking_api.services.transactions_service import TransactionsService
from banking_api.models.transaction import TransactionSearch


def test_transactions_service_delete_transaction(load_sample_data: None) -> None:
    """Test TransactionsService.delete_transaction method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    # Test deleting existing transaction
    assert service.delete_transaction("tx_0000000") is True
    # Test deleting non-existing transaction
    assert service.delete_transaction("non_existent_id") is False


def test_transactions_service_get_recent_transactions(
    load_sample_data: None
) -> None:
    """Test TransactionsService.get_recent_transactions method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    recent = service.get_recent_transactions(n=5)
    assert len(recent) <= 5
    # Verify date ordering if possible, or just length/content


def test_transactions_service_get_transactions_to_merchant(
    load_sample_data: None
) -> None:
    """Test TransactionsService.get_transactions_to_merchant method.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()
    # Find a valid merchant_id from data
    # In sample data, we might not know one, but we can search for one first
    all_tx = service.get_transactions(limit=1).transactions
    if all_tx:
        merchant_id = all_tx[0].merchant_id
        # valid merchant
        txs = service.get_transactions_to_merchant(merchant_id)
        assert isinstance(txs, list)

    # invalid merchant
    txs = service.get_transactions_to_merchant(-1)
    assert len(txs) == 0


def test_transactions_service_get_transactions_filters(
    load_sample_data: None
) -> None:
    """Test TransactionsService.get_transactions with various filters.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()

    # Test min/max amount
    result = service.get_transactions(
        min_amount=10.0,
        max_amount=100.0,
        limit=5
    )
    for tx in result.transactions:
        assert 10.0 <= tx.amount <= 100.0

    # Test is_fraud filter
    result = service.get_transactions(is_fraud=0, limit=5)
    for tx in result.transactions:
        assert tx.isFraud == 0

    # Test merchant_state
    # Assuming CA exists or empty
    result = service.get_transactions(merchant_state="CA", limit=5)
    if result.transactions:
        for tx in result.transactions:
            assert tx.merchant_state == "CA"


def test_transactions_service_search_filters(load_sample_data: None) -> None:
    """Test TransactionsService.search_transactions with various criteria.

    Parameters
    ----------
    load_sample_data : None
        Fixture to ensure data is loaded.
    """
    service = TransactionsService()

    # Search by client_id
    criteria = TransactionSearch(client_id=1556)
    result = service.search_transactions(criteria)
    if result.transactions:
        for tx in result.transactions:
            assert tx.client_id == 1556

    # Search by amount range
    criteria = TransactionSearch(amount_range=[10.0, 50.0])
    result = service.search_transactions(criteria)
    for tx in result.transactions:
        assert 10.0 <= tx.amount <= 50.0

    # Search by merchant city
    # Assuming Online exists or empty
    criteria = TransactionSearch(merchant_city="Online")
    result = service.search_transactions(criteria)
    if result.transactions:
        for tx in result.transactions:
            assert tx.merchant_city == "Online"


def test_transactions_service_get_by_id_not_found(
    load_sample_data: None
) -> None:
    """Test get_transaction_by_id with non-existent ID."""
    service = TransactionsService()
    assert service.get_transaction_by_id("non_existent") is None
