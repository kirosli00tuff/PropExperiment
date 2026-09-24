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
