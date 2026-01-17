#!/usr/bin/env python3
"""
main.py - Bank Regulatory XML Report Generator
Only saves XML files that pass XSD validation
"""

import os
import sys
from datetime import datetime

# Added src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from data_cleaner import DataCleaner
from xml_generator import XMLGenerator
from xsd_validator import XSDValidator


def main():
    """Main execution function"""
    print("="*70)
    print("BANK REGULATORY XML REPORT GENERATION")
    print("  VALIDATION FIRST: XML only saved if it passes XSD validation")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Initialize components
        loader = DataLoader(data_dir="data")
        cleaner = DataCleaner()
        generator = XMLGenerator(output_dir="reports")
        validator = XSDValidator(xsd_path="schemas/bank_reporting.xsd")
        
        # Loaded all CSV data
        print("STEP 1: Loading CSV Files")
        print("-"*70)
        dataframes = loader.load_all_csv_files()
        loader.display_data_overview()
        
        # Getting list of banks
        bank_ids = loader.get_bank_ids()
        print(f"\n Found {len(bank_ids)} banks to process\n")
        
        # Track results
        successful = []
        failed = []
        validation_failed = []
        
        # Process each bank
        for idx, bank_id in enumerate(bank_ids, 1):
            print(f"\n{'='*70}")
            print(f"PROCESSING BANK {idx}/{len(bank_ids)}: {bank_id}")
            print(f"{'='*70}")
            
            # Get bank data
            bank_data = loader.get_bank_data(bank_id)
            if not bank_data:
                print(f" No data found for {bank_id}")
                failed.append(bank_id)
                continue
            
            # Clean data
            print("→ Step 1: Cleaning and validating data...")
            cleaned_data, errors = cleaner.clean_and_validate(bank_data)
            
            if errors:
                print(f"  Found {len(errors)} validation issues:")
                for error in errors[:5]:
                    print(f"   • {error}")
                
                # Check for critical errors
                critical_keywords = ['Missing required', 'Empty', 'must be positive']
                critical_errors = [e for e in errors if any(kw in e for kw in critical_keywords)]
                
                if critical_errors:
                    print(f" Critical errors found. Cannot generate XML for {bank_id}\n")
                    failed.append(bank_id)
                    continue
                else:
                    print(f"  Non-critical warnings. Continuing...\n")
            else:
                print(f" Data validation passed\n")
            
            # Generate XML (but don't save yet!)
            print("→ Step 2: Generating XML in memory...")
            report_date = bank_data.get('bank_data', {}).get('report_date')
            
            try:
                xml_content = generator.generate_xml(cleaned_data, report_date)
                print(f" XML generated ({len(xml_content)} characters)\n")
            except Exception as e:
                print(f" XML generation failed: {e}")
                failed.append(bank_id)
                continue
            
            # Validate XML string BEFORE saving
            print("→ Step 3: Validating XML against XSD schema...")
            is_valid, validation_errors = validator.validate_string(xml_content)
            
            if is_valid:
                print(" XML is VALID against XSD schema!\n")
                
                # NOW save the XML file
                print("→ Step 4: Saving validated XML file...")
                try:
                    xml_filepath = generator.save_xml(xml_content, bank_id)
                    successful.append(bank_id)
                except Exception as e:
                    print(f" Failed to save XML: {e}")
                    failed.append(bank_id)
                    continue
                
                # Save validation report
                validation_report = os.path.join("reports", f"{bank_id}_validation.json")
                validator.save_validation_report(xml_filepath, is_valid, validation_errors, validation_report)
                
            else:
                print(f" XSD Validation FAILED ({len(validation_errors)} errors):")
                for error in validation_errors[:3]:
                    print(f"   • {error}")
                if len(validation_errors) > 3:
                    print(f"   ... and {len(validation_errors) - 3} more errors")
                
                print(f"  XML file NOT saved (failed validation)")
                validation_failed.append(bank_id)
                
                # Save validation report without XML file
                validation_report = os.path.join("reports", f"{bank_id}_validation_FAILED.json")
                report_data = {
                    'validation_timestamp': datetime.now().isoformat(),
                    'bank_id': bank_id,
                    'xsd_schema': validator.xsd_path,
                    'is_valid': False,
                    'validation_status': 'FAILED',
                    'error_count': len(validation_errors),
                    'errors': validation_errors,
                    'xml_file': 'NOT SAVED - Validation failed'
                }
                
                import json
                with open(validation_report, 'w') as f:
                    json.dump(report_data, f, indent=2)
                print(f"    Validation report: {validation_report}\n")
        
        # Step 3: Summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Total Banks Processed: {len(bank_ids)}")
        print(f" Valid & Saved: {len(successful)}")
        print(f" Validation Failed (Not Saved): {len(validation_failed)}")
        print(f" Processing Failed: {len(failed)}")
        
        if successful:
            print(f"\n Successfully validated and saved:")
            for bank in successful:
                print(f"   • {bank}")
        
        if validation_failed:
            print(f"\n Failed XSD validation (XML not saved):")
            for bank in validation_failed:
                print(f"   • {bank}")
        
        if failed:
            print(f"\n Failed during processing:")
            for bank in failed:
                print(f"   • {bank}")
        
        print(f"\n Valid XML reports saved to: reports/")
        print(f" Validation reports saved to: reports/")
        print(f" End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Exit code: 0 only if all banks succeeded
        if failed or validation_failed:
            sys.exit(1)
        else:
            sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print("Ensure all required files exist:")
        print("  • data/ directory with CSV files")
        print("  • schemas/bank_reporting.xsd")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f" Import Error: {e}")
        print("\nPlease ensure:")
        print("  1. All files are in the 'src/' directory")
        print("  2. Create src/__init__.py (can be empty)")
        print("  3. Check file names match exactly")
        sys.exit(1)
    except Exception as e:
        print(f" Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)