import xmlschema
from lxml import etree
import os
from typing import Tuple, List, Dict
import json
from datetime import datetime


class XSDValidator:
    """Validates XML reports against XSD schema"""
    
    def __init__(self, xsd_path: str = "schemas/bank_reporting.xsd"):
        self.xsd_path = xsd_path
        
        if not os.path.exists(xsd_path):
            raise FileNotFoundError(f"XSD schema not found: {xsd_path}")
        
        # Load schema once during initialization
        try:
            self.schema = xmlschema.XMLSchema(xsd_path)
            self.lxml_schema = self._load_lxml_schema()
        except Exception as e:
            raise ValueError(f"Failed to load XSD schema: {e}")
    
    def _load_lxml_schema(self):
        """Load schema using lxml for alternative validation"""
        try:
            with open(self.xsd_path, 'rb') as f:
                xsd_doc = etree.parse(f)
            return etree.XMLSchema(xsd_doc)
        except Exception:
            return None
    
    def validate_file(self, xml_file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate an XML file against the XSD schema
        
        Args:
            xml_file_path: Path to XML file to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not os.path.exists(xml_file_path):
            return False, [f"XML file not found: {xml_file_path}"]
        
        errors = []
        
        try:
            # Primary validation with xmlschema
            if self.schema.is_valid(xml_file_path):
                return True, []
            
            # Get detailed errors
            try:
                self.schema.validate(xml_file_path)
            except xmlschema.XMLSchemaValidationError as e:
                errors.append(f"Validation error: {str(e)}")
            
            # Try alternative validation with lxml
            if self.lxml_schema:
                lxml_valid, lxml_errors = self._validate_with_lxml(xml_file_path)
                errors.extend(lxml_errors)
            
            return False, errors
            
        except Exception as e:
            errors.append(f"Validation exception: {str(e)}")
            return False, errors
    
    def _validate_with_lxml(self, xml_file_path: str) -> Tuple[bool, List[str]]:
        """Alternative validation using lxml library"""
        errors = []
        
        try:
            with open(xml_file_path, 'rb') as f:
                xml_doc = etree.parse(f)
            
            if self.lxml_schema.validate(xml_doc):
                return True, []
            
            # Collect errors from log
            for error in self.lxml_schema.error_log:
                errors.append(f"Line {error.line}: {error.message}")
            
            return False, errors
            
        except Exception as e:
            errors.append(f"LXML error: {str(e)}")
            return False, errors
    
    def validate_string(self, xml_content: str) -> Tuple[bool, List[str]]:
        """
        Validate an XML string against the XSD schema
        
        Args:
            xml_content: XML content as string
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # Write to temporary file and validate
        temp_file = "temp_validation.xml"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            return self.validate_file(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def check_xml_structure(self, xml_file_path: str) -> Dict:
        """
        Analyze XML structure without strict validation
        Returns diagnostic information about the XML
        """
        try:
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            root = etree.fromstring(content.encode())
            
            # Gather structural information
            structure_info = {
                'root_tag': root.tag,
                'root_attributes': dict(root.attrib),
                'child_elements': [child.tag for child in root],
                'total_elements': len(list(root.iter())),
                'has_text_content': any(elem.text and elem.text.strip() for elem in root.iter())
            }
            
            return structure_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def save_validation_report(self, xml_file_path: str, is_valid: bool, 
                              errors: List[str], output_file: str) -> Dict:
        """
        Save detailed validation report to JSON file
        
        Args:
            xml_file_path: Path to the validated XML file
            is_valid: Whether validation passed
            errors: List of validation errors
            output_file: Path to save the JSON report
        
        Returns:
            Dictionary containing the report data
        """
        # Get file info
        file_size = os.path.getsize(xml_file_path) if os.path.exists(xml_file_path) else 0
        
        # Build report
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'xml_file': xml_file_path,
            'xsd_schema': self.xsd_path,
            'file_size_bytes': file_size,
            'is_valid': is_valid,
            'validation_status': 'PASSED' if is_valid else 'FAILED',
            'error_count': len(errors),
            'errors': errors
        }
        
        structure = self.check_xml_structure(xml_file_path)
        if 'error' not in structure:
            report['structure'] = structure
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"    Validation report: {output_file}")
        return report
    
    def batch_validate(self, xml_files: List[str]) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate multiple XML files
        
        Args:
            xml_files: List of XML file paths
        
        Returns:
            Dictionary mapping file paths to (is_valid, errors) tuples
        """
        results = {}
        
        for xml_file in xml_files:
            results[xml_file] = self.validate_file(xml_file)
        
        return results


if __name__ == "__main__":
    # Test the validator
    print("Testing XSD Validator...")
    print("="*70)
    
    try:
        validator = XSDValidator("schemas/bank_reporting.xsd")
        print(f" Loaded XSD schema: {validator.xsd_path}\n")
        
        # Test with sample XML
        test_xml = """<?xml version="1.0"?>
<BankRegulatoryReport reportDate="2024-12-31" bankId="US-BANK-12345">
    <ReportHeader>
        <BankName>Test Bank</BankName>
        <ReportingPeriod>
            <StartDate>2024-10-01</StartDate>
            <EndDate>2024-12-31</EndDate>
        </ReportingPeriod>
        <Currency>USD</Currency>
        <ReportType>QUARTERLY</ReportType>
    </ReportHeader>
    <CapitalAdequacy>
        <Tier1Capital>10000000000.00</Tier1Capital>
        <Tier2Capital>2500000000.00</Tier2Capital>
        <TotalCapital>12500000000.00</TotalCapital>
        <RiskWeightedAssets>100000000000.00</RiskWeightedAssets>
        <CAR>12.50</CAR>
        <MinimumRequirement>10.50</MinimumRequirement>
        <ComplianceStatus>COMPLIANT</ComplianceStatus>
    </CapitalAdequacy>
    <LiquidityMetrics>
        <LCR>
            <Ratio>125.50</Ratio>
            <HighQualityLiquidAssets>50000000000.00</HighQualityLiquidAssets>
            <NetCashOutflows>40000000000.00</NetCashOutflows>
        </LCR>
        <NSFR>110.25</NSFR>
    </LiquidityMetrics>
    <CreditExposures>
        <TotalExposures>150000000000.00</TotalExposures>
        <PortfolioBreakdown>
            <Corporate>
                <ExposureAmount>80000000000.00</ExposureAmount>
                <RiskWeight>65.00</RiskWeight>
            </Corporate>
            <Retail>
                <ExposureAmount>50000000000.00</ExposureAmount>
                <RiskWeight>45.00</RiskWeight>
            </Retail>
            <Sovereign>
                <ExposureAmount>20000000000.00</ExposureAmount>
                <RiskWeight>20.00</RiskWeight>
            </Sovereign>
        </PortfolioBreakdown>
    </CreditExposures>
</BankRegulatoryReport>"""
        
        print("Validating sample XML...")
        is_valid, errors = validator.validate_string(test_xml)
        
        if is_valid:
            print(" Sample XML is valid!\n")
        else:
            print(" Sample XML validation failed:")
            for error in errors:
                print(f"   • {error}")
        
    except FileNotFoundError as e:
        print(f" {e}")
        print("Please ensure schemas/bank_reporting.xsd exists")
    except Exception as e:
        print(f" Error: {e}")