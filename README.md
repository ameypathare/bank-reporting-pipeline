##  Project Overview
This project simulates a real-world **bank regulatory reporting system** that was developed to eliminate manual work and ensure 100% compliance for quarterly submissions to financial authorities. It mirrors the architecture and business logic of a production system used in a risk management environment. 

The pipeline follows a modular, production-ready design:<br>
CSV Data Source → Python Data Processing → XML Generation → XSD Validation → Report Delivery

Please note:<br>
<font color="red">
The data ingested is fake. Due to organization's rules & regulations can't display the data & code used in production.
</font>



### **Key Modules**
1.  **`data_loader.py`** - Ingests and validates source data from CSV files.
2.  **`data_cleaner.py`** - Applies business rules, data quality checks, and prepares data for reporting.
3.  **`xml_generator.py`** - Transforms cleaned data into the precise XML schema required by regulators.
4.  **`xsd_validator.py`** - Validates the generated XML against the official regulatory XSD schema, ensuring zero compliance errors.
5.  **`main.py`** - Orchestrates the complete pipeline execution.


##  Business Value & Impact

| Metric | Before Automation | After Automation | Impact |
| :--- | :--- | :--- | :--- |
| **Processing Time** | Many hours per quarter, including weekend work. | **< 5 minutes** fully automated. | **99% time reduction**, freeing the risk team for strategic analysis. |
| **Data Accuracy** | Manual Excel work prone to errors. | **100% accuracy** with automated XSD validation. | **Zero regulatory rejections** and compliance penalties. |
| **Operational Risk** | High dependency on individual knowledge. | Documented, repeatable code. | Eliminated key-person risk and ensured business continuity. |
| **Report Reliability** | Missed deadlines under pressure. | **100% on-time submission** guaranteed. | Protected the bank's regulatory reputation. |
