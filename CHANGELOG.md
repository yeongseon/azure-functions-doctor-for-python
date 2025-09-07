# 📦 Changelog

- bump version to 0.11.0 (9b64954b1ed7f1ad8fbc9c37fdecf759c6f17f1a)

- merge handler tests into single file; remove duplicate; add type hints (f1367558997e6a2630ac4496157683cd23a2bf59)

- update changelog (f6f40e2f48cbaa0fff33bea600480ec61d72aba5)

- bump version to 0.10.0 (2979e22dc658b0cf2f1b0266a58f4ba9ddebc6b8)

- update CLI name references and use new example screenshot filename (ec953a1e677e1e28ed3693ed24e813b56f24357a)

- accept 'jsonpath' in Condition TypedDict (fix mypy) (cbcf52850cdd1f86823008baaf267ee22d40f81c)

- rename command to 'azure-functions doctor' and update UI; doctor: include severity metadata and normalize statuses (7b327f9f9dbceb5afc13e6d090be14f1daccadc3)

- update changelog (7c01e2cba5f71ebd4326bc8a441e4a81d278bf76)

- bump version to 0.9.0 (6cf33bc61cb2c8256f1eff52295292ae365d256b)

- replace 'func-doctor' with 'azure-functions' in docs and examples (30057fce6f80fba9e5a4d15dcdbc795823a9b90f)

- update CLI tests to use 'doctor' subcommand (25423c5fb1ea81f3a6401cb9a6f0bfbb9adce300)

- rename subcommand to 'doctor' and add 'azure-functions' console script entrypoints (7101e7f92ecb25f3c9d382674048bb94adc628c7)

- update changelog (c0cb87053d831b1003518e78768f4645ee570dc7)

- bump version to 0.8.0 (52b07238fbc699434e615e00b7828ab06e5dbe82)

- Run formatters (black/ruff) adjustments (1895c63c1d014ba42b6c8e2d899c9178227637f1)

- update changelog (31e2c19f216b44d7a60c33e31cbad87e3561fad4)

- bump version to 0.7.0 (f1a3ebb19a11194282a9e86222174fd89aedfff7)

- merge new handler tests and update programming model/rule-loading tests (019d875570b245ff787e8b73e72097df32cdfb11)

- simplify rule loader, add allow_v1 flag for CLI (c0d52982df13a70587afa67509bb4bf3e80bf4ae)

- add conditional_exists and callable_detection handlers (428b59fbdca4e3151cd8410eb60ee957b1024d34)

- add v1/v2 rule stubs and severities (fcbe157ac2c3246b9171a56b4ee5075ca89dfc89)

- add Severity column to v2 programming model checks (ad021874bc78d42369346f81a2c9b4d7e9bdf0f6)

- update changelog (ffc692f5465f58c8816e9ff28d2e7841d5a5196e)

- bump version to 0.6.0 (f6bad63d9cfd913b6bb6461c9fc8ca8d53ae70eb)

- update legacy rules.json for backward compatibility (a9ba697213ebe60570d701c53c91ce064ada4afb)

- update documentation for v1/v2 programming model support (c7653652bb4045cd624cb6d6b521fa1500103900)

- improve UI and add v1 project support with warning (fd04e11d825d34d7fa6a25816712f25ce7ad1328)

- implement separate rule sets for v1 and v2 programming models (2bb5952602e2d63e9676bb383958b1d6aec0c8e2)

- implement programming model detection for v1 and v2 (568f756521cb6657bcf6a12617a9872bd074bedd)

- bump version to 0.5.1

- Fix verbose option behavior
- verbose now only controls hint display, not logging level
- Update CHANGELOG.md with fix details (a6a8690e8f5ac10e9092d2783ecba200403f5caa)

- separate verbose option from logging level control (9b373a91243fcf5668afec8491beea95b258fa7d)

- update changelog (deeb342676ef59776d8812758b64632bc730e9ee)

- bump version to 0.5.0 (248da2a31fa91b09270d72627a2d20569526360d)

- improve error handling and robustness (1c90078671dbee99ce13d3c0a1920447bcfc141f)

- bump version to 0.4.1 (a9fc413faef0efb421ce93cafcc267bb349ada39)

- unify output using Rich Console (ebaf2071df99d2f61eb34a8940ff5e386176a134)

- bump version to 0.4.0 (a21ca7cb94a14e29eb2d3f5d5abb3aaeb35d2bc0)

- add v1/v2 compatibility check at initialization (af3621b35dcef7513839f8e0b8f07b329cf82a9a)

- mark local.settings.json implemented; test: assert optional local.settings.json passes (ab2c16d5dfdab13720a66bf539c61998a0bc8dc6)

- update changelog (1fef4982e53a40df6ac191e8d11aea3607d1d015)

- bump version to 0.3.0 (cb009efdfbae834ee293973df6346c8251e34e90)

- fix documentation build issues (df9046675e4cb25d4f0d1f9e754a034d63c42aa1)

- resolve diagnostic failures and pre-commit issues (cc2a27eedd63c0dbf6d0c35ab2ca93a98b7bf26b)

- implement major code structure improvements (18c3d60ef104003ebc93788a25db5e7fcc34b0cd)

- align local version with PyPI release (0.2.0) (68a011cfc517751eda20de5b19d9a1f378296187)

- update changelog (afdf7359dafaf8ff444552b08152a5d9cd25271b)

- bump version to 0.1.11 (39be13cfef2f5725f46766d897c4b822504b20fc)

- remove overly ambitious roadmap document (3a9d4d15b45709d6a68e77d22939f3288a8bfae8)

- add comprehensive roadmap for static analysis and CI/CD platform (66db758d6d426b0bd76fdcb7d76c2fac60b165b0)

- add architecture diagram and remove emojis from README (654c34195bd21ed502218bd12624843ce1fb89db)

- enhance open source documentation and add contribution templates (2a7a811e19d1394982b88643145196a7c13883f9)

- implement centralized logging infrastructure (8b508c585e54b825fde4456fd53bc995c2e41652)

- Merge branch 'main' of https://github.com/yeongseon/azure-functions-doctor-for-python (40194d23ffe4160319e0d8c428b366e1760c5274)

- Merge branch 'main' of https://github.com/yeongseon/azure-functions-doctor-for-python (3459db77278e4d0a1a1a337b9e13e9fe804ad4aa)

- update release process guide to reflect hatch-based workflow (d0a814cd6222723180a3d10d6f7051041bfb2917)

- configure default and test PyPI repositories for hatch publish (931563cf2e6d5b463863fed12f7ffe0da79443b9)

- add publish-pypi and publish-test targets for PyPI release (f769088317f3e23dafaf4b0f3b3aa90ab98db31a)

- bump version to 0.1.10 (e7b53af13a317f886e95c88d3c5cce26a5e36ba0)

- use Hatch inside virtualenv with automatic bootstrap (e2bec3f660a7366a3255888bde1a519756bfa523)

- update changelog (95e1596371c72e478a87a1d06846b14fa8877bb9)

- update changelog (01d9c94bc3adba61f4921df9aee69ef063623e4c)

- bump version to 0.1.9 (5c6af020db3e59dd6ce32e6285aefd6381f8e8c3)

- rename CLI command from azfunc-doctor to func-doctor in docs and scripts (ecbd0320830548de7c74dfb48ab9dccb636c0974)

- update README and documentation for improved usage and structure (cae2b7191443d747d4ca3ec44a513b15b155e7cb)

- replace screenshot with lowercase filename for azfunc-doctor example (1bbf2e1db358d47508a6d3a69ba40f3063507ce8)

- improve README usage section with clearer structure and sample image (2af7acbe4c389aaf79890dbdcf3422beb41f1192)

- simplify changelog template to fix template errors (8bf9f9905508a44d4ad8e384ca670ce34e0036f3)

- update changelog (a973c03fb168c8b2df2231260dba9a030f6310e1)

- bump version to 0.1.8 (a339eb5cf40530e8b64a50ec5e8cb88db1453ed2)

- fix packaging path and changelog format issues (fb98bd2333be27ae023a7f62083f8468cf4640be)

- update changelog (1dbd7c5fc35cad09b973b524fea8fd7ef3e46a02)

- bump version to 0.1.7 (726b7b6d6f515327b4058ae10a602dcb90067f1a)

- remove unnecessary wheel target config for src layout (b1b8e60a37b4d11a8806bddc2f8a4ad598c3393b)

- fix ModuleNotFoundError by adding src to pytest PYTHONPATH (9e2b07136523a3ffeabfddec1263521918dd344b)

- update changelog (047381f9717d6989ed81f3c08dc06c29ea83dee1)

- bump version to 0.1.6 (4261829476f5868ecabd103cea5cff926fec7a48)

- replace 'import' with 'target' in package_installed condition (1ab3d0aa88019688f7c515248899828535818e7e)

- update changelog (f5485f8a54eb91bca222a081ff8bb6837e9b5f0f)

- bump version to 0.1.5 (18b397efb41e1ea0f198a8be5295c4f11843dc42)

- add __init__.py to assets for package recognition (7a1c6547f0d873a309ed9f6097cd157fc3a350c4)

- add unit tests for generic_handler including new rule types (c9cdede1f25868dd5928f80f0380614307d25a17)

- update tests to load rules.json from embedded package resources (695eb65c51a6184cd519860587c39b98f3a011b3)

- add 'source_code_contains' rule type and improve rule handlers (1ed6f7be63a5638c8b2fca1ca97a4598d0058059)

- load rules.json from package resources using importlib.resources (8af58a3caeead16090cdd93934fe65d8027fb4f9)

- move rules.json to package assets and update pyproject.toml include path (030fcee105a32d875f3eccfaa941400229e4a623)

- update diagnostics list for Python Programming Model v2 (be5f16a14b82869287753ef05e6702c4e7913b0a)

- update CI badge to match renamed test.yml workflow (a8d8ec356aedc4d0cf3b8671c264b167b799972b)

- rename CI workflow to test.yml (89cd70df618fceacbab2af6740164d1c842f002d)

- add Codecov upload step and coverage badge (663e0db6bb7eb514bc8ed0de94d5c522cda06502)

- fix diagnostics tests by copying rules.json into temp directories (7f61ea91a393ed127000af7f0c746ed08f46b9b6)

- move rules.json to project root and update loader path (35d76849728f45aaef0d2b2d643f12a641696eda)

- add packaging dependency for Windows CLI compatibility (30e0161ab33e5bf33211fdf0cf22f40be2989f72)

- update changelog (a1765777b493cc5cba2a7ddb548762659588f0dc)

- bump version to 0.1.4 (dfc1a2aeec65297d5a91fa42a7a1eded1a196ad2)

- fix packaging path and add missing dependency (40ae5e2d04a0362dffec03d5ac3992ad8565ee22)

- update changelog (3df3a2eb351dc39ba81d287902f48d3e08b6eae1)

- bump version to 0.1.3 (340053cea4359e2156a3269d04ecae5345b2c041)

- add automatic commit after version bump in release targets (69ba5da761dcd850ad96f9eb792b37a3b762e9b4)

- correct wheel target package path for src layout (86239d9c10037f2ec4aa635a108f42e5764c6888)

- bump version to 0.1.2 (4b1546283c0351c2fd5ad967452b39120564e7c9)

- update changelog (9dd6ebda32c8be419179331643cf8e17350380ef)

- remove unsupported commit.remote from git-cliff template (9f429fb328962d93492fce6f2aca50ec3e44ca92)

- separate version bump from release logic to avoid duplicate version update (3a3e1c24292b7c11d67ab6eaff4632a0add8b37d)

- sync tag and version, improve Makefile release steps (e97ec207204058e1ef7b2eefbf76e9b7d5c61b21)

- declare version as dynamic in pyproject.toml for PEP 621 compliance (41cc80d3005fcd24280533a66f7eda8b046b6ced)

- update README badges for CI and release workflows (628f8a7e21317f3ba744dde10da99a9ef5b47852)

- consolidate changelog for 0.1.1 and clear unreleased (07cfb5df5ecaf91c5e632a25774a037cc11e753d)

- generate changelog for v0.1.1 (d96c275d907f28f696f6128d7431b04e21ba86a8)

- switch to dynamic versioning and fix Makefile targets (7cdee62a6f7fe7a8a2f7220ae0a41a602b54403f)

- update changelog (916ee3d1b4d643192a9bcad2896a1b8d498c6482)

- update changelog (0b116f48d48621bb35b70543be1ba19786671ac3)

- use twine for PyPI upload on tag push (9af1dbe7778fd2c301e4ce48848285a902f86538)

- trigger PyPI publish on tag push (054d22632b406b5874f7240208654ca56b4840b5)

- reflect latest commits in CHANGELOG.md (bd094b00f7d5fe646d1b1f830e3adbb05fefbe8b)

- update PyPI classifiers to include Python 3.11 and 3.12 (7115bd5eb1783331d7becc723f15f92e962852f8)

- fix project name to 'azure-functions-doctor' across all files (4559727181598a2aa2af8cc3f527eda237fd1501)

- add GitHub Actions release workflow (48a45485064bc599e58ab8be63eb25e0dcfc8ce0)

- update changelog (4f1a1e658bd5705e85b1d9ccc058fdab11305e83)

- add changelog for v0.1.0 (2f9a0d00f273445314da3e2999a84010e4a5084c)

- update README for basic-hello with Python model v2 instructions (44e332998ce0935271a5f93f65d584289b89bd9e)

- add release process guide and git-cliff config (0984e73a19e2c814acfcbc178deee46876f9f66b)

- add changelog generation and release process to Makefile and docs site (7ebb433982852fbfe754d6830c1324eaf3bf2f77)

- fix packaging path and add metadata for PyPI (682ccc13226967caa1e46e0f43bf0a7849ae6edd)

- update logo assets with new design (2bf4fa1bd6f2a77186bd65adc1568ba7176ef280)

- add GitHub workflow, PyPI, coverage, license, and download badges to README (4d67eedb274af56ba76d68523958c7dad31bc89f)

- update mkdocs.yml to reflect new repository name (ce2b9515d5d97d884c6450ab5c9c7e8aae8d0c36)

- enlarge logo in README and finalize CLI doc structure (fb7a695b14a1e592d7b8393960a4e4e879cac65b)

- Merge branch 'main' of https://github.com/yeongseon/azure-functions-doctor (083cbe6af7cff4d559597eab35f4c8339c5f36f4)

- enlarge logo size in README for better visibility (fd9445c68b1d832420b0278389a61792d48970e1)

- enlarge logo size in README for better visibility (f8f6d9c0fdb14cef6a65d8dbeb7e964c8c02c16a)

- update README and add relocated logo_assets directory (c81e1424557d04812f63e78ab8deaea0beae2826)

- update README and remove old logo assets (9e19f37a161cfbf632f73f6894039e885a447deb)

- update CLI usage, main docs, and add CONTRIBUTING guide (884199ff408540d9ad52794ac7641ce6fe4eaed2)

- add official logo assets for Azure Functions Doctor (a69d52e77296937184e35fc4ac239f14024469f5)

- update project title and links for renamed repo (bb6f59afef6106ae91bae9c23672bb20c03ce074)

- restructure rule logic and output handling (cf49aef15c37d549d2275d6303a93c8e025e9f28)

- Configure docs environment and ensure Python 3.9 compatibility (982387b0753091a1ed1f3b6e4500e104bcaa7ff6)

- Add MkDocs config, Makefile target, and GitHub Pages deployment workflow (47b935ae36e9c2e8338a454a2a1f156770afd42e)

- integrate API auto-documentation using mkdocstrings (e59e3ef61e1a27c32ea0fbac6e1578d9622d2713)

- restructure check logic and improve test coverage (1a2709c9f03fb6b2492159d4005bf232a45b9770)

- Modularize check logic and add handler registry (21f4f0f118e2dff7593f6b3624657a0c1bb5d66d)

- update main README with installation, usage, and example links (310a437331cfb5211897c09f50a06d6400cbb8ba)

- add README for basic-hello Azure Function example (bce8b849e73e7236e1948e23f6baaedf80eceefd)

- add basic hello world Azure Function (HTTP trigger) (659362e063ed33745a552fceaa0b7d8afb0303be)

- update development and usage guides (8e262c92567a27b94d426d3cf09ead74ba4a5dab)

- fix artifact upload conflict by including Python version in name (d8fdca4e8f47a4827a60fb3d3a218f02d886a41b)

- rewrite CLI tests using subprocess to verify full entrypoint (41b02e4faddb622d2ecd67dafe91fcdf163ac01d)

- improve diagnose command with rich output and verbose option (27f9cc259b30097840a9155b44c9d1c007b1c45a)

- increase line length limit from 100 to 120 for Black and Ruff (7e9808e4fdb567a634ea6bd97deca6e9aebb0fba)

- organize pyproject.toml and include py.typed for PEP 561 support (eab6e83360a1134893ecff15523874d48b8b1c9e)

- add modular checks and API compatibility with diagnostic output (fd98178733cd08c27e85a53849065c8e2b81a54a)

- modularize doctor checks and standardize diagnostic result format (692eb93a4a9df51e5e16351befab049c999d9782)

- update diagnostic checklist with unified table and official references (ed64d6e7a682a49176a0ce35877422bed7718480)

- explicitly register diagnose command and fix CLI entrypoint (e41ed3548d29140c801b57c2d0abdb1a2727ceaf)

- migrate CLI from Click to Typer (253e8c047be3d65cfd4a97bf7f8ee358bc547101)

- pin tool versions and unify configuration (bb49a027ee23abe8750f25363cdff8975bc083c4)

- improve Hatch environment and pyproject.toml structure (f1a33615598bb90c3c1dfb6af7c8520b2f4aafd2)

- migrate to full Hatch-based workflow with unified Makefile and CI (8127be701f006fb22be094eb4b1233ec16c54b5b)

- add CLI usage, development guide, and diagnostics roadmap with mkdocs config (779384836e773f016f4a3fc06c77f028e6815d66)

- add commitizen configuration and Makefile targets for patch/minor/major (ee464494be83929343ec749180fc2cd84dc25590)

- add initial changelog with current features and setup history (4652ff36bf36321d6398e5e00a98b4d7b2b2c9cb)

- migrate CLI from Typer to Click and fix typecheck/lint issues (e7482b6ca27885db50125f19778755dc7e051ecb)

- remove .tox and htmlcov in Windows clean-all script (483f5c5656acbcab4d7700fa9fbe7a832f13ce50)

- prevent NUL file creation on Windows when checking for uv (3eee166f5376d43d0e0f6c6792b95f7b2e5cb751)

- extract Windows clean commands into scripts (3a063b806168e5f09242e84275c3ecec5341ef35)

- update pyproject.toml configuration (e12a26300588a189bdc37f70c1a9a485e7e1b2e8)

- add module-level and function docstrings (7ee433ab4f9cb35877e8ec82e00068cc0decc574)

- add tox target for multi-version testing (13bbef209db339bfa4df3713d1efec8d170806a0)

- configure tox environments in pyproject.toml (0adb6ad2d065aa349d1d0629a42ca21641e3a6de)

- add cross-platform uv detection with pip fallback (285454d5828f11f1e240a7887b5b246f047b5aa7)

- fix missing venv setup in GitHub Actions with uv (6a01121a52b4a5a94a19f6ab58d846af36b550a0)

- fix missing venv setup for uv-based environment (f912cbb6fd34266a4b3ebaa9c2b14bc5179c7b00)

- clean up tool configs and improve Makefile portability (c73237982ef1cb3bd73808b43367d7bbc59a3790)

- update README to reflect renamed package path (2af0995e215ab28099b0afb50356c98904579997)

- update site name in mkdocs config to match new package name (5e05007611c5074f659c6cce093f3d35add55ea7)

- update module name in documentation to azure_functions_doctor (206132cd430685977c4f9ebd406516b45fc9a1d3)

- update coverage config to match renamed package (35cb199d434d7e47c625f23c9fa612eab945018f)

- update hatch build path to match renamed package (10d17bd6f177cdb2acdd366a923110d2dc24b139)

- update pyproject.toml for renamed package and mypy/ruff config (3b11ad1f0160f2a92615c86458c1db117c030c3f)

- rename package from azure_function_doctor to azure_functions_doctor (92783158cc044f7074afc94a5582807f793bf9c8)

- update .editorconfig for markdown and YAML handling (27100660adcc0bbd7babf4ff9d942e4cb39238ce)

- add .editorconfig for consistent code style (f69d3e3ee8f375664fe22f63e9091d9578b78919)

- finalize dev environment setup and update documentation (1e932f8becbc00cdd9d42b3168b4711bd80259e8)

- convert test_doctor to pytest format (4a3acec18f495c1727812447fb31f69fe4c86863)

- add pre-commit, coverage, and CI configuration (329d8a78a2e3f984aafb67798686c82997901c17)

- add hatch-based release and publish automation (b08c1b69a1ccfcbd08b656af0d26592c564dbb83)

- migrate to pytest and update Makefile test command (a9f54096802786c57bbb32073ff023344d77a4c2)

- apply full initial setup with CLI, testing, and formatting tools (153aa236852935e6be5cad498f3bb2004b6cec77)

- initial project setup with CLI, Makefile, docs, and packaging (a39efbd9a2d2b953905b6ce3925badab2b44c117)

- Initial commit (457425ebde591e34042116d1e5f92ac7006a03cd)

