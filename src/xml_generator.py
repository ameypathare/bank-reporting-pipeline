import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Dict
import os


class XMLGenerator:
    """Generates XML reports from cleaned bank data"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_xml(self, cleaned_data: Dict, report_date: str = None) -> str:
        """
        Generate XML report from cleaned data
        
        Args:
            cleaned_data: Dictionary containing bank_info, capital_info, liquidity_info, credit_info, calculated
            report_date: Report date in YYYY-MM-DD format (optional, uses current date if not provided)
        
        Returns:
            Pretty-printed XML string
        """
        if not cleaned_data:
            raise ValueError("No cleaned data provided for XML generation")
        
        # Use provided report date or current date
        effective_date = report_date or datetime.now().strftime("%Y-%m-%d")
        
        # Extract data sections
        bank_info = cleaned_data.get('bank_info', {})
        capital_info = cleaned_data.get('capital_info', {})
        liquidity_info = cleaned_data.get('liquidity_info', {})
        credit_info = cleaned_data.get('credit_info', {})
        calculated = cleaned_data.get('calculated', {})
        
        # Create root element
        root = ET.Element("BankRegulatoryReport")
        root.set("reportDate", effective_date)
        root.set("bankId", bank_info.get('bank_id', 'UNKNOWN'))
        
        # Build XML sections
        root.append(self._create_report_header(bank_info))
        root.append(self._create_capital_section(capital_info, calculated))
        root.append(self._create_liquidity_section(liquidity_info))
        root.append(self._create_credit_section(credit_info, calculated))
        
        # Convert to pretty XML string
        xml_str = ET.tostring(root, encoding='unicode')
        return self._prettify_xml(xml_str)
    
    def _create_report_header(self, bank_info: Dict) -> ET.Element:
        """Create ReportHeader section"""
        header = ET.Element("ReportHeader")
        
        ET.SubElement(header, "BankName").text = bank_info.get('bank_name', 'Unknown Bank')
        
        # Reporting period
        period = ET.SubElement(header, "ReportingPeriod")
        ET.SubElement(period, "StartDate").text = bank_info.get('reporting_period_start', '')
        ET.SubElement(period, "EndDate").text = bank_info.get('reporting_period_end', '')
        
        ET.SubElement(header, "Currency").text = bank_info.get('currency', 'USD')
        ET.SubElement(header, "ReportType").text = bank_info.get('report_type', 'QUARTERLY')
        
        # Add contact info as XML comment
        contact_name = bank_info.get('contact_name', 'N/A')
        contact_email = bank_info.get('contact_email', 'N/A')
        header.append(ET.Comment(f"Contact: {contact_name} - {contact_email}"))
        
        return header
    
    def _create_capital_section(self, capital_info: Dict, calculated: Dict) -> ET.Element:
        """Create CapitalAdequacy section"""
        capital = ET.Element("CapitalAdequacy")
        
        # Add generation timestamp as comment
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        capital.append(ET.Comment(f"Generated at {timestamp}"))
        
        # Capital amounts
        ET.SubElement(capital, "Tier1Capital").text = f"{capital_info.get('tier1_capital', 0):.2f}"
        ET.SubElement(capital, "Tier2Capital").text = f"{capital_info.get('tier2_capital', 0):.2f}"
        ET.SubElement(capital, "TotalCapital").text = f"{calculated.get('total_capital', 0):.2f}"
        ET.SubElement(capital, "RiskWeightedAssets").text = f"{capital_info.get('risk_weighted_assets', 0):.2f}"
        
        # CAR ratio and requirements
        car_ratio = calculated.get('car_ratio', 0)
        ET.SubElement(capital, "CAR").text = f"{car_ratio:.2f}"
        ET.SubElement(capital, "MinimumRequirement").text = f"{capital_info.get('minimum_requirement', 10.5):.2f}"
        
        # Compliance status
        min_req = capital_info.get('minimum_requirement', 10.5)
        status = "COMPLIANT" if car_ratio >= min_req else "NON-COMPLIANT"
        ET.SubElement(capital, "ComplianceStatus").text = status
        
        return capital
    
    def _create_liquidity_section(self, liquidity_info: Dict) -> ET.Element:
        """Create LiquidityMetrics section"""
        liquidity = ET.Element("LiquidityMetrics")
        
        # LCR subsection
        lcr = ET.SubElement(liquidity, "LCR")
        ET.SubElement(lcr, "Ratio").text = f"{liquidity_info.get('lcr_ratio', 0):.2f}"
        ET.SubElement(lcr, "HighQualityLiquidAssets").text = f"{liquidity_info.get('hqla_amount', 0):.2f}"
        ET.SubElement(lcr, "NetCashOutflows").text = f"{liquidity_info.get('net_cash_outflows', 0):.2f}"
        
        # NSFR
        ET.SubElement(liquidity, "NSFR").text = f"{liquidity_info.get('nsfr_ratio', 0):.2f}"
        
        # Regulatory thresholds
        thresholds = ET.SubElement(liquidity, "RegulatoryThresholds")
        ET.SubElement(thresholds, "LCR_Minimum").text = "100.00"
        ET.SubElement(thresholds, "NSFR_Minimum").text = "100.00"
        
        return liquidity
    
    def _create_credit_section(self, credit_info: Dict, calculated: Dict) -> ET.Element:
        """Create CreditExposures section"""
        credit = ET.Element("CreditExposures")
        
        ET.SubElement(credit, "TotalExposures").text = f"{calculated.get('total_exposure', 0):.2f}"
        
        portfolio = ET.SubElement(credit, "PortfolioBreakdown")
        
        # Corporate portfolio
        corporate = ET.SubElement(portfolio, "Corporate")
        ET.SubElement(corporate, "ExposureAmount").text = f"{credit_info.get('corporate_exposure', 0):.2f}"
        ET.SubElement(corporate, "RiskWeight").text = f"{credit_info.get('corporate_rw', 0):.2f}"
        
        corp_impaired = credit_info.get('corporate_impaired', 0)
        if corp_impaired > 0:
            ET.SubElement(corporate, "ImpairedLoans").text = f"{corp_impaired:.2f}"
            corp_exposure = credit_info.get('corporate_exposure', 1)
            impairment_rate = (corp_impaired / corp_exposure) * 100 if corp_exposure > 0 else 0
            ET.SubElement(corporate, "ImpairmentRate").text = f"{impairment_rate:.2f}"  
        
        # Retail portfolio
        retail = ET.SubElement(portfolio, "Retail")
        ET.SubElement(retail, "ExposureAmount").text = f"{credit_info.get('retail_exposure', 0):.2f}"
        ET.SubElement(retail, "RiskWeight").text = f"{credit_info.get('retail_rw', 0):.2f}"
        
        retail_impaired = credit_info.get('retail_impaired', 0)
        if retail_impaired > 0:
            ET.SubElement(retail, "ImpairedLoans").text = f"{retail_impaired:.2f}"
            retail_exposure = credit_info.get('retail_exposure', 1)
            impairment_rate = (retail_impaired / retail_exposure) * 100 if retail_exposure > 0 else 0
            ET.SubElement(retail, "ImpairmentRate").text = f"{impairment_rate:.2f}" 
        
        # Sovereign portfolio
        sovereign = ET.SubElement(portfolio, "Sovereign")
        ET.SubElement(sovereign, "ExposureAmount").text = f"{credit_info.get('sovereign_exposure', 0):.2f}"
        ET.SubElement(sovereign, "RiskWeight").text = f"{credit_info.get('sovereign_rw', 0):.2f}"
        
        sov_impaired = credit_info.get('sovereign_impaired', 0)
        if sov_impaired > 0:
            ET.SubElement(sovereign, "ImpairedLoans").text = f"{sov_impaired:.2f}"
            sov_exposure = credit_info.get('sovereign_exposure', 1)
            impairment_rate = (sov_impaired / sov_exposure) * 100 if sov_exposure > 0 else 0
            ET.SubElement(sovereign, "ImpairmentRate").text = f"{impairment_rate:.2f}"  
        
        return credit
    
    def _prettify_xml(self, xml_str: str) -> str:
        """Format XML with proper indentation"""
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def save_xml(self, xml_content: str, bank_id: str) -> str:
        """
        Save XML content to file in the output directory
        
        Args:
            xml_content: XML string to save
            bank_id: Bank identifier for filename
        
        Returns:
            Full file path of saved XML
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{bank_id}_report_{timestamp}.xml"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"    Saved: {filepath}")
        return filepath


if __name__ == "__main__":
    # Test XML generator
    generator = XMLGenerator(output_dir="reports")
    
    # Sample test data
    test_data = {
        'bank_info': {
            'bank_id': 'US-BANK-12345',
            'bank_name': 'Test Bank Corporation',
            'reporting_period_start': '2024-10-01',
            'reporting_period_end': '2024-12-31',
            'currency': 'USD',
            'report_type': 'QUARTERLY',
            'contact_name': 'John Smith',
            'contact_email': 'reports@testbank.com'
        },
        'capital_info': {
            'tier1_capital': 28500000000.00,
            'tier2_capital': 7500000000.00,
            'risk_weighted_assets': 290000000000.00,
            'minimum_requirement': 10.5
        },
        'liquidity_info': {
            'lcr_ratio': 125.50,
            'hqla_amount': 95000000000.00,
            'net_cash_outflows': 75600000000.00,
            'nsfr_ratio': 110.25
        },
        'credit_info': {
            'corporate_exposure': 220000000000.00,
            'corporate_rw': 65.00,
            'corporate_impaired': 3500000000.00,
            'retail_exposure': 150000000000.00,
            'retail_rw': 45.00,
            'retail_impaired': 1250000000.00,
            'sovereign_exposure': 80000000000.00,
            'sovereign_rw': 20.00,
            'sovereign_impaired': 0.00
        },
        'calculated': {
            'total_capital': 36000000000.00,
            'car_ratio': 12.41,
            'total_exposure': 450000000000.00
        }
    }
    
    try:
        xml_content = generator.generate_xml(test_data, "2024-12-31")
        filepath = generator.save_xml(xml_content, test_data['bank_info']['bank_id'])
        
        print("\nGenerated XML (first 25 lines):")
        print("="*70)
        lines = xml_content.split('\n')[:25]
        print('\n'.join(lines))
        
    except Exception as e:
        print(f"Error: {e}")