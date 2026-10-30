
from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.assistant import IronStoreAssistant


TEST_CASES = [
    # HR POLICIES
    {
        "category": "HR",
        "question": "What are the eligibility requirements for remote and hybrid work?",
        "expected_sources": ["IronStore_Remote_Work_Policy.pdf"],
    },
    {
        "category": "HR",
        "question": "Can employees request annual leave during probation?",
        "expected_sources": [
            "IronStore_Leave_and_Absence_Policy.pdf",
            "IronStore_Employee_Handbook.pdf",
        ],
    },
    {
        "category": "HR",
        "question": "How do employees request reimbursement for business expenses?",
        "expected_sources": ["IronStore_Expense_Reimbursement_Policy.pdf"],
    },
    {
        "category": "HR",
        "question": "What are the procedures for reporting sickness absence?",
        "expected_sources": ["IronStore_Leave_and_Absence_Policy.pdf"],
    },
    {
        "category": "HR",
        "question": "How are public holidays determined for employees?",
        "expected_sources": ["IronStore_Employee_Handbook.pdf"],
    },

    # PRODUCT CATALOGUE
    {
        "category": "PRODUCT",
        "question": "List the products available in the Art and Craft Supplies catalogue.",
        "expected_sources": [
            "IronStore_Product_Catalog_Art_and_Craft_Supplies.pdf"
        ],
    },
    {
        "category": "PRODUCT",
        "question": "What is included in BuildBench Precision Modelling Tool Set 9?",
        "expected_sources": [
            "IronStore_Product_Catalog_Art_and_Craft_Supplies.pdf"
        ],
    },
    {
        "category": "PRODUCT",
        "question": "What are the specifications of ColourLedger Swatch and Inventory Book?",
        "expected_sources": [
            "IronStore_Product_Catalog_Art_and_Craft_Supplies.pdf"
        ],
    },
    {
        "category": "PRODUCT",
        "question": "Describe the Nordline Graphite Drawing Set 24.",
        "expected_sources": [
            "IronStore_Product_Catalog_Art_and_Craft_Supplies.pdf"
        ],
    },
    {
        "category": "PRODUCT",
        "question": "Find products and specifications in the Computer Accessories catalogue.",
        "expected_sources": [
            "IronStore_Product_Catalog_Computer_Accessories.pdf"
        ],
    },

    # INSUFFICIENT OR PARTIAL INFORMATION
    {
        "category": "ABSTENTION",
        "question": "What exact maternity leave duration and pay does IronStore guarantee in every country?",
        "expected_sources": ["IronStore_Leave_and_Absence_Policy.pdf"],
    },
    {
        "category": "ABSTENTION",
        "question": "What exact number of paid bereavement leave days applies to every employee?",
        "expected_sources": ["IronStore_Leave_and_Absence_Policy.pdf"],
    },
    {
        "category": "ABSTENTION",
        "question": "What are the specifications and availability of StackMate Modular Craft Organiser 24?",
        "expected_sources": [
            "IronStore_Product_Catalog_Art_and_Craft_Supplies.pdf"
        ],
    },
    {
        "category": "ABSTENTION",
        "question": "What is the guaranteed remote working arrangement for every IronStore employee?",
        "expected_sources": ["IronStore_Remote_Work_Policy.pdf"],
    },
    {
        "category": "ABSTENTION",
        "question": "What is the exact statutory parental leave entitlement for every country where IronStore operates?",
        "expected_sources": ["IronStore_Leave_and_Absence_Policy.pdf"],
    },
]


def main():

    print("=" * 65)
    print("IRONSTORE - RETRIEVAL EVALUATION")
    print("=" * 65)

    assistant = IronStoreAssistant()

    total_expected = 0
    total_found = 0
    successful_cases = 0

    for index, test in enumerate(TEST_CASES, start=1):

        print(f"\n[{index}/{len(TEST_CASES)}] {test['category']}")
        print(f"Question: {test['question']}")

        expected = set(test["expected_sources"])
        total_expected += len(expected)

        try:
            documents = assistant.retrieve(test["question"])

            retrieved = {
                doc.metadata.get("filename", "Unknown")
                for doc in documents
            }

            matched = expected.intersection(retrieved)
            missing = expected.difference(retrieved)

            total_found += len(matched)

            if matched:
                successful_cases += 1
                status = "PASS"
            else:
                status = "FAIL"

            print(f"Status: {status}")
            print(f"Expected: {sorted(expected)}")
            print(f"Retrieved: {sorted(retrieved)}")
            print(f"Matched: {len(matched)}/{len(expected)}")

            if missing:
                print(f"Missing: {sorted(missing)}")

        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")

    case_hit_rate = successful_cases / len(TEST_CASES) * 100
    source_recall = total_found / total_expected * 100

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"Successful cases: {successful_cases}")
    print(f"Case hit rate: {case_hit_rate:.1f}%")
    print(f"Expected sources found: {total_found}/{total_expected}")
    print(f"Expected source recall: {source_recall:.1f}%")
    print("=" * 65)


if __name__ == "__main__":
    main()
