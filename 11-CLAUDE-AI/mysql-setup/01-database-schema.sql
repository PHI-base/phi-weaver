-- PHI-Canto Tracking Database Schema
-- Simple hybrid approach to complement Obsidian vault

-- Create database
CREATE DATABASE phi_canto_tracking;
USE phi_canto_tracking;

-- Core entities table for species (hosts and pathogens)
CREATE TABLE species (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    type ENUM('host', 'pathogen') NOT NULL,
    taxonomy_id INT,
    common_name VARCHAR(255),
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Literature articles being curated
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pmid VARCHAR(20) UNIQUE,
    doi VARCHAR(255),
    title TEXT NOT NULL,
    journal VARCHAR(255),
    pub_year INT,
    authors TEXT,
    status ENUM('queued', 'in_progress', 'curated', 'reviewed', 'published') DEFAULT 'queued',
    curator VARCHAR(100),
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    obsidian_note_path VARCHAR(500), -- Link to Obsidian note
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Proteins/genes being studied
CREATE TABLE proteins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gene_id VARCHAR(50),
    uniprot_id VARCHAR(20),
    species_id INT,
    name VARCHAR(255),
    gene_name VARCHAR(100),
    function_summary TEXT,
    protein_type ENUM('effector', 'resistance', 'virulence', 'other'),
    obsidian_note_path VARCHAR(500), -- Link to Obsidian note
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (species_id) REFERENCES species(id)
);

-- Track curation work sessions
CREATE TABLE curation_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_date DATE NOT NULL,
    curator VARCHAR(100) NOT NULL,
    article_id INT,
    session_duration_hours DECIMAL(4,2),
    proteins_curated INT DEFAULT 0,
    interactions_added INT DEFAULT 0,
    experiments_annotated INT DEFAULT 0,
    notes TEXT,
    obsidian_session_log VARCHAR(500), -- Link to session log
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- Track protein-article relationships
CREATE TABLE protein_article_mentions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    protein_id INT,
    article_id INT,
    mention_context TEXT,
    experimental_evidence ENUM('complementation', 'knockout', 'overexpression', 'biochemical', 'other'),
    curated BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (protein_id) REFERENCES proteins(id),
    FOREIGN KEY (article_id) REFERENCES articles(id),
    UNIQUE KEY unique_protein_article (protein_id, article_id)
);

-- Simple progress tracking view
CREATE VIEW curation_progress AS
SELECT
    DATE(cs.session_date) as date,
    cs.curator,
    COUNT(cs.id) as sessions,
    SUM(cs.proteins_curated) as total_proteins,
    SUM(cs.interactions_added) as total_interactions,
    SUM(cs.session_duration_hours) as total_hours
FROM curation_sessions cs
GROUP BY DATE(cs.session_date), cs.curator
ORDER BY cs.session_date DESC;

-- Species summary view
CREATE VIEW species_summary AS
SELECT
    s.type,
    COUNT(s.id) as species_count,
    COUNT(p.id) as protein_count
FROM species s
LEFT JOIN proteins p ON s.id = p.species_id
GROUP BY s.type;