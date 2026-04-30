import pytest
from scripts.contact_finder import predict_buying_role

@pytest.mark.parametrize("title,expected_role", [
    # Blocker
    ("Legal Counsel", "Blocker"),
    ("Compliance Officer", "Blocker"),
    ("Procurement Manager", "Blocker"),
    ("Purchasing Agent", "Blocker"),

    # Champion
    ("VP of Engineering", "Champion"),
    ("Vice President", "Champion"),
    ("Head of Product", "Champion"),
    ("Director of Marketing", "Champion"),
    ("Senior Director", "Champion"),

    # Economic Buyer
    ("CEO", "Economic Buyer"),
    ("Chief Financial Officer", "Economic Buyer"),
    ("COO", "Economic Buyer"),
    ("President", "Economic Buyer"),
    ("Founder", "Economic Buyer"),
    ("Managing Director", "Economic Buyer"),
    ("General Manager", "Economic Buyer"),
    ("Partner", "Economic Buyer"),
    ("Owner", "Economic Buyer"),

    # Evaluator
    ("Engineering Manager", "Evaluator"),
    ("Senior Manager", "Evaluator"),
    ("Team Lead", "Evaluator"),
    ("Tech Lead", "Evaluator"),
    ("Principal Engineer", "Evaluator"),

    # End User
    ("Software Engineer", "End User"),
    ("Data Analyst", "End User"),
    ("Support Specialist", "End User"),
    ("Frontend Developer", "End User"),
    ("UX Designer", "End User"),

    # Unknown/Edge Cases
    ("Intern", "Unknown"),
    ("Coffee Maker", "Unknown"),
    ("", "Unknown"),
    ("Random Title", "Unknown"),

    # Case Insensitivity
    ("ceo", "Economic Buyer"),
    ("vIcE PrEsIdEnT", "Champion"),
])
def test_predict_buying_role(title, expected_role):
    assert predict_buying_role(title) == expected_role
