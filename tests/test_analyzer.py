from ai_code_review.analyzer import review_code, review_diff


def test_detects_hardcoded_secret_and_bare_except() -> None:
    code = '''password = "super-secret-123"\ntry:\n    run()\nexcept:\n    pass\n'''
    result = review_code(code, use_ai=False)
    rule_ids = {finding.rule_id for finding in result.findings}
    assert "hardcoded-secret" in rule_ids
    assert "bare-except" in rule_ids


def test_clean_code_has_no_findings() -> None:
    result = review_code("def add(a, b):\n    return a + b\n", use_ai=False)
    assert result.findings == []


def test_diff_review_only_considers_added_lines() -> None:
    diff = '''--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,3 @@\n def ok():\n     return True\n+password = "secret-value"\n'''
    result = review_diff(diff, use_ai=False)
    assert any(f.rule_id == "hardcoded-secret" for f in result.findings)
