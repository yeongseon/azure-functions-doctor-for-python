# 📦 Changelog

## Build

- Bump version to 0.1.3 ([340053c…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/340053cea4359e2156a3269d04ecae5345b2c041))


## Chore

- Add automatic commit after version bump in release targets ([69ba5da…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/69ba5da761dcd850ad96f9eb792b37a3b762e9b4))


## Fix

- Correct wheel target package path for src layout ([86239d9…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/86239d9c10037f2ec4aa635a108f42e5764c6888))


## Build

- Bump version to 0.1.2 ([4b15462…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4b1546283c0351c2fd5ad967452b39120564e7c9))


## Chore

- Declare version as dynamic in pyproject.toml for PEP 621 compliance ([41cc80d…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/41cc80d3005fcd24280533a66f7eda8b046b6ced))

- Switch to dynamic versioning and fix Makefile targets ([7cdee62…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/7cdee62a6f7fe7a8a2f7220ae0a41a602b54403f))


## Ci

- Separate version bump from release logic to avoid duplicate version update ([3a3e1c2…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/3a3e1c24292b7c11d67ab6eaff4632a0add8b37d))

- Sync tag and version, improve Makefile release steps ([e97ec20…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/e97ec207204058e1ef7b2eefbf76e9b7d5c61b21))


## Docs

- Update changelog ([9dd6ebd…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/9dd6ebda32c8be419179331643cf8e17350380ef))

- Update README badges for CI and release workflows ([628f8a7…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/628f8a7e21317f3ba744dde10da99a9ef5b47852))

- Consolidate changelog for 0.1.1 and clear unreleased ([07cfb5d…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/07cfb5df5ecaf91c5e632a25774a037cc11e753d))

- Generate changelog for v0.1.1 ([d96c275…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/d96c275d907f28f696f6128d7431b04e21ba86a8))


## Fix

- Remove unsupported commit.remote from git-cliff template ([9f429fb…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/9f429fb328962d93492fce6f2aca50ec3e44ca92))


## Ci

- Use twine for PyPI upload on tag push ([9af1dbe…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/9af1dbe7778fd2c301e4ce48848285a902f86538))

- Trigger PyPI publish on tag push ([054d226…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/054d22632b406b5874f7240208654ca56b4840b5))


## Docs

- Update changelog ([916ee3d…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/916ee3d1b4d643192a9bcad2896a1b8d498c6482))

- Update changelog ([0b116f4…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/0b116f48d48621bb35b70543be1ba19786671ac3))


## Build

- Add changelog generation and release process to Makefile and docs site ([7ebb433…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/7ebb433982852fbfe754d6830c1324eaf3bf2f77))

- Fix packaging path and add metadata for PyPI ([682ccc1…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/682ccc13226967caa1e46e0f43bf0a7849ae6edd))

- Add tox target for multi-version testing ([13bbef2…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/13bbef209db339bfa4df3713d1efec8d170806a0))

- Configure tox environments in pyproject.toml ([0adb6ad…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/0adb6ad2d065aa349d1d0629a42ca21641e3a6de))

- Add hatch-based release and publish automation ([b08c1b6…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/b08c1b69a1ccfcbd08b656af0d26592c564dbb83))


## Chore

- Update PyPI classifiers to include Python 3.11 and 3.12 ([7115bd5…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/7115bd5eb1783331d7becc723f15f92e962852f8))

- Fix project name to 'azure-functions-doctor' across all files ([4559727…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4559727181598a2aa2af8cc3f527eda237fd1501))

- Update logo assets with new design ([2bf4fa1…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/2bf4fa1bd6f2a77186bd65adc1568ba7176ef280))

- Configure docs environment and ensure Python 3.9 compatibility ([982387b…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/982387b0753091a1ed1f3b6e4500e104bcaa7ff6))

- Organize pyproject.toml and include py.typed for PEP 561 support ([eab6e83…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/eab6e83360a1134893ecff15523874d48b8b1c9e))

- Pin tool versions and unify configuration ([bb49a02…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/bb49a027ee23abe8750f25363cdff8975bc083c4))

- Improve Hatch environment and pyproject.toml structure ([f1a3361…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/f1a33615598bb90c3c1dfb6af7c8520b2f4aafd2))

- Migrate to full Hatch-based workflow with unified Makefile and CI ([8127be7…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/8127be701f006fb22be094eb4b1233ec16c54b5b))

- Add commitizen configuration and Makefile targets for patch/minor/major ([ee46449…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/ee464494be83929343ec749180fc2cd84dc25590))

- Remove .tox and htmlcov in Windows clean-all script ([483f5c5…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/483f5c5656acbcab4d7700fa9fbe7a832f13ce50))

- Update pyproject.toml configuration ([e12a263…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/e12a26300588a189bdc37f70c1a9a485e7e1b2e8))

- Update coverage config to match renamed package ([35cb199…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/35cb199d434d7e47c625f23c9fa612eab945018f))

- Update hatch build path to match renamed package ([10d17bd…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/10d17bd6f177cdb2acdd366a923110d2dc24b139))

- Update pyproject.toml for renamed package and mypy/ruff config ([3b11ad1…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/3b11ad1f0160f2a92615c86458c1db117c030c3f))

- Update .editorconfig for markdown and YAML handling ([2710066…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/27100660adcc0bbd7babf4ff9d942e4cb39238ce))

- Add .editorconfig for consistent code style ([f69d3e3…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/f69d3e3ee8f375664fe22f63e9091d9578b78919))

- Finalize dev environment setup and update documentation ([1e932f8…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/1e932f8becbc00cdd9d42b3168b4711bd80259e8))

- Add pre-commit, coverage, and CI configuration ([329d8a7…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/329d8a78a2e3f984aafb67798686c82997901c17))

- Apply full initial setup with CLI, testing, and formatting tools ([153aa23…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/153aa236852935e6be5cad498f3bb2004b6cec77))

- Initial project setup with CLI, Makefile, docs, and packaging ([a39efbd…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/a39efbd9a2d2b953905b6ce3925badab2b44c117))


## Ci

- Add GitHub Actions release workflow ([48a4548…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/48a45485064bc599e58ab8be63eb25e0dcfc8ce0))

- Fix artifact upload conflict by including Python version in name ([d8fdca4…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/d8fdca4e8f47a4827a60fb3d3a218f02d886a41b))

- Fix missing venv setup in GitHub Actions with uv ([6a01121…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/6a01121a52b4a5a94a19f6ab58d846af36b550a0))

- Fix missing venv setup for uv-based environment ([f912cbb…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/f912cbb6fd34266a4b3ebaa9c2b14bc5179c7b00))


## Docs

- Reflect latest commits in CHANGELOG.md ([bd094b0…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/bd094b00f7d5fe646d1b1f830e3adbb05fefbe8b))

- Update changelog ([4f1a1e6…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4f1a1e658bd5705e85b1d9ccc058fdab11305e83))

- Add changelog for v0.1.0 ([2f9a0d0…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/2f9a0d00f273445314da3e2999a84010e4a5084c))

- Update README for basic-hello with Python model v2 instructions ([44e3329…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/44e332998ce0935271a5f93f65d584289b89bd9e))

- Add release process guide and git-cliff config ([0984e73…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/0984e73a19e2c814acfcbc178deee46876f9f66b))

- Add GitHub workflow, PyPI, coverage, license, and download badges to README ([4d67eed…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4d67eedb274af56ba76d68523958c7dad31bc89f))

- Update mkdocs.yml to reflect new repository name ([ce2b951…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/ce2b9515d5d97d884c6450ab5c9c7e8aae8d0c36))

- Enlarge logo in README and finalize CLI doc structure ([fb7a695…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/fb7a695b14a1e592d7b8393960a4e4e879cac65b))

- Enlarge logo size in README for better visibility ([fd9445c…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/fd9445c68b1d832420b0278389a61792d48970e1))

- Enlarge logo size in README for better visibility ([f8f6d9c…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/f8f6d9c0fdb14cef6a65d8dbeb7e964c8c02c16a))

- Update README and add relocated logo_assets directory ([c81e142…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/c81e1424557d04812f63e78ab8deaea0beae2826))

- Update README and remove old logo assets ([9e19f37…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/9e19f37a161cfbf632f73f6894039e885a447deb))

- Update CLI usage, main docs, and add CONTRIBUTING guide ([884199f…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/884199ff408540d9ad52794ac7641ce6fe4eaed2))

- Update project title and links for renamed repo ([bb6f59a…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/bb6f59afef6106ae91bae9c23672bb20c03ce074))

- Add MkDocs config, Makefile target, and GitHub Pages deployment workflow ([47b935a…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/47b935ae36e9c2e8338a454a2a1f156770afd42e))

- Integrate API auto-documentation using mkdocstrings ([e59e3ef…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/e59e3ef61e1a27c32ea0fbac6e1578d9622d2713))

- Update main README with installation, usage, and example links ([310a437…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/310a437331cfb5211897c09f50a06d6400cbb8ba))

- Add README for basic-hello Azure Function example ([bce8b84…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/bce8b849e73e7236e1948e23f6baaedf80eceefd))

- Update development and usage guides ([8e262c9…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/8e262c92567a27b94d426d3cf09ead74ba4a5dab))

- Update diagnostic checklist with unified table and official references ([ed64d6e…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/ed64d6e7a682a49176a0ce35877422bed7718480))

- Add CLI usage, development guide, and diagnostics roadmap with mkdocs config ([7793848…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/779384836e773f016f4a3fc06c77f028e6815d66))

- Add initial changelog with current features and setup history ([4652ff3…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4652ff36bf36321d6398e5e00a98b4d7b2b2c9cb))

- Add module-level and function docstrings ([7ee433a…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/7ee433ab4f9cb35877e8ec82e00068cc0decc574))

- Update README to reflect renamed package path ([2af0995…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/2af0995e215ab28099b0afb50356c98904579997))

- Update site name in mkdocs config to match new package name ([5e05007…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/5e05007611c5074f659c6cce093f3d35add55ea7))

- Update module name in documentation to azure_functions_doctor ([206132c…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/206132cd430685977c4f9ebd406516b45fc9a1d3))


## Feat

- Add official logo assets for Azure Functions Doctor ([a69d52e…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/a69d52e77296937184e35fc4ac239f14024469f5))

- Add basic hello world Azure Function (HTTP trigger) ([659362e…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/659362e063ed33745a552fceaa0b7d8afb0303be))

- Add modular checks and API compatibility with diagnostic output ([fd98178…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/fd98178733cd08c27e85a53849065c8e2b81a54a))

- Modularize doctor checks and standardize diagnostic result format ([692eb93…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/692eb93a4a9df51e5e16351befab049c999d9782))


## Fix

- Explicitly register diagnose command and fix CLI entrypoint ([e41ed35…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/e41ed3548d29140c801b57c2d0abdb1a2727ceaf))

- Prevent NUL file creation on Windows when checking for uv ([3eee166…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/3eee166f5376d43d0e0f6c6792b95f7b2e5cb751))

- Add cross-platform uv detection with pip fallback ([285454d…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/285454d5828f11f1e240a7887b5b246f047b5aa7))


## Refactor

- Restructure rule logic and output handling ([cf49aef…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/cf49aef15c37d549d2275d6303a93c8e025e9f28))

- Restructure check logic and improve test coverage ([1a2709c…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/1a2709c9f03fb6b2492159d4005bf232a45b9770))

- Modularize check logic and add handler registry ([21f4f0f…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/21f4f0f118e2dff7593f6b3624657a0c1bb5d66d))

- Improve diagnose command with rich output and verbose option ([27f9cc2…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/27f9cc259b30097840a9155b44c9d1c007b1c45a))

- Migrate CLI from Click to Typer ([253e8c0…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/253e8c047be3d65cfd4a97bf7f8ee358bc547101))

- Migrate CLI from Typer to Click and fix typecheck/lint issues ([e7482b6…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/e7482b6ca27885db50125f19778755dc7e051ecb))

- Extract Windows clean commands into scripts ([3a063b8…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/3a063b806168e5f09242e84275c3ecec5341ef35))

- Clean up tool configs and improve Makefile portability ([c732379…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/c73237982ef1cb3bd73808b43367d7bbc59a3790))

- Rename package from azure_function_doctor to azure_functions_doctor ([9278315…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/92783158cc044f7074afc94a5582807f793bf9c8))


## Style

- Increase line length limit from 100 to 120 for Black and Ruff ([7e9808e…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/7e9808e4fdb567a634ea6bd97deca6e9aebb0fba))


## Test

- Rewrite CLI tests using subprocess to verify full entrypoint ([41b02e4…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/41b02e4faddb622d2ecd67dafe91fcdf163ac01d))

- Convert test_doctor to pytest format ([4a3acec…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/4a3acec18f495c1727812447fb31f69fe4c86863))

- Migrate to pytest and update Makefile test command ([a9f5409…](https://github.com/yeongseon/azure-functions-doctor-for-python/commit/a9f54096802786c57bbb32073ff023344d77a4c2))


