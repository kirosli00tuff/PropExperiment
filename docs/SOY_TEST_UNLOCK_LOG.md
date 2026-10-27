# Soybean-complex test seal: unlock log

Append-only. reports/stage_e32_briefs/seal/soy_test_seal.py writes each entry BEFORE any sealed byte is decrypted. Do not edit or delete entries. Kept apart from docs/HOLDOUT_UNLOCK_LOG.md on purpose: data.holdout.prior_unlocks would count a soybean unlock entry there as holdout 1's.

## 2026-10-27T05:54:55.007032+00:00 SEALED soy test ZL store ohlcv-1m_ZL_v_0_2010-07-01_2019-04-30_ext2010h.parquet

- file 1 of 114: data/processed_hist/ext2010h/ZL/ohlcv-1m_ZL_v_0_2010-07-01_2019-04-30_ext2010h.parquet (trade dates 2010-07-01..2019-04-30)
- plaintext sha256 58bab10295af02267c1226770217053423651e8cb143593b8589bfcaca020812; sealed sha256 f8278363ab496f3e87d7ab7c29a9a382fc0f5185089e7f838f88327bcf8ebeb0
- manifest sha256: e57518d73407f5ed6d0c298afa118505c81a75c8ca639b3b977d4b12fd7c9f9a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:55.680002+00:00 SEALED soy test ZS store ohlcv-1m_ZS_v_0_2010-07-01_2019-04-30_ext2010h.parquet

- file 2 of 114: data/processed_hist/ext2010h/ZS/ohlcv-1m_ZS_v_0_2010-07-01_2019-04-30_ext2010h.parquet (trade dates 2010-07-01..2019-04-30)
- plaintext sha256 ac1fb0bafe34fdcba89a64709a38069d5dcdd103951dd4e3ac1ca8cd00176f74; sealed sha256 15601b014aac76ad173d83befd6b1d032e5896a5f5a2f9728b73e9fa2bf1aae0
- manifest sha256: 742ac6d42c02cd052a3a03f0bf69b6481e7ce556a024dd8e598dc2d17c8d769e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:56.152188+00:00 SEALED soy test ZL store ohlcv-1m_ZL_v_0_2019-05-06_2024-02-29_step2.parquet

- file 3 of 114: data/processed_step2/ZL/ohlcv-1m_ZL_v_0_2019-05-06_2024-02-29_step2.parquet (trade dates 2019-05-06..2024-02-29)
- plaintext sha256 d863413e75c01c59ea802a9225bc39b7439e3bca5e57841ead9aeb4602000bb0; sealed sha256 b925cbd9c49f4a5f1823fda0f49e23465ed879982ebdbdff2ba3c2a88f882d96
- manifest sha256: 5184df1f5fc4840a097f252c32a00b00e960472069945a617cddb415294a319e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:56.564688+00:00 SEALED soy test ZM store ohlcv-1m_ZM_v_0_2019-05-06_2024-02-29_step2.parquet

- file 4 of 114: data/processed_step2/ZM/ohlcv-1m_ZM_v_0_2019-05-06_2024-02-29_step2.parquet (trade dates 2019-05-06..2024-02-29)
- plaintext sha256 422d70575c74acf9825908f3b38384457595a382ef3cbbdcda4e36ffcbf0aac0; sealed sha256 eb5d688c34457a052832f84fc777316af6aeb87da9ff670b07b5d87d079adc27
- manifest sha256: 31abdcfe1d3f19538f20cb8ee6dc40491e74b944c3dc5ca718e3033f4a73316d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.016005+00:00 SEALED soy test ZS store ohlcv-1m_ZS_v_0_2019-05-06_2024-02-29_step2.parquet

- file 5 of 114: data/processed_step2/ZS/ohlcv-1m_ZS_v_0_2019-05-06_2024-02-29_step2.parquet (trade dates 2019-05-06..2024-02-29)
- plaintext sha256 bc46610d4b99ae4bf6808d12ba05cd4193f4c1e3423c84f58c29549f7a3d30ef; sealed sha256 06423808ca76a02c0b4f9380d63a88fab5b425edc853c3fe1fba1318d64c4524
- manifest sha256: 9eda46ffe85b50e041f6bd10775745c42fd3b49d617e99eb0b67503e553134f2
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.150501+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-04-01_2017-05-01.dbn.zst

- file 6 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-04-01_2017-05-01.dbn.zst (2017-04-01T00:00:00+00:00..2017-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 9a8232d6d73a7ab05a8292e43bd8cdc133a5be3d1401e5eb79a42c2a665478fe; sealed sha256 8900f97fe780dfe03219233e39262ab82d9f73f799f839ea008b1731fb80762e
- manifest sha256: 6e97d897de19722e68ed59d4dde4358f1da40628e9792881c264ff31f474b9b7
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.284746+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-05-01_2017-06-01.dbn.zst

- file 7 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-05-01_2017-06-01.dbn.zst (2017-05-01T00:00:00+00:00..2017-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 f49768910d672f9b3eb757880375b725f3a7bd9121012bfd213153b480588f59; sealed sha256 1c474369fa6fa96fda7f3c72d9f73c030a3ad5c7943dd6a450fba402ff5e1a76
- manifest sha256: 82d6cd4ed28a95b671a7ac1a97eb852453dc681ad6a6423c3aaaed8c0cfc4092
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.421256+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-06-01_2017-07-01.dbn.zst

- file 8 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-06-01_2017-07-01.dbn.zst (2017-06-01T00:00:00+00:00..2017-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 7181745e11b2f50c8cf5ea87795356b49fcc3e663a59fab9734c6f4373a13e21; sealed sha256 791bb47fdaf38f1d7e4aeb59e095a0e69ac9823e1b5eac0de49e269198660b5d
- manifest sha256: e5f7ac71bd35443978a5658dd8f65410d69309226387ca196d888cc81bda2639
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.552164+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-07-01_2017-08-01.dbn.zst

- file 9 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-07-01_2017-08-01.dbn.zst (2017-07-01T00:00:00+00:00..2017-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 0ef3403d4d84de38297120c30822ac5182d29ff02cd71aba479cfb05012273ef; sealed sha256 396dc8f5139002ef0f95a7dda259d5e46803a04167fc4d4703e2d2b25b4d8d5d
- manifest sha256: 0baddbf130035e511206bbd8251146095070bac30fdb3c36f3be0c649d627ac4
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.686740+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-08-01_2017-09-01.dbn.zst

- file 10 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-08-01_2017-09-01.dbn.zst (2017-08-01T00:00:00+00:00..2017-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 e879c90cf129e205bd5906df07691e87e4a8b02974569e3474ca3050d48b5773; sealed sha256 1c8d37711d6b9fb32e4a60426b8594397b5992fe4e6e00e379f6a7a99fb03942
- manifest sha256: b69f124ffa1a0dedebfca9e520630a0e3365ae3c97a4bf7880d1495b7d1b4e93
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.827483+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-09-01_2017-10-01.dbn.zst

- file 11 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-09-01_2017-10-01.dbn.zst (2017-09-01T00:00:00+00:00..2017-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 d4fb7b762eeeda02a8c1ae43ed0169717ad8471e6527746c1d7e0a380d0d22ab; sealed sha256 0d0ee1ae954224ce19cd56e4d727c15a7411c49402617a93c540a353111d49bf
- manifest sha256: 23e4740405a996f3ec425256aa7ac7f21831ee942a8a31aff3316628d9de2f44
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:57.977743+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-10-01_2017-11-01.dbn.zst

- file 12 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-10-01_2017-11-01.dbn.zst (2017-10-01T00:00:00+00:00..2017-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 ce0174002b6c7f9d086c902b6f80b1e0a95c3cbedeffd23c7314db2f267147c8; sealed sha256 62b8f44910eb6d44f90dad88f28e1441c9b160fef0ecdceba4124a1beee004dc
- manifest sha256: 5ee2433fafa3f7dbe3a4441731cdcd4fbdb254ef1ee342aa40c97e71af8ea027
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.121261+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-11-01_2017-12-01.dbn.zst

- file 13 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-11-01_2017-12-01.dbn.zst (2017-11-01T00:00:00+00:00..2017-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 a25c80112c3bb88b67e8e13a0c62e2a1fc5abcbd865ce88e0cc82bce82f410d4; sealed sha256 20751e08a31e1905b7228319455499e80fdf5c74f4a4ee0d3d186515755ee14b
- manifest sha256: af144640c9b3945b06421c652995c174c590d6aafff53756ae22ae1b85ede39e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.261560+00:00 SEALED soy test ZL raw ohlcv-1m range=2017-12-01_2018-01-01.dbn.zst

- file 14 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2017-12-01_2018-01-01.dbn.zst (2017-12-01T00:00:00+00:00..2018-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 b9eeac6d66f561a5af38d4369dd80ae11832e14e1c55a092e4b222fb673a5c3e; sealed sha256 9a7ed1cf635f7bd79cb7baa5969f1930a3274d816ba7d5207cc620a280bf3616
- manifest sha256: e3320a2039d963b8749607939311e5b4f4f3d3750512f3fdd4b14e17bd2ae64f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.400564+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-01-01_2018-02-01.dbn.zst

- file 15 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-01-01_2018-02-01.dbn.zst (2018-01-01T00:00:00+00:00..2018-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 0d735b3443d02f8ff736c7ae152abeabdf5df57d2a5cd9f70a165c2b065d62f2; sealed sha256 61e14b8c4c18ea818aacf141cb1876fd076c08908bcc89d71fb0409378267ba0
- manifest sha256: 225e09ba1b702cb8e20ef5e8e35290d25a4e18d271cbdc3ce2414af77ab94555
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.538499+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-02-01_2018-03-01.dbn.zst

- file 16 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-02-01_2018-03-01.dbn.zst (2018-02-01T00:00:00+00:00..2018-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 04d9610ffb43fa526cb85d4afefd4b3b895fab87a1ea6f626ed604b469dae538; sealed sha256 1621f5736ad8d3edf635f42a2dd0b17a01fff6b14aabb3fdd25c3da7e5417587
- manifest sha256: 583f6213e06f3918f78edcd5634b8fe2370e41a9a9bb719f8d6f41b20de7d24f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.676432+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-03-01_2018-04-01.dbn.zst

- file 17 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-03-01_2018-04-01.dbn.zst (2018-03-01T00:00:00+00:00..2018-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 51df09823a41a819138dfdecf5199d298517654ac19b179ba52c7c70b04f0c1c; sealed sha256 0710ab70e76888eb42e6e016d8de7ff29fa58742ff9059581c0bd16795f11e15
- manifest sha256: 753f1159ab876e7c0bcaa9c27a504034d02fb920dfb54bbc8e4305c21ef7245d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.809854+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-04-01_2018-05-01.dbn.zst

- file 18 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-04-01_2018-05-01.dbn.zst (2018-04-01T00:00:00+00:00..2018-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 ef05cb6943f70813c35c7bfbd134b1b3ee7d5b12f71af45eeae2f57932b44ba5; sealed sha256 9c6ca68ff1a773e3b49944240ff922b27794d01d2afdd21c5e99090e5dc856ec
- manifest sha256: e66de2798299b8dcc853f51ce8c598b4bf493685f2bdb092c46cac111ac25b4a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:58.946429+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-05-01_2018-06-01.dbn.zst

- file 19 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-05-01_2018-06-01.dbn.zst (2018-05-01T00:00:00+00:00..2018-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 c399628e1dd8d1f23c45d37f10671cb9075c0a527edc43d320e3cbaaa641cb48; sealed sha256 8c06e5b5741555309bcc936334e8e524a7282ea887d76102415e537fd0e17181
- manifest sha256: 572e192b59bab2c08db5995af9e40006b706f140776ee9e7f225c21f71dccd58
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.085749+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-06-01_2018-07-01.dbn.zst

- file 20 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-06-01_2018-07-01.dbn.zst (2018-06-01T00:00:00+00:00..2018-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 92d4758ac14348b3e055ec17abd40adea7879eed35b53b85ef7cca60119cef35; sealed sha256 88e84acb2c04bb4e80c829ddcff88784e3dd7c903d2a3fa71213a26333e66be4
- manifest sha256: 47a454f5644308038b79ef3361fcd140c9f19379dca58769eff8515ea02c049e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.219096+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-07-01_2018-08-01.dbn.zst

- file 21 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-07-01_2018-08-01.dbn.zst (2018-07-01T00:00:00+00:00..2018-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 9f304a1fc4b8ad5ab61003fd264c0df4626ae1cd068b1bcfd31ed4bcfa66d697; sealed sha256 b6b17cea69794549f63437070bc58827969205bc85a0af2b69900c436750b7e8
- manifest sha256: 3e5f0f7874e1dc051e6fc406c86f26abb6c5e41295a36427d8cccbbe528499f2
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.353616+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-08-01_2018-09-01.dbn.zst

- file 22 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-08-01_2018-09-01.dbn.zst (2018-08-01T00:00:00+00:00..2018-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 c7df99db9a463014a48ffb91660c832642cafdaeb36ac5c98b228478840be3d2; sealed sha256 8e07c2e938fc3785b6d9f69ee7570cf7a85fbaa5cd552b7c5936be82dddba51b
- manifest sha256: 96e0fb29aad6a045ffdb83607fac9e6153d75854eddcb8c057e7231a6cde2856
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.485930+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-09-01_2018-10-01.dbn.zst

- file 23 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-09-01_2018-10-01.dbn.zst (2018-09-01T00:00:00+00:00..2018-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 c7d76b194a712aadc1ef9e8613df62521ddcf755538f09265656986cfe075a61; sealed sha256 e08fe16909310e2540af42a664ed42fba86ea81f40ea57acf974193ec7c6f278
- manifest sha256: 860aa9a98ba108dbf44c8f1381566aa94b5632c25a2ca0cd3c39d05b2ed4d409
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.620236+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-10-01_2018-11-01.dbn.zst

- file 24 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-10-01_2018-11-01.dbn.zst (2018-10-01T00:00:00+00:00..2018-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 8ff1c896ce1a152b1ce5e5c9c40f4f833cd01e16d65980834d3ebc307ff0dda2; sealed sha256 aa97ef9c1c637a78170faa44602bd311098afc89e4c0a23836a944a3e95434a9
- manifest sha256: f821802437cba88b20f7ee5aca0b69b1fcd7fd3863e5aa16952a5d10b613c2ce
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.755477+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-11-01_2018-12-01.dbn.zst

- file 25 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-11-01_2018-12-01.dbn.zst (2018-11-01T00:00:00+00:00..2018-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 9ae9cc5b06fff433176d9975b5149c7f19ea5d0cb42fdb429165ec5a2dd920e9; sealed sha256 d190854c487c8eff50dff3783cdc5c533f5cc4221cce2eb3fe527c2829bb1977
- manifest sha256: 1507551dc99200197fd1812feeb8b53dee8c13acb9dea250e1217ae3580fd77c
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:54:59.893961+00:00 SEALED soy test ZL raw ohlcv-1m range=2018-12-01_2019-01-01.dbn.zst

- file 26 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2018-12-01_2019-01-01.dbn.zst (2018-12-01T00:00:00+00:00..2019-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 85a1334153bd2ccb4301d5390194acb956f93d098eba0ca23798b182723183f0; sealed sha256 3e0218d652b1d90ab076faa7fc0949b6ffa63e968bc2ace12502fbadc61f6e6e
- manifest sha256: 705dbbacc3d5efec59e18370cd6a9602f08168f95a712cc82e7cda759bfb1858
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.028970+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-01-01_2019-02-01.dbn.zst

- file 27 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-01-01_2019-02-01.dbn.zst (2019-01-01T00:00:00+00:00..2019-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 7936121f28d782207be27f75ab1de8973a93f4fba0110c638d6d9fd7f6a1ceed; sealed sha256 68b333b487c2eb060b78b3149c2787188b320ad9a2aa0f1ebbebb9cefd57480b
- manifest sha256: bb6b5d7de9e40f96e982ea8f72f0ab3c60abee7d955c6eb29a9c203fdd844c04
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.168638+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-02-01_2019-03-01.dbn.zst

- file 28 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-02-01_2019-03-01.dbn.zst (2019-02-01T00:00:00+00:00..2019-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 39b793628abeefa8d67ef051b34afa60e3db6520875f6d7367d08ef7f17d9a2f; sealed sha256 ad9d960977c0e6f44faa3cff53369e2dc18fe128522fdeeb0190985703f00f80
- manifest sha256: dd6400e961bd4a67d7def3cc39ad8b2f16016e143577aa808a3b82d7b8330504
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.301449+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-03-01_2019-04-01.dbn.zst

- file 29 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-03-01_2019-04-01.dbn.zst (2019-03-01T00:00:00+00:00..2019-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 3122a5b48ac41ca541eebd49c067379c9d99fa1a7004bc5a3291a508e669e84b; sealed sha256 81528be21162caf3f4178cd089bf9a4e0938aa4365ab53819b443fe293c3308a
- manifest sha256: d47fb82a2a61a1c92313237180571267be2f384f300d720dc20b174047d97dc8
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.434262+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-04-01_2019-05-01.dbn.zst

- file 30 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-04-01_2019-05-01.dbn.zst (2019-04-01T00:00:00+00:00..2019-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 b430f01834d917d5373995bb0a38f12410b9b50a71cbda394910b3a3135d1f39; sealed sha256 fa7f5db774f1f37cf3f171fb96a243af972b1036c9db838403d1de74c0bd4bce
- manifest sha256: 94c8a6fb5ead0ea8180988e084df10a5fcaba663432a352e47999d0ab250aa89
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.576175+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-05-01_2019-06-01.dbn.zst

- file 31 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-05-01_2019-06-01.dbn.zst (2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 00830b938fda418535a1ce406d4f6941494bbab38fe8eb75ba4d5e92364b01aa; sealed sha256 e4b136205efd538753e6de92a0f39c6167760aeafd297b67e72c5db2b7d9bff1
- manifest sha256: bdbbf338544f75b6c77742500e5ffe71b2af735889decc86d3e5f427bf8f038a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.715996+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-06-01_2019-07-01.dbn.zst

- file 32 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-06-01_2019-07-01.dbn.zst (2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 dc87c5378251210a0428a31a906bf109f6f67ccc3b7d8c7bd6c0e9858de0376d; sealed sha256 2574400b85ad0a8ca2ff3a70be62da8ba9b769f8576484d2ff8a58f43ebb560f
- manifest sha256: def9f368885676fba318be5b2559ec3de20dc140621bb3e5a26c4c1728ec8348
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.851787+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-07-01_2019-08-01.dbn.zst

- file 33 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-07-01_2019-08-01.dbn.zst (2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 d367a48504aab6a1cbfebb8db97966d345dbbe3091e9d0baed253489f0d9660b; sealed sha256 fbf7490bb5f060e0a84eb98b0b7fd7219f91d4fb03882393d3fc9cd727846514
- manifest sha256: a7206690482e446e59945676d4c0b53082b9687a53f28855fb2cb4aeb7706ce4
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:00.979921+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-08-01_2019-09-01.dbn.zst

- file 34 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-08-01_2019-09-01.dbn.zst (2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 2cbf7c5d8302de61fb5aed29305ef7e883491906fbdb63032c03a05322d3b582; sealed sha256 c9f1b2fa68560865258f8aefc1dd7805d02c1ca2baed265a258c07128cbe8e64
- manifest sha256: f0063d950af49974aa3bb515739bde7c3ac49466634190a52dd8d34e052e83a7
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.115416+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-09-01_2019-10-01.dbn.zst

- file 35 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-09-01_2019-10-01.dbn.zst (2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 342ce1b1efaf1183d14942eb840a939b7e0ce6a1568daf1f04efe9cadd923124; sealed sha256 c3725f0f28bad3d8d397e0c36d22ecee525e8dc0ee15e835ea426d4fd39bf6d4
- manifest sha256: 696bb4c4a666b5dfb0e047acf4a9df9e67b8be42f2038878e53d64976465b3b5
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.243596+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-10-01_2019-11-01.dbn.zst

- file 36 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-10-01_2019-11-01.dbn.zst (2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 d259f1158fbd096e36f3da1528f5acd0c9228db3cd3eadcedb1eb2aafee8ebad; sealed sha256 0c9cdc1b3dc2fc8bf7fa53d17e5825d160db6d428f1f58dc6331e393cf3c97c0
- manifest sha256: ba5566309c50fc1d851e2ba667573cb9b8839d246cac219925456b3127544b9c
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.377540+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-11-01_2019-12-01.dbn.zst

- file 37 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-11-01_2019-12-01.dbn.zst (2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 05dc165d33db0b6eef6719ae5b3de6f80e1aa0185cb1290a3ff71760de3312eb; sealed sha256 444f7c5a3768507806815764412ac74b1467152ae12c385092a76976c189f5c2
- manifest sha256: 0615dddafba6648f3ad5b621e760da7ff04246525e0ee404c33e3fd475cfd8b3
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.517721+00:00 SEALED soy test ZL raw ohlcv-1m range=2019-12-01_2020-01-01.dbn.zst

- file 38 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2019-12-01_2020-01-01.dbn.zst (2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 8c1102b4858761213b2f824e7a929a6fd81a2d1f8ceb607e989844a984188ae8; sealed sha256 8ed346cb6432a970568712096215d1f0b87d8d6cf118f2581669d58e42b6468f
- manifest sha256: 332b38ef00d13a495969659fc7c4692f9c1be9f33c96f8244d47f17d287746ac
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.649579+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-01-01_2020-02-01.dbn.zst

- file 39 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-01-01_2020-02-01.dbn.zst (2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 aa6648c4bb7f4e4990e94eabdd62b2796025bff480f6e5c329f875c6f3452b25; sealed sha256 0e158e0c900c34213be7369d93636d2597ebb297faacdb971d88cf692cb3b521
- manifest sha256: 73ed616706b720ea206d89d2f98eb22da3827fb090ced35279798fcd30af8566
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.777326+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-02-01_2020-03-01.dbn.zst

- file 40 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-02-01_2020-03-01.dbn.zst (2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 add216b064bdf486f62145bc0068b14558fd85a34041d1ea1cc4fd01a0a72f02; sealed sha256 e6c61e30c459d6e7dd97292f5a78b41d052b651a05e5eba6934e8b3b5576b4eb
- manifest sha256: 335e9a4f89b0c95aa667c3d98e6c6a421455c10e3603635a02dca04f6b4c1e34
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:01.914807+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-03-01_2020-04-01.dbn.zst

- file 41 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-03-01_2020-04-01.dbn.zst (2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 c5f1a6d81fb4b526f5d177cdb4c8d7f0ae69a40411c843b030a8d95bb2079510; sealed sha256 019b7f6e655c017a7f173867390a55e88f4309c474e45635a7596f3c3fdc442d
- manifest sha256: 5e5f348c078f4a541691d90519109511b935f92c22f10609c6c7d1d995a509e0
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.052599+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-04-01_2020-05-01.dbn.zst

- file 42 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-04-01_2020-05-01.dbn.zst (2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 aafd0b6c754f68783a0d02e39606662770b2bd046b5b3897c06f8abee911fc0c; sealed sha256 b21303089e7b05f8881ab0438bfa7701cb04474cd72bc796c62c843949face54
- manifest sha256: 38072db5ec093f8bd8a4f1f0ab71f33cb03e2c40403cff10c3576c8228c53c3c
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.183841+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-05-01_2020-06-01.dbn.zst

- file 43 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-05-01_2020-06-01.dbn.zst (2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 cfc5924321c16a726a0cf192514a5c337d73cd8bef068f7e98ba8d0773648049; sealed sha256 10c7b669fa5e71a32de87d042f44e9651526fa69b905a832670d3cd19cfaa235
- manifest sha256: 27c76b85ab369cd1b494d9533f65c4fba61144704e76957f06773f04f8925209
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.314981+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-06-01_2020-07-01.dbn.zst

- file 44 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-06-01_2020-07-01.dbn.zst (2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 86203bc0d5df7c5f6a2ccd8fff53282c24cd8f8190aad61dcdbb8714262650cc; sealed sha256 9c276bcfec86f175832e858aad45070258d17bb2494287e3d45ce01d260615b8
- manifest sha256: 8b0214ad7a789731d1f3cedbbad787fd3b1420bb3126302302a75de72665d260
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.447748+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-07-01_2020-08-01.dbn.zst

- file 45 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-07-01_2020-08-01.dbn.zst (2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 781708b71c86ba717de477ddb46d03a5c9ca0a451043397f4b9817ceaef8373b; sealed sha256 e67ae8d1d45856312ca7c83107fd8850f71c4beb9e5656924c843071ee4c74eb
- manifest sha256: 1600baddbf99066279ab05d4ee78a89cae2864b1f2a71a529f11447bae262688
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.593742+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-08-01_2020-09-01.dbn.zst

- file 46 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-08-01_2020-09-01.dbn.zst (2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 c5673c9caaec026616869dfc98a0657a55833c8b9a7bfb43257240a48d329f8a; sealed sha256 b9e8473277b642fb94be03dffe7454c7a55bee14de5b98633190b5a460ab82ac
- manifest sha256: fc0eff6c43ac65d0c93504e71738209981fb221433ca2c0ce80339df0a1452c1
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.736441+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-09-01_2020-10-01.dbn.zst

- file 47 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-09-01_2020-10-01.dbn.zst (2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 9c0cfc37de987434bded3a92612d0b226966a9267e7e6dd62a35dab31abe97c8; sealed sha256 855273f0d7f053ab8a99f4c3101dfd4692287930c888fb92f814083b734578ad
- manifest sha256: 28c8a7a024f501a07f08ebbc130dabfbd0ab43c53b29eff7579dda6e555cc63d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:02.879246+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-10-01_2020-11-01.dbn.zst

- file 48 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-10-01_2020-11-01.dbn.zst (2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 b95ca40eaec8d3cd55d5d9e79d2180e3c04f0c6b0bb10a2853bbcdf20c667c39; sealed sha256 fe83d59bc32e2b7120b366504a4869e1ac77761e55f6aaeeb7654bf6540243ae
- manifest sha256: 22550a7a8c699e81a41694eb3c43e050b7339e25cf601962013856f794b2c10b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.027075+00:00 SEALED soy test ZL raw ohlcv-1m range=2020-11-01_2020-12-01.dbn.zst

- file 49 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZL_v_0/range=2020-11-01_2020-12-01.dbn.zst (2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 e4db5a31e7baa6024c2b3ef47cc1c04bd44ef47bafb16a2cd7da6ffa365d14a3; sealed sha256 ff4f68fa2e14427b98d07caebd96b6a6bf41fdf3bee80592f3546335eacb4354
- manifest sha256: 0563f01d53e142b11949bfdb07a9c3d2237a327bcf9e048f6bbf0a843cc89127
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.162743+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-05-01_2019-06-01.dbn.zst

- file 50 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-05-01_2019-06-01.dbn.zst (2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 514878c83ae7bba343a1f23adb5ef9aa509c0071f4e726b65a6d20cdf17de8fd; sealed sha256 9e075b86564e60315a3b7021cc6db0fc0e12f9adc1c2f0bcef0763d6b73d2c33
- manifest sha256: 71222d24d6e4b0c9ccd787d49c686d6df21de758920a6390b67bcc6f5833891c
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.296323+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-06-01_2019-07-01.dbn.zst

- file 51 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-06-01_2019-07-01.dbn.zst (2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 974561bd126479a78de05e11b523484246a632ae05f01b05e18fa22ed51c6c53; sealed sha256 117c2981271c820bf647f8df4c31a758a15ec432c1872580c0525351afd3a27e
- manifest sha256: 23df9cff32f29b179e2f9fcf5e4804c04e05ae51de9b331c087bfab6fa58b572
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.429096+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-07-01_2019-08-01.dbn.zst

- file 52 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-07-01_2019-08-01.dbn.zst (2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 80993923f31bec51ad4ef3b48b4ddc107b5d7a76c88d8c522be04b740dee5cea; sealed sha256 af746a7ced405ca05bf375f2b350d4ec7da314db726bd76ea0f90db653f0221f
- manifest sha256: 46d693eb9c5b35218fb0f69174e8991cfd39847c200e771b9c3600f8bc48b355
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.564914+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-08-01_2019-09-01.dbn.zst

- file 53 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-08-01_2019-09-01.dbn.zst (2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 61d567e39c74a376762aa46d0362c800cab80fad0c3982e6c98ff73e4afc7d50; sealed sha256 43b828b06acfd1b6a94a561531ff201e825c0d6f5bebd46f01bd10be1d36c947
- manifest sha256: 0c1d9c30503024a8519512e4b2d68d8542917099373565e902a5ea644ea0028d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.699780+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-09-01_2019-10-01.dbn.zst

- file 54 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-09-01_2019-10-01.dbn.zst (2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 f5d17346d7c4569d1d1857026b6aa2b3068ec31ca25f34f8d4e1037528a849b8; sealed sha256 46d94a9161e294ddb6a13ba0fea9eac2e2db3635263d334e0ac3f7033c3772a1
- manifest sha256: 1281577316687c15d14c40289fc95d043720925a119144af335cd3dc9ce47557
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.834252+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-10-01_2019-11-01.dbn.zst

- file 55 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-10-01_2019-11-01.dbn.zst (2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 7befa359ac65a07d957b31c0370f63edefb8b4cd56ab32bc1aea584db2c76b1a; sealed sha256 19954f3a08095345e4463d2ce8d36f6658462aa326ede1c67fee42a42b43fff7
- manifest sha256: 159b243c142812f54c49fb22667423644d9cf1ba28799ee6e5814d27a7d188bc
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:03.968574+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-11-01_2019-12-01.dbn.zst

- file 56 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-11-01_2019-12-01.dbn.zst (2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 d167a52de8524063474185b505b6a12cd991a35173ee0c7027e085ecd690b4e0; sealed sha256 3719339db4b8c3a83c6a189a871c258fab739452f02b1f581aa7210c5b0da0a3
- manifest sha256: 4cdfa8b984a4fc855ee1ca38e192d8bdb54e5a742f4e864a911112f28c46a107
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.103901+00:00 SEALED soy test ZM raw ohlcv-1m range=2019-12-01_2020-01-01.dbn.zst

- file 57 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2019-12-01_2020-01-01.dbn.zst (2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 03a8997e6452ffa13a290cdf6528ecded8b4a1f85d4644474fd576f9a90857a0; sealed sha256 83d3715770590520ca4c72a2a569e5c9345e5b9e7e55bb6b6afe71d695ca9949
- manifest sha256: 214f952fc73e0015133c0c70aca68a0039682c357cf80e9630472bad619f2be4
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.238331+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-01-01_2020-02-01.dbn.zst

- file 58 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-01-01_2020-02-01.dbn.zst (2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 d00f9afca2515e14a19f47624c63d165f3442cf9080b5e8853572af6b3bb4042; sealed sha256 68e46dff94305286a545aa6562626ec6ac389a8fac4967861aae05f6d7419093
- manifest sha256: b666cbc307f7ba3bfeb6984062a2f6da0127878609daec73c13b2dbea85abfeb
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.369836+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-02-01_2020-03-01.dbn.zst

- file 59 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-02-01_2020-03-01.dbn.zst (2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 d15e871cdf4f7a9713f66566991d529e1e5f325e8d7111ee4be4f07b320fbce6; sealed sha256 a375a7703b1205f7e3a94b6e9e8cdc6163b509bba514771406a981ad5a44848a
- manifest sha256: 07c09b68d8d55f6351942a89e2bd495dfa11f4d945153762685aa754ac70c4af
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.498225+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-03-01_2020-04-01.dbn.zst

- file 60 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-03-01_2020-04-01.dbn.zst (2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 4abf5d75bcf794840691d1505aa0449276e9e46831e6044befb4953bf4763815; sealed sha256 60ffaca1bd56f4845cd8f3d7ad8a8a9e3ccaf7057bb0d62657a942831104639a
- manifest sha256: ce4e38b83e7149546a43275d915085aa68fbdf523b42dddc1bb11cb1b4b0ef7e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.632794+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-04-01_2020-05-01.dbn.zst

- file 61 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-04-01_2020-05-01.dbn.zst (2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 6fb1521058450b1c772eb29db789be9c6f770f86d9cbeac9356dd5924cd5c36d; sealed sha256 459b528244ffd758f89c24d56b4f6f6c33e706cb1c2b1c768cc184426c8f2278
- manifest sha256: af85690118c87879fe136981ed2514318f38927fcb450ec7e6db748e4a5c3662
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.767090+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-05-01_2020-06-01.dbn.zst

- file 62 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-05-01_2020-06-01.dbn.zst (2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 d7aad0408a846b1cf3432f9c2eb8fca67b2a0213c1ca6023f91b0cb8b5ff8e90; sealed sha256 62bba88c7e2b8cafad9023ba46bc508abd4e0f8b8490218268fb28eb2bec743c
- manifest sha256: 0b29262fca4037583e07d9f9fd35beec08b98473084d95a1eb75b4f6b4883f69
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:04.901490+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-06-01_2020-07-01.dbn.zst

- file 63 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-06-01_2020-07-01.dbn.zst (2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 4ffb509f3157247344a77f8f676ce120e09e0470bd6788f8304f57af238a63d8; sealed sha256 a234ee31415cb5c269810b81815eee9871aab370b0b5eb8876edd59d07606b18
- manifest sha256: 5b4a1f4161522e909d3e02f10b85339b1a8c6c520ef4c641c5cb2d706c3c4376
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.031055+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-07-01_2020-08-01.dbn.zst

- file 64 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-07-01_2020-08-01.dbn.zst (2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 725ce1c1e100919bdc480216422bc140cb54440060038306ad145bf3f28c5fe9; sealed sha256 672dadc14162babc3316e67fd17b59695416cce0b861b7277fccdab41d8b7910
- manifest sha256: 820b17eb5fd9f67fbb9ec87a479084a32242390323dd874e3f11c4f2f7bf6b5a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.167074+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-08-01_2020-09-01.dbn.zst

- file 65 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-08-01_2020-09-01.dbn.zst (2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 14fc8582b071120baf91d27da60dab024f21acb8ccbaaf656ca326e18efddf44; sealed sha256 5a06bbfe6be5b1e1dbd090e3be33f9aadf7e532987131c744a1661746e0fc884
- manifest sha256: a1a06eb1c49082f6326603b0ab68a7bd1baca891d7dbb37051d8788a42b79294
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.301382+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-09-01_2020-10-01.dbn.zst

- file 66 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-09-01_2020-10-01.dbn.zst (2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 a091ad55270f102e700c6222ab4dcc707b427a488f4c9690e19de351e164035c; sealed sha256 53befadab6010c680e1009e77a608c17ac292086266da29e0b2f89f303f31fa3
- manifest sha256: f2e4b491bda4c75835bb223ad5ba25fd44a7d3219ff9393af68cc6fa73fd3f9d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.436324+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-10-01_2020-11-01.dbn.zst

- file 67 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-10-01_2020-11-01.dbn.zst (2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 a1e466b47e30dca053bc7d3fea7978a21343711649cb1b41556e8b6040e218ef; sealed sha256 10f688f651bedb2369b7b2ee512458899ec03ab170610860afb26c681423ddbf
- manifest sha256: 6e054ad013e53d0d6564355d6e2ee093cf901d1f7e4bdf2d8665bf201f15ed8e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.569627+00:00 SEALED soy test ZM raw ohlcv-1m range=2020-11-01_2020-12-01.dbn.zst

- file 68 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZM_v_0/range=2020-11-01_2020-12-01.dbn.zst (2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 3ceef124e06011529b916e6f6fced2f11fcf2889840e30365a47f56f7ba52755; sealed sha256 a3929d71354f565fa4189ae91d4ba8b1181c328f151d4e0de19a0d5c8aaab666
- manifest sha256: ae64012e367108a9e19ba7481dd45e64c247b28c9907eab1cb20e204aa0e8a16
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.702718+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-04-01_2017-05-01.dbn.zst

- file 69 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-04-01_2017-05-01.dbn.zst (2017-04-01T00:00:00+00:00..2017-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 026f9c460136eed4fc92713d3a92bdfb09ccd16ec228cac513b9bea8a632f05c; sealed sha256 8c081fc370a36ea9368debd3f407427c2e31d3eb20ef69325dbecb762c89d10e
- manifest sha256: f92dee018c059e837e5aff1c020b856aefc93b7576af93e908948da703dc8595
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.837340+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-05-01_2017-06-01.dbn.zst

- file 70 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-05-01_2017-06-01.dbn.zst (2017-05-01T00:00:00+00:00..2017-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 74b0d8f0b3f6c758d10907d08007ee24440097028b5bca027bf9ce68ec59da85; sealed sha256 b1e9582bf936a57f5ab70e60d538716eb07ee701fefe538f39e0ff252f5d7fdc
- manifest sha256: fa00477feb16729cfca6e9bfd9977da5ca8ab9aeb9d1b73382d7005575b0feef
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:05.963669+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-06-01_2017-07-01.dbn.zst

- file 71 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-06-01_2017-07-01.dbn.zst (2017-06-01T00:00:00+00:00..2017-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 9e16ecf393bdae48f0af5aaa1b2de52b8c326032ad3c43de7d6bfe974ce4fecd; sealed sha256 20e4a4ca1f2b43ed9d2a0ae241c2ed48c28917b2937230641b37702066287b6c
- manifest sha256: 87bb423ec820185d7d572e5634baad5a96e6d05e4f38186b8f9a155c113905fc
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.098206+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-07-01_2017-08-01.dbn.zst

- file 72 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-07-01_2017-08-01.dbn.zst (2017-07-01T00:00:00+00:00..2017-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 802f879deb4b7d7721bf1b90a8085eb04839cc7546403fb24127de16a65ae0b3; sealed sha256 b8ef88d5a903d48419ea92a58e3e21b96c70460c7b509825ad07c555faff90d1
- manifest sha256: 059a5ead45a4c2fca74884b019c736f913b94d82076759141f191ae2a2afb32e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.231692+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-08-01_2017-09-01.dbn.zst

- file 73 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-08-01_2017-09-01.dbn.zst (2017-08-01T00:00:00+00:00..2017-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 7e8e3f922582b2eb9b8e8b22de0a9b802b44f223dc6a1508c493107250d34498; sealed sha256 1d7ae0da6cbbd6c746eabf841e5a3dd5582ab6746b300b0a3cebdb511fc478a9
- manifest sha256: a15cdc9f0ce57e94fa640934fdf617bcf30a99b1a60658ade93e914e94f582cf
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.368537+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-09-01_2017-10-01.dbn.zst

- file 74 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-09-01_2017-10-01.dbn.zst (2017-09-01T00:00:00+00:00..2017-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 e01638022a7e3503ecaf8148c79f10da02078dde9100c461e97c92d6532df15d; sealed sha256 6b6541b620111cbd86baa4c0649c49005eda1aa5722470d1cbf9318f9e5af1f2
- manifest sha256: a9df1664034fbf97e2366a632279cd8c439fddea7a58873e5f22e85af57d0825
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.508221+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-10-01_2017-11-01.dbn.zst

- file 75 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-10-01_2017-11-01.dbn.zst (2017-10-01T00:00:00+00:00..2017-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 d37819652b5c062e65a3236d4a19cea837a9733c8cf199f6df24f698e676b780; sealed sha256 8cd305797df0323c29208ebaba15ce3f746c3b933a6970c206ba93e57e349f8c
- manifest sha256: 902c815338fd65965c6724809b41a0ab99f1e3271252ca63ef1c53e249baef94
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.645247+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-11-01_2017-12-01.dbn.zst

- file 76 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-11-01_2017-12-01.dbn.zst (2017-11-01T00:00:00+00:00..2017-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 67f81d152f7dfdf3a62d09cb5b3b7706718368b74622842ad259df643e29474c; sealed sha256 17c08bf34e2360102119235f1bd21a55662d65cf8cfe36676a38cf36006c5efa
- manifest sha256: 33d407f262f5b0b534283b60065ab70c53fe3f19e7db13710ee421bbb8ce0cc0
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.779061+00:00 SEALED soy test ZS raw ohlcv-1m range=2017-12-01_2018-01-01.dbn.zst

- file 77 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2017-12-01_2018-01-01.dbn.zst (2017-12-01T00:00:00+00:00..2018-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 1b6396f54b0f8ac32efe096c473f3f7ef9bedbe57add11253bbb5b209a5e5335; sealed sha256 cac951974fb6c8b16a264c92e96cdc53021a6d6b9e769ec65f5a49c9bf260814
- manifest sha256: 72a651db632b6ee1a7b10980bc646bc7035e0ec946e89861cfd6323eb6186747
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:06.913359+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-01-01_2018-02-01.dbn.zst

- file 78 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-01-01_2018-02-01.dbn.zst (2018-01-01T00:00:00+00:00..2018-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 85473ab60201d2cb3bec1b12a233813d57e0986f2004cbf8ca8263057261d51d; sealed sha256 1610810da7918b7495f45d30ef54f86c1a9904da954ac517d038324a5dcfb492
- manifest sha256: 75c49d2807ac0344316fd73a317d3a4947833ea19aa56636d28f9e90304d447e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.049763+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-02-01_2018-03-01.dbn.zst

- file 79 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-02-01_2018-03-01.dbn.zst (2018-02-01T00:00:00+00:00..2018-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 b334385f5efa797586a365466c3e92da99b3b5d097494f6cf932e6bf250d1ebf; sealed sha256 c93211a67aa7d6af6c3692ffafc06c497948e1ab73a1e330f130d150aa12274a
- manifest sha256: 79e4efba35563f8d1b99d21b4b6d03a05495d6718c5e32c55faa49ca74ed886a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.185046+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-03-01_2018-04-01.dbn.zst

- file 80 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-03-01_2018-04-01.dbn.zst (2018-03-01T00:00:00+00:00..2018-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 d78a1bb1e30684b5fe54141b3bb214dc7518a86b8172ba07ef0b5d3665e8e0e9; sealed sha256 88ee178301c3e11e6bdf051f61629c69fd3369b6a4b43d0e98c957a65528e553
- manifest sha256: 43a1040ce60610ae7e73b4ae404126b07ca6e3301f458f7c04c1fbfec7ce28ae
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.321971+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-04-01_2018-05-01.dbn.zst

- file 81 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-04-01_2018-05-01.dbn.zst (2018-04-01T00:00:00+00:00..2018-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 f5f58a3b524ce3b8e2e59dde257cb99bf222d39ce8906535b6092306fbb51a43; sealed sha256 8c0411669721f07ea7bc61a30bc2f6171820a35160ee2a5b7e155bd800a5c81f
- manifest sha256: f5797cd5cc36b33ffaeb9f28ddf151881d9624e044ed7458705c0d7084a6329a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.455163+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-05-01_2018-06-01.dbn.zst

- file 82 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-05-01_2018-06-01.dbn.zst (2018-05-01T00:00:00+00:00..2018-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 4c603646e7d4823575a7b68dd55c6bacde2858e4fcae88c6e2fa681684be73b1; sealed sha256 038bb2a783d487e8b4d1a09ad61b7db0be2199a6d26b85b6be9232f270e7a1ef
- manifest sha256: d5b81e23ae377701f99e44969fe504dab5ab85d29030801559dba8bcd26804ba
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.592256+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-06-01_2018-07-01.dbn.zst

- file 83 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-06-01_2018-07-01.dbn.zst (2018-06-01T00:00:00+00:00..2018-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 a1b7832c76bb86fca34a5c55851fc44280bf3dcad5bade77b88b705c37868a6a; sealed sha256 ca5161f0d24c039c58f2f3289e1480ce8e421a00ed51a30a85353b8ddfbe7dd3
- manifest sha256: 517aaaa09f97bbabf9867fb9b6ca4c92ce34a57e296892799406877b899ee476
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.729874+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-07-01_2018-08-01.dbn.zst

- file 84 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-07-01_2018-08-01.dbn.zst (2018-07-01T00:00:00+00:00..2018-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 b289fde8dc60a6e5783dee1f4a4eb369c562305d6b2274c8135fab66b887febc; sealed sha256 a4a5ed6dd6081e5f95de5e7e7f372aa4a33e03819befefe415f325b98b805f56
- manifest sha256: a0ffe5980a3e5d25cb4b815b81ec6a4618443b389b0b38ed2c28c8c28ff65012
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.867489+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-08-01_2018-09-01.dbn.zst

- file 85 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-08-01_2018-09-01.dbn.zst (2018-08-01T00:00:00+00:00..2018-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 1c49c9da3fd3ccfc7ad49c69e6ede2791b6a568ffb917df0b3c2f9e8e893ff82; sealed sha256 3f8628ad7c140788cd5a557eb520dcbde0eddbd349890508e1a86aee40607730
- manifest sha256: 92ae9d12a4f74f99b8093e26643b0cab4fdaebb7347981388bc117e68d897649
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:07.995358+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-09-01_2018-10-01.dbn.zst

- file 86 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-09-01_2018-10-01.dbn.zst (2018-09-01T00:00:00+00:00..2018-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 dc2e09a6f67b95650fa2bb45d80a6ab08c9d4fe8f30cdce09248cd90c1f5d81c; sealed sha256 e25f185f337ffac903464fc872071be91c98817bb82e239b5d27bdc7f161a54a
- manifest sha256: 4e9e5c197352e0d378739b7cf0f3b8176da1ee357b86d38d616cea684e64ca2b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.132792+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-10-01_2018-11-01.dbn.zst

- file 87 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-10-01_2018-11-01.dbn.zst (2018-10-01T00:00:00+00:00..2018-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 67aaa3ebd6d6618f429b33175b28ee7853f5ea2969ef175046fe0e2c93def7b4; sealed sha256 e24b9cae9bd1a3a2b7fa37ff36fedd653fcb873cf9c7377b4459e3713fdb351a
- manifest sha256: b134b1dd6b6aaccd4f79cdadaf2188058ef7ffdc443a3eca5a7ce04de3c2ea26
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.270129+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-11-01_2018-12-01.dbn.zst

- file 88 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-11-01_2018-12-01.dbn.zst (2018-11-01T00:00:00+00:00..2018-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 4ecd1651955523f28d23f52fc51f16902b4a7539b932e5d7d3abd88a259d68ac; sealed sha256 c9c59c420a55f6cc62b263808da5e1d1acd8b8a086551d4006c8610bac0ad322
- manifest sha256: 62d8c92a05a515cd40dae70e82d59ae73297e8157cc9f88937a8461f13790a49
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.408068+00:00 SEALED soy test ZS raw ohlcv-1m range=2018-12-01_2019-01-01.dbn.zst

- file 89 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2018-12-01_2019-01-01.dbn.zst (2018-12-01T00:00:00+00:00..2019-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 b08b3f070c0a592aef26d848c251b38d9899a97c1caa88ecbc5d05ba82d97266; sealed sha256 fb726435a391ac2a7b7676fa47f78767aa5cf0c41b3ecfd09e822f9eafd52869
- manifest sha256: bc2beb21ed93d5b29bce9d9c834ffad0ea2e932d111363f029a2aa16d8a5522a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.555645+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-01-01_2019-02-01.dbn.zst

- file 90 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-01-01_2019-02-01.dbn.zst (2019-01-01T00:00:00+00:00..2019-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 dc9052a4c53f6ed54e7b577db0bea828112eaf65b41bbbd857a3cf79c4a54d19; sealed sha256 8943ca3ec86aedf7fb6438a290ddadae49699df0e8d6502342079dc0185d1745
- manifest sha256: efe1d61eb496eaeee26964e2a3e8f9c9f658696e07ba8db7e7da0eb513ca5d39
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.688383+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-02-01_2019-03-01.dbn.zst

- file 91 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-02-01_2019-03-01.dbn.zst (2019-02-01T00:00:00+00:00..2019-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 d5bbe24e5d2682a94eb457130437cf21629b033108c36409df479fd6dce2387d; sealed sha256 876145b4407db81d7a173584c31c2fe2fdad6a49ed61b26304e249776c6fd1cd
- manifest sha256: 4952b7ce1f6b1351cf6acb94f66619711cb11155485fe15ea795f1832f594f5b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.822964+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-03-01_2019-04-01.dbn.zst

- file 92 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-03-01_2019-04-01.dbn.zst (2019-03-01T00:00:00+00:00..2019-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 f0c3e3457693f43f83f6af133e16d8cbda98ee2b0488c522fcb903ad18fe1714; sealed sha256 adbaa8e96e9d4715faeffb3bab1ab537eabecb2d7d68b97ab2423565fa3c56c0
- manifest sha256: a55a8fa2379b61bd06349a3a8a3f0b2ecd365cbeda55f8e0c6074510c78c9de3
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:08.956741+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-04-01_2019-05-01.dbn.zst

- file 93 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-04-01_2019-05-01.dbn.zst (2019-04-01T00:00:00+00:00..2019-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 da19f6d64c4367edf8c8516d0b7022ba2dba96e3420802d1bef5d3f18be1d077; sealed sha256 ad4a4d82b640ff1c5e015d227511dac453c3cab25824942e7e6f0b45882957e7
- manifest sha256: ddfba133510d925ff08db60aff11564419a03fd2319a812254418ba27f240a3e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.089999+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-05-01_2019-06-01.dbn.zst

- file 94 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-05-01_2019-06-01.dbn.zst (2019-05-01T00:00:00+00:00..2019-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 217496d0d84fd2544c72eab3a87aca42cf54b5b75d31dd5d2673e74204b0dd6c; sealed sha256 d32da70b2a69f5ec27f0777ec181e7e9991d35d6a4e95148dbdbcda2ef313bd5
- manifest sha256: e6f0115b7ac2d97ff9a7e7098f4d5c50b131cee05e6c5c86e5604cb7e7458060
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.224778+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-06-01_2019-07-01.dbn.zst

- file 95 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-06-01_2019-07-01.dbn.zst (2019-06-01T00:00:00+00:00..2019-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 6de29dbe5ed2e5bcf20d2ffaffe82b65dbb6b43e390f8aee13dd1a90f5ed735c; sealed sha256 ffbe244b82eeb2b1a3fc77bbfcac8a29665a69190ba3edc197180db8949a5a3d
- manifest sha256: d7635f0c520c2d27f2acc8f89b311e8c398f486ccb4a02837f055c19e451a154
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.358758+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-07-01_2019-08-01.dbn.zst

- file 96 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-07-01_2019-08-01.dbn.zst (2019-07-01T00:00:00+00:00..2019-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 f56b01862a5e24196982844d2c1c89214eb5c91211c4b902298476f374fc6cc6; sealed sha256 088bacc56878e24117950758acade5cfc5579db709f02a97075b02c3d1e06568
- manifest sha256: e17c078cae245ca2de37b3b56c3a41800240cc9d31a653bdd6216c7650f02ce4
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.492097+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-08-01_2019-09-01.dbn.zst

- file 97 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-08-01_2019-09-01.dbn.zst (2019-08-01T00:00:00+00:00..2019-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 fd2485ee4090f3a0bbf148a3e8c4a7df06c601ee1f0a5c2e043dc1f6f2b4bc49; sealed sha256 292051379568164f1b24d2e3acf92ba19fd747caef7a03f81660e83a03f02882
- manifest sha256: 08198832a2ce8929d56d2150b569f5bfb47f0cfb33f94a995f2df964027d580e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.626636+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-09-01_2019-10-01.dbn.zst

- file 98 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-09-01_2019-10-01.dbn.zst (2019-09-01T00:00:00+00:00..2019-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 a77bd7864f16489b3311d3f123d442affb44265ae3993c1cecca0a808c899e31; sealed sha256 03bc3ca53c35bd3ed082aaf7c479a1cccaac116bf5774a98229d663864bba28c
- manifest sha256: 1e7d37b40ec1978dc7be0fef0a177bbb83de78ce2170feefb9ad36d2e75189f2
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.761562+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-10-01_2019-11-01.dbn.zst

- file 99 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-10-01_2019-11-01.dbn.zst (2019-10-01T00:00:00+00:00..2019-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 9d69818a99117fb380917d494543154886de595c6c803c114b6ba84298f5272a; sealed sha256 687fdd61a280284f420e45ce97169d8082efc35a7e1ffcc6b5b9f7b834eb0288
- manifest sha256: 5ce09aa773f02863652487b31fcf8b6a2a6e0ac1143ef7f25c5445976a42973b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:09.899182+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-11-01_2019-12-01.dbn.zst

- file 100 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-11-01_2019-12-01.dbn.zst (2019-11-01T00:00:00+00:00..2019-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 a03495aee3a66865e0c25458b577b5fd8c6624758cdfec2af3f58c1f97a80fc7; sealed sha256 dd77dd07652346fbc07af76dfa10bedc4f1a931dd03ee10d0dc22c3e82055cfa
- manifest sha256: dd5b295a0343c6e093e99a47d266924864262014a1f0268e69a24feaca98027b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.034778+00:00 SEALED soy test ZS raw ohlcv-1m range=2019-12-01_2020-01-01.dbn.zst

- file 101 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2019-12-01_2020-01-01.dbn.zst (2019-12-01T00:00:00+00:00..2020-01-01T00:00:00+00:00 (UTC))
- plaintext sha256 4410311806c77808264eed1f1dfe1649a846a34fe81a834efbb38a22db6cf659; sealed sha256 ef1b736e712817ae5810d5fa2fb98701f408c89fd44e44808b685c52cb1e6f72
- manifest sha256: e56da20f58a77b5782f8e181f86055f1cf8fe394eb5304afb9aa9c7237f2256d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.175833+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-01-01_2020-02-01.dbn.zst

- file 102 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-01-01_2020-02-01.dbn.zst (2020-01-01T00:00:00+00:00..2020-02-01T00:00:00+00:00 (UTC))
- plaintext sha256 db47c95502972662df4d1d32f58fd08a981b6f42085cedcbda853eb98bf05d55; sealed sha256 1605b828e026d03b5f2db628eb72c411751234fc9b068c3de72bdee9d939f601
- manifest sha256: de78ea535bb4d493cd9c95044d89059b06f46168d00e6477b073438e6609cd83
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.305933+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-02-01_2020-03-01.dbn.zst

- file 103 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-02-01_2020-03-01.dbn.zst (2020-02-01T00:00:00+00:00..2020-03-01T00:00:00+00:00 (UTC))
- plaintext sha256 393d937570ff9b758758ca55a8e31f35f4683972d15c9b021c1c9116e64a3d83; sealed sha256 25656c706dba23da78865671eb2e8470a419bcdefb9fdef2b180809d294fdd26
- manifest sha256: 461ddc43bfbd1be5c5997738e802392c023c81543a809d902b84a27c2c125169
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.442669+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-03-01_2020-04-01.dbn.zst

- file 104 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-03-01_2020-04-01.dbn.zst (2020-03-01T00:00:00+00:00..2020-04-01T00:00:00+00:00 (UTC))
- plaintext sha256 a389b837b4b830a540b5afa406a1559d479c27c7eb7b60db9b279b618821622a; sealed sha256 bf8ae4bfd8da1984418be91114808c2d4993b6af34593db30aba33f7edad054a
- manifest sha256: dc92d9e5329a4f739645cd490a25724a9986dbffadf5e8aa60da39b1eaf0c285
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.577640+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-04-01_2020-05-01.dbn.zst

- file 105 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-04-01_2020-05-01.dbn.zst (2020-04-01T00:00:00+00:00..2020-05-01T00:00:00+00:00 (UTC))
- plaintext sha256 98dd72569cd76ef9d7a5b148618ceb0562d7939b961c96c1e31ab8f0d760ab5c; sealed sha256 90b299750f596125b2af6f8d60686f5f7945ee717e4eefd5abd530f55e08f37f
- manifest sha256: 4de517febb29e0490a82c8e2a807b54aa2c103013a12730de71ae8b4b5dc368d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.711108+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-05-01_2020-06-01.dbn.zst

- file 106 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-05-01_2020-06-01.dbn.zst (2020-05-01T00:00:00+00:00..2020-06-01T00:00:00+00:00 (UTC))
- plaintext sha256 f5ae12cf38fefa1e54c659a1f02b608762a3f278160ac4222e936ca2d8bcb689; sealed sha256 637794446aecbe0a734db79086837c658823e9e8ab26b4ff3e11e99cbac4126d
- manifest sha256: 3408b29fd4824de04696a72d1c5fe6fa4c2888faf409fd5995a75faf0a454b36
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.846946+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-06-01_2020-07-01.dbn.zst

- file 107 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-06-01_2020-07-01.dbn.zst (2020-06-01T00:00:00+00:00..2020-07-01T00:00:00+00:00 (UTC))
- plaintext sha256 5c9ed890982a9189f407196fa9dfc13635b3c5aa0373fce870e6c60c40480d22; sealed sha256 07c742a4ee83ee0468321e7102b1ab1a259e8d7127036c788c611241cb69980b
- manifest sha256: 625172b93a8970ee3018af5b708d338fdb60661bb8ab647b0b0b279f31e45954
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:10.973619+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-07-01_2020-08-01.dbn.zst

- file 108 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-07-01_2020-08-01.dbn.zst (2020-07-01T00:00:00+00:00..2020-08-01T00:00:00+00:00 (UTC))
- plaintext sha256 1cfcda51b93963630ca23351487fb85902c00dd185cc553b62a188d35c8e96ac; sealed sha256 fcecf3d484928610098bfad32e771935c8f4eb8bad4a13415ac479090c43cc73
- manifest sha256: 282f009181082279fae1fcf27e766092579a301c88e33eb41990256dc6f86d19
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.108128+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-08-01_2020-09-01.dbn.zst

- file 109 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-08-01_2020-09-01.dbn.zst (2020-08-01T00:00:00+00:00..2020-09-01T00:00:00+00:00 (UTC))
- plaintext sha256 4c620b558a542600f26626ec54accda992b807afded9e7194d7d567c29a7b528; sealed sha256 298027b9c38f9188342f1e44eb02fa71ee8f2022cdda7e9aef76e457dfa0ba56
- manifest sha256: f9ff2c3f767ed6e04911afe2bada4451692695a63b533d0f423616a2bdda6f41
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.246713+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-09-01_2020-10-01.dbn.zst

- file 110 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-09-01_2020-10-01.dbn.zst (2020-09-01T00:00:00+00:00..2020-10-01T00:00:00+00:00 (UTC))
- plaintext sha256 5c9d085fdc806fdc6669c575fdb47c31f6dd4b8e22d3f22b9dde6200d744818a; sealed sha256 91b0a3519fce23785b45cf8b3277e83b5a7e7c97ad9f4994c93ea0eff5eff8b8
- manifest sha256: d58bb1de7aa5aeaa5b21abf78f5344c0e756b7ebe652230a9546623bab4e598e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.390026+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-10-01_2020-11-01.dbn.zst

- file 111 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-10-01_2020-11-01.dbn.zst (2020-10-01T00:00:00+00:00..2020-11-01T00:00:00+00:00 (UTC))
- plaintext sha256 37227d7dde840d6c0abd3b57e4b95bdfec97fcd98530712547bca1b8a7407e87; sealed sha256 1f9ea09fad799e8f42d2c75307908c49d34e2bb635dacb2ce98591550406fe75
- manifest sha256: 13a8e0ae382d46108f1228b410eb880d28e76fa32a87c5ec6b1341a68b1b95ab
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.517446+00:00 SEALED soy test ZS raw ohlcv-1m range=2020-11-01_2020-12-01.dbn.zst

- file 112 of 114: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ZS_v_0/range=2020-11-01_2020-12-01.dbn.zst (2020-11-01T00:00:00+00:00..2020-12-01T00:00:00+00:00 (UTC))
- plaintext sha256 f563c5a657f40392c4b382b2de16e3fbfa943c35f4c106c23daaf63efec16bd4; sealed sha256 df4efe84c996cad22c1d96292fcd870aff789ec31f148d2db9dcd94c59b318bd
- manifest sha256: c32a5b3dffc4ed0e25b744a4b28885c43ef47e546de94de1e28979e80305b68a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.651762+00:00 SEALED soy test ZL cache ZL.parquet

- file 113 of 114: reports/stage_e22_microbook/cache/ZL.parquet (trade dates 2010-07-01..2024-02-29)
- plaintext sha256 32c5a9f8c50d3bc49d8a2454dc06949130800486cb406cb6aa28e5e38e85a023; sealed sha256 d337b8c95865f4387002d783bbb4dda0791a905014e124fe4998acc466fbfead
- manifest sha256: bd4f0212236b2ff40c1e87d8fabc60afd696bc44877c4994f5c3c59f5765f742
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-10-27T05:55:11.789982+00:00 SEALED soy test ZS cache ZS.parquet

- file 114 of 114: reports/stage_e22_microbook/cache/ZS.parquet (trade dates 2010-07-01..2024-02-29)
- plaintext sha256 a1ec1648b4b4e19ce1bc884faaa18fd5c9e8071651abb1e7abea18844b7aca1b; sealed sha256 7a5b0a6b47f8feaebf960087ff6d7022fc0aa9b03e322e459543a4f341ad5eaf
- manifest sha256: 173c89b4debb21345c7c0e65912f95e127008e595c5a5ceba9b5d3806ab23c64
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
