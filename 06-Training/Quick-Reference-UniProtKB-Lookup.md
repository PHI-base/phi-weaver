---
created: 2026-04-21
type: quick-reference
tags: [uniprot, gene-lookup, reference-card]
project: PHI-Canto
---

# UniProtKB Gene Lookup - Quick Reference

## 🔍 Search Strategies

| Method | Format | Example |
|--------|--------|---------|
| **Gene Name** | `[gene] [species]` | `Tri5 Fusarium graminearum` |
| **Locus Tag** | `[locus] [species]` | `FGRRES_03537 Fusarium graminearum` |
| **Function** | `[description] [species]` | `trichodiene synthase Fusarium graminearum` |
| **BLAST** | Protein sequence | Use when above searches fail |

## ⚡ Quick Steps

1. **Search**: Use gene name + species in UniProt search
2. **Filter**: Check "Reviewed" for Swiss-Prot entries  
3. **Verify**: Confirm species, gene name, function match
4. **Copy**: Entry accession (P12345) **NOT** entry name (TRI5_FUSGR)
5. **Paste**: Accession into PHI-Canto

## 🎯 Entry vs Entry Name

| ✅ USE THIS | ❌ DON'T USE |
|-------------|-------------|
| **Entry**: P12345 | **Entry Name**: TRI5_FUSGR |
| **Entry**: Q9XYZ1 | **Entry Name**: CUTB_FUSSO |

## 🏆 Selection Priority

1. **Reviewed** + Reference proteome
2. **Reviewed** + Study strain  
3. **Unreviewed** + Reference proteome
4. **Unreviewed** + Study strain

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **No results** | Try broader terms, check spelling |
| **Multiple entries** | Choose reviewed from reference proteome |
| **Wrong species** | Add species name to search |
| **Gene not found** | Try BLAST with protein sequence |
| **PHI-Canto error** | Check Entry vs Entry Name, typos |

## 📍 Key URLs

- **UniProt**: <https://www.uniprot.org/>
- **BLAST**: <https://www.uniprot.org/blast/>
- **Reference Proteomes**: <https://www.uniprot.org/help/reference_proteome>

## 💡 Pro Tips

- **Use quotes** for exact gene names: `"AVR-Pik"`
- **Filter early** with "Reviewed" checkbox
- **Check synonyms** in gene name sections
- **Note proteome ID** for consistency across related genes
- **BLAST unknown genes** - often faster than manual search

## 🔗 PHI-Canto Integration

**PHI-Canto expects**: UniProtKB accession only
**Auto-retrieves**: Gene name, description, organism details
**Result**: Standardized gene identification across database

---
*Keep this card handy during curation sessions for quick gene lookups*