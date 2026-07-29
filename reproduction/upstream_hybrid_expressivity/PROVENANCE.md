# Upstream implementation provenance

These files are a mechanically copied, evaluator-visible snapshot of the
authors' public implementation:

- repository: `https://github.com/SprocketLab/hybrid-expressivity`
- audited Git SHA: `7beeb0de80f89eb5d75301aef8e97ee9b36ca999`
- source subtree: `micro_hf/`
- retrieval date: 2026-07-28

The only source edit is the package-relative import in `data_utils.py`.
`models/__init__.py` is intentionally narrowed to the three model files used
here so unrelated upstream modules are not required. `LICENSE.upstream` is
copied from the public repository.

SHA-256 before the relative-import edit:

| Upstream path | SHA-256 |
|---|---|
| `micro_hf/models/hybrid.py` | `2b6dff0c91cf2b7b207ec14662459ef9a9f412aa665da6690b7cfa5dda73d867` |
| `micro_hf/models/mamba.py` | `4ba25f6c703e1d5e899e1bb2f5832d7bb246f51d2a821275c2f20e796aaf2aed` |
| `micro_hf/models/rope.py` | `d08732e63cbddb148b1c3a692278994cf42b86de98274957844e4ab9d6fdfa2c` |
| `micro_hf/generate.py` | `f2fb47708ec954eab60afbd67a408398bfa63cb7a424620314938c3349763bf7` |
| `micro_hf/data_utils.py` | `81d6852fcd00980a98e8206f9ee516831f94abffb041f7164f71fba284798bc1` |

