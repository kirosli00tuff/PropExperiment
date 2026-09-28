# Holdout unlock log

Append-only. `data/holdout.py` writes each entry BEFORE any sealed byte is decrypted. Do not edit or delete entries.

## 2026-09-17T14:47:27.806548+00:00 SEALED

- holdout trade dates 2026-06-22..2026-09-16 (85198 bars)
- sealed raw files: range=2026-06-01_2026-07-01.dbn.zst, range=2026-07-01_2026-08-01.dbn.zst, range=2026-08-01_2026-09-01.dbn.zst, range=2026-09-01_2026-09-16.dbn.zst
- manifest sha256: 0c8d7edb869a66682c0c957d226140408b8265d9a236ea6feac1baa04ef76490

## 2026-09-17T22:14:30.118839+00:00 MANIFEST HARDENED

- added repo-relative paths (a moved repo must not look unsealed and get re-bought)
- pinned this log's byte length and sha256 so a deletion or rewrite fails verify_seal
- no sealed bytes were read or decrypted

## 2026-09-23T23:52:36.609106+00:00 SEALED holdout 2 raw chunk range=2024-03-01_2024-04-01.dbn.zst

- chunk 1 of 13, sealed on arrival, oldest first
- plaintext sha256 c8b73be2fe736aef7947da0f53233f01dbef21b72c412d46f01ac35f1958a25d; sealed sha256 b852f90cfc8169315e23033b0d5b9315752d6647872fa8728bfafb60103c1f9a
- manifest sha256: 498368d00bac69ef4da35c9fbba4e6915b70fc6e21faa755d03497bc9ec1b8c2
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:52:42.981440+00:00 SEALED holdout 2 raw chunk range=2024-04-01_2024-05-01.dbn.zst

- chunk 2 of 13, sealed on arrival, oldest first
- plaintext sha256 68a761e0ae3cfd7117762db25e73ded999a3410f0e3c5e2fec6618d71a49b9a5; sealed sha256 5e7836b2e44e71dce096c21ee86a2f13ac3c8a1eaa832cd3d8b35bdba10a96c4
- manifest sha256: 96052701e1b4daa3cb52305ed8d7940a3e8bac327d025f2aff40142f6f6d6204
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:53:37.071756+00:00 SEALED holdout 2 raw chunk range=2024-05-01_2024-06-01.dbn.zst

- chunk 3 of 13, sealed on arrival, oldest first
- plaintext sha256 4b33683180d4f1b7d866bc5bdd04cb5134fd2bf727db08433cf4a0c7356559ba; sealed sha256 972a6db0870063d57bfb68e903300c23a16bbd8fae9b412898a4e49cbaea1602
- manifest sha256: bdee758546086eda15d218591b824a038989b2b1d64a335dfb6af6095edd05da
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:53:49.360767+00:00 SEALED holdout 2 raw chunk range=2024-06-01_2024-07-01.dbn.zst

- chunk 4 of 13, sealed on arrival, oldest first
- plaintext sha256 0eb7e4e084fe1dcc4c3eee4094c1e6cd157c0d905d711b8c966d0f30dd214533; sealed sha256 e4c4a5fd1127dc5c883a361c5b229898dbf4776daf4ae5fa2bdfe4464c421d27
- manifest sha256: c4a76dac26b1ff9c575b4eb72323bd6e5ae4061b8ad7365267cbeeae29e461b6
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:53:57.610751+00:00 SEALED holdout 2 raw chunk range=2024-07-01_2024-08-01.dbn.zst

- chunk 5 of 13, sealed on arrival, oldest first
- plaintext sha256 5502c5f43a95d328811a12c88154dbd4cce4d75c57fe4588e83733efbc16dbee; sealed sha256 68cf3b2891c8afb9255b8ccf8b765900de9845bdafd60bbac92622d650113367
- manifest sha256: 8c1aaf5105ac6f8b026e5ee2b299eb0e8a4e360ac9e8859e407fc230d4c3e90a
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:54:05.895414+00:00 SEALED holdout 2 raw chunk range=2024-08-01_2024-09-01.dbn.zst

- chunk 6 of 13, sealed on arrival, oldest first
- plaintext sha256 f728089b0421219f578e637872d467be0c3433538c8936411028991b24feede8; sealed sha256 2dfd57e72d5a6b05065c0870ddfe4e4eca59d1cb990238006ac32d42a75d682e
- manifest sha256: 440917339513f138b95013e5e64a8060a9e63bffcf7f319165a51e49a2ed5dd2
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:54:38.126046+00:00 SEALED holdout 2 raw chunk range=2024-09-01_2024-10-01.dbn.zst

- chunk 7 of 13, sealed on arrival, oldest first
- plaintext sha256 f63322a5689cdb53d95de2bf29ac46bf7884dd132faddcfe9bdd16f9f62aa57f; sealed sha256 33b5d061f15d4a68ef587585b870bb550146c2bc8fdb7252bc509df4d63f78bf
- manifest sha256: 63bdfaa0e94db144885396e3f80f4c1b1f311f0b2d794bae99102bf21de5c3c5
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:54:54.143778+00:00 SEALED holdout 2 raw chunk range=2024-10-01_2024-11-01.dbn.zst

- chunk 8 of 13, sealed on arrival, oldest first
- plaintext sha256 e5f0697ea065ed5b7719d696007182f095e29a0d2d6b3f0888f11bb5ddedb167; sealed sha256 976b7d4f2d4f4d825c10be8891789dc2afd478b8da57bedf50a9c7933f1bdc32
- manifest sha256: e507ed6118cb2be6894d306e13c6b8d296478af5569e982e74c4bb62cba85b4f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:55:00.469381+00:00 SEALED holdout 2 raw chunk range=2024-11-01_2024-12-01.dbn.zst

- chunk 9 of 13, sealed on arrival, oldest first
- plaintext sha256 723b119966a55521210df5d5825f9163aeff60140b3aa0a8f27f913c2c874917; sealed sha256 6db22f1d9793ae53bb88de2eb5850be8a72ef92e6210a03d0e32dcaf1f5bfb08
- manifest sha256: 0751b694cc3144f31311b35ff1c0a3df41a1fdcfd475898e3871982e8098d677
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:55:11.140633+00:00 SEALED holdout 2 raw chunk range=2024-12-01_2025-01-01.dbn.zst

- chunk 10 of 13, sealed on arrival, oldest first
- plaintext sha256 d37b94179c2e7228cdac774073c9b64759cbff02d38be7e64a19546d5cbc702d; sealed sha256 61fe0de15bc09e8e6441ed87b3df9be1686ec7388e860cbc77887e8f6f678a7a
- manifest sha256: 6318fd1cf7d2925515bef5d1a679334d5c011fb4ef9e71db172572a7b62a7933
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:55:23.730107+00:00 SEALED holdout 2 raw chunk range=2025-01-01_2025-02-01.dbn.zst

- chunk 11 of 13, sealed on arrival, oldest first
- plaintext sha256 7c0a5d47e38d189bf90dfc78ae12a73c6af37f4d92a42ae9296ac831f2956bec; sealed sha256 b26648555d57806a6743e67779cbd7535cd44e153d1dba8bf2726d328f734857
- manifest sha256: c80b6eb9d28edac7c422036e5f66735308f82306d854e145d6b11db225e06e17
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:55:38.767232+00:00 SEALED holdout 2 raw chunk range=2025-02-01_2025-03-01.dbn.zst

- chunk 12 of 13, sealed on arrival, oldest first
- plaintext sha256 6ae62624d1db28ff1d91dc74374650efaa7daf81f62bb795b665cc41eac9b5e3; sealed sha256 14caff5a1fca301c78b07e30427cf591e7eb2669f1caaa2f59a2c2ed546b202d
- manifest sha256: e535f36b1456925ee1613421ee4af22aa4cda141884826d334308b9e534bad5d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-23T23:55:51.072354+00:00 SEALED holdout 2 raw chunk range=2025-03-01_2025-04-01.dbn.zst

- chunk 13 of 13, sealed on arrival, oldest first
- plaintext sha256 cd11973e8ff8ad28315eedc4191dc67cd4b0d4d204bff5acc44f27d3175a8e43; sealed sha256 132d4648c352dd9cbfafbb19902fb9e75de8931bddb27643ffda3fea3f9574f2
- manifest sha256: 17e7c902f3d288913959f373d266cd902c586633f5c4fc3e413bb124ec73664d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal

## 2026-09-28T01:19:09.422660+00:00 SEALED holdout 2 MCL raw chunk range=2024-03-01_2024-04-01.dbn.zst

- product MCL (MCL.v.0), chunk 1 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 b5d57dbf443b7563e53fe12225798c5cf552299ea445962d1c8a49163f401c79; sealed sha256 db7cf74f92e1107d07d449cccb34c4a574e11b3fa5b36a3fcbfbe2900821181a
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: b50972104a0fe5d3a387806a227976000ac4bd0974bc48b0d60d99e2026c13e5
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:19:16.343764+00:00 SEALED holdout 2 MCL raw chunk range=2024-04-01_2024-05-01.dbn.zst

- product MCL (MCL.v.0), chunk 2 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6903888eaf69b305a2d8452709f4ee01d650a5e1a298ee8e2e945337a95951db; sealed sha256 93f060a3133b20731093a513121783a560d6565c2cd1cdd99c7fabc137ff056c
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: ad2551c86c965fa339f328f3ce446870f524fdf757f043f8ca91f3b3003d3b13
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:19:24.054807+00:00 SEALED holdout 2 MCL raw chunk range=2024-05-01_2024-06-01.dbn.zst

- product MCL (MCL.v.0), chunk 3 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6e3640480fd94ea0e8651efa1acff3fa554788938f6f3fa7e30e652903290cce; sealed sha256 d6de267ad9fa6f2c2e956c7a429576900d86a74c0f52cb8f0cb478aa65b73e77
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 09d3fcfe8ea0b99cfc01becda1e9b6b5e3f358e61e36f7fa25258fef4acb331e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:19:46.357997+00:00 SEALED holdout 2 MCL raw chunk range=2024-06-01_2024-07-01.dbn.zst

- product MCL (MCL.v.0), chunk 4 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 234f0d7a6ad32de026813a7ba9778555b1a0ce30701a16812925c3a50e61230f; sealed sha256 64652490e5eb5350b009a1d962d3758b4b6c8650891e3a2bd3796dd2aff295e9
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 0b21eac1ea54b7d77f4c0208388e802538267018de91e6ca8a70c208ddf4aa19
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:19:53.859224+00:00 SEALED holdout 2 MCL raw chunk range=2024-07-01_2024-08-01.dbn.zst

- product MCL (MCL.v.0), chunk 5 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 40d81eafa7ad994de662157cf48718c95dfeccf43bb02a390ad3ac6fcf0f9673; sealed sha256 804717222b79998caa7d267c5c0c39b4d75b14833226273815bdcbdf2bbc9c91
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: fffa616a9077f0fc6ce6b7d81bd9c7ada06e4e711979fddabdc13858e7d7d407
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:01.393437+00:00 SEALED holdout 2 MCL raw chunk range=2024-08-01_2024-09-01.dbn.zst

- product MCL (MCL.v.0), chunk 6 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 f5d7d6949e2a8a9bff0728d2a388ef1e7a42d1fd4339806a0c0221677378e89f; sealed sha256 fe8b6b550c248d4d786c3d222b782f00077ac7f8e9321fbd504223b0469af8a6
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 105d32b9adeee52b990a2e0174a35edd60b59e4a4cc190c389d0d3477b947972
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:08.403209+00:00 SEALED holdout 2 MCL raw chunk range=2024-09-01_2024-10-01.dbn.zst

- product MCL (MCL.v.0), chunk 7 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 fe7fa3727d5767120dcaeeb139bc142fa6fde61ac5758a52e5fc823630ca7970; sealed sha256 b91c4367d8874f570c92c9f8e1de301cd9a4c0e8277f3decdaeb78ece2da8b2e
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: b850acb904ba17387d72f606852120f1c3dab7093d15b0642aefa396b4bd85dd
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:16.365859+00:00 SEALED holdout 2 MCL raw chunk range=2024-10-01_2024-11-01.dbn.zst

- product MCL (MCL.v.0), chunk 8 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 437691add132dc32fca4b6631412bba7afe5a3a1ba78c4c769ec216f1400c19c; sealed sha256 f50bce509fd9fd284de0fd98590bb436ea385c0a9f4ccc3fcaa40e694c5b8ec9
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 80403a584b270d7cdaa1bf76396bcf61fa7b051b040823b859c912b0c745cd22
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:24.437315+00:00 SEALED holdout 2 MCL raw chunk range=2024-11-01_2024-12-01.dbn.zst

- product MCL (MCL.v.0), chunk 9 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 2a488f0a9cb73d76404ba7f21ad85b9f202a4552c8c8d008e82ddc7630b240ea; sealed sha256 2366c393332a1f63e433f3fd111580f0d94c25087eb76ed2dd4c3df7d048f700
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 214db6435d8b8eb0eaa489ccd96673f4cc892717ddd1e8dd35c8b7a1827aff72
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:32.017955+00:00 SEALED holdout 2 MCL raw chunk range=2024-12-01_2025-01-01.dbn.zst

- product MCL (MCL.v.0), chunk 10 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 a82ef8bed6475e481cd79814c44b614b21306e64bd6db19a86a7397a56bdefec; sealed sha256 4f834b8be2f874ba21371e470d7430938428fbe1816a37639b6069f5c588456d
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: a945e2bad8647880d8db6c22161c2374a7ad33f883d38d2bd8f9db29f1674dff
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:41.044170+00:00 SEALED holdout 2 MCL raw chunk range=2025-01-01_2025-02-01.dbn.zst

- product MCL (MCL.v.0), chunk 11 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 f5963aa06237af9a2c35dc9b639928cfcea14f5400b2bcee6ccf3d67ec58bfe0; sealed sha256 b33efacc964dc981cf697a781976ef185b3d6f91eb9d541b395b301323254dbc
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 76ce8739ce75eabecceda14011596c669f9ca4a931d55d363df243c3da6989d8
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:46.568137+00:00 SEALED holdout 2 MCL raw chunk range=2025-02-01_2025-03-01.dbn.zst

- product MCL (MCL.v.0), chunk 12 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 a2dab12c3e222242f87916c7520bea6233bc310e224f34896abbb5f2d7c4b622; sealed sha256 819e494b0a975ed6b79d54701314df26cdd7954e3717810877946933d9300dd4
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: 5d44f5649009a3d8f41d9844135ee45cb2b7620c049060fe350a252e7dce641b
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:20:55.040408+00:00 SEALED holdout 2 MCL raw chunk range=2025-03-01_2025-04-01.dbn.zst

- product MCL (MCL.v.0), chunk 13 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 4ffd8e58ee08c1be9d0ee3b08b539b8b008482e62b2829b0241244f5f0004672; sealed sha256 a51d594e00e568a65ed6a26a7e0de53a866ff4980e335a13c5b472f0f53b5e0d
- manifest MCL_HOLDOUT2_MANIFEST.json sha256: b0619bc94147cbee2365347f1493f4ca50f3b96664bf7bd4c2cbde2a964abc01
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:09.173787+00:00 SEALED holdout 2 NG raw chunk range=2024-03-01_2024-04-01.dbn.zst

- product NG (NG.v.0), chunk 1 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 dab3d83f596682f6a00fb815996d32164003015b2fdc220f854a5e2a727b8a66; sealed sha256 7dc94d56e2ea77308073dee369e91a8a52a140049942006186f450cad33ec2b6
- manifest NG_HOLDOUT2_MANIFEST.json sha256: f4948c564ebe1050f7f0a34c13c55ccdda50db23e9db9ff64c016e5d355a20db
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:15.696468+00:00 SEALED holdout 2 NG raw chunk range=2024-04-01_2024-05-01.dbn.zst

- product NG (NG.v.0), chunk 2 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 e6b39f9f29ec3f7db23c0e6338a795e0ee3b7fa4fbf184081ca905924913ace7; sealed sha256 dbba55783063b69404d876a4743683c617602cb35b341d9295a9561c5aa676f2
- manifest NG_HOLDOUT2_MANIFEST.json sha256: a190132bcfcaf7c80c3de6cd6f7879a715ec749239833715da1e3e19d9058a13
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:23.896779+00:00 SEALED holdout 2 NG raw chunk range=2024-05-01_2024-06-01.dbn.zst

- product NG (NG.v.0), chunk 3 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 d8b87472361d00845143acfdc38860cfe595e35f1696cdcdf5ac4fc6df16c877; sealed sha256 48999a6e9d58bf975a2f22be2e716151e755e455d2d6f21945dd72fd3d0ca60a
- manifest NG_HOLDOUT2_MANIFEST.json sha256: 37ebaff119ffeec8f78762f61ebfa4f90e95407569e844aa286f0db97cbba29f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:31.595802+00:00 SEALED holdout 2 NG raw chunk range=2024-06-01_2024-07-01.dbn.zst

- product NG (NG.v.0), chunk 4 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 5999c149aed233f40d890e19f10350a2372bdd33aa5444b540fd72d28fbfe719; sealed sha256 13911e148097a0bd7bfab73062cd1523669e22329490265a636eb9c836ce441f
- manifest NG_HOLDOUT2_MANIFEST.json sha256: 06be32df03d47c51d44073ce1774ae3de77f547ed754b0730d9fff39c6a97784
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:39.546856+00:00 SEALED holdout 2 NG raw chunk range=2024-07-01_2024-08-01.dbn.zst

- product NG (NG.v.0), chunk 5 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 932ee4e1d951f524eb5574fae03b35975b3547ed45bea7bd4acf1e0f385816d2; sealed sha256 1437a0a0a78448c31719dd39ea52ee57fb7383d74ca7c8543beaa494e0723350
- manifest NG_HOLDOUT2_MANIFEST.json sha256: 38cf14cebb36d1e2f450fbf33e7c67eff7613b047f39b0551f14ea9bd5238242
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:47.243120+00:00 SEALED holdout 2 NG raw chunk range=2024-08-01_2024-09-01.dbn.zst

- product NG (NG.v.0), chunk 6 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 3c311c21bc20787a0b696b2b1275f2b69580d4b34c7aa528af106f612226f1ee; sealed sha256 b7e5146de2ef2d3c6adecc1a34494a12f00b205cf70bd1fdb367b9260e7e5283
- manifest NG_HOLDOUT2_MANIFEST.json sha256: aadbde370667b31a6087b46d1a872cfc80ea1b846325175fc7168559eb98136f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:30:54.526345+00:00 SEALED holdout 2 NG raw chunk range=2024-09-01_2024-10-01.dbn.zst

- product NG (NG.v.0), chunk 7 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 0652eeb6a4cdc6505db83fce8dc54cf38f3deeebdbbac590b362befb9112482b; sealed sha256 a67485b39a23f7725fa47c6dc99505a45775c7188b6d635f64dde494e31d6e39
- manifest NG_HOLDOUT2_MANIFEST.json sha256: 9288b2fa2887a7fe7ffa4948cd6284d4d55315947874f3ea77ff200180482651
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:07.784420+00:00 SEALED holdout 2 NG raw chunk range=2024-10-01_2024-11-01.dbn.zst

- product NG (NG.v.0), chunk 8 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 df112a998b1c93a6461bd2073a0f3cffd59ce150ec1cc1df91e46714eeac8e27; sealed sha256 3acd25a7611d2d5b6021561bb50e705f67853c03eead48b3c26e0faa16d25570
- manifest NG_HOLDOUT2_MANIFEST.json sha256: a9d4b08b2458ec4ad47555adb6255c5cfae39074c874c95a4b8607498a8c93ca
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:17.454393+00:00 SEALED holdout 2 NG raw chunk range=2024-11-01_2024-12-01.dbn.zst

- product NG (NG.v.0), chunk 9 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 a4ee242c9a9fb7bc9b3f21e9d4cd6e41fbc604070409a9735e37c111ae44b4b4; sealed sha256 eab5c7e9271c441e1057bb69250167589759ade1e2f818897b53a9062c86922b
- manifest NG_HOLDOUT2_MANIFEST.json sha256: 57d8ee56bf258b4af0691a2b5728b5c57dbe00d9e54929a2828be8d615cd7f4d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:31.169928+00:00 SEALED holdout 2 NG raw chunk range=2024-12-01_2025-01-01.dbn.zst

- product NG (NG.v.0), chunk 10 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 e110ca4826ea5901dec14bf9f93a4ad574e55b0b89e9bd34268b0bccd6c728d9; sealed sha256 84b3d1972e23ce292a93c2cb369904ef593897333c4dcffda0fbf7065cd4accb
- manifest NG_HOLDOUT2_MANIFEST.json sha256: ba49f3df5b452c1951997c7021c35994c4e3086e95926c89aa72997a2ae3f7bb
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:40.922016+00:00 SEALED holdout 2 NG raw chunk range=2025-01-01_2025-02-01.dbn.zst

- product NG (NG.v.0), chunk 11 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 e291c3a7b1aca72bda616f89b6c77d7bc4a9b60c3d7dbdc59aea4448613dafef; sealed sha256 079b8fe692fdc54da0c0f62eefab7d3e7c06033b7fad344731e71d650303fa89
- manifest NG_HOLDOUT2_MANIFEST.json sha256: fb845a18f323524b3192e61fd660c10ae919693f9bc263081ced9c573588d226
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:49.596373+00:00 SEALED holdout 2 NG raw chunk range=2025-02-01_2025-03-01.dbn.zst

- product NG (NG.v.0), chunk 12 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 a419dd5bafde17a9501836bae2a1be8138585979876d4174966c0859b7098f37; sealed sha256 844d154f09483cf5ba8fde8545b9429f6430936b06f9a30fe2ae3573c04e4897
- manifest NG_HOLDOUT2_MANIFEST.json sha256: fd8ace530de885d885e8d28c6c6700fdc6f92ee517a25ef488a43a86998d3111
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:31:56.986374+00:00 SEALED holdout 2 NG raw chunk range=2025-03-01_2025-04-01.dbn.zst

- product NG (NG.v.0), chunk 13 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 b2042d831ec6c09846a5311e45f7c15f507b1935fb1ef838e91cfa16b314ce53; sealed sha256 ef7c8cca59ed7aba92c17c42d9f9fde605007d6980f6845fe7f04a5410e74bcd
- manifest NG_HOLDOUT2_MANIFEST.json sha256: f4500dc896a59e28fa839ee04656c7f5a2f3f7d87215081e804e668a32b5587d
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:41:22.921759+00:00 SEALED holdout 2 MGC raw chunk range=2024-03-01_2024-04-01.dbn.zst

- product MGC (MGC.v.0), chunk 1 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 bd51ae9ff5a0938e801b041ce9d048ad26171a016b5449e4cd872926a0f2712c; sealed sha256 9ecdeb54a2ebc776b9d26f649326e67b9b4c1e06ff4814c54a733c1a01007ebc
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: a07b7077efb1752358528d2e552b88798e9930708eb0d76bfad29f37323b6ffb
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:41:30.978589+00:00 SEALED holdout 2 MGC raw chunk range=2024-04-01_2024-05-01.dbn.zst

- product MGC (MGC.v.0), chunk 2 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 852549e9868ed3eef2e539369cb6cb8d8d38ee7821b8866e46e6cdf2eeaa5c66; sealed sha256 80e1b445db135f61af34a8240d44839a7da1bc08b467f494d35b1b91362a11dd
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: abce5a625d586358b723fc2564d9a902f797260e31df2705ade802bf6bf87a76
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:41:51.221079+00:00 SEALED holdout 2 MGC raw chunk range=2024-05-01_2024-06-01.dbn.zst

- product MGC (MGC.v.0), chunk 3 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 778b26491bf08c83535ebdcd3b0e5934ddd9a5d25fc45daa0a28550048ce78a2; sealed sha256 e8ba7cdc0523d0ef0c7cdefdaa6bcce702c60456bba0c09f12b791bf98f2f755
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 8cbac5e2a830f2e1954d68b554b075fed67ddef0efb3525cefd5c78a5775f8d5
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:05.252849+00:00 SEALED holdout 2 MGC raw chunk range=2024-06-01_2024-07-01.dbn.zst

- product MGC (MGC.v.0), chunk 4 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 a2040471068dea9a93c82c70f3e0a8dbbba482b3df0b3d17d68c4f324c7dd6c1; sealed sha256 a5489208b71563ae77ceca0adbf12687c2dfe9afc8c7b85c538293b0e2ec62a8
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 230d829d2aa80ead6ed46dc98d59ea86c2eb55c7e3a14514501d498d988c2c76
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:14.681039+00:00 SEALED holdout 2 MGC raw chunk range=2024-07-01_2024-08-01.dbn.zst

- product MGC (MGC.v.0), chunk 5 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 1c9a7fc2e1e79abb8eb99205d763730e01a3d209ae226e59756b680654a78cf5; sealed sha256 0ab4f8c2811894dc469a682d3b299a8fe471f54460d6e533c951ab1f9df5eb69
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 8a8444389192d99c3772ea9db8a17c156341f5c6f904f084521c3722ab5dddd8
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:25.028371+00:00 SEALED holdout 2 MGC raw chunk range=2024-08-01_2024-09-01.dbn.zst

- product MGC (MGC.v.0), chunk 6 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 8b48eac8928aa88d589f6f173350c39e8a255562fd4ed8d1b6d862039ae1743a; sealed sha256 8a3adcda06032f1e9283cdfd13b18afffecf37eb14127b4237d7ee82d153d2e8
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: a75ace8e877f786ffeb20304f5d93e0a7b17bcfecd405c97c36704993f0674cc
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:35.594687+00:00 SEALED holdout 2 MGC raw chunk range=2024-09-01_2024-10-01.dbn.zst

- product MGC (MGC.v.0), chunk 7 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 91cab52a06baf11315c449d713c3ef57977c7b9562112166251ebb17bf47d477; sealed sha256 fb30e2ee16e5e2b5171d86814a2c2e8e3829183c996340d23a474e6a365bb39c
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 9f365882b7c28ce22c53622f2047113341510b4446622ffce911031b78c0cefe
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:43.526873+00:00 SEALED holdout 2 MGC raw chunk range=2024-10-01_2024-11-01.dbn.zst

- product MGC (MGC.v.0), chunk 8 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 d7fb830d516b0a2310968e84a4b42f224ecff811bc1f33a0829689b9333a00c2; sealed sha256 0fe7e8216dfc777a78f7b40937bf20bba6e3e38148bf3d9688c620b5da708712
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 29ba60caad07d372f1af84cbbdf98a8f171856855c29982866cfbdc9c4ee742e
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:42:50.570308+00:00 SEALED holdout 2 MGC raw chunk range=2024-11-01_2024-12-01.dbn.zst

- product MGC (MGC.v.0), chunk 9 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 e523c0091a9b94c7a6801a430b4e8ae7fd3fa8bc3a3045406d1fa88fe8111323; sealed sha256 53d638090a8e28b237b695e2c6b031940e84f25be90da461cc90bab6aac30beb
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 020534734c3a03eec44a0bcab014b5b461b22250bfa41f6723f8658fbddf709c
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:43:11.952216+00:00 SEALED holdout 2 MGC raw chunk range=2024-12-01_2025-01-01.dbn.zst

- product MGC (MGC.v.0), chunk 10 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 1f09c6032a90fedffe95cf626dfc72fb8b672f79ab938770eac2c1a997d378d8; sealed sha256 df76b5804bcf8c835b1553468097caba69393f7f8c0cab50d85acd43c21cb304
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: f31b9f775277f7dd54fa67b17f2eca9e6736870238069a14b3de3a73b3040c49
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:43:24.406441+00:00 SEALED holdout 2 MGC raw chunk range=2025-01-01_2025-02-01.dbn.zst

- product MGC (MGC.v.0), chunk 11 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6a890b55d0ba1322d845964b1df902ff1f75f8a402cbdfa89ac6e6ff41ca909c; sealed sha256 70a80b29e1a06047ee179fa62fc3694bfc8e173d20d7c7657d7032cff81e15ff
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 601992fd335e22ad74e22e000d056231f79e19f302854ed9fe820a016de0c9bd
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:43:32.548020+00:00 SEALED holdout 2 MGC raw chunk range=2025-02-01_2025-03-01.dbn.zst

- product MGC (MGC.v.0), chunk 12 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 63e51a678406d7c31c6cd1d7a444a3405a65420abdc898622f9a7da53f7e47ee; sealed sha256 b9c0d1625f3e4b3bd5b5b4c66d216814886144897d9f06ca0ac642fc51527540
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 4df677c042669d82c0534675fa5709290e06851ed4758100e9ab62d5f1ec6016
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:43:41.008776+00:00 SEALED holdout 2 MGC raw chunk range=2025-03-01_2025-04-01.dbn.zst

- product MGC (MGC.v.0), chunk 13 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6271e286c6b6a9bac54de8042b6dbaadeff9fd90c750071cd2799ee8a69a7fe2; sealed sha256 de717e8c6d67bad9945347c34a7817a2e0b505773b3b8d1abe9bf7b3dfdda908
- manifest MGC_HOLDOUT2_MANIFEST.json sha256: 4cea98f965510042cdf017b3f188d3ce5e253646587173279840e95744170fb5
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:47:49.292114+00:00 SEALED holdout 2 MHG raw chunk range=2024-03-01_2024-04-01.dbn.zst

- product MHG (MHG.v.0), chunk 1 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6c8d915af21a63907634a33380c6f2a26123dbbc510d0b009779b3a8787b6d76; sealed sha256 e4794095dad9254bec061249184ea2263b969997bb5cd4e9eeed3aa4b3331b26
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: 679739763f9fada6147a3ddd1e8d2b6ffaff8d93ffa2e1e09df850bb2e30e5af
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:47:57.008681+00:00 SEALED holdout 2 MHG raw chunk range=2024-04-01_2024-05-01.dbn.zst

- product MHG (MHG.v.0), chunk 2 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 9b538c3fd3f9cc9b30c20ce8346b1f679ec5f10ef27642b8b3954aac7e8d94f4; sealed sha256 ea88231fea4bbd0d1f5ce910024ff0e864e2b6c6690fb37b1c79936fff0ac717
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: 6c3cf244707b9beed85cc7411b4847eedeeab6315c56828d65e89d4acc01a1aa
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:06.370427+00:00 SEALED holdout 2 MHG raw chunk range=2024-05-01_2024-06-01.dbn.zst

- product MHG (MHG.v.0), chunk 3 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 b097d988875d70c4e3456ecc31ae92b35ea39d8f238a2749b56f0c4b64ad7e95; sealed sha256 7dbe005b631df6943f7bed4e04416a4ad9f3dcbea63d66ace29fe0eee0424f3d
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: 1d5ab3ccb16c245faf5dc2e50b28eb0599e13b41c245814285d6e96fd8238514
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:13.900942+00:00 SEALED holdout 2 MHG raw chunk range=2024-06-01_2024-07-01.dbn.zst

- product MHG (MHG.v.0), chunk 4 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 104cb6fde59d64b53d9d967a0f86b33f2c4a0638e4dc225c4861f517970f95be; sealed sha256 82b4477e88ba5db0bcfdcac013855213a052067bc6a642d02e23be9a5a0736e1
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: a50cb0618da96843437144c96498fc9a42fa6b927f89cae1a87734b62ce54350
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:21.666175+00:00 SEALED holdout 2 MHG raw chunk range=2024-07-01_2024-08-01.dbn.zst

- product MHG (MHG.v.0), chunk 5 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 2eb6e80d4681b5c7ac0eac20e24e65f4decbbb750b1c80cb2d36bac9e021a13a; sealed sha256 5b6ca9df899b71440833a703e7ea9536e88cdb4d86567863b0cd4e8d5b25b2eb
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: a532e5d6f90176053f93acd0c3053218c8b716f78165fe4271cc92e0f89d0c99
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:29.940805+00:00 SEALED holdout 2 MHG raw chunk range=2024-08-01_2024-09-01.dbn.zst

- product MHG (MHG.v.0), chunk 6 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 8be06d278db9ea1346d3ecedb2c91c1f92b954b02f323703c609c09d8a1f96dc; sealed sha256 7eb39fa9949af163b63f965c953daf37abf97db50bbbddb9a0105ab9e621cba3
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: eaecbfb9e6f7b7ef530999c74b4f9c3cdddf57fadfc9f2900aeb4589d82f64ea
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:41.754197+00:00 SEALED holdout 2 MHG raw chunk range=2024-09-01_2024-10-01.dbn.zst

- product MHG (MHG.v.0), chunk 7 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 093c4fd02fd0744bfc3ddc823e2dbaac5a8259e0e467c8cf9f218fdce8238f08; sealed sha256 6d66e3fba0a7578cc56130956ae2637958ae5c42b87673207abe54dbfebd8953
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: 0187a09104bc9596d8c7bb7f44684615b0891098b33713883cd6c49bca1b4719
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:51.892592+00:00 SEALED holdout 2 MHG raw chunk range=2024-10-01_2024-11-01.dbn.zst

- product MHG (MHG.v.0), chunk 8 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 777f4f67411b385d2a0d6a08a3f50b4301b34573e4d8465b8e83f706a02bc0c0; sealed sha256 cc39a9362e761c0a41c15c5883fa09f498f83da02201abeb96c69ba54fda2508
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: dea537e133ca83837c07d3719529acd440ebebdf767c427473e87b36deeb7f1f
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:48:59.256915+00:00 SEALED holdout 2 MHG raw chunk range=2024-11-01_2024-12-01.dbn.zst

- product MHG (MHG.v.0), chunk 9 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 d1a5e1909dd511feafce7dfe5508ce676dd4948b3b1ec10109ef968ffa66b117; sealed sha256 9d976a47ff31dd831624b6e7ecf7b924cd9dd3867ddbf98d0d6331d844c908a6
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: b3c030027461a59cf847772ad0f997b5929ced820fbf688db9117072f4a819b0
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:49:09.826122+00:00 SEALED holdout 2 MHG raw chunk range=2024-12-01_2025-01-01.dbn.zst

- product MHG (MHG.v.0), chunk 10 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 e571627d94914a98156f7936c24e568155786c7dfaa8e02791b80164630ede99; sealed sha256 17e80b298b2597ac06fc7731704ab5c032b1904565ff621d8104f6c0981f1f64
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: 7b09b5b95060f563195dba099ed8a78647551b23eee8860f268631bfc8f8e685
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:49:16.417806+00:00 SEALED holdout 2 MHG raw chunk range=2025-01-01_2025-02-01.dbn.zst

- product MHG (MHG.v.0), chunk 11 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 6e6962dcb901cadfb6876eb88b0d842dd42ead1d517c98ae255771c45226af34; sealed sha256 5f2061ce6f7897c8fd8baf8b09672f675815d004f3d898cb9e788a454e3e0277
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: c91d0f7e75dbbf84160f8f630f22d366b3969488b7e9cb6276c2be67ee1a73d1
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:49:23.541985+00:00 SEALED holdout 2 MHG raw chunk range=2025-02-01_2025-03-01.dbn.zst

- product MHG (MHG.v.0), chunk 12 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 b9e16b9f2a127278314accefab3c2fa59fd05fb409358fe66ae281ae0fdc21dd; sealed sha256 6f7a20d6e278a7f6556bd1ef0da6e827b943fcd73b34a2c9f2cfa7556feeb140
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: e945c8114e33b6e62be23cc27d0c689dc5faedfd7f0220030599322c12f5f538
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87

## 2026-09-28T01:49:33.049142+00:00 SEALED holdout 2 MHG raw chunk range=2025-03-01_2025-04-01.dbn.zst

- product MHG (MHG.v.0), chunk 13 of 13, sealed on arrival in the download call, oldest first
- plaintext sha256 95be408752c581317154f9d9769aff39b49c78ea745ecf55cf06121ec1127744; sealed sha256 35fc5cfa015581b7122e9463fd190fb01c6d478363598e82bb96139e75823490
- manifest MHG_HOLDOUT2_MANIFEST.json sha256: aee129d984b1aa7cdbc4a4e83eb1b5647df6c8c19ba4fc86cffd5e1ad20e0c54
- the sealed copy on disk decrypted back to the plaintext sha256 before removal
- harness sha256 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87
