# tests/test_geocoding.py
"""Tests for geocoding service with caching and rate limiting."""

import pytest
import time
from modules.geolocation import (
    safe_geocode,
    add_distance,
    LRUCache,
    RateLimiter,
    _hash_address
)
import pandas as pd


class TestLRUCache:
    """Test LRU cache implementation."""
    
    def test_cache_basic(self):
        cache = LRUCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None
    
    def test_cache_eviction(self):
        cache = LRUCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_lru_order(self):
        cache = LRUCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # Access key1, making it most recent
        cache.set("key3", "value3")  # Should evict key2, not key1
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"


class TestRateLimiter:
    """Test rate limiter implementation."""
    
    def test_rate_limit_basic(self):
        limiter = RateLimiter(min_interval=0.1)
        
        start = time.time()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start
        
        # Should wait at least min_interval between calls
        assert elapsed >= 0.1
    
    def test_exponential_backoff(self):
        limiter = RateLimiter(min_interval=0.05)
        # First call to set last_request_time
        limiter.wait()
        # Record failures
        limiter.record_failure()
        limiter.record_failure()
        
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        
        # Should apply exponential backoff (2^2 * 0.05 = 0.2)
        assert elapsed >= 0.15  # Allow some tolerance
    
    def test_reset_on_success(self):
        limiter = RateLimiter(min_interval=0.05)
        limiter.record_failure()
        limiter.record_failure()
        limiter.record_success()  # Reset counter
        
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        
        # Should not apply exponential backoff after reset
        assert elapsed < 0.2


class TestAddressHashing:
    """Test privacy-focused address hashing."""
    
    def test_hash_consistency(self):
        addr = "123 Main St, Chicago, IL"
        hash1 = _hash_address(addr)
        hash2 = _hash_address(addr)
        assert hash1 == hash2
    
    def test_hash_uniqueness(self):
        hash1 = _hash_address("123 Main St")
        hash2 = _hash_address("456 Oak Ave")
        assert hash1 != hash2
    
    def test_hash_length(self):
        hash_val = _hash_address("test address")
        assert len(hash_val) == 12  # First 12 chars of SHA256


class TestSafeGeocode:
    """Test enhanced geocoding function."""
    
    def test_lat_lon_mode(self):
        """Test direct lat/lon coordinates."""
        result = safe_geocode(lat=41.8781, lon=-87.6298)
        assert result is not None
        assert abs(result.latitude - 41.8781) < 0.001
        assert abs(result.longitude - (-87.6298)) < 0.001
    
    def test_invalid_lat_lon(self):
        """Test invalid lat/lon handling."""
        result = safe_geocode(lat="invalid", lon="invalid")
        assert result is None
    
    def test_empty_address(self):
        """Test empty address handling."""
        result = safe_geocode(address="")
        assert result is None
    
    def test_none_inputs(self):
        """Test all None inputs."""
        result = safe_geocode()
        assert result is None
    
    # Note: Skip actual geocoding tests to avoid hitting external API
    # In real tests, use mocking for external API calls


class TestDistanceCalculation:
    """Test distance computation."""
    
    def test_add_distance(self):
        df = pd.DataFrame({
            'hospital_name': ['A', 'B', 'C'],
            'lat': [41.8781, 42.0, None],
            'lon': [-87.6298, -87.5, None]
        })
        
        user_lat, user_lon = 41.8781, -87.6298
        result = add_distance(df, user_lat, user_lon)
        
        assert 'distance_km' in result.columns
        assert result.loc[0, 'distance_km'] < 1  # Same location
        assert result.loc[1, 'distance_km'] > 0
        assert result.loc[2, 'distance_km'] == float('inf')  # Missing coords
    
    def test_distance_calculation(self):
        """Test actual distance between known points."""
        df = pd.DataFrame({
            'lat': [40.7128],  # NYC
            'lon': [-74.0060]
        })
        
        # Chicago coordinates
        user_lat, user_lon = 41.8781, -87.6298
        result = add_distance(df, user_lat, user_lon)
        
        # NYC to Chicago is roughly 1150 km
        assert 1100 < result.loc[0, 'distance_km'] < 1200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
