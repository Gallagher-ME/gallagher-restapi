# Master-Dev Sync Status

## Summary
The `master` branch can be synced from the `dev` branch, but there are **merge conflicts** that need to be resolved first.

## Branch Status
- **Master branch**: `130a26c` - Tagged as v1.0.4
- **Dev branch**: `fae2ab0` - Tagged as v2.0.0
- **Branch relationship**: Unrelated histories (dev branch was grafted)

## Key Findings

### 1. Unrelated Histories
The `dev` branch has been grafted and contains unrelated history to `master`. This means the two branches do not share a common ancestor. To merge them, the `--allow-unrelated-histories` flag must be used.

### 2. Major Version Change
- Master is at version **1.0.4**
- Dev is at version **2.0.0**

This indicates a major rewrite/refactoring between the branches.

### 3. Merge Conflicts
When attempting to merge `dev` into `master` with `--allow-unrelated-histories`, the following files have conflicts:

#### Configuration Files
- `pyproject.toml` - Project configuration conflicts

#### Test Files
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_access_zones.py`
- `tests/test_alarm_zones.py`
- `tests/test_cardholder_methods.py`
- `tests/test_client.py`
- `tests/test_events.py`
- `tests/test_fence_zones.py`
- `tests/test_inputs.py`
- `tests/test_outputs.py`
- `tests/test_status_overrides.py`

### 4. Major Changes Between Branches

From the diff statistics:
- 31 files changed
- 5,504 insertions
- 2,406 deletions

#### Key structural changes in dev:
1. **Source code reorganization**: Code moved from `gallagher_restapi/` to `src/gallagher_restapi/`
2. **Dependency management**: Switched from Poetry (`poetry.lock`, `poetry.toml`) to uv (`uv.lock`)
3. **Complete rewrite**: `client.py` and `models.py` were completely rewritten
4. **New files**:
   - `.github/workflows/release.yml` - CI/CD workflow
   - `mypy.ini` - Type checking configuration
   - `tests/fixture.json` - Test fixtures
   - `tests/models/test_model.py` - Model tests
   - New test files for lockers and operator groups
5. **Enhanced README**: Major documentation improvements (432 new lines)

## Conclusion

**YES, master CAN be synced from dev**, but the following actions are required:

1. Use `git merge --allow-unrelated-histories dev` when merging into master
2. Manually resolve 11 merge conflicts (primarily in test files and configuration)
3. Review and test thoroughly as this represents a major version upgrade (v1.0.4 → v2.0.0)
4. Consider whether to:
   - Merge and resolve conflicts (recommended if dev represents the desired future state)
   - Keep branches separate if they represent different product versions
   - Create a new release branch for v2.0.0

## Merge Command

```bash
git checkout master
git merge --allow-unrelated-histories dev
# Resolve conflicts in the 11 files listed above
git commit
git push origin master
```

## Recommendations

Given the major version change and structural differences:
1. **Review dev branch changes thoroughly** before merging to ensure all functionality is preserved
2. **Test the merged code extensively** after conflict resolution
3. **Consider creating a backup branch** of master before merging
4. **Update documentation** to reflect the v2.0.0 changes
5. **Communicate the breaking changes** to users if this is a public API
