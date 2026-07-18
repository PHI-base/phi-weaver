---
created: 2026-05-07
type: inbox
tags: [inbox]
project: PHI-Canto
---

# PHI-Canto documentation

This document contains the new documentation pages that were written for PHI-Canto (as of 5 May 2022). Note that most of the pages in PHI-Canto’s documentation are reused from the version of Canto used by PomBase, and those pages are not included here. The complete documentation can be viewed online at <https://canto.phi-base.org/docs/index>.

# Table of contents

-   Starting a session
-   Adding genes
-   Adding strains
-   Creating genotypes
-   Creating metagenotypes (multi-species genotypes)
-   Annotating genes
    -   Gene Ontology annotations
    -   Protein modification
    -   Physical interaction
    -   RNA level
    -   Protein level
-   Annotating genotypes
    -   Pathogen phenotype
    -   Host phenotype
    -   The phenotype curation process
-   Annotating metagenotypes
    -   Pathogen-host interaction phenotype
    -   The phenotype curation process
    -   Gene-for-gene phenotype
    -   Disease name
-   Experimental evidence
-   Experimental conditions
-   Annotation extensions
-   Finishing a session

# Getting started

## Finding a publication

To start a curation session in Canto, enter the PubMed ID of your chosen publication in the search box on the left of the page. Note that the ‘PMID:’ prefix is optional.

![](Z:\OBS-25-MU-Feb\Writage/d7c3291ac9d8f614be76dbd3729f7fcf.png)

## Starting a session

When you enter a curation session in Canto, you will see a message with a few basic details about the paper and how to proceed:

![](Z:\OBS-25-MU-Feb\Writage/8e991f6b25062d22f1ffdaeb8101f97b.png)

If you want to delegate curation to someone else (e.g. the first author or another current lab member), click “Reassign paper”, and fill in the name and email address of the intended recipient on the next page.

Otherwise, click “Start curating”, confirm your name, email address, and (optionally) your [ORCID](http://orcid.org/) on the next page, then continue. After starting the session, you will receive an email reminding you of the curation session link and basic instructions.

![](Z:\OBS-25-MU-Feb\Writage/986c33a3a8202f87383fab0b8bbbe796.png)

Note: you can also begin curation and then reassign a session later; there is a “Reassign” button near the upper right corner of the page:

![](Z:\OBS-25-MU-Feb\Writage/86f6c4b465731f1697d9fa0151120590.png)

Once you have begun a session, your session will be preserved at a stable URL, so you do not need to complete the curation in one go. Most pages have at least one ‘?’ icon, which links to help documentation (mouse over to see a brief description). You can use the ‘Contact curators’ link at any point if you get stuck, or have any questions.

## Adding genes and organisms

To start curating a paper, you will first be asked to supply a UniProtKB accession number for each gene from your publication:

![](Z:\OBS-25-MU-Feb\Writage/9463424cfac64801bac1c4e6f99c89dd.png)

In the case where your publication contains host organisms with no genes specified, you can pick these hosts using the organism picker below the gene entry field (you can search for hosts by scientific name, common name, or NCBI Taxonomy ID):

![](Z:\OBS-25-MU-Feb\Writage/01a59403a46e6a5841ed82b0fee2e6df.png)

### Finding genes in UniProtKB

PHI-Canto uses [UniProt Knowledgebase](https://www.uniprot.org/help/uniprotkb) (UniProtKB) gene accession numbers to disambiguate genes/proteins. This is to ensure that we are talking about the correct gene product – especially because the same names are sometimes used for different proteins – and to standardize entries, because not all strains of an organism are in UniProt.

1.  **Identify the reference proteome** (we use the designated reference proteome to integrate different strain information at the gene level in PHI-base). In PHI-Canto you will be able to specify the strain you used.
-   Look up the reference proteome for your organism using the species name (<https://www.uniprot.org/help/reference_proteome>).
-   If there is no reference proteome, use the strain studied.
1.  **Identify the gene of interest in the reference proteome**
-   Start from the [UniProt homepage](https://www.uniprot.org/), then perform any of the following steps:
    -   Search for the author assigned gene name/primary name (e.g. Tri5) or synonyms, plus species name (e.g *Fusarium graminearum*).
    -   If the gene does not have a ‘given name’ but a locus ID is provided, search using the locus_id (e.g. FGRRES_03537) plus species name (e.g. *Fusarium graminearum*). If the entry identifier used is not the reference strain, copy the protein sequence and go to the BLAST step below.
    -   Search on a protein description (e.g. Trichodiene synthase)
    -   Obtain the protein sequence for your gene of interest and BLAST against UniprotKB (<https://www.uniprot.org/blast/>) with your protein sequence.  
        **Note:** If there are multiple entries for your gene product from the reference strain, please select the ‘Reviewed entry’. Use the left hand filter for ‘Reviewed entries’.
    -   If the gene cannot be located in UniProt, contact the authors, UniProt, or PHI-base for help locating the canonical database entry.
1.  **Add the entry into PHI-Canto.** Once the entry of interest is located, select the entry accession number (also called ‘Entry’) from column 1 of the results table, and use this to retrieve the entry into PHI-Canto on the gene entry page. Be careful not to confuse the ‘Entry’ column with the ‘Entry name’ column. PHI-Canto uses the accession number to retrieve details (such as the gene name, gene product, and organism). If PHI-Canto is unable to find your entry, check for typos (e.g. 0 for O), ensure you are using the ‘entry’ not ‘entry name’, and check that your accession is from UniProtKB, not UniParc.

![](Z:\OBS-25-MU-Feb\Writage/7976b3d374d4c098a5c6f1fa142dac0c.png)

### Information not valid for curation

If the paper does not mention individual genes – which is typical of methods papers, many types of high-throughput study, reviews – check the box labeled ‘This paper does not contain any gene-specific information’, and select a reason from the pulldown that appears.

![](Z:\OBS-25-MU-Feb\Writage/4c9a6e6509b7398973789ee53dbc809a.png)

Complete the session by clicking ‘Continue’ and then ‘Finish’. Further comment is optional.

If the paper mentions specific genes, but does not contain any data that can be curated in Canto for them (see Curating specific data types), enter the genes and finish the session as described below (see Finishing and submitting).

Please note that you should only curate information supported by experiments in the paper you are curating. If you want to capture other information not directly shown in a particular paper, please contact the curators (contact@phi-base.org) to discuss how to proceed.

## Adding strains

Once you have specified your genes and any host organisms (with no specified genes), the next screen will allow you to confirm the genes and organisms that have been retrieved from UniProt.

![](Z:\OBS-25-MU-Feb\Writage/2c0dcfad73a7075776e91c0a4ba28f8b.png)

The next step is to add one or more ‘experimental strains’ for every organism in your curation session. Note that for the purposes of PHI-Canto, the term *strain* is used broadly to refer to any taxonomic classifier more specific than a species. This includes (but is not limited to): subspecies, varieties, pathovars, cultivars, and strains in the conventional sense.

You can add experimental strains using the strain picker that is located below each pathogen and host on the page:

![](Z:\OBS-25-MU-Feb\Writage/674ab060e9f6286bc6c43db0e159cf62.png)

You can select a strain from the list by using your mouse or the arrow keys on the keyboard (use Enter or Tab to confirm a strain with the keyboard). Typing a strain name into the text input will filter to the list of strains to match what you typed:

![](Z:\OBS-25-MU-Feb\Writage/4a2f7970812570010a3695aeb257d855.png)

If you want to add a strain that is not in the list, type its name into the text input, then click the ‘Add strain’ button, or hit Enter on your keyboard. Custom strains will be highlighted in orange once added:

![](Z:\OBS-25-MU-Feb\Writage/9b0225f06434155eecd9e00c76de6663.png)

Use the ‘Unknown strain’ button if the publication does not specify a strain for the organism (or does not describe the organism more specifically than its species).

To delete a strain, click the cross symbol next to the strain name. Note that you will be unable to delete a strain if it is used by other genotypes in the curation session.

Note: if your new strain contains background mutations, please do not specify these in the strain name unless it is conventional for the strain name to include the names of other mutations. Otherwise, you should specify background mutations using the ‘Background’ information on a genotype (see Creating alleles and genotypes).

Once you have specified strains for each organism, you can continue to the curation summary page; from there, you can annotate genes and genotypes with the annotation types described in this article.

## Curating specific data types

Annotations in PHI-Canto are divided into three types: gene annotations, genotype annotations, and metagenotype annotations. Follow the links below for specific instructions.

### Gene annotations

-   **GO molecular function**: A molecular function is a catalytic (e.g. protein serine/threonine kinase activity, pyruvate carboxylase activity) or binding activity, or any other activity that occurs at the molecular level.
-   **GO biological process**: A biological process is a series of events accomplished by one or more ordered assemblies of molecular functions, such as cell cycle regulation, ion transport, or signal transduction.
-   **GO cellular component**: Cellular components include subcellular structures and macromolecular complexes, such as nucleus, nuclear inner membrane, nuclear pore, and proteasome complex.
-   **protein modification**: A protein modification is a covalent modification or other change that alters the measured molecular mass of a peptide or protein amino acid residue.
-   **physical interaction**: Examples: co-purification, two-hybrid, affinity capture.

### Genotype annotations

See the Creating alleles and genotypes documentation for instructions on creating genotypes.

-   **pathogen phenotype**: Annotate normal or abnormal phenotypes of pathogen organisms with this genotype.
-   **host phenotype**: Annotate normal or abnormal phenotypes of host organisms with this genotype.

### Metagenotype annotations

See the Creating alleles and genotypes documentation for instructions on creating metagenotypes.

-   **pathogen-host interaction phenotype**: Annotate normal or abnormal phenotypes of organisms within this pathogen-host interaction (metagenotype).

## Finishing and submitting

When you have finished entering data from your paper, click the ‘Submit to curators’ button on the right-hand side of the Curation Summary page:

![](Z:\OBS-25-MU-Feb\Writage/58200174d92d1cce1e7be19b26b03f62.png)

To submit a curation session that does not contain any annotations based on experimental data, check the ‘No experimental results to add?’ checkbox, then select a reason from the pulldown menu that appears:

![](Z:\OBS-25-MU-Feb\Writage/187cc75219cf176e64fa2a752d287242.png)

After you have clicked ‘Submit to curators’, you will see a text box in which you can put any comments or questions for the curators (this is optional):

![](Z:\OBS-25-MU-Feb\Writage/7cdd35455b95f970a2ce5f31b39bc1c0.png)

After you click ‘Finish’, you will not be able to make any further changes to your session. However, you can view the annotations in the session at any time. If you need to make any further changes to your curation session after submission, please contact the PHI-Canto curation team.

# Creating alleles and genotypes

## Pathogen or Host Genotype Management

The Genotype Management pages are used to create genotypes containing one or more alleles. To start creating genotypes, follow the ‘Pathogen genotype management’ link or the ‘Host genotype management’ link from the curation summary page, depending on whether you want to create genotypes for a pathogen or a host.

![](Z:\OBS-25-MU-Feb\Writage/dc642e94daa44745269c3c2b9b0149c3.png)

Once on the page, If you have more than one organism in the session, the first thing you will need to do is select the organism that you want to create a genotype for:

![](Z:\OBS-25-MU-Feb\Writage/bf865f306574155012b94327cd752a6f.png)

After selecting an organism, a table of its genes will appear below.

![](Z:\OBS-25-MU-Feb\Writage/2f111071cb98c39bc78c31ca91810b53.png)

### Creating single-allele genotypes

For each gene, you can use the ‘Deletion’ button as a shortcut to add a single-allele deletion genotype. For other allele types, you can use the ‘Other genotype…’ button to show a pop-up that allows you to create single-allele genotypes.

![](Z:\OBS-25-MU-Feb\Writage/0dd59eb366b26f9e48acb9120657e25b.png)

1.  **Allele name:** this field is optional. Fill this in if the allele is named, e.g. TRI5-1-499. For the *wild type* and *deletion* allele types, a default name will be assigned. For other types, the allele will be denoted ‘unnamed’ if no name is provided. As you type the allele name, an autocomplete list will appear if there are matches to any alleles already in Canto’s database. If your allele name appears, you can select it, and its type and description will be filled in; you will only have to choose the expression level.
2.  **Allele type:** choose an allele type from the drop-down list. If the specific mutations are not known, choose ‘unknown’. If the alterations are complex (for instance, a mixture of insertions, point mutations, etc.), choose ‘other’ and describe the changes as free text.
3.  **Allele description:** for some allele types, e.g. *partial deletion* or *substitution*, further description is required. In these cases, an example description will be displayed in the box as grey text. You should number nucleotide positions starting with the ‘A’ of the initiator ATG for protein-coding genes. Mutations in promoter regions can also be specified by prefixing the numbers with a hyphen ‘-’ sign.
4.  **Expression:** you will be prompted to define the expression level relative to wild-type (deletion mutants are automatically set to null). Note that ‘expression’ refers to the amount of gene product present in the assayed cells. If the product level was not measured (e.g. by Western blot for a protein), choose ‘Not assayed’, even if a construct such as an inducible promoter was used to try to alter expression.
5.  **Descriptions for ‘unknown’ alleles:** if you know the description for any allele that is listed as ‘unknown’ in Canto, please enter it. To do so, type in the allele name, but do not select anything from the autocomplete list. Instead, proceed as if no match had been found, and you will be able to choose a type and enter a description.

As you add alleles, each will appear in a table on the right (any single alleles added via the Single Allele Phenotype option on the gene page will also appear here):

![](Z:\OBS-25-MU-Feb\Writage/d6fbc3d016b736b6e83a39a3bd85e6da.png)

### Creating multi-locus genotypes

Genotypes containing multiple alleles are not created directly; rather, they are created by combining single-allele genotypes.

To create a multi-allele genotype, first add all of the constituent single alleles to the single-allele table. Then select two or more alleles by ticking the boxes at the left side of the table. Selecting two or more alleles will enable the ‘Combine selected genotypes’ button:

![](Z:\OBS-25-MU-Feb\Writage/eda6150d17879e0c6de0d983a4989dc5.png)

Click the button to combine the selected genotypes into a multi-allele genotype. The new multi-allele genotype will appear in a separate table below:

![](Z:\OBS-25-MU-Feb\Writage/f9726c2727c1ad6e7fbdf3b1333b2a29.png)

#### Using wild-type alleles in genotypes

Generally speaking, a wild-type gene at its normal (endogenous) expression level should not be annotated with a phenotype unless the gene is expressed at a higher level (overexpression) or lower level (knockdown) than normal. Additionally, wild-type genes with normal expression should not be included in multi-allele genotypes unless they are over- or under-expressed.

Wild-type genes with normal expression level may be used in a metagenotype, but only where the metagenotype is used as an experimental control for a pathogen-host interaction (a control metagenotype). The control metagenotype, and its corresponding phenotype, are necessary to disambiguate naturally-occurring phenotypes (caused by strain sequence variation in the natural strain) from experimental phenotypes (caused by mutations introduced by the author). Note that in PHI-Canto, the normal expression level is called the ‘wild type product level’ when creating an allele. See the section on Creating control metagenotypes for details on how to create experimental controls.

### Editing and copying genotypes

When you mouse over any genotype in either table, a set of options appears in a popup:

![](Z:\OBS-25-MU-Feb\Writage/3c9d2e09b7050cca66f745f1bae886af.png)

**Start a pathogen / host phenotype annotation:** begins the workflow to add a pathogen or host phenotype for the selected genotype (see ‘Curating phenotypes’ for more details).

**View annotations:** links to a page that shows details for the selected genotype, plus any phenotype annotations associated with the genotype. Links are available to edit the details of the selected genotype, or to quickly create an additional genotype using the copy and edit function (by following the ‘Duplicate’ link). Links are also available to edit existing annotations on the selected genotype (Edit); create new annotations based on existing ones (Copy and edit); or remove existing annotations (Delete). You can also create new phenotype annotations by following the link in the ‘Actions’ section.

**Edit details:** links to a page where you can edit the details of the selected genotype, such as its name, background mutations, strain, and comments. You can also add, edit, or remove alleles for the genotype.

**Copy and edit:** links to the genotype editing page as described above, but creates a new genotype with the amended details after the editing is complete (annotations are not copied to the new genotype).

**Add/edit background:** display a text box that can be used to specify background alleles. If any background alleles have been previously specified, they can be edited by changing the text. Background alleles can be removed by deleting all the text from the text box. Background alleles will appear in a column in the genotype table:

![](Z:\OBS-25-MU-Feb\Writage/a5a7ebf11ed3c5cdca356c1caf9c14f8.png)

Note: If your genotype is from a strain that already includes the names of background alleles, you do not need to specify the names of background alleles in the Background field.

Note: If a single allele has a background, the background will be included with any multi-allele genotype that uses the allele. If two or more alleles have backgrounds, the backgrounds will be combined in the multi-allele genotype (alleles with duplicate backgrounds will only be included once). To change the background, use one of the ‘Add/edit background’, ‘Edit details’, or ‘Copy and edit’ options.

**Delete:** delete the selected genotype. The action is disabled for any genotype that has phenotype annotations. To delete a genotype with annotations, first delete the annotations (you can view the annotations with the ‘View annotations’ link, or by returning to the curation summary page).

## Metagenotype Management

The *metagenotype* is an abstract concept that combines a pathogen genotype with a host genotype: it is the underlying genotype of a pathogen–host interaction. Metagenotypes are annotated with *pathogen–host interaction phenotypes*.

Metagenotypes are created by combining genotypes: a pathogen genotype and a host genotype are selected, then combined to form a new metagenotype. In Canto, you can create metagenotypes by following the Metagenotype Management link on the curation summary page or the Genotype Management page.

![](Z:\OBS-25-MU-Feb\Writage/99fb8813f4a0f8f195e98671967cae80.png)

Since every metagenotype requires a pathogen and host genotype, you cannot access the Metagenotype Management page until you have created at least one pathogen genotype (the wild-type host genotypes are always available by default).

Once you enter the Metagenotype Management page, if you have more than one organism in your session, the first thing you need to do is select the pathogen and host organisms that will be part of the metagenotype:

![](Z:\OBS-25-MU-Feb\Writage/92165692b2da212bebd573263cd35bff.png)

If you only have one pathogen or one host, they will be selected by default. After selecting an organism, a table of its genotypes will be shown (unless the organism has no genotypes).

### Creating metagenotypes

You can select a pathogen or host genotype by clicking the radio buttons next to the rows of the genotype tables.

![](Z:\OBS-25-MU-Feb\Writage/8e944cbac07a0ba68dcef40ecb63b1d0.png)

After picking one genotype from the pathogen side and one from the host side, you will be able to create a metagenotype by clicking the ‘Make metagenotype’ button:

![](Z:\OBS-25-MU-Feb\Writage/0cb767db01a6385ace3c1a5092c286de.png)

Host organisms may have no alleles (and therefore no genotypes). In this case, the Metagenotype Management page will show a list of the strains that have been added to the session for that organism. This list represents the wild-type genotypes for each particular strain. The wild-type host genotypes can be selected in the same way as mutant host genotypes (by clicking the radio button next to the row).

![](Z:\OBS-25-MU-Feb\Writage/dbe96b3f466f13593d4020bea9ae8f76.png)

Selecting a host strain has the intent of describing an interaction between the wild-type host (of the specified strain) with some mutant pathogen. It is not necessary to select the strain for a mutant genotype, because this strain information is always embedded in the mutant genotype itself.

#### Creating control metagenotypes

Before annotating a metagenotype with a pathogen-host interaction phenotype (or gene-for-gene phenotype), you should first create a *control metagenotype*, which contains the control genotypes for the pathogen and the host. The control genotypes will usually, but not always, contain wild-type alleles of the genes of interest.

After the control metagenotype is created, you should create another metagenotype that describes mutant alleles within either the pathogen genotype, host genotype, or both genotypes simultaneously (the experimental metagenotype can be linked to the control metagenotype by way of an annotation extension, which is described in Curating phenotypes).

Please note there may be cases where it is not possible to create a control metagenotype: for example, where an empty vector (without a pathogen gene) is infiltrated into a plant leaf as a control experiment.

### Managing metagenotypes

Each row of the metagenotype table (shown at the bottom of the Metagenotype Management page) has links for common actions:

![](Z:\OBS-25-MU-Feb\Writage/86b4c8b69133ecaf523249ea8e6939af.png)

**Annotate pathogen-host interaction phenotype:** begin the workflow to create a pathogen-host interaction phenotype annotation (see ‘Curating phenotypes’ for more details). After completing the annotation, you will be taken to the metagenotype details page.

**Annotate gene-for-gene phenotype:** begin the workflow to create a gene-for-gene interaction phenotype annotation (see ‘Curating phenotypes’ for more details). After completing the annotation, you will be taken to the metagenotype details page.

**View phenotype annotations:** show a details page for the selected metagenotype, plus any phenotype annotations associated with the metagenotype. You can edit, copy and edit, or delete phenotype annotations on this page. New phenotype annotations can be created by following the link in the ‘Actions’ section.

(Please note that it is not possible to edit the selected metagenotype from the Metagenotype Details page. Edits can only be made to the pathogen or host parts of the metagenotype by using the Genotype Management pages.)

**Delete:** delete the selected metagenotype. The action is disabled for any metagenotype that has phenotype annotations. To delete a metagenotype with annotations, first delete the annotations (you can view the annotations with the ‘View phenotype annotations’ link, or by returning to the curation summary page).

# Curating phenotypes

## Introduction

A phenotype is any observable characteristic or trait of an organism that results from the interactions between its genotype and the environment. PHI-Canto supports annotation of single- and multi-allele phenotypes on pathogen genotypes, host genotypes and metagenotypes (pathogen and host genotype), using terms from PHIPO (the Pathogen-Host Interaction Phenotype Ontology) and additional useful details such as evidence and experimental conditions.

When using PHIPO terms – or terms from any ontology – always pay careful attention to the term definitions. They are usually more detailed, and often more informative, than the term names alone. For each annotation, ensure that the definition of the selected term accurately describes the experiment you are trying to capture, and that the results shown in the paper fit all parts of the term definition.

If you want to browse terms in PHIPO, you can use any of the term browsers linked to from PHIPO’s page on the [OBO Foundry](https://obofoundry.org/ontology/phipo) (for example, OntoBee or OLS). The OBO Foundry also provides downloads of PHIPO in OWL and OBO formats.

## Starting a phenotype annotation

### Single-species phenotypes

#### Genotype Management workflow

Using the Pathogen Genotype Management or Host Genotype Management pages, you can make phenotype annotations to a genotype of a single species. These genotypes can be either single-allele or multi-allele:

-   A single allele is a mutation, or set of mutations, in one copy of a gene at one locus (which may be the endogenous locus or a different locus, such as a plasmid or an insertion at a non-native position). You can also annotate under- or over-expression of the wild type allele as a single ‘mutation’.
-   You can also annotate phenotypes on a double mutant, triple mutant, or any strain in which more than one gene has its sequence or expression altered, including any case where you have more than one allele of the same gene present (e.g. one on the chromosome, and another on a plasmid). To do so, you must enter details of all relevant alleles in the genotype (background details such as mating type and markers are optional).

You can begin a phenotype annotation after creating a genotype (following the instructions in Creating alleles and genotypes). After the genotype is created, you should see a menu appear with a list of actions. Select ‘Start a pathogen/host phenotype annotation’, then continue by following the steps in ‘The phenotype curation process’ section (see below).

![](Z:\OBS-25-MU-Feb\Writage/84035473f8506a65da3117f6f2ed8868.png)

#### Single allele workflow

If you only need to annotate the phenotype of a single allele, you can select a gene from the list of genes on the curation summary page, then select ‘Single allele phenotype’ from the list of curation types:

![](Z:\OBS-25-MU-Feb\Writage/f73ee696021035a1d9887d030a1917ae.png)

After selecting the option, a pop-up will appear where you can enter allele details:

![](Z:\OBS-25-MU-Feb\Writage/5f531adeead974130d951d1cdbd4f071.png)

After selecting ‘OK’, you will begin the phenotype curation process for the allele you have created (see ‘The phenotype curation process’ below).

### Pathogen-host interaction phenotypes

To annotate a phenotype on a pathogen-host interaction (a metagenotype), go to the Metagenotype Management page and select either ‘Annotate pathogen-host interaction phenotype’ or ‘Annotate gene-for-gene phenotype’ from the list of actions next to the relevant metagenotype.

![](Z:\OBS-25-MU-Feb\Writage/86b4c8b69133ecaf523249ea8e6939af.png)

Note that you must first have created a metagenotype; see Creating alleles and genotypes for instructions.

#### Curating pathogen effectors

If you are curating a pathogen effector within a pathogen–host interaction, it is essential that you also make a GO Biological Process annotation on the pathogen gene involved in the interaction, using the GO term “effector-mediated modulation of host process by symbiont” ([GO:0140418](http://purl.obolibrary.org/obo/GO_0140418)) or one of its child terms. This will allow the data to be displayed correctly in PHI-base.

Where the molecular function of the effector is known, you will also need to annotate a GO Molecular Function on the pathogen gene. This molecular function annotation must have a ‘part_of’ annotation extension that links to GO:0140418 or any of its child terms. See the instructions for Gene Ontology Annotation for further guidance on making GO annotations.

## The phenotype curation process

### Selecting a PHIPO term

PHIPO consists of two branches: a single-species branch, which includes phenotypes associated with either pathogen or host species in isolation; and a pathogen-host interaction branch, which includes phenotypes associated with the outcomes of pathogen-host interactions. Pathogen genotypes can be annotated with single-species phenotype terms, such as ‘sexual spores absent’ and ‘decreased hyphal growth’, as well as chemistry phenotypes, such as ‘resistance to voriconazole’, ‘sensitive to voriconazole’, and ‘normal growth on voriconazole’. Host genotypes can also be annotated with single-species terms, such as ‘presence of effector-independent host hypersensitive response’. Metagenotypes can be annotated with pathogen-host interaction phenotype terms, such as ‘absence of pathogen growth on host surface’ and ‘stunted host growth during pathogen colonization’. Note that some terms in the pathogen-host branch describe changes in the pathogen, while other terms describe changes in the host.

To find a PHIPO term, type text into the search box. When suggestions from the autocomplete feature appear, choose one and proceed.

![](Z:\OBS-25-MU-Feb\Writage/ded054f100f3288413f30eb0f96f1827.png)

If your initial search does not find any suitable terms, try again with a broader term (e.g. ‘reproductive phenotype’). Selecting a term takes you to a page where you can read the definition to confirm that it is applicable. More specific ‘child’ terms will be shown (where available), and you can select one of these more specific terms in an iterative process.

![](Z:\OBS-25-MU-Feb\Writage/5ce4cc89323b68c1fed2635bff004922.png)

PHIPO terms are organized in a hierarchical structure, and annotations with PHIPO should be as specific as possible to describe the data from your experiment. You can request a new term if the most specific term available does not adequately describe your disease. Select the ‘Suggest a new child term’ link and fill in the form that is shown:

![](Z:\OBS-25-MU-Feb\Writage/ef0ec80f5a3512805ffb7fc8bcdfa302.png)

### Experimental evidence

After you choose a term, you will be prompted to select an experimental evidence code from a pulldown menu:

![](Z:\OBS-25-MU-Feb\Writage/dd6568aaffcc9b048745136c2d280f51.png)

### Experimental conditions

After selecting experimental evidence, you can optionally enter any experimental conditions. It is not necessary to record all of the experimental conditions, just those that are key to the experiment.

Conditions are aspects of the experimental setup that may be relevant to various different methods, and are independent of what cells, strain, organism, etc. are used. Examples include:

-   Minimal medium vs. rich medium
-   Agar plates vs. liquid medium
-   Delivery mechanism (e.g. agrobacterium, heterologous organism, pathogen inoculation)
-   Addition of certain chemicals; for instance, in a salt stress experiment it may be of interest to note what salts were added. (Note that in cases where the PHIPO term already describes sensitivity or resistance to a certain chemical, it is not necessary to specify that same chemical in the experimental conditions.)
-   Temperature (high, standard or low).
-   Exclusion of some chemicals that one might normally expect to be present.

To add conditions, type text and select from the autocomplete options. Several conditions can be added for one experiment.

![](Z:\OBS-25-MU-Feb\Writage/9543f6fd7a29a5ad70faaabcbf12096d.png)

Condition terms previously used in the session appear below the text box and can be reused by selecting them:

![](Z:\OBS-25-MU-Feb\Writage/c5708ccc1f0256fb33b3655a4aed91f4.png)

It is also possible to add experimental conditions that do not appear in the autocomplete list. To do this, type your experimental condition, then either click inside the text box, or hit Enter or Tab on your keyboard. The condition should change to a tag:

![](Z:\OBS-25-MU-Feb\Writage/5fddc2462218ded46fdc69ebaa78acb5.png)

PHI-Canto will display custom experimental conditions in red text, pending their review by an expert curator before they are added to the main list of experimental conditions.

### Finalizing the annotation

Once you have entered all the data for your annotation, you will see a confirmation page that shows a preview of your annotation before it is created. For single-species phenotypes, the annotation preview will look like this:

![](Z:\OBS-25-MU-Feb\Writage/0a646036eb23f33444fb30aaf9bbedf6.png)

For pathogen-host interaction phenotypes and gene-for-gene phenotypes, the preview will look like this:

![](Z:\OBS-25-MU-Feb\Writage/30adf4defa4eb3d9a87a594fef989e5a.png)

### Figure and table numbers

The confirmation page includes a text box for including the Figure or Table number related to the annotation. Please prefix figure numbers with ‘Figure’ and table numbers with ‘Table’. Prefix supplementary figure and table numbers with an ‘S’, for example: ‘Figure S1’.

### Annotation comments

The confirmation page also has a text box where you can add additional information as a comment on each annotation. We recommend that comments include any details that do not fit the available evidence codes.

The data in the comments section will not be shown on the PHI-base website; the comments are intended to facilitate the checking of a session by the approval team (PHI-base and carefully selected species experts) prior to approval of the curated session.

Once you select ‘OK’ on this screen, your annotation will be saved. You can then either make further annotations, pause the session and come back to it later, or submit the completed curation session for approval.

## Annotation extensions

You can add annotation extensions to provide additional specificity for PHIPO annotations (see below for specific examples). After you have selected an ontology term and evidence, the PHI-Canto interface will display a list of available extension types (if no extension types are available, this step is skipped, and you will go straight to the annotation summary page).

Select an extension type to show a pop-up where you can specify the required details for the extension. For example, an annotation to ‘abolished pathogen penetration into host’ can have any of these extensions:

![](Z:\OBS-25-MU-Feb\Writage/c66a1fbfeaff44ed7dd29795fc5a121f.png)

You can add multiple extension types to one annotation, but be aware that this has the effect of saying that *all* the extensions apply to the annotation at once (usually meaning all extensions were present together at some point in time).

If the extensions did *not* occur together (for example, if different tissues were infected in two separate experiments, rather than both infected at once), then you should apply the extensions to separate annotations. You can use ‘Copy and edit’ on an annotation to speed up the process of adding individual extensions: finish the first annotation with one extension, copy-and-edit to create another annotation, then edit the extensions on the new annotation.

After adding an annotation extension, the extension name shown in annotation tables (and elsewhere) will be a more concise unique identifier.

When you edit or duplicate an annotation, you can also add more extensions, or remove existing extensions. Use the ‘Edit…’ button in the annotation editing pop-up to do this:

![](Z:\OBS-25-MU-Feb\Writage/3e686a93f5e5c7b15cbf1035f461c622.png)

It is not possible to edit an existing extension; instead, you must delete the existing extension (by clicking the red cross next to the extension name), then add a new extension.

![](Z:\OBS-25-MU-Feb\Writage/4c5aeadec1ee025ee816f2a8358a1bf8.png)

PHI-Canto supports the following extensions for phenotype annotations:

#### Pathogen or Host phenotype extensions

-   **Penetrance:** the proportion of a population that shows the phenotype. The penetrance measurement can be qualitative or quantitative. The pulldown menu for qualitative options is selected by default. For a quantitative value, switch the radio button and enter a percentage (e.g. 38%) in the text box.
-   **Severity:** Only qualitative values are supported; choose from the pulldown menu. (Note: severity was previously called ‘expressivity’, and can still be used in the sense of the extent to which a phenotype is expressed.)
-   **Assayed feature:** A specific gene, RNA or protein, used in an assay. The pulldown menu is populated with genes from the list you entered for the paper. You can add another gene at this point if necessary.

#### Pathogen-host interaction phenotype extensions

-   **Host tissue infected:** relates a pathogen-host interaction to the tissue type (or anatomical region) where the interaction occurred. Terms describing the tissue types are specified by the [BRENDA Tissue Ontology](https://brenda-enzymes.org/ontology.php?ontology_id=3).
-   **Infective ability:** relates a pathogen-host interaction phenotype with one of the set of high-level phenotype terms from PHI-base, and describes the overall change in factors like pathogenicity and virulence. For example, the phenotype ‘abolished pathogen penetration into host’ can be extended with ‘loss of pathogenicity’, such that the phenotype was an effect of a change in the infective ability of the pathogen.
-   **Compared to control genotype:** records a pathogen genotype and a host genotype (combined as a metagenotype) that are used as an experimental control for the genotypes in the interaction. Usually the control genotypes will be the wild-type genotypes of the pathogen and host, but they may also be mutant genotypes.
-   **Outcome of interaction:** describes the overall outcome of the interaction in terms of whether disease was present or absent in the host.

#### Gene-for-gene phenotype extensions

-   **Host tissue infected:** relates a pathogen-host interaction to the tissue type (or anatomical region) where the interaction occurred. Terms describing the tissue types are specified by the [BRENDA Tissue Ontology](https://brenda-enzymes.org/ontology.php?ontology_id=3).
-   **Compared to control genotype:** records a pathogen genotype and a host genotype (combined as a metagenotype) that are used as an experimental control for the genotypes in the interaction. Usually the control genotypes will be the wild-type genotypes of the pathogen and host, but they may also be mutant genotypes.
-   **Gene-for-gene interaction:** describes multiple properties of a gene-for-gene interaction, including: whether a gene conferring disease resistance in the host was present, absent, or compromised; the presence or absence of a pathogen effector molecule that can be recognized by the host; and whether the interaction caused disease in the host (a compatible interaction) or did not (an incompatible interaction).
-   **Inverse gene-for-gene interaction:** describes multiple properties of an inverse gene-for-gene interaction, including: whether a gene conferring disease susceptibility in the host was present, absent, or compromised; the presence or absence of a pathogen necrotrophic effector molecule that can be recognized by the host susceptibility locus; and whether the interaction caused disease in the host (a compatible interaction) or did not (an incompatible interaction).

## Editing, deleting and duplicating phenotypes

**Edit:** If you want to make changes to an annotation you have made, use the ‘Edit’ link next to the annotation in the table. In the pop-up edit the appropriate fields, then select ‘OK’.

![](Z:\OBS-25-MU-Feb\Writage/9b34388c8c674d0c0b220c6dedb7e40a.png)

**Transfer:** this link allows you to copy the phenotype annotation to one or more genotypes or metagenotypes in the session. Single species phenotypes can be transferred to other genotypes, and pathogen-host interaction phenotypes can be transferred to other metagenotypes. You can choose to include or exclude the annotation extensions of the original annotation on the new annotations.

![](Z:\OBS-25-MU-Feb\Writage/11f032366e50023f1c5ff155dc7344ea.png)

**Copy and edit:** this link allows you to copy an annotation to another genotype or metagenotype, or to create a new annotation with minor edits on the same genotype or metagenotype. For example, you may want to indicate that you have observed a phenotype under more than one set of conditions, e.g. at both standard and high temperatures. The interface works the same way as editing an annotation, except that a new annotation is created, and the old annotation is retained without changes.

The ‘Copy and edit’ action differs from the ‘Transfer’ action in that you can edit the annotation before copying it.

![](Z:\OBS-25-MU-Feb\Writage/91ebd6fa7553d62423516e06bcd2d9a9.png)

**Delete:** The ‘Delete’ link deletes the annotation.

# Curating disease names

## Introduction

PHI-Canto allows curation of infectious diseases that result from pathogen–host interactions. An infectious disease is defined as ‘a disorder resulting from the presence and activity of a microbial, viral, fungal, or parasitic agent […] transmitted by direct or indirect contact.’ ([NCIT:C26726](http://purl.obolibrary.org/obo/NCIT_C26726)) PHI-Canto supports annotation of disease names on metagenotypes (a combination of pathogen and host genotype), using terms from the [PHI-base Disease Ontology](https://github.com/PHI-base/phido) (PHIDO).

Each metagenotype containing a wild type gene should be annotated with at least one disease annotation (assuming a disease name is known). Diseases should only be annotated on pathogen–host interactions where the disease is present: that is, with a susceptible host strain and a compatible pathogen strain. The host must also be a natural host for the pathogen (i.e. not a model host). The annotated tissue type should correspond to where the disease is normally expected to be observed: for example, *Fusarium ear blight* would normally be observed on an *inflorescence* ([BTO:0000628](http://purl.obolibrary.org/obo/BTO_0000628)).

When using PHIDO terms – or terms from any ontology – always pay careful attention to the term definitions. They are usually more detailed, and often more informative, than the term names alone. For each annotation, ensure that the definition of the selected term accurately describes the experiment you are trying to capture, and that the results shown in the paper fit all parts of the term definition.

## Starting a disease annotation

To annotate a disease on a pathogen-host interaction (a metagenotype), go to the Metagenotype Management page and select ‘Annotate disease name’ from the list of actions next to the relevant metagenotype.

![](Z:\OBS-25-MU-Feb\Writage/95b6fb334fadd91120250850dced5d1e.png)

Note that you must first have created a metagenotype; see Creating alleles and genotypes for instructions.

## The disease curation process

### Selecting a term

Next, to find a PHIDO term, type text into the search box. When suggestions from the autocomplete feature appear, choose one and proceed.

![](Z:\OBS-25-MU-Feb\Writage/e49e12e3e4cf3c4212d9d8b4e0d244d2.png)

If your initial search does not find any suitable terms, try again with a broader term (e.g. ‘blight’ or ‘bacterial’). Selecting a term takes you to a page where you can read the definition to confirm that it is applicable.

Annotations with PHIDO should be as specific as possible to describe the data from your experiment. You can request a new term if the most specific term available does not adequately describe your disease. Select the ‘Suggest a new child term’ link and fill in the form that is shown:

![](Z:\OBS-25-MU-Feb\Writage/ef0ec80f5a3512805ffb7fc8bcdfa302.png)

### Annotation extensions

You can add annotation extensions to provide additional specificity for PHIDO annotations (see below for specific examples). After you have selected an ontology term and evidence, the PHI-Canto interface will display a list of available extension types.

Select an extension type to show a pop-up where you can specify the required details for the extension:

![](Z:\OBS-25-MU-Feb\Writage/f274f21459b6579d2167d79a75775a54.png)

You can add multiple extension types to one annotation, but be aware that this has the effect of saying that *all* the extensions apply to the annotation at once (usually meaning all extensions were present together at some point in time).

If the extensions did *not* occur together (for example, if different tissues were infected in two separate experiments, rather than both infected at once), then you should apply the extensions to separate annotations. You can use ‘Copy and edit’ on an annotation to speed up the process of adding individual extensions: finish the first annotation with one extension, copy-and-edit to create another annotation, then edit the extensions on the new annotation.

After adding an annotation extension, the extension name shown in annotation tables (and elsewhere) will be a more concise unique identifier.

When you edit or duplicate an annotation, you can also add more extensions, or remove existing extensions. Use the ‘Edit…’ button in the annotation editing pop-up to do this:

![](Z:\OBS-25-MU-Feb\Writage/0a88349947f45018b4ac974f5566686d.png)

It is not possible to edit an existing extension; instead, you must delete the existing extension (by clicking the red cross next to the extension name), then add a new extension.

![](Z:\OBS-25-MU-Feb\Writage/3a8c892d17ae62e8a57f5b72206ebaf6.png)

PHI-Canto supports the following extensions for disease annotations:

-   **Host tissue infected:** relates a disease annotation to the tissue type (or anatomical region) where the disease occurred. Terms describing the tissue types are specified by the [BRENDA Tissue Ontology](https://brenda-enzymes.org/ontology.php?ontology_id=3).

### Finalizing the annotation

Once you have entered all the data for your annotation, you will see a confirmation page that shows a preview of your annotation before it is created. The annotation preview will look like this:

![](Z:\OBS-25-MU-Feb\Writage/a00810ca2827759e8c89f59f66a572d0.png)

### Figure and table numbers

The confirmation page includes a text box for including the Figure or Table number related to the annotation. Please prefix figure numbers with ‘Figure’ and table numbers with ‘Table’. Prefix supplementary figure and table numbers with an ‘S’, for example: ‘Figure S1’.

![](Z:\OBS-25-MU-Feb\Writage/55dea2dfd6ff0e79a14d2d8c2bf1938e.png)

### Annotation comments

The confirmation page also has a text box where you can add additional information as a comment on each annotation. We recommend that comments include any details that do not fit the available evidence codes.

The data in the comments section will not be shown on the PHI-base website; the comments are intended to facilitate the checking of a session by the approval team (PHI-base and carefully selected species experts) prior to approval of the curated session.

Once you select ‘OK’ on this screen, your annotation will be saved. You can then either make further annotations, pause the session and come back to it later, or submit the completed curation session for approval.

## Editing, deleting and duplicating disease annotations

**Edit:** If you want to make changes to an annotation you have made, use the ‘Edit’ link next to the annotation in the table. In the pop-up edit the appropriate fields, then select ‘OK’.

![](Z:\OBS-25-MU-Feb\Writage/d6cf0a7ea3a7b84db23181d7b65c0559.png)

**Copy and edit:** this link allows you to copy an annotation to another metagenotype, or to create a new annotation with minor edits on the same metagenotype. For example, you may want to indicate that you have observed the same disease at the same tissue type in a different organism. The interface works the same way as editing an annotation, except that a new annotation is created, and the old annotation is retained without changes.

![](Z:\OBS-25-MU-Feb\Writage/be8ad9d2f4cf14813a0cd549911a0666.png)

**Delete:** The ‘Delete’ link deletes the annotation.

# Curating Physical Interactions

If you have physical interactions to curate, please read the Directionality section carefully.

We recommend that you only annotate interactions that you think are biologically meaningful. For example, do not include known or suspected contaminants from mass spectrometry results (e.g. ribosomal proteins, translation factors, ‘sticky’ proteins).

When you choose ‘Physical interaction’, a popup appears with a dropdown menu for the species involved in the interaction. To curate an interspecies interaction, select different species for each field. To curate an intraspecies (or intra-organism) interaction, select the same species in both fields. Note that only species added to the curation session can be selected. After selecting the first species, the rest of the form fields will appear, including a text field for optional comments.

Choose the gene for the first species in the ‘Gene’ field and the gene for the interacting species in the ‘Interacting gene’ field. Choose an evidence type from the ‘Interaction type’ dropdown menu. Some evidence types have a brief description that indicates their directionality. Further information on evidence supporting physical interactions, including examples of experiment types in each category, is available on the [BioGRID help wiki](https://wiki.thebiogrid.org/doku.php/experimental_systems) and in the Directionality section below.

Click ‘OK’ to finish the annotation and close the popup. An example of a completed physical interaction annotation is shown below.

![](Z:\OBS-25-MU-Feb\Writage/06cf6012486e10f4e7e3e9b1e93b1abf.png)

Note that only pairwise genetic interactions can be annotated in PHI-Canto.

## Directionality

Some experiments that detect physical interactions have an inherent directionality. For example, in a typical two-hybrid experiment one protein (A) is fused to a DNA binding domain and a second (B) is fused to a transcription activation domain. The reciprocal experiment, with A fused to the activation domain and B fused to the DNA binding domain, may or may not have been done.

For such asymmetric interactions, PHI-Canto allows you to curate in only one direction starting from the gene you select first, as indicated in the interaction type selector.

If the evidence description looks the wrong way around, you will have to change genes and start again (you can finish and then delete an interaction annotation if you find that you have started with the wrong gene).

| Evidence                                      | Relationship (A → B)                   |
|-----------------------------------------------|----------------------------------------|
| Affinity Capture-Luminescence                 | affinity captures                      |
| Affinity Capture-MS                           | affinity captures                      |
| Affinity Capture-RNA                          | affinity captures                      |
| Affinity Capture-Western                      | affinity captures                      |
| Far Western                                   | captures                               |
| FRET (fluorescence resonance energy transfer) | fluorescence resonance energy donor to |
| Protein-peptide                               | binds to peptide                       |
| Protein-RNA                                   | binds to RNA                           |
| Two-hybrid                                    | binds activation domain construct with |

Use one of the Affinity Capture evidence types for co-immunoprecipitation. If you have done the experiment in both directions, you should curate two annotations to describe the interaction completely. Curate starting from one gene, then switch genes to annotate the reciprocal experiment. Other experiment types are symmetric and therefore only need to be entered once, and you can start from either of the interacting genes.

| Evidence                                       | Relationship (A → B) |
|------------------------------------------------|----------------------|
| Co-crystal Structure                           | co-crystallizes with |
| Co-fractionation                               | co-fractionates with |
| Co-purification                                | co-purifies with     |
| Reconstituted Complex                          | forms complex with   |
| PCA\* (protein-fragment complementation assay) | interacts with       |

\* Note that PCA is not exactly symmetric, since there will be one N-terminal and one C-terminal reporter fusion construct, but it is treated as symmetric in PHI-Canto.
