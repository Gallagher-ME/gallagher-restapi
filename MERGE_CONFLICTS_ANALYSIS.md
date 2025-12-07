# Detailed Merge Conflicts Analysis

## Overview
This document provides a detailed analysis of the merge conflicts that will occur when syncing master from dev.

## Conflict Categories

### 1. Project Configuration (pyproject.toml)

**Nature of Conflict**: Complete restructuring of project configuration

**Master (v1.0.4)**:
- Uses Poetry as package manager (`tool.poetry`)
- Version: 1.0.4
- Dependencies: httpx ^0.26.0, pytz ^2024.1, dacite ^1.8.1
- Build system: poetry-core

**Dev (v2.0.0)**:
- Uses uv as package manager (`project` section)
- Version: 2.0.0
- Dependencies: httpx >=0.28.1,<1.0.0, pytz >=2025.2, pydantic >=2.12.3,<3.0.0
- Build system: uv-build
- **Key change**: Replaced `dacite` with `pydantic` for data validation

**Resolution Approach**: Accept dev version (represents the future state)

---

### 2. Test Configuration (tests/conftest.py)

**Nature of Conflict**: Test fixtures and setup have been rewritten

**Changes in dev**:
- More comprehensive test fixtures
- Updated mocking strategies
- Better test isolation

**Resolution Approach**: Accept dev version (improved test infrastructure)

---

### 3. Test Files (All test_*.py files)

**Affected Files**:
- tests/test_access_zones.py
- tests/test_alarm_zones.py
- tests/test_cardholder_methods.py
- tests/test_client.py
- tests/test_events.py
- tests/test_fence_zones.py
- tests/test_inputs.py
- tests/test_outputs.py
- tests/test_status_overrides.py

**Nature of Conflict**: Tests rewritten to work with new Pydantic-based models

**Key Differences**:
1. Master tests use `dacite` for data parsing
2. Dev tests use `pydantic` for data validation
3. Dev tests have more comprehensive coverage
4. Dev tests use new fixture.json file

**Resolution Approach**: Accept dev versions (tests are updated for v2.0.0 API)

---

## Structural Changes (No Conflicts, but Important)

### Code Organization
- **Master**: Code in `gallagher_restapi/` directory
- **Dev**: Code in `src/gallagher_restapi/` directory (follows PEP 517/518 layout)

### Dependency Management
- **Master**: Uses Poetry (`poetry.lock`, `poetry.toml`)
- **Dev**: Uses uv (`uv.lock`)

### New Files in Dev (No conflicts)
1. `.github/workflows/release.yml` - Automated release workflow
2. `mypy.ini` - Type checking configuration
3. `tests/fixture.json` - Centralized test data
4. `tests/models/test_model.py` - Model validation tests
5. `tests/test_lockers.py` - New locker functionality tests
6. `tests/test_operator_groups.py` - New operator group tests
7. `src/gallagher_restapi/py.typed` - PEP 561 type stub marker

### Removed Files in Dev
1. `gallagher_restapi/` directory (moved to `src/`)
2. `poetry.lock` and `poetry.toml` (replaced with uv)

---

## Resolution Strategy

### Recommended Approach: Accept All Dev Changes

Given that dev represents v2.0.0 (a major version bump), the recommended strategy is:

```bash
# 1. Create a backup of master
git checkout master
git branch master-backup-before-v2

# 2. Merge dev with unrelated histories
git merge --allow-unrelated-histories dev

# 3. For all conflicts, accept dev version
git checkout --theirs pyproject.toml
git checkout --theirs tests/conftest.py
git checkout --theirs tests/test_access_zones.py
git checkout --theirs tests/test_alarm_zones.py
git checkout --theirs tests/test_cardholder_methods.py
git checkout --theirs tests/test_client.py
git checkout --theirs tests/test_events.py
git checkout --theirs tests/test_fence_zones.py
git checkout --theirs tests/test_inputs.py
git checkout --theirs tests/test_outputs.py
git checkout --theirs tests/test_status_overrides.py

# 4. Complete the merge
git add .
git commit -m "Merge dev into master for v2.0.0 release"

# 5. Test thoroughly
uv sync
uv run pytest
uv run mypy src/

# 6. Push to master
git push origin master
```

---

## Breaking Changes Summary

### API Changes
1. **Pydantic instead of dacite**: All models now use Pydantic for validation
2. **Package structure**: Import path changes from `gallagher_restapi` to likely needs update
3. **Dependency updates**: Newer versions of all dependencies

### Build System Changes
1. **Poetry → uv**: Different commands for installation and testing
2. **Project layout**: Now follows src-layout pattern

### New Features in v2.0.0
1. Enhanced type checking (mypy)
2. Improved test coverage
3. Better model validation
4. Automated release workflow
5. New functionality: lockers, operator groups

---

## Post-Merge Checklist

After merging, verify:

- [ ] All tests pass: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Package can be built: `uv build`
- [ ] README is up to date
- [ ] Version is correctly set to 2.0.0
- [ ] CHANGELOG reflects breaking changes
- [ ] Documentation is updated
- [ ] Old poetry files are removed
- [ ] GitHub Actions workflows work correctly

---

## Risk Assessment

**Risk Level**: HIGH

**Reasons**:
1. Complete package manager change (Poetry → uv)
2. Major dependency change (dacite → Pydantic)
3. Structural reorganization (src layout)
4. Major version bump (1.0.4 → 2.0.0)

**Mitigation**:
1. Thorough testing after merge
2. Keep master-backup branch
3. Update documentation
4. Communicate breaking changes to users
5. Consider beta release before final v2.0.0

---

## Timeline Recommendation

1. **Day 1**: Create backup, perform merge, resolve conflicts
2. **Day 2-3**: Run full test suite, fix any issues
3. **Day 4**: Update documentation, prepare release notes
4. **Day 5**: Release v2.0.0 with clear migration guide

---

## Conclusion

**Master CAN be synced from dev**, but it requires:
- Careful conflict resolution (accept all dev changes)
- Comprehensive testing
- Documentation updates
- User communication about breaking changes

The merge is feasible but represents a major upgrade that should be handled with care.
