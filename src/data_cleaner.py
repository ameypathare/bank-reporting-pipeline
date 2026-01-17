import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import re


class DataCleaner:
    """Cleans and validates bank data with comprehensive text cleaning"""
    
    def __init__(self):
        self.validation_errors = []
        self.cleaned_data = {}
        
    def clean_and_validate(self, bank_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Clean and validate bank data
        Returns: (cleaned_data, error_messages)
        """
        self.validation_errors = []
        self.cleaned_data = {}
        
        try:
            # 1. Validate required data exists
            self._validate_required_data(bank_data)
            
            if self.validation_errors:
                return {}, self.validation_errors
            
            # 2. Clean and transform each dataset
            if 'bank_data' in bank_data:
                self._clean_bank_data(bank_data['bank_data'])
            
            if 'capital_data' in bank_data:
                self._clean_capital_data(bank_data['capital_data'])
            
            if 'liquidity_data' in bank_data:
                self._clean_liquidity_data(bank_data['liquidity_data'])
            
            if 'credit_data' in bank_data:
                self._clean_credit_data(bank_data['credit_data'])
            
            # 3. Calculate derived fields
            self._calculate_derived_fields()
            
            # 4. Perform cross-validation
            self._cross_validate()
            
            return self.cleaned_data, self.validation_errors
            
        except Exception as e:
            self.validation_errors.append(f"Cleaning error: {str(e)}")
            return {}, self.validation_errors
    

    @staticmethod
    def clean_text(text: Any, options: Dict = None) -> str:
        """
        Comprehensive text cleaning utility
        
        Args:
            text: Input text to clean
            options: Dictionary of cleaning options
                - strip: Remove leading/trailing whitespace (default: True)
                - upper: Convert to uppercase (default: False)
                - lower: Convert to lowercase (default: False)
                - title: Convert to title case (default: False)
                - remove_extra_spaces: Replace multiple spaces with single space (default: True)
                - remove_special_chars: Remove special characters (default: False)
                - remove_numbers: Remove numeric characters (default: False)
                - remove_newlines: Remove newline characters (default: True)
                - ascii_only: Keep only ASCII characters (default: False)
                - max_length: Truncate to max length (default: None)
        
        Returns:
            Cleaned text string
        """
        if text is None or pd.isna(text):
            return ''
        
        # Convert to string
        text = str(text)
        
        # Default options
        opts = {
            'strip': True,
            'upper': False,
            'lower': False,
            'title': False,
            'remove_extra_spaces': True,
            'remove_special_chars': False,
            'remove_numbers': False,
            'remove_newlines': True,
            'ascii_only': False,
            'max_length': None
        }
        
        # Update with provided options
        if options:
            opts.update(options)
        
        # Remove newlines and tabs
        if opts['remove_newlines']:
            text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Remove extra whitespace
        if opts['remove_extra_spaces']:
            text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        if opts['remove_special_chars']:
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Remove numbers
        if opts['remove_numbers']:
            text = re.sub(r'\d+', '', text)
        
        # ASCII only
        if opts['ascii_only']:
            text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Case conversion
        if opts['upper']:
            text = text.upper()
        elif opts['lower']:
            text = text.lower()
        elif opts['title']:
            text = text.title()
        
        # Strip whitespace
        if opts['strip']:
            text = text.strip()
        
        # Truncate to max length
        if opts['max_length'] and len(text) > opts['max_length']:
            text = text[:opts['max_length']].strip()
        
        return text
    
    @staticmethod
    def clean_bank_id(bank_id: Any) -> str:
        """Clean and validate bank ID format"""
        text = DataCleaner.clean_text(bank_id, {'upper': True, 'strip': True})
        # Remove any spaces or special chars except dash
        text = re.sub(r'[^A-Z0-9-]', '', text)
        return text
    
    @staticmethod
    def clean_currency_code(currency: Any) -> str:
        """Clean currency code (3 letter uppercase)"""
        text = DataCleaner.clean_text(currency, {
            'upper': True,
            'strip': True,
            'remove_numbers': True,
            'remove_special_chars': True
        })
        return text[:3] if len(text) >= 3 else text
    
    @staticmethod
    def clean_email(email: Any) -> str:
        """Clean email address"""
        text = DataCleaner.clean_text(email, {
            'lower': True,
            'strip': True,
            'remove_extra_spaces': True
        })
        # Remove spaces from email
        text = text.replace(' ', '')
        return text
    
    @staticmethod
    def clean_name(name: Any) -> str:
        """Clean person or bank name"""
        text = DataCleaner.clean_text(name, {
            'strip': True,
            'remove_extra_spaces': True,
            'ascii_only': True
        })
        # Remove leading/trailing special characters
        text = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', text)
        return text
    
    @staticmethod
    def clean_date_string(date: Any) -> str:
        """Clean date string"""
        text = DataCleaner.clean_text(date, {
            'strip': True,
            'remove_extra_spaces': True
        })
        # Keep only numbers and common date separators
        text = re.sub(r'[^0-9/-]', '', text)
        return text
    
    @staticmethod
    def clean_enum_value(value: Any, valid_values: List[str]) -> str:
        """Clean and validate enum value"""
        text = DataCleaner.clean_text(value, {
            'upper': True,
            'strip': True,
            'remove_special_chars': True
        })
        # Check if matches any valid value
        for valid in valid_values:
            if text == valid.upper():
                return valid
        return text
    
    @staticmethod
    def clean_numeric(value: Any, default: float = 0.0) -> float:
        """Clean numeric value"""
        if value is None or pd.isna(value):
            return default
        
        # If already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        # Clean string representation
        text = str(value).strip()
        # Remove currency symbols and commas
        text = re.sub(r'[$,€£¥]', '', text)
        
        try:
            return float(text)
        except (ValueError, TypeError):
            return default
    

    def _validate_required_data(self, bank_data: Dict):
        """Check if all required data is present"""
        required_datasets = ['bank_data', 'capital_data', 'liquidity_data', 'credit_data']
        
        for dataset in required_datasets:
            if dataset not in bank_data:
                self.validation_errors.append(f"Missing required dataset: {dataset}")
        
        # Check for empty values in bank_data
        if 'bank_data' in bank_data:
            bank_info = bank_data['bank_data']
            required_fields = ['bank_id', 'bank_name', 'report_date', 'currency']
            
            for field in required_fields:
                value = bank_info.get(field)
                if pd.isna(value) or value == '' or value is None:
                    self.validation_errors.append(f"Empty {field} in bank data")
    
    def _clean_bank_data(self, bank_info: Dict):
        """Clean bank information data with text cleaning"""
        cleaned = {}
        
        # Bank ID - clean and validate
        bank_id = self.clean_bank_id(bank_info.get('bank_id', ''))
        if not re.match(r'^[A-Z]{2}-[A-Z]{4}-\d{5}$', bank_id):
            self.validation_errors.append(f"Invalid bank ID format: {bank_id}")
        cleaned['bank_id'] = bank_id
        
        # Bank name - clean text
        bank_name = self.clean_name(bank_info.get('bank_name', ''))
        if len(bank_name) < 2:
            self.validation_errors.append(f"Bank name too short: {bank_name}")
        cleaned['bank_name'] = bank_name
        
        # Dates - clean date strings
        for date_field in ['report_date', 'reporting_period_start', 'reporting_period_end']:
            date_val = bank_info.get(date_field)
            if date_val:
                cleaned[date_field] = self.clean_date_string(date_val)
        
        # Currency - clean and validate
        currency = self.clean_currency_code(bank_info.get('currency', ''))
        if len(currency) != 3 or not currency.isalpha():
            self.validation_errors.append(f"Invalid currency code: {currency}")
        cleaned['currency'] = currency
        
        # Report type - clean enum value
        valid_types = ['QUARTERLY', 'ANNUAL', 'ADHOC', 'MONTHLY']
        report_type = self.clean_enum_value(bank_info.get('report_type', ''), valid_types)
        if report_type not in valid_types:
            self.validation_errors.append(f"Invalid report type: {report_type}")
        cleaned['report_type'] = report_type
        
        # Contact info - clean email and name
        cleaned['contact_email'] = self.clean_email(bank_info.get('contact_email', ''))
        cleaned['contact_name'] = self.clean_name(bank_info.get('contact_name', ''))
        
        self.cleaned_data['bank_info'] = cleaned
    
    def _clean_capital_data(self, capital_info: Dict):
        """Clean capital adequacy data with numeric cleaning"""
        cleaned = {}
        
        # Monetary amounts - clean numeric values
        amount_fields = ['tier1_capital', 'tier2_capital', 'risk_weighted_assets']
        
        for field in amount_fields:
            value = self.clean_numeric(capital_info.get(field), default=0.0)
            if value <= 0:
                self.validation_errors.append(f"{field} must be positive: {value}")
            cleaned[field] = value
        
        # Minimum requirement
        min_req = self.clean_numeric(capital_info.get('minimum_requirement'), default=10.5)
        if min_req < 8.0 or min_req > 15.0:
            self.validation_errors.append(f"Minimum requirement out of range: {min_req}")
        cleaned['minimum_requirement'] = min_req
        
        self.cleaned_data['capital_info'] = cleaned
    
    def _clean_liquidity_data(self, liquidity_info: Dict):
        """Clean liquidity metrics data with numeric cleaning"""
        cleaned = {}
        
        # LCR ratio
        lcr_ratio = self.clean_numeric(liquidity_info.get('lcr_ratio'), default=0.0)
        if lcr_ratio < 80.0 or lcr_ratio > 200.0:
            self.validation_errors.append(f"LCR ratio out of range: {lcr_ratio}")
        cleaned['lcr_ratio'] = lcr_ratio
        
        # NSFR ratio
        nsfr_ratio = self.clean_numeric(liquidity_info.get('nsfr_ratio'), default=0.0)
        if nsfr_ratio < 90.0 or nsfr_ratio > 150.0:
            self.validation_errors.append(f"NSFR ratio out of range: {nsfr_ratio}")
        cleaned['nsfr_ratio'] = nsfr_ratio
        
        # HQLA
        hqla = self.clean_numeric(liquidity_info.get('hqla_amount'), default=0.0)
        if hqla <= 0:
            self.validation_errors.append(f"HQLA must be positive: {hqla}")
        cleaned['hqla_amount'] = hqla
        
        # Net cash outflows
        net_cash = self.clean_numeric(liquidity_info.get('net_cash_outflows'), default=0.0)
        if net_cash <= 0:
            self.validation_errors.append(f"Net cash outflows must be positive: {net_cash}")
        cleaned['net_cash_outflows'] = net_cash
        
        self.cleaned_data['liquidity_info'] = cleaned
    
    def _clean_credit_data(self, credit_info: Dict):
        """Clean credit exposure data with numeric cleaning"""
        cleaned = {}
        
        # Exposure amounts
        exposure_fields = ['corporate_exposure', 'retail_exposure', 'sovereign_exposure']
        for field in exposure_fields:
            value = self.clean_numeric(credit_info.get(field), default=0.0)
            if value < 0:
                self.validation_errors.append(f"{field} cannot be negative: {value}")
            cleaned[field] = value
        
        # Risk weights
        rw_fields = ['corporate_rw', 'retail_rw', 'sovereign_rw']
        for field in rw_fields:
            value = self.clean_numeric(credit_info.get(field), default=0.0)
            if value < 0 or value > 150:
                self.validation_errors.append(f"{field} out of range (0-150%): {value}")
            cleaned[field] = value
        
        # Impaired loans
        impaired_fields = ['corporate_impaired', 'retail_impaired', 'sovereign_impaired']
        for field in impaired_fields:
            value = self.clean_numeric(credit_info.get(field), default=0.0)
            if value < 0:
                self.validation_errors.append(f"{field} cannot be negative: {value}")
            cleaned[field] = value
        
        self.cleaned_data['credit_info'] = cleaned


    def _calculate_derived_fields(self):
        """Calculate derived financial metrics"""
        if 'capital_info' in self.cleaned_data:
            cap = self.cleaned_data['capital_info']
            total_capital = cap.get('tier1_capital', 0) + cap.get('tier2_capital', 0)
            rwa = cap.get('risk_weighted_assets', 1)
            
            car_ratio = (total_capital / rwa) * 100 if rwa > 0 else 0
            
            self.cleaned_data['calculated'] = {
                'total_capital': total_capital,
                'car_ratio': round(car_ratio, 2)
            }
        
        if 'credit_info' in self.cleaned_data:
            credit = self.cleaned_data['credit_info']
            total_exposure = (
                credit.get('corporate_exposure', 0) +
                credit.get('retail_exposure', 0) +
                credit.get('sovereign_exposure', 0)
            )
            
            if 'calculated' not in self.cleaned_data:
                self.cleaned_data['calculated'] = {}
            
            self.cleaned_data['calculated']['total_exposure'] = total_exposure
    
    def _cross_validate(self):
        """Cross-validate between different data sections"""
        if 'liquidity_info' in self.cleaned_data:
            liq = self.cleaned_data['liquidity_info']
            calculated_lcr = (liq.get('hqla_amount', 0) / liq.get('net_cash_outflows', 1)) * 100
            
            reported_lcr = liq.get('lcr_ratio', 0)
            diff = abs(calculated_lcr - reported_lcr)
            
            if diff > 5.0:  # Allow 5% tolerance
                self.validation_errors.append(
                    f"LCR validation mismatch: Reported={reported_lcr}%, Calculated={calculated_lcr:.2f}%"
                )


if __name__ == "__main__":
    # Test the data cleaner with messy data
    cleaner = DataCleaner()
    
    print("="*70)
    print("TEXT CLEANING TESTS")
    print("="*70)
    
    # Test text cleaning utilities
    print("\n1. General Text Cleaning:")
    messy_text = "  Hello   World!\n\n  Extra   Spaces  "
    print(f"   Input:  '{messy_text}'")
    print(f"   Output: '{DataCleaner.clean_text(messy_text)}'")
    
    print("\n2. Bank ID Cleaning:")
    messy_id = "us-bank-12345"
    print(f"   Input:  '{messy_id}'")
    print(f"   Output: '{DataCleaner.clean_bank_id(messy_id)}'")
    
    print("\n3. Email Cleaning:")
    messy_email = "  John.Doe@BANK.COM  "
    print(f"   Input:  '{messy_email}'")
    print(f"   Output: '{DataCleaner.clean_email(messy_email)}'")
    
    print("\n4. Numeric Cleaning:")
    messy_number = "$1,234,567.89"
    print(f"   Input:  '{messy_number}'")
    print(f"   Output: {DataCleaner.clean_numeric(messy_number)}")
    
    # Test with messy bank data
    print("\n" + "="*70)
    print("FULL DATA CLEANING TEST")
    print("="*70)
    
    test_data = {
        'bank_data': {
            'bank_id': 'us-bank-12345',  
            'bank_name': '  Test  Bank   Corp  ',  
            'report_date': '2024-12-31',
            'currency': 'usd',  
            'report_type': 'quarterly',  
            'contact_email': '  JOHN@TEST.COM  ',  
            'contact_name': '  John   Smith  '  
        },
        'capital_data': {
            'tier1_capital': '$10,000,000,000.00',  
            'tier2_capital': 2500000000.00,
            'risk_weighted_assets': 100000000000.00,
            'minimum_requirement': 10.5
        },
        'liquidity_data': {
            'lcr_ratio': 125.50,
            'hqla_amount': 50000000000.00,
            'net_cash_outflows': 40000000000.00,
            'nsfr_ratio': 110.25
        },
        'credit_data': {
            'corporate_exposure': 80000000000.00,
            'corporate_rw': 65.00,
            'corporate_impaired': 1000000000.00,
            'retail_exposure': 50000000000.00,
            'retail_rw': 45.00,
            'retail_impaired': 500000000.00,
            'sovereign_exposure': 20000000000.00,
            'sovereign_rw': 20.00,
            'sovereign_impaired': 0.00
        }
    }
    
    cleaned_data, errors = cleaner.clean_and_validate(test_data)
    
    if errors:
        print("\n  Validation Warnings:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("\n All validations passed!")
    
    print("\n Cleaned Data:")
    print(f"\nBank Info:")
    for key, value in cleaned_data.get('bank_info', {}).items():
        print(f"   {key}: '{value}'")
    
    print(f"\nCapital Info:")
    for key, value in cleaned_data.get('capital_info', {}).items():
        print(f"   {key}: {value}")