---
created: {{date}}
type: literature
tags: [literature, status/{{status}}]
project: {{project}}
pmid: {{pmid}}
curator: {{curator}}
priority: {{priority}}
---

# {{title}}

## Article Information

| Field | Value |
|-------|-------|
| **PMID** | [{{pmid}}](https://pubmed.ncbi.nlm.nih.gov/{{pmid}}) |
| **DOI** | {{doi}} |
| **Journal** | {{journal}} |
| **Year** | {{year}} |
| **Authors** | {{authors}} |
| **Curator** | {{curator}} |
| **Status** | {{status}} |
| **Priority** | {{priority}} |

## Curation Status

- [ ] Article reviewed and analyzed
- [ ] Pathogen-host interactions identified
- [ ] Protein functions characterized
- [ ] Experimental evidence documented
- [ ] PHI-base entries created
- [ ] Quality review completed

## Pathogen-Host System

| Component | Species | Details |
|-----------|---------|---------|
| **Pathogen** | *{{pathogen_species}}* | {{pathogen_details}} |
| **Host** | *{{host_species}}* | {{host_details}} |
| **Interaction Type** | {{interaction_type}} | {{interaction_description}} |

## Proteins/Genes of Interest

### {{protein_1_name}} ({{gene_id_1}})

- **Function**: {{protein_1_function}}
- **Role in Pathogenesis**: {{protein_1_role}}
- **Experimental Evidence**: {{protein_1_evidence}}
- **UniProt ID**: {{uniprot_id_1}}
- **PHI-base Entry**: {{phi_base_id_1}}

### {{protein_2_name}} ({{gene_id_2}})

- **Function**: {{protein_2_function}}
- **Role in Pathogenesis**: {{protein_2_role}}
- **Experimental Evidence**: {{protein_2_evidence}}
- **UniProt ID**: {{uniprot_id_2}}
- **PHI-base Entry**: {{phi_base_id_2}}

## Experimental Methods

### Key Experiments
- {{experiment_1}}
- {{experiment_2}}
- {{experiment_3}}

### Evidence Quality
- **Complementation**: {{complementation_evidence}}
- **Knockout/Deletion**: {{knockout_evidence}}
- **Overexpression**: {{overexpression_evidence}}
- **Biochemical**: {{biochemical_evidence}}
- **Phenotype**: {{phenotype_evidence}}

## Curation Notes

### Summary
{{curation_summary}}

### Key Findings
- {{finding_1}}
- {{finding_2}}
- {{finding_3}}

### Challenges/Issues
{{challenges}}

### Related Literature
- [[{{related_paper_1}}]]
- [[{{related_paper_2}}]]
- [[{{related_paper_3}}]]

## Database Entries

### Articles Table
```sql
UPDATE articles SET 
    status = '{{status}}',
    curator = '{{curator}}',
    updated_date = CURRENT_TIMESTAMP
WHERE pmid = '{{pmid}}';
```

### Proteins Added/Updated
- {{protein_list}}

### Interactions Documented
- {{interaction_list}}

## Session Logs
{{session_references}}

---

**Curation Workflow:**
1. ✅ Literature analysis completed
2. ✅ Proteins identified and characterized  
3. ✅ Experimental evidence evaluated
4. ✅ Database entries created
5. ✅ Quality review completed

**Next Steps:** {{next_steps}}

**Links:**
- [[08-Wiki/Article-Registry|Back to Article Registry]]
- [[08-Wiki/Curation-Protocols/Standard-Process|Curation Protocol]]