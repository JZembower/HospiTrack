# tests/test_sorting.py
"""Tests for sorting logic and complaint-adjusted quality."""

import pytest
import pandas as pd
import numpy as np
from modules.sorting_logic import (
    parse_mortality,
    prepare_mortality_sort,
    apply_complaint_adjustment
)


class TestMortalityParsing:
    """Test mortality text parsing."""
    
    def test_parse_better(self):
        result = parse_mortality("46% better")
        assert result == ("better", 46)
    
    def test_parse_worse(self):
        result = parse_mortality("12% worse")
        assert result == ("worse", -12)
    
    def test_parse_not_used(self):
        result = parse_mortality("not used")
        assert result[0] == "not used"
        assert np.isnan(result[1])
    
    def test_parse_invalid(self):
        result = parse_mortality(None)
        assert result[0] == "not used"
        assert np.isnan(result[1])


class TestMortalitySorting:
    """Test mortality sort preparation."""
    
    def test_prepare_mortality_sort(self):
        df = pd.DataFrame({
            'hospital_name': ['A', 'B', 'C'],
            'detail_mortality_overall_text': ['30% better', '10% worse', 'not used']
        })
        
        result = prepare_mortality_sort(df)
        
        assert 'mortality_type' in result.columns
        assert 'mortality_sort_value' in result.columns
        assert 'mortality_order' in result.columns
        
        # Check types
        assert result.loc[0, 'mortality_type'] == 'better'
        assert result.loc[1, 'mortality_type'] == 'worse'
        assert result.loc[2, 'mortality_type'] == 'not used'
        
        # Check ordering (better=0, worse=1, not used=2)
        assert result.loc[0, 'mortality_order'] == 0
        assert result.loc[1, 'mortality_order'] == 1
        assert result.loc[2, 'mortality_order'] == 2


class TestComplaintAdjustment:
    """Test complaint-based quality adjustment."""
    
    def test_chest_pain_adjustment(self):
        df = pd.DataFrame({
            'hospital_name': ['A', 'B'],
            'total_quality_points': [100, 200],
            'adj_total_heartattack': [150, 250]
        })
        
        result, label = apply_complaint_adjustment(df, 'Chest Pain')
        
        assert 'adjusted_quality_points' in result.columns
        assert result.loc[0, 'adjusted_quality_points'] == 150
        assert result.loc[1, 'adjusted_quality_points'] == 250
        assert 'Chest Pain' in label
    
    def test_stroke_adjustment(self):
        df = pd.DataFrame({
            'hospital_name': ['A', 'B'],
            'total_quality_points': [100, 200],
            'adj_total_stroke': [120, 180]
        })
        
        result, label = apply_complaint_adjustment(df, 'Stroke')
        
        assert result.loc[0, 'adjusted_quality_points'] == 120
        assert result.loc[1, 'adjusted_quality_points'] == 180
    
    def test_overall_adjustment(self):
        df = pd.DataFrame({
            'hospital_name': ['A', 'B'],
            'total_quality_points': [100, 200]
        })
        
        result, label = apply_complaint_adjustment(df, 'Overall')
        
        assert result.loc[0, 'adjusted_quality_points'] == 100
        assert result.loc[1, 'adjusted_quality_points'] == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
