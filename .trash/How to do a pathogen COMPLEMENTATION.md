2025-07-23
**END RESULT:**
---
date: '[[2025-07-23]]'
modified: []
---

<<[[2025-07-22]] - [[2025-07-24]]>>

# TODAY'S NOTES:

## To do today:


Links: Facility-logs, check OUTLOOK tasks!
[[phibase-tasks]]
Link to [B63-Teams-channel- Facilities](https://teams.microsoft.com/l/channel/19%3A-eJMUlzePuJio_E7enJy8YEQgVHf8tF7j0oYMictctQ1%40thread.tacv2/General?groupId=0f5a19dc-6009-4ce6-8d21-e2530b68a74c&tenantId=b6883625-8941-4342-b0e3-7b8cc8392f64)


# EXPERIMENTS-ACTIVE
```dataview
TABLE Title, StartDate as "Start date"
FROM ("01-EXPERIMENTS")
WHERE Completed != true
```


> [!example] Today's Notes
```dataview
table without id
file.link as Note,
file.folder as Folder,
file.mtime as "Last Modified"
FROM -"Dailies"
where file.mtime > (date(now) - dur(12 hours))
sort file.mtime desc
```

---
date-created: 2025-07-23
date-modified: 2025-07-23
title: How to do a pathogen COMPLEMENTATION
tags: []
Project:
type:
status:
Related:
people:
source: internal
alias:
---





**Choose either:**
- [ ]  Ectopic - for in planta tests
- [ ]  not assayed - for in in vitro tests

>[! FUTURE CHANGE] 
>There should be a possibility to select 'nothing'. Currently if no selection is done, then we cannot click 'OK'.


# **STEPS:**
## 1. go HOME: to article **SUMMARY**

![[Pasted image 20250723113504.png|300]]

## 2. select **Annotate genotypes / PATHOGEN GENOTYPE MANAGMENT**
   
   ![[Pasted image 20250723113931.png]]
   
 
## 3. Select gene for complementation

In this case **Gene** FG05398.1, the choose **Actions** 'Other genotype'

![[Pasted image 20250723114403.png|400]]
Enter into 'Allele name' field: 'cdc25delta - CDC25 transformant 
**Choose 'Strain used'**

**Choose 'Allele type': 'transformant'**
Enter text for **Allele description**: **complemented by re-introducing the wild-type allele at an ectopic locus**


![[Pasted image 20250723115028.png]]



## Final result:

![[Pasted image 20250723121328.png]]