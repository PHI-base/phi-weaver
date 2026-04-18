-- Sample data for PHI-Canto tracking database
-- Based on the Fusarium effectors project already in the vault

USE phi_canto_tracking;

-- Insert sample species
INSERT INTO species (name, type, taxonomy_id, common_name, notes) VALUES
('Fusarium graminearum', 'pathogen', 229533, 'wheat head blight fungus', 'Major cereal pathogen, teleomorph Gibberella zeae'),
('Triticum aestivum', 'host', 4565, 'wheat', 'Common wheat, major crop plant'),
('Arabidopsis thaliana', 'host', 3702, 'thale cress', 'Model plant organism'),
('Nicotiana benthamiana', 'host', 4100, 'tobacco', 'Common host for transient expression studies');

-- Insert sample articles from Fusarium effectors research
INSERT INTO articles (pmid, title, journal, pub_year, authors, status, curator, obsidian_note_path) VALUES
('38234567', 'FgTPP1 effector manipulates host immunity in Fusarium graminearum', 'Plant Pathology', 2024, 'Smith et al.', 'curated', 'martin.urban', '04-Literature/FgTPP1-effector-2024.md'),
('38456789', 'Characterization of FgSCP effector protein in wheat pathogenesis', 'Molecular Plant Pathology', 2024, 'Jones et al.', 'in_progress', 'martin.urban', '04-Literature/FgSCP-characterization-2024.md'),
('37123456', 'Fg62 effector targets host transcription factors', 'Nature Plants', 2023, 'Brown et al.', 'queued', NULL, '04-Literature/Fg62-transcription-targets.md');

-- Insert sample proteins from Fusarium effectors project
INSERT INTO proteins (gene_id, species_id, name, gene_name, function_summary, protein_type, obsidian_note_path) VALUES
('FGSG_11164', 1, 'Trehalose-6-phosphate phosphatase', 'FgTPP1', 'Effector that manipulates host trehalose metabolism and immune responses', 'effector', '02-Projects/Fusarium-effectors/proteins/FgTPP1.md'),
('FGSG_08454', 1, 'Secreted cysteine-rich protein', 'FgSCP', 'Small secreted effector with unknown host targets', 'effector', '02-Projects/Fusarium-effectors/proteins/FgSCP.md'),
('FGSG_01831', 1, 'Fg62 effector protein', 'Fg62', 'Targets host transcription factors to suppress immunity', 'effector', '02-Projects/Fusarium-effectors/proteins/Fg62.md'),
('FGSG_03895', 1, 'OSP24-like effector', 'OSP24', 'Outer spore protein with potential effector function', 'effector', NULL),
('FGSG_02847', 1, 'Nuclear localization signal protein', 'FgNls1', 'Effector with nuclear targeting capability', 'effector', NULL);

-- Insert sample curation sessions
INSERT INTO curation_sessions (session_date, curator, article_id, session_duration_hours, proteins_curated, interactions_added, experiments_annotated, notes, obsidian_session_log) VALUES
('2026-04-12', 'martin.urban', 1, 2.5, 3, 5, 8, 'Literature review and initial protein characterization for FgTPP1', '11-CLAUDE-AI/SESSION-LOGS/2026-04-12-fusarium-effectors-2.md'),
('2026-04-11', 'martin.urban', NULL, 1.5, 0, 0, 0, 'Vault setup and project initialization', '11-CLAUDE-AI/SESSION-LOGS/2026-04-11-vault-setup.md'),
('2026-04-18', 'martin.urban', 2, 1.0, 1, 2, 3, 'Working on FgSCP characterization', NULL);

-- Insert protein-article relationships
INSERT INTO protein_article_mentions (protein_id, article_id, mention_context, experimental_evidence, curated) VALUES
(1, 1, 'Main subject protein with detailed functional analysis', 'complementation', TRUE),
(2, 2, 'Primary focus with structural and functional studies', 'knockout', FALSE),
(3, 3, 'Transcription factor targeting mechanism described', 'biochemical', FALSE),
(1, 2, 'Mentioned in comparison with other effectors', 'other', FALSE);

-- Show some example queries to demonstrate how it works
-- These are comments for reference, not executed

/*
-- View current curation progress
SELECT * FROM curation_progress WHERE date >= '2026-04-01';

-- Find all effector proteins for Fusarium
SELECT p.*, s.name as species_name
FROM proteins p
JOIN species s ON p.species_id = s.id
WHERE p.protein_type = 'effector' AND s.name LIKE '%Fusarium%';

-- Check article curation status
SELECT
    a.title,
    a.status,
    a.curator,
    COUNT(pam.id) as protein_mentions
FROM articles a
LEFT JOIN protein_article_mentions pam ON a.id = pam.article_id
GROUP BY a.id, a.title, a.status, a.curator;

-- Species summary
SELECT * FROM species_summary;
*/